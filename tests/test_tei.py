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
from pathlib import Path
from lxml.etree import _ElementTree as ElementTree

TEST_DIR = Path(__file__).parent/"test-data"
TEST_DOC = TEST_DIR/"07_VL51_P279v.xml"  
TEST_APPARATUS = TEST_DIR/"sblgnt-apparatus-1Cor1.xml"  


def test_read_tei_doc():
    doc = read_tei(TEST_DOC)
    assert isinstance(doc, ElementTree)


def test_read_tei_apparatus():
    apparatus = read_tei(TEST_APPARATUS)
    assert isinstance(apparatus, ElementTree)


def test_get_siglum():
    doc = read_tei(TEST_DOC)
    siglum = get_siglum(doc)
    assert siglum == "51"


def test_get_language():
    doc = read_tei(TEST_DOC)
    language = get_language(doc)
    assert language == "lat"


def test_get_verses_doc():
    verses = get_verses(read_tei(TEST_DOC))
    assert len(verses) == 43
    assert verses[0] == "B07K1V1"
    assert verses[-1] == "B07K2V12"


def test_get_verses_app():
    verses = get_verses(read_tei(TEST_APPARATUS))
    assert len(verses) == 31
    assert verses[0] == "B07K1V1"
    assert verses[-1] == "B07K1V31"


def test_get_verse_text():
    doc = read_tei(TEST_DOC)
    assert get_verse_text(doc, "B07K1V1") == "paulus uocatus apostolus xpi ihu per uoluntatem di et sostenes frater"


def test_add_siglum():
    apparatus = read_tei(TEST_APPARATUS)
    add_siglum(apparatus, "51")
    assert get_siglum(apparatus) == "51"


def test_get_reading_permutations():
    permutations = get_reading_permutations(read_tei(TEST_APPARATUS), "B07K1V1")
    assert len(permutations) == 2
    assert permutations[0].text == "Παῦλος κλητὸς ἀπόστολος Χριστοῦ Ἰησοῦ διὰ θελήματος θεοῦ καὶ Σωσθένης ὁ ἀδελφὸς"
    assert permutations[1].text == "Παῦλος κλητὸς ἀπόστολος Ἰησοῦ Χριστοῦ διὰ θελήματος θεοῦ καὶ Σωσθένης ὁ ἀδελφὸς"

    assert permutations[0].readings[0].tag == "{http://www.tei-c.org/ns/1.0}lem"
    assert permutations[1].readings[0].tag == "{http://www.tei-c.org/ns/1.0}rdg"
