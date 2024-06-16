from pathlib import Path
import tempfile
from vorlagellm.tei import (
    read_tei,
)
from vorlagellm.rag import build_apparatus_embeddingdocs, build_teidoc_embeddingdocs, get_apparatus_db, get_db, get_teidoc_db, sentence_components
from .test_tei import TEST_APPARATUS, TEST_DOC

class MockEmbeddingModel:
    def embed_documents(self, documents):
        embeddings = []
        for ii, doc in enumerate(documents):
            embeddings.append([ii]*128)
        return embeddings

    def embed_query(self, query):
        return [0]*128


def test_build_teidoc_embeddingdocs():
    doc = read_tei(TEST_DOC)
    embedding_docs = build_teidoc_embeddingdocs(doc)
    assert len(embedding_docs) == 43
    assert embedding_docs[0].metadata['verse'] == 'B07K1V1'
    assert embedding_docs[0].page_content == "paulus uocatus apostolus xpi ihu per uoluntatem di et sostenes frater"


def test_build_apparatus_embeddingdocs():
    apparatus = read_tei(TEST_APPARATUS)
    embedding_docs = build_apparatus_embeddingdocs(apparatus)
    assert len(embedding_docs) == 45
    assert embedding_docs[0].metadata['index'] == 0
    assert embedding_docs[0].metadata['verse'] == 'B07K1V1'
    assert embedding_docs[0].page_content == 'Παῦλος κλητὸς ἀπόστολος Χριστοῦ Ἰησοῦ διὰ θελήματος θεοῦ καὶ Σωσθένης ὁ ἀδελφὸς'


def test_get_apparatus_db():
    apparatus = read_tei(TEST_APPARATUS)

    with tempfile.TemporaryDirectory() as tmpdirname:
        output = Path(tmpdirname)/"apparatus.db"
        
        db = get_apparatus_db(apparatus, MockEmbeddingModel(), output)
        result = db.similarity_search("text", k=3)
        assert len(result) == 3
        assert result[0].metadata['index'] == 0
        assert result[0].metadata['verse'] == 'B07K1V1'
        assert result[0].page_content == 'Παῦλος κλητὸς ἀπόστολος Χριστοῦ Ἰησοῦ διὰ θελήματος θεοῦ καὶ Σωσθένης ὁ ἀδελφὸς'
        assert result[1].metadata['index'] == 1
            
        # Get persistence
        db = get_db(None, MockEmbeddingModel(), output)
        result = db.similarity_search("text", k=3)
        assert len(result) == 3
        assert result[0].metadata['index'] == 0
        assert result[0].metadata['verse'] == 'B07K1V1'
        assert result[0].page_content == 'Παῦλος κλητὸς ἀπόστολος Χριστοῦ Ἰησοῦ διὰ θελήματος θεοῦ καὶ Σωσθένης ὁ ἀδελφὸς'


def test_get_teidoc_db():
    doc = read_tei(TEST_DOC)

    with tempfile.TemporaryDirectory() as tmpdirname:
        output = Path(tmpdirname)/"doc.db"
        
        db = get_teidoc_db(doc, MockEmbeddingModel(), output)
        result = db.similarity_search("text", k=3)
        assert len(result) == 3
        assert result[0].metadata['verse'] == 'B07K1V1'
        assert result[0].page_content == 'paulus uocatus apostolus xpi ihu per uoluntatem di et sostenes frater'
            
        # Get persistence
        db = get_db(None, MockEmbeddingModel(), output)
        result = db.similarity_search("text", k=3)
        assert len(result) == 3
        assert result[0].metadata['verse'] == 'B07K1V1'
        assert result[0].page_content == 'paulus uocatus apostolus xpi ihu per uoluntatem di et sostenes frater'


def test_sentence_components_default_word_count():
    sentence = "This is an example sentence"
    expected_output = ['This is', 'is an', 'an example', 'example sentence']
    result = sentence_components(sentence)
    assert result == expected_output, f"Expected {expected_output} but got {result}"


def test_sentence_components_word_count_three():
    sentence = "This is an example sentence"
    expected_output = ['This is an', 'is an example', 'an example sentence']
    result = sentence_components(sentence, 3)
    assert result == expected_output, f"Expected {expected_output} but got {result}"


def test_sentence_components_single_word():
    sentence = "Hello"
    expected_output = []
    result = sentence_components(sentence)
    assert result == expected_output, f"Expected {expected_output} but got {result}"


def test__sentence_components_empty_sentence():
    sentence = ""
    expected_output = []
    result = sentence_components(sentence)
    assert result == expected_output, f"Expected {expected_output} but got {result}"


def test_sentence_components_longer_word_count():
    sentence = "This is an example sentence for testing"
    expected_output = ['This is an example', 'is an example sentence', 'an example sentence for', 'example sentence for testing']
    result = sentence_components(sentence, 4)
    assert result == expected_output, f"Expected {expected_output} but got {result}"

