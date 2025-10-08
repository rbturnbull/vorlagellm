import typer
from typing_extensions import Annotated
from pathlib import Path
from rich.progress import track
from rich.console import Console
from langchain_openai import OpenAIEmbeddings
import llmloader

from .chains import build_chain, build_corresponding_text_chain, build_source_chain
from .prompts import readings_list_to_str
from .rag import get_apparatus_db, get_teidoc_db, get_db, get_similar_verses, get_similar_verses_by_phrase
from .agreements import count_witness_agreements, WitnessComparison
from vorlagellm.tei import (
    read_tei,
    get_siglum,
    add_siglum,
    get_language,
    get_verses,
    get_reading_permutations,
    find_readings,
    get_verse_text,
    add_doc_metadata,
    add_witness_readings,
    write_tei,
    add_wit_detail,
    find_elements,
    get_language_code,
    get_verse_element,
    add_responsibility_statement,
    extract_text,
    reading_has_witness,
    get_apparatus_verse_text,
    write_elements,
    find_parent,
    app_has_witness,
)
from .ensemble import do_ensemble

console = Console()

app = typer.Typer()

DEFAULT_MODEL_ID = "gpt-4.1"
DEFAULT_EMBEDDING_MODEL_ID = "text-embedding-3-large"


@app.command()
def run(
    doc: Path, 
    apparatus: Path,
    output:Path,
    api_key:str="",
    model:str=DEFAULT_MODEL_ID,
    apparatus_db:Path=None,
    doc_db:Path=None,
    siglum:str="",
    notes:Path=None,
    include:list[str]=None,
    ignore:list[str]=None,
):
    """ Runs the main VorlageLLM pipeline on a document to predict which source readings from an apparatus could have produced its text. """
    llm = llmloader.load(model=model, api_key=api_key)
    doc_path = doc
    doc = read_tei(doc_path)
    apparatus_path = apparatus
    apparatus = read_tei(apparatus_path)

    # Add as witness to apparatus
    siglum = siglum or get_siglum(doc)
    assert siglum, f"Could not determine siglum in '{doc_path}'. Please add a siglum to the TEI XML or add a siglum in the command line with --siglum"
    witness_element = add_siglum(apparatus, siglum)

    if notes and Path(notes).exists():
        notes = Path(notes).read_text()
    else:
        notes = ""

    # Add responsibility statement
    _, resp_id = add_responsibility_statement(apparatus, siglum, model)

    # Add metadata to apparatus
    add_doc_metadata(witness_element, doc)

    # Get languages
    doc_language = get_language(doc)
    doc_language_code = get_language_code(doc)
    assert doc_language, f"Could not determine language of document {doc_path}"

    apparatus_language = get_language(apparatus)
    assert apparatus_language, f"Could not determine language of apparatus {apparatus_path}"

    # Create database for apparatus
    if doc_db:
        embeddings_model = OpenAIEmbeddings(model=DEFAULT_EMBEDDING_MODEL_ID)
        doc_db = get_teidoc_db(doc, model=embeddings_model, path=doc_db)
    
    if apparatus_db:
        embeddings_model = OpenAIEmbeddings(model=DEFAULT_EMBEDDING_MODEL_ID)
        apparatus_db = get_apparatus_db(apparatus, model=embeddings_model, path=apparatus_db, ignore_types=ignore)

    # Create chain to use
    corresponding_text_chain = build_corresponding_text_chain(llm, doc_language=doc_language, apparatus_language=apparatus_language)
    source_chain = build_source_chain(llm, doc_language=doc_language, apparatus_language=apparatus_language, notes=notes)

    verses = get_verses(apparatus)
    if include:
        verses = [v for v in verses if v in include]

    for verse in verses:
        doc_verse_text = get_verse_text(doc, verse)
        console.rule(f"Verse '{verse}'", style="bold red")
        console.print(f"Text: {doc_verse_text}")
        apparatus_verse_element = get_verse_element(apparatus, verse)

        for app in find_elements(apparatus_verse_element, ".//app"):
            if app_has_witness(app, siglum):
                continue

            readings = find_readings(app, ignore_types=ignore)
            if len(readings) < 2:
                continue

            apparatus_verse_text = get_apparatus_verse_text(app)

            console.print(f"Apparatus text: [blue]{apparatus_verse_text}[/blue]")
                
            reading_texts = [extract_text(reading) for reading in readings]
            reading_list = ", ".join([("⸂" + reading + "⸃") if reading else "⸂OMISSION⸃" for reading in reading_texts])
            readings_string = readings_list_to_str([extract_text(reading) for reading in readings])
            permutations = "\n".join([permutation.text for permutation in get_reading_permutations(apparatus, verse, witness=siglum, bracket_app=app, max_permutations=10, ignore_types=ignore)])
            doc_corresponding_text = corresponding_text_chain.invoke(dict(
                doc_verse_text=doc_verse_text,
                permutations=permutations,
                reading_list=reading_list
            ))
            console.print(f"Corresponding text: [blue]{doc_corresponding_text}[/blue]")

            # find similar verses
            similar_verses = set()
            if doc_db:
                doc_verse_text = doc_verse_text or ""
                similar_verses.update(get_similar_verses_by_phrase(doc_db, doc_verse_text))
                if doc_corresponding_text:
                    similar_verses.update(get_similar_verses_by_phrase(doc_db, doc_corresponding_text))
            if apparatus_db:
                for reading in readings:
                    similar_verses.update(get_similar_verses_by_phrase(apparatus_db, extract_text(reading)))
            similar_verses.discard(verse)
            
            similar_verse_examples = ""
            if similar_verses:
                similar_verse_examples = (
                    f"Here are {len(similar_verses)} similar texts to the one that you need to analyze. "
                    f"You will see the {doc_language} language text and then all potential {apparatus_language} source texts. "
                    f"Even though might not clear which {apparatus_language} was the actual source, consider the translation technique going from {apparatus_language} to {doc_language}.\n"
                    "See the way that the translator has translated particular words and gramatical constructions that are similar to the texts you need to analyze. \n\n"
                )
                for similar_verse in similar_verses:
                    example_doc_text = get_verse_text(doc, similar_verse)
                    similar_verse_permutations = get_reading_permutations(apparatus, similar_verse, witness=siglum, max_permutations=5, ignore_types=ignore)
                    similar_readings = readings_list_to_str([similar_verse_permutation.text for similar_verse_permutation in similar_verse_permutations])
                    similar_verse_examples += (
                        f"{doc_language} example {similar_verse}:\n{example_doc_text}\n"
                        f"Possible {apparatus_language} source(s):\n{similar_readings}\n\n"
                    )
                similar_verse_examples += (
                    f"Here is the {doc_language} text to analyze:\n{doc_corresponding_text}\n[Full text in context: {doc_verse_text}]\n\n"
                    f"Here is the source {apparatus_language} text to analyze with the textual variant in brackets like this: ⸂ ⸃:\n{apparatus_verse_text}\n\n"
                    f"Here are the potential {apparatus_language} readings that go between the brackets that could be the source of '{doc_corresponding_text}':\n{readings_string}"
                )     

            results, justification = source_chain.invoke(dict(
                doc_verse_text=doc_verse_text,
                doc_corresponding_text=doc_corresponding_text,
                apparatus_verse_text=apparatus_verse_text,
                readings=readings_string,
                similar_verse_examples=similar_verse_examples,
            ))

            for index, reading in enumerate(readings):
                reading_text = extract_text(reading)
                if index in results:
                    console.print(f"[bold green]✓ {reading_text}")
                    add_witness_readings(reading, siglum)
                else:
                    console.print(f"[grey62]𐄂 {reading_text}")

            add_wit_detail(app, siglum, phrase=doc_corresponding_text, phrase_lang=doc_language_code, note=justification, resp_id=resp_id)
                            
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
    """
    Creates a database for the document.
    """
    embeddings_model = OpenAIEmbeddings(model=DEFAULT_EMBEDDING_MODEL_ID)
    doc_path = doc
    doc = read_tei(doc_path)    
    db = get_teidoc_db(doc, model=embeddings_model, path=db)
    return db


