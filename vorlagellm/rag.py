from pathlib import Path
from langchain.schema import Document as EmbeddingDocument
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from vorlagellm.tei import (
    get_verses,
    get_reading_permutations,
    get_verse_text,
)
from rich.progress import track


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
    for verse in track(get_verses(apparatus)):
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
        db = Chroma(persist_directory=str(path), embedding_function=model)
    else:
        print(f"Embedding {len(docs)} items to {path}")
        batch_size = 100
        num_batches = len(documents) // batch_size + (1 if len(documents) % batch_size != 0 else 0)

        db = None

        with Progress() as progress:
            task = progress.add_task("[cyan]Indexing documents...", total=len(documents))

            for i in range(num_batches):
                batch = documents[i * batch_size:(i + 1) * batch_size]
                if i == 0:
                    db = Chroma.from_documents(
                        documents=batch,
                        embedding=model, 
                        persist_directory=str(path),
                    )                        
                else:
                    db.add_documents(batch)
                progress.update(task, advance=len(batch))
    return db
    

def get_apparatus_db(apparatus, model:OpenAIEmbeddings, path:Path|str) -> Chroma:
    if path and Path(path).exists():
        return get_db(None, model, path)
    items = build_apparatus_embeddingdocs(apparatus)
    return get_db(items, model, path)


def get_teidoc_db(teidoc, model:OpenAIEmbeddings, path:Path|str) -> Chroma:
    if path and Path(path).exists():
        return get_db(None, model, path)
    items = build_teidoc_embeddingdocs(teidoc)
    return get_db(items, model, path)