import typer
from typing_extensions import Annotated
from pathlib import Path
from rich.progress import track
from rich.console import Console
from langchain_openai import OpenAIEmbeddings

from .llms import get_llm
from .chains import build_chain
from .prompts import readings_list_to_str
from .rag import get_apparatus_db, get_teidoc_db, get_db, get_similar_verses
from vorlagellm.tei import (
    read_tei,
    get_siglum,
    add_siglum,
    get_language,
    get_verses,
    get_reading_permutations,
    get_verse_text,
    add_witness_readings,
    write_tei,
    add_wit_detail,
    find_elements,
    reading_has_witness,
    write_elements,
    find_parent,
)

console = Console()

app = typer.Typer()

DEFAULT_MODEL_ID = "gpt-4o"
DEFAULT_EMBEDDING_MODEL_ID = "text-embedding-3-large"

@app.command()
def add(
    doc: Path, 
    apparatus: Path,
    output:Path,
    hf_auth:Annotated[str, typer.Argument(envvar=["HF_AUTH"])]="",
    openai_api_key:Annotated[str, typer.Argument(envvar=["OPENAI_API_KEY"])]="",
    model_id:str=DEFAULT_MODEL_ID,
    apparatus_db:Path=None,
    doc_db:Path=None,
    siglum:str="",
    include:list[str]=None,
    window:int=3,    
):
    llm = get_llm(hf_auth=hf_auth, openai_api_key=openai_api_key, model_id=model_id)
    doc_path = doc
    doc = read_tei(doc_path)
    apparatus_path = apparatus
    apparatus = read_tei(apparatus_path)

    # Add as witness to apparatus
    siglum = siglum or get_siglum(doc)
    assert siglum, f"Could not determine siglum in '{doc_path}'. Please add a siglum to the TEI XML or add a siglum in the command line with --siglam"
    add_siglum(apparatus, siglum)

    # Get languages
    doc_language = get_language(doc)
    assert doc_language, f"Could not determine language of document {doc_path}"

    apparatus_language = get_language(apparatus)
    assert apparatus_language, f"Could not determine language of apparatus {apparatus_path}"

    # Create database for apparatus
    if doc_db:
        embeddings_model = OpenAIEmbeddings(model=DEFAULT_EMBEDDING_MODEL_ID)
        doc_db = get_teidoc_db(doc, model=embeddings_model, path=doc_db)
            
    # if apparatus_db:
    #     apparatus_db = get_apparatus_db(apparatus, model=embeddings_model, path=apparatus_db)

    # Create chain to use
    chain = build_chain(llm, doc_language=doc_language, apparatus_language=apparatus_language)

    verses = get_verses(apparatus)
    if include:
        verses = [v for v in verses if v in include]

    for verse in verses:
    # for verse in track(verses):
        print("Processing verse", verse)
        permutations = get_reading_permutations(apparatus, verse)
        if len(permutations) < 2:
            continue
        readings = readings_list_to_str([permutation.text for permutation in permutations])
        text = get_verse_text(doc, verse)

        similar_verse_examples = ""
        
        if doc_db:
            similar_verses = get_similar_verses(doc_db, verse, window=window)
            similar_verse_examples = (
                f"Here are {len(similar_verses)} similar texts to the one that you need to analyze. "
                f"You will see the {doc_language} language text and then all potential {apparatus_language} source texts. "
                f"Even though might not clear which {apparatus_language} was the actual source, consider the translation technique going from {apparatus_language} to {doc_language}.\n"
                "See the way that the translator has translated particular words and gramatical constructions. \n\n"
            )
            for example_index, similar_verse in enumerate(similar_verses):
                similar_verse_permutations = get_reading_permutations(apparatus, similar_verse)
                similar_readings = readings_list_to_str([similar_verse_permutation.text for similar_verse_permutation in similar_verse_permutations])
                similar_verse_examples += (
                    f"{apparatus_language} example {example_index+1} [{similar_verse}]:\n{similar_verses[similar_verse].page_content}\n"
                    f"Available {apparatus_language}:\n{similar_readings}\n\n"
                )

            similar_verse_examples += (
                f"Here again is the {doc_language} text to analyze:\n '{text}'\n"
                f"Here again is list of potential {apparatus_language} readings:\n{readings}\n"
            )           
        
        console.print(f"[bold]{verse}: [blue]{text}")
        results, justification = chain.invoke(dict(
            text=get_verse_text(doc, verse),
            readings=readings,
            similar_verse_examples=similar_verse_examples,
        ))

        for index, permutation in enumerate(permutations):
            if index in results:
                console.print(f"[bold green]✓ {permutation.text}")
                add_witness_readings(permutation.readings, siglum)
            else:
                console.print(f"[grey62]𐄂 {permutation.text}")

        if justification:
            apps = set()
            for permutation in permutations:
                apps.update(permutation.apps)
            add_wit_detail(apps, siglum, justification)
                
            console.print(justification, style="blue")

        # Write TEI XML output
        print("Writing TEI XML output to", output)
        write_tei(apparatus, output)

    return apparatus


@app.command()
def doc_db(
    doc: Path, 
    db:Path,
):
    embeddings_model = OpenAIEmbeddings(model=DEFAULT_EMBEDDING_MODEL_ID)
    doc_path = doc
    doc = read_tei(doc_path)    
    db = get_teidoc_db(doc, model=embeddings_model, path=db)
    return db


@app.command()
def similar(
    db:Path,
    verse:str,
    window:int=3,
):
    embeddings_model = OpenAIEmbeddings(model=DEFAULT_EMBEDDING_MODEL_ID)
    db = get_db(None, embeddings_model, db)
    similar_verses = get_similar_verses(db, verse, window=window)
    
    console.print(f"Similar verses to [bold red]{verse}[/bold red]:")
    for similar_verse, doc in similar_verses.items():
        console.print(f"[green]{similar_verse}[/green]: {doc.page_content}")


@app.command()
def evaluate(
    apparatus:Path,
    gold_siglum:str,
    prediction_siglum:str,
    false_positives:Path=None,
    false_negatives:Path=None,
):
    apparatus = read_tei(apparatus)
    readings = find_elements(apparatus, ".//rdg")
    tp = sum(reading_has_witness(reading, gold_siglum) and reading_has_witness(reading, prediction_siglum) for reading in readings)
    fp = sum(reading_has_witness(reading, prediction_siglum) and not reading_has_witness(reading, gold_siglum) for reading in readings)
    fn = sum(reading_has_witness(reading, gold_siglum) and not reading_has_witness(reading, prediction_siglum) for reading in readings)
    recall = tp / (tp + fn)
    precision = tp / (tp + fp)
    f1 = 2 * (precision * recall) / (precision + recall)
    console.print(f"Recall: {recall:.1%}")
    console.print(f"Precision: {precision:.1%}")
    console.print(f"F1: {f1:.1%}")

    if false_positives:
        fp_readings = [reading for reading in readings if reading_has_witness(reading, prediction_siglum) and not reading_has_witness(reading, gold_siglum)]
        abs = set(find_parent(reading, "ab") for reading in fp_readings)
        breakpoint()
        console.print(f"Writing {len(fp_readings)} false positives to {false_positives}")
        write_elements(abs, false_positives, "falsePositives")

    if false_negatives:
        fn_readings = [reading for reading in readings if reading_has_witness(reading, gold_siglum) and not reading_has_witness(reading, prediction_siglum)]
        abs = set(find_parent(reading, "ab") for reading in fn_readings)
        console.print(f"Writing {len(fn_readings)} false negatives to {false_negatives}")
        write_elements(abs, false_negatives, "falseNegatives")
