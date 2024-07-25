import tempfile
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
    find_elements,
    add_wit_detail,
    reading_has_witness,
    find_parent,
    app_has_witness,
    write_elements,
    get_apparatus_verse_text,
    readings_for_witness,
    add_responsibility_statement,
    add_doc_metadata,
)
import pytest
from pathlib import Path
from lxml import etree as ET
from lxml.etree import Element
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
    assert language == "Latin"


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


def test_get_verse_text_empty():
    doc = read_tei(TEST_DOC)
    assert get_verse_text(doc, "1Cor1.1") == None


def test_add_siglum():
    apparatus = read_tei(TEST_APPARATUS)
    assert has_witness(apparatus, "51") == False
    add_siglum(apparatus, "51")
    assert has_witness(apparatus, "51")


def test_get_reading_permutations():
    permutations = get_reading_permutations(read_tei(TEST_APPARATUS), "B07K1V1")
    assert len(permutations) == 2
    assert permutations[0].text == "Παῦλος κλητὸς ἀπόστολος Χριστοῦ Ἰησοῦ διὰ θελήματος θεοῦ καὶ Σωσθένης ὁ ἀδελφὸς"
    assert permutations[1].text == "Παῦλος κλητὸς ἀπόστολος Ἰησοῦ Χριστοῦ διὰ θελήματος θεοῦ καὶ Σωσθένης ὁ ἀδελφὸς"

    assert permutations[0].readings[0].tag == "{http://www.tei-c.org/ns/1.0}rdg"
    assert permutations[1].readings[0].tag == "{http://www.tei-c.org/ns/1.0}rdg"


def test_write_tei():
    apparatus = read_tei(TEST_APPARATUS)
    add_siglum(apparatus, "51")
    with tempfile.TemporaryDirectory() as tmpdirname:
        output = Path(tmpdirname)/"test-apparatus.xml"
        write_tei(apparatus, output)
        assert output.exists()
        new_apparatus = read_tei(output)
        assert has_witness(new_apparatus, "51")


def test_add_with_detail():
    apparatus = read_tei(TEST_APPARATUS)
    apps = find_elements(apparatus, ".//app")

    add_wit_detail(apps, "SIGLUM", "Justification statement")
    details = apparatus.findall(".//witDetail")
    assert len(details) == len(apps)
    for detail in details:
        note = detail.find(".//note")
        assert note.text == "Justification statement"
        assert detail.attrib['wit'] == "SIGLUM"


def test_reading_has_witness_with_siglum():
    reading = Element('rdg', wit="#NIV #WH")
    assert reading_has_witness(reading, 'NIV') == True, "Test failed: #NIV should be found."

def test_reading_has_witness_with_prefixed_siglum():
    reading = Element('rdg', wit="#NIV #WH")
    assert reading_has_witness(reading, '#NIV') == True, "Test failed: #NIV should be found."

def test_reading_has_witness_without_siglum():
    reading = Element('rdg', wit="#WH #Treg")
    assert reading_has_witness(reading, 'NIV') == False, "Test failed: #NIV should not be found."

def test_reading_has_witness_without_wit_attribute():
    reading = Element('rdg')
    assert reading_has_witness(reading, 'NIV') == False, "Test failed: wit attribute is missing, should return False."

def test_reading_has_witness_with_empty_wit_attribute():
    reading = Element('rdg', wit="")
    assert reading_has_witness(reading, 'NIV') == False, "Test failed: wit attribute is empty, should return False."


def test_reading_has_witness_with_multiple_witnesses():
    reading = Element('rdg', wit="#NIV #WH #Treg")
    assert reading_has_witness(reading, 'Treg') == True, "Test failed: #Treg should be found."
    assert reading_has_witness(reading, 'WH') == True, "Test failed: #WH should be found."



def test_find_parent_ab():
    xml_data = """
    <root>
        <ab>
            <section>
                <target>Some content</target>
            </section>
        </ab>
    </root>
    """
    root = ET.fromstring(xml_data)
    target_element = root.find('.//target')
    parent_element = find_parent(target_element, 'ab')
    assert parent_element is not None
    assert parent_element.tag == 'ab'

def test_find_parent_noab():
    xml_data = """
    <root>
        <noab>
            <section>
                <target>Another content</target>
            </section>
        </noab>
    </root>
    """
    root = ET.fromstring(xml_data)
    target_element = root.find('.//target')
    parent_element = find_parent(target_element, 'ab')
    assert parent_element is None

def test_find_parent_root():
    xml_data = """
    <root>
        <ab>
            <section>
                <target>Some content</target>
            </section>
        </ab>
    </root>
    """
    root = ET.fromstring(xml_data)
    ab_element = root.find('.//ab')
    parent_element = find_parent(ab_element, 'root')
    assert parent_element is not None
    assert parent_element.tag == 'root'


def test_find_parent_nonexistent():
    xml_data = """
    <root>
        <ab>
            <section>
                <target>Some content</target>
            </section>
        </ab>
    </root>
    """
    root = ET.fromstring(xml_data)
    target_element = root.find('.//target')
    parent_element = find_parent(target_element, 'nonexistent')
    assert parent_element is None


