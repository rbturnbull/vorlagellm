from pathlib import Path
from langchain.schema import Document as EmbeddingDocument
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from vorlagellm.tei import (
    get_verses,
    get_reading_permutations,
    get_verse_text,
)


def sentence_components(sentence:str, word_count:int=2) -> list[str]:
    words = sentence.split()
    return [" ".join(words[i:i+word_count]) for i in range(len(words) - word_count + 1) ]


def get_similar_verses(db, verse:str, window:int=0) -> dict[str,EmbeddingDocument]:
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
    
    if window:
        for verse_text in verse_results['documents']:
            for components in sentence_components(verse_text, window):
                for similar in db.similarity_search(components):
                    similar_verse = similar.metadata['verse']

                    if similar_verse != verse and similar_verse not in similar_docs:
                        similar_docs[similar_verse] = similar    
    
    return similar_docs


def get_similar_verses_by_phrase(db, phrase:str) -> set[str]:
    similar_verses = set()
    for similar in db.similarity_search(phrase):
        similar_verses.add(similar.metadata['verse'])
    
    return similar_verses


def build_apparatus_embeddingdocs(apparatus) -> list[EmbeddingDocument]:
    documents = []
    for verse in get_verses(apparatus):
        permutations = get_reading_permutations(apparatus, verse)
        for ii, permutation in enumerate(permutations):  
            metadata = dict(
                index=ii,
                verse=verse,
                # readings=permutation.readings,
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