@app.command()
def apparatus_db(
    apparatus: Path, 
    db:Path,
):
    """
    Creates a database for the apparatus.
    """
    embeddings_model = OpenAIEmbeddings(model=DEFAULT_EMBEDDING_MODEL_ID)
    apparatus = read_tei(apparatus)    
    db = get_apparatus_db(apparatus, model=embeddings_model, path=db)
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
    tn = sum(not reading_has_witness(reading, gold_siglum) and not reading_has_witness(reading, prediction_siglum) for reading in readings)
    recall = tp / (tp + fn)
    precision = tp / (tp + fp)
    f1 = 2 * (precision * recall) / (precision + recall)
    fpr = fp / (fp + tn)
    fnr = fn / (fn + tp)
    console.print(f"Recall: {recall:.1%}")
    console.print(f"Precision: {precision:.1%}")
    console.print(f"False Negative Rate: {fnr:.1%}")
    console.print(f"False Positive Rate: {fpr:.1%}")
    console.print(f"False Positives: {fp}")
    console.print(f"False Negatives: {fn}")
    console.print(f"True Positives: {tp}")
    console.print(f"True Negatives: {tn}")

    console.print(f"F1: {f1:.1%}")

    if false_positives:
        fp_readings = [reading for reading in readings if reading_has_witness(reading, prediction_siglum) and not reading_has_witness(reading, gold_siglum)]
        abs = set(find_parent(reading, "ab") for reading in fp_readings)
        console.print(f"Writing {len(fp_readings)} false positives to {false_positives}")
        write_elements(abs, false_positives, "listApp", type="false-positives")

    if false_negatives:
        fn_readings = [reading for reading in readings if reading_has_witness(reading, gold_siglum) and not reading_has_witness(reading, prediction_siglum)]
        abs = set(find_parent(reading, "ab") for reading in fn_readings)
        console.print(f"Writing {len(fn_readings)} false negatives to {false_negatives}")
        write_elements(abs, false_negatives, "listApp", type="false-negatives")


@app.command()
def agreements(
    apparatus:Path,
    siglum1:str,
    siglum2:str,
    horizontal:bool=False,
):
    apparatus = read_tei(apparatus)
    counter = count_witness_agreements(apparatus, siglum1, siglum2)

    # results = [
    #     counter[WitnessComparison.UNAMBIGUOUS_AGREEMENT],
    #     counter[WitnessComparison.AMBIGUOUS_AGREEMENT],
    #     counter[WitnessComparison.UNAMBIGUOUS_DISAGREEMENT],
    #     counter[WitnessComparison.MISSING],
    # ]
    if horizontal:
        print("siglum1", "siglum2", "\t".join([category.plural for category in WitnessComparison]), sep="\t")
        print(siglum1, siglum2, "\t".join([str(counter[category]) for category in WitnessComparison]), sep="\t")
    else:
        print("siglum1", siglum1, sep="\t")        
        print("siglum2", siglum2, sep="\t")        
        for category in WitnessComparison:
            print(category.plural, counter[category], sep="\t")


@app.command()
def ensemble(siglum:str, output:Path, apparatuses:list[Path]):
    apparatuses = [read_tei(apparatus) for apparatus in apparatuses]
    result = do_ensemble(apparatuses, siglum)
    print(f"Writing ensemble to {output}")
    write_tei(result, output)