def test_write_elements():
    # Create sample XML elements
    child1 = Element('child1')
    child1.text = 'Content 1'
    child2 = Element('child2')
    child2.text = 'Content 2'
    children = [child1, child2]

    # Create a temporary file
    with tempfile.NamedTemporaryFile() as tmp_file:
        output_file = Path(tmp_file.name)
    
        # Write elements to the temporary file
        write_elements(children, output_file)
        
        # Parse the written file and verify its content
        tree = read_tei(output_file)
        root = tree.getroot()
        
        assert root.tag == 'body'
        assert len(root) == 2
        assert root[0].tag == 'child1'
        assert root[0].text == 'Content 1'
        assert root[1].tag == 'child2'
        assert root[1].text == 'Content 2'


def test_write_elements_custom_root_tag():
    # Create sample XML elements
    child1 = Element('child1')
    child1.text = 'Content 1'
    child2 = Element('child2')
    child2.text = 'Content 2'
    children = [child1, child2]

    # Create a temporary file
    with tempfile.NamedTemporaryFile() as tmp_file:
        output_file = Path(tmp_file.name)
    
        # Write elements to the temporary file with a custom root tag
        write_elements(children, output_file, root_tag='custom_root')
        
        # Parse the written file and verify its content
        tree = read_tei(output_file)
        root = tree.getroot()
        
        assert root.tag == 'custom_root'
        assert len(root) == 2
        assert root[0].tag == 'child1'
        assert root[0].text == 'Content 1'
        assert root[1].tag == 'child2'
        assert root[1].text == 'Content 2'


def test_app_has_witness_found():
    xml_str = """
    <app>
        <rdg wit="A B C">Text 1</rdg>
        <rdg wit="D E F">Text 2</rdg>
    </app>
    """
    app = ET.fromstring(xml_str)
    siglum = "A"
    assert app_has_witness(app, siglum) == True

def test_app_has_witness_not_found():
    xml_str = """
    <app>
        <rdg wit="A B C">Text 1</rdg>
        <rdg wit="D E F">Text 2</rdg>
    </app>
    """
    app = ET.fromstring(xml_str)
    siglum = "G"
    assert app_has_witness(app, siglum) == False

def test_app_has_witness_empty_readings():
    xml_str = """
    <app>
    </app>
    """
    app = ET.fromstring(xml_str)
    siglum = "A"
    assert app_has_witness(app, siglum) == False

def test_app_has_witness_multiple_readings():
    xml_str = """
    <app>
        <rdg wit="A">Text 1</rdg>
        <rdg wit="B">Text 2</rdg>
        <rdg wit="C">Text 3</rdg>
    </app>
    """
    app = ET.fromstring(xml_str)
    siglum = "B"
    assert app_has_witness(app, siglum) == True

def test_app_has_witness_multiple_sigla():
    xml_str = """
    <app>
        <rdg wit="A B C">Text 1</rdg>
    </app>
    """
    app = ET.fromstring(xml_str)
    siglum = "B"
    assert app_has_witness(app, siglum) == True


def test_get_apparatus_verse_text_simple():
    xml_str = """
    <ab>
        This is a sample text 
        <app>with apparatus</app> 
        and more text.
    </ab>
    """
    parser = ET.XMLParser(remove_blank_text=True)
    app = ET.fromstring(xml_str, parser=parser).find('.//app')
    assert get_apparatus_verse_text(app) == "This is a sample text ⸂with apparatus⸃ and more text."


def test_get_apparatus_verse_text_lem():
    xml_str = """
    <ab>
        This is a sample text 
        <app><lem>with apparatus</lem></app> 
        and more text.
    </ab>
    """
    parser = ET.XMLParser(remove_blank_text=True)
    app = ET.fromstring(xml_str, parser=parser).find('.//app')
    assert get_apparatus_verse_text(app) == "This is a sample text ⸂with apparatus⸃ and more text."


def test_get_apparatus_verse_text_lemma_readings():
    xml_str = """
    <ab>
        This is a sample text 
        <app><lem>with apparatus</lem><rdg>with apparatus</rdg><rdg>with apparatus2</rdg></app> 
        and more text.
    </ab>
    """
    parser = ET.XMLParser(remove_blank_text=True)
    app = ET.fromstring(xml_str, parser=parser).find('.//app')
    assert get_apparatus_verse_text(app) == "This is a sample text ⸂with apparatus⸃ and more text."


def test_get_apparatus_verse_text_readings():
    xml_str = """
    <ab>
        This is a sample text 
        <app><rdg>with apparatus</rdg><rdg>with apparatus2</rdg></app> 
        and more text.
    </ab>
    """
    parser = ET.XMLParser(remove_blank_text=True)
    app = ET.fromstring(xml_str, parser=parser).find('.//app')
    assert get_apparatus_verse_text(app) == "This is a sample text ⸂with apparatus⸃ and more text."


