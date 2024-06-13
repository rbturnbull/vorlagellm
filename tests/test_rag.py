from vorlagellm.tei import (
    read_tei,
    get_siglum,
    add_siglum,
    get_language,
    get_verses,
    get_reading_permutations,
    get_verse_text,
    has_witness,
    add_witness_readings,
    write_tei,
)
from vorlagellm.rag import build_apparatus_embeddingdocs, build_teidoc_embeddingdocs
from .test_tei import TEST_APPARATUS, TEST_DOC

def test_build_teidoc_embeddingdocs():
    doc = read_tei(TEST_DOC)
    embedding_docs = build_teidoc_embeddingdocs(doc)
    assert len(embedding_docs) == 43
    assert embedding_docs[0].metadata['verse'] == 'B07K1V1'
    assert embedding_docs[0].page_content == "paulus uocatus apostolus xpi ihu per uoluntatem di et sostenes frater"

