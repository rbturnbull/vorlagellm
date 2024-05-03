from pathlib import Path
from lxml import etree
from lxml.etree import _ElementTree as ElementTree
from lxml.etree import _Element as Element


def read_tei(path:Path) -> ElementTree:
    with open(path, 'r') as f:
        return etree.parse(f)


def find_element(doc:ElementTree|Element, xpath:str) -> Element|None:
    if isinstance(doc, ElementTree):
        doc = doc.getroot()
    return doc.find(xpath, namespaces=doc.nsmap)


def get_siglum(doc:ElementTree|Element) -> str:
    """
    Get the attribute of the 'n' attribute in the <title type="document"> element.

    Returns an empty string if the element is not found.
    """
    title = find_element(doc, ".//title[@type='document']")
    if title is None:
        return ""
    
    return title.attrib.get('n', "")


def add_siglum():
    raise NotImplementedError()


def get_language():
    raise NotImplementedError()


def get_verses():
    raise NotImplementedError()


def get_reading_permutations():
    raise NotImplementedError()


def get_verse_text():
    raise NotImplementedError()


def add_witness_readings():
    raise NotImplementedError()


def write_tei():
    raise NotImplementedError()

    