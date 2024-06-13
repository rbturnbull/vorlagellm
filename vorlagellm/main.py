import typer
from typing_extensions import Annotated
from pathlib import Path
from rich.progress import track
from rich.console import Console

from .llms import get_llm
from .chains import build_chain
from .prompts import readings_list_to_str
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
def versionllm(
    doc: Path, 
    apparatus: Path,
    output:Path,
    hf_auth:Annotated[str, typer.Argument(envvar=["HF_AUTH"])]="",
    openai_api_key:Annotated[str, typer.Argument(envvar=["OPENAI_API_KEY"])]="",
    model_id:str=DEFAULT_MODEL_ID,
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

