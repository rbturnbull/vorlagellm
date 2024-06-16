import typer
from typing_extensions import Annotated
from pathlib import Path
from rich.progress import track
from rich.console import Console
from langchain_openai import OpenAIEmbeddings

from .llms import get_llm
from .chains import build_chain
from .prompts import readings_list_to_str
from .rag import get_apparatus_db, get_teidoc_db, get_db, sentence_components
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
)

console = Console()

app = typer.Typer()

DEFAULT_MODEL_ID = "gpt-4o"


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
):
    llm = get_llm(hf_auth=hf_auth, openai_api_key=openai_api_key, model_id=model_id)
    doc_path = doc
    doc = read_tei(doc_path)
    apparatus_path = apparatus
    apparatus = read_tei(apparatus_path)

    # Add as witness to apparatus
    siglum = siglum or get_siglum(doc)
    assert siglum, "Could not determine siglum"
    add_siglum(apparatus, siglum)

    # Get languages
    doc_language = get_language(doc)
    assert doc_language, f"Could not determine language of document {doc_path}"

    apparatus_language = get_language(apparatus)
    assert apparatus_language, f"Could not determine language of apparatus {apparatus_path}"

    # Create database for apparatus
    if doc_db:
        embeddings_model = OpenAIEmbeddings(model="text-embedding-3-large")
        doc_db = get_teidoc_db(doc, model=embeddings_model, path=doc_db)
            
    # if apparatus_db:
    #     apparatus_db = get_apparatus_db(apparatus, model=embeddings_model, path=apparatus_db)

    # Create chain to use
    chain = build_chain(llm, doc_language=doc_language, apparatus_language=apparatus_language)

    for verse in track(get_verses(apparatus)):
        print("Processing verse", verse)
        permutations = get_reading_permutations(apparatus, verse)
        if len(permutations) < 2:
            continue
        readings = readings_list_to_str([permutation.text for permutation in permutations])
        text = get_verse_text(doc, verse)
        console.print(f"[bold] {verse}: [blue]{text}")
        results = chain.invoke(dict(
            text=get_verse_text(doc, verse),
            readings=readings,
        ))

        for index, permutation in enumerate(permutations):
            if index in results:
                console.print(f"[bold green] {permutation.text}")
                add_witness_readings(permutation.readings, siglum)
            else:
                console.print(f"[grey62] {permutation.text}")

    # Write TEI XML output
    print("Writing TEI XML output to", output)
    write_tei(apparatus, output)

    return apparatus


@app.command()
def doc_db(
    doc: Path, 
    db:Path,
):
    embeddings_model = OpenAIEmbeddings(model="text-embedding-3-large")
    doc_path = doc
    doc = read_tei(doc_path)    
    db = get_teidoc_db(doc, model=embeddings_model, path=db)
    return db


@app.command()
def similar(
    db:Path,
    verse:str,
):
    embeddings_model = OpenAIEmbeddings(model="text-embedding-3-large")
    db = get_db(None, embeddings_model, db)
    verse_results = db.get(where={"verse": verse}, include=['embeddings', 'documents'])
    if not verse_results['embeddings']:
        print(f"Verse {verse} not found.")
        return

    similar_docs = dict()
    for embedding_vector in verse_results['embeddings']:
        for similar in db.similarity_search_by_vector(embedding_vector):
            similar_verse = similar.metadata['verse']

            if similar_verse != verse and similar_verse not in similar_docs:
                similar_docs[similar_verse] = similar
    
    for verse_text in verse_results['documents']:
        for components in sentence_components(verse_text, 2):
            for similar in db.similarity_search(components):
                similar_verse = similar.metadata['verse']

                if similar_verse != verse and similar_verse not in similar_docs:
                    similar_docs[similar_verse] = similar

    verse_text = verse_results['documents'][0]
    console.print(f"Similar verses to [bold red]{verse}[/bold red]: {verse_text}")
    for similar_verse, doc in similar_docs.items():
        console.print(f"[bold red]{similar_verse}[/bold red]: {doc.page_content}")
