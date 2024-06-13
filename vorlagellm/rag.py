from pathlib import Path
from langchain.schema import Document as EmbeddingDocument
from langchain.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from vorlagellm.tei import (
    get_verses,
    get_reading_permutations,
    get_verse_text,
)


def build_apparatus_embeddingdocs(apparatus) -> list[EmbeddingDocument]:
    documents = []
    for verse in get_verses(apparatus):
        permutations = get_reading_permutations(apparatus, verse)
        for ii, permutation in enumerate(permutations):  
            metadata = dict(
                index=ii,
                verse=verse,
                readings=permutation.readings,
            )
            document= EmbeddingDocument(page_content=permutation.text, metadata=metadata)
            documents.append(document)
    return documents


def build_teidoc_embeddingdocs(teidoc) -> list[EmbeddingDocument]:
    documents = []
    for verse in get_verses(teidoc):
        text = get_verse_text(teidoc, verse)
        metadata = dict(
            verse=verse,
        )
        document= EmbeddingDocument(page_content=text, metadata=metadata)
        documents.append(document)
    return documents


def get_db(docs:list[EmbeddingDocument], model:OpenAIEmbeddings, path:Path|str) -> Chroma:
    if Path(path).exists():
        apparatus_db = Chroma(persist_directory=str(path), embedding_function=model)
    else:
        apparatus_db = Chroma.from_documents(
            documents=docs, 
            embedding=model, 
            persist_directory=str(path),
        )
    
    return apparatus_db
    

def get_apparatus_db(apparatus, model:OpenAIEmbeddings, path:Path|str) -> Chroma:
    return get_db(build_apparatus_embeddingdocs(apparatus), model, path)


def get_teidoc_db(teidoc, model:OpenAIEmbeddings, path:Path|str) -> Chroma:
    return get_db(build_teidoc_embeddingdocs(teidoc), model, path)