def test_readings_for_witness_single_witness():
    xml_data = '''<app>
        <rdg wit="SIGLUM1">Text 1</rdg>
        <rdg wit="SIGLUM2">Text 2</rdg>
    </app>'''
    root = ET.fromstring(xml_data)
    result = readings_for_witness(root, 'SIGLUM1')
    assert len(result) == 1
    assert next(iter(result)).text == 'Text 1'

def test_readings_for_witness_multiple_witnesses():
    xml_data = '''<app>
        <rdg wit="SIGLUM1 SIGLUM2">Text 1</rdg>
        <rdg wit="SIGLUM3">Text 2</rdg>
        <rdg wit="SIGLUM1 SIGLUM3">Text 3</rdg>
    </app>'''
    root = ET.fromstring(xml_data)
    result = readings_for_witness(root, 'SIGLUM1')
    assert len(result) == 2
    texts = [reading.text for reading in result]
    assert 'Text 1' in texts
    assert 'Text 3' in texts

def test_readings_for_witness_no_match():
    xml_data = '''<app>
        <rdg wit="SIGLUM2">Text 1</rdg>
        <rdg wit="SIGLUM3">Text 2</rdg>
    </app>'''
    root = ET.fromstring(xml_data)
    result = readings_for_witness(root, 'SIGLUM1')
    assert len(result) == 0

def test_readings_for_witness_empty_wit():
    xml_data = '''<app>
        <rdg wit="">Text 1</rdg>
        <rdg wit="SIGLUM1">Text 2</rdg>
    </app>'''
    root = ET.fromstring(xml_data)
    result = readings_for_witness(root, 'SIGLUM1')
    assert len(result) == 1
    assert next(iter(result)).text == 'Text 2'


def test_add_doc_metadata_existing_biblFull():
    witness_element = ET.Element("witness")
    bibl_full = ET.SubElement(witness_element, "biblFull")
    doc = ET.ElementTree(ET.Element("root"))
    file_desc = ET.SubElement(doc.getroot(), "fileDesc")
    title_stmt = ET.SubElement(file_desc, "titleStmt")
    title_stmt.text = "Test Title"

    result = add_doc_metadata(witness_element, doc)

    assert result is not None
    assert result.tag == "biblFull"
    assert len(result) == 0  # biblFull already existed, so no new children should be added


def test_add_doc_metadata_no_biblFull():
    witness_element = ET.Element("witness")
    doc = ET.ElementTree(ET.Element("root"))
    file_desc = ET.SubElement(doc.getroot(), "fileDesc")
    title_stmt = ET.SubElement(file_desc, "titleStmt")
    title_stmt.text = "Test Title"

    result = add_doc_metadata(witness_element, doc)

    assert result is not None
    assert result.tag == "biblFull"
    assert len(result) == 1  # One child (fileDesc) should be added
    assert result[0].tag == "titleStmt"
    assert result[0].text == "Test Title"


def test_add_doc_metadata_fileDesc_with_multiple_children():
    witness_element = ET.Element("witness")
    doc = ET.ElementTree(ET.Element("root"))
    file_desc = ET.SubElement(doc.getroot(), "fileDesc")
    title_stmt = ET.SubElement(file_desc, "titleStmt")
    title_stmt.text = "Test Title"
    publication_stmt = ET.SubElement(file_desc, "publicationStmt")
    publication_stmt.text = "Test Publication"

    result = add_doc_metadata(witness_element, doc)

    assert result is not None
    assert result.tag == "biblFull"
    assert len(result) == 2  # One child (fileDesc) should be added
    assert result[0].tag == "titleStmt"
    assert result[0].text == "Test Title"
    assert result[1].tag == "publicationStmt"
    assert result[1].text == "Test Publication"


def test_add_responsibility_statement_valid():
    # Create a sample XML document
    xml_string = """
    <TEI>
        <titleStmt>
            <title>Sample Title</title>
        </titleStmt>
    </TEI>
    """
    doc = ET.ElementTree(ET.fromstring(xml_string))

    # Call the function
    siglum = "A"
    model_id = "model_123"
    result = add_responsibility_statement(doc, siglum, model_id)

    # Verify the result
    assert result.tag == "respStmt"
    resp = result.find("resp")
    assert resp is not None
    assert "when" in resp.attrib
    assert resp.text == f"Witness '{siglum}' using VorlageLLM using LLM '{model_id}'"

def test_add_responsibility_statement_no_title_stmt():
    # Create a sample XML document without titleStmt
    xml_string = """
    <TEI>
        <fileDesc></fileDesc>
    </TEI>
    """
    doc = ET.ElementTree(ET.fromstring(xml_string))
    add_responsibility_statement(doc, "A", "model_123")


def test_add_responsibility_statement_test_doc():
    doc = read_tei(TEST_DOC)
    result = add_responsibility_statement(doc, "A", "model_123")
    assert len(result) == 1
    assert result[0].tag == "resp"
    assert "Witness 'A' using VorlageLLM using LLM 'model_123'" == result[0].text

