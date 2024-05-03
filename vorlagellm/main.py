import typer
from typing_extensions import Annotated
from pathlib import Path

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

app = typer.Typer()

DEFAULT_MODEL_ID = 'gpt-4-turbo'


@app.command()
def versionllm(
    doc: Path, 
    apparatus: Path,
    output:Path,
    hf_auth:Annotated[str, typer.Argument(envvar=["HF_AUTH"])]="",
    openai_api_key:Annotated[str, typer.Argument(envvar=["OPENAI_API_KEY"])]="",
    model_id:str=DEFAULT_MODEL_ID,
):
    llm = get_llm(hf_auth=hf_auth, openai_api_key=openai_api_key, model_id=model_id)
    doc = read_tei(doc)
    apparatus = read_tei(apparatus)

    # Add as witness to apparatus
    siglum = get_siglum(doc)
    add_siglum(apparatus, siglum)

    # Get languages
    doc_language = get_language(doc)
    apparatus_language = get_language(apparatus)

    # Create chain to use
    chain = build_chain(llm, doc_language=doc_language, apparatus_language=apparatus_language)

    for verse in get_verses(apparatus):
        permutations = get_reading_permutations(apparatus, verse)
        readings = readings_list_to_str([permutation.text for permutation in permutations])
        results = chain.invoke(dict(
            text=get_verse_text(doc, verse),
            readings=readings,
        ))

        for index in results:
            readings = permutations[index].readings
            add_witness_readings( readings, siglum )

    # Write TEI XML output
    write_tei(apparatus, output)

    return apparatus

