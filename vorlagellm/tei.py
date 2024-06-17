from pathlib import Path
from lxml import etree as ET
from lxml.etree import _ElementTree as ElementTree
from lxml.etree import _Element as Element
import re
from dataclasses import dataclass

from .languages import convert_language_code


@dataclass
class Permutation:
    text:str
    readings:list[Element]
    apps:list[Element]=None


def read_tei(path:Path) -> ElementTree:
    with open(path, 'r') as f:
        return ET.parse(f)


def find_element(doc:ElementTree|Element, xpath:str) -> Element|None:
    if isinstance(doc, ElementTree):
        doc = doc.getroot()
    element = doc.find(xpath, namespaces=doc.nsmap)
    if element is None:
        element = doc.find(xpath)
    return element


def find_elements(doc:ElementTree|Element, xpath:str) -> Element|None:
    if isinstance(doc, ElementTree):
        doc = doc.getroot()
    return doc.findall(xpath, namespaces=doc.nsmap)


def get_siglum(doc:ElementTree|Element) -> str:
    """
    Get the attribute of the 'n' attribute in the <title type="document"> element.

    Returns an empty string if the element is not found.
    """
    title = find_element(doc, ".//title[@type='document']")
    if title is None:
        return ""
    
    return title.attrib.get('n', "")


def get_language_code(doc:ElementTree|Element) -> str:
    """ Reads the element <text> and returns the value of the xml:lang attribute."""
    text = find_element(doc, ".//text")
    if text is None:
        return ""
    
    return text.attrib.get("{http://www.w3.org/XML/1998/namespace}lang", "")


def get_language(doc:ElementTree|Element) -> str:
    code = get_language_code(doc)
    return convert_language_code(code)
    

    
def get_verses(doc:ElementTree|Element) -> list[str]:
    """ Returns a list of "n" attributes in <ab> elements."""
    ab_elements = find_elements(doc, ".//ab")
    return [ab.attrib['n'] for ab in ab_elements if 'n' in ab.attrib]


def get_reading_permutations(apparatus:ElementTree|Element, verse:str) -> list[Permutation]:
    verse_element = get_verse_element(apparatus, verse)
    if verse_element is None:
        return []

    permutations = [Permutation(text="", readings=[])]

    apps = []

    for child in verse_element:
        tag = re.sub(r"{.*}", "", child.tag)
        if tag == "app":
            apps.append(child)
            new_permutations = []
            readings = find_elements(child, ".//lem") + find_elements(child, ".//rdg")
            for reading in readings:
                reading_text = extract_text(reading) or ""
                for permutation in permutations:
                    new_permutation = Permutation(text=permutation.text + " " + reading_text, readings=permutation.readings + [reading])
                    new_permutations.append(new_permutation)
            permutations = new_permutations
        else:
            for permutation in permutations:
                permutation.text += " " + extract_text(child)

    def clean_text(text:str) -> str:
        return re.sub(r"\s+", " ", text.strip())

    return [Permutation(text=clean_text(permutation.text), readings=permutation.readings, apps=apps) for permutation in permutations]


def extract_text(node:Element) -> str:
    text = node.text or ""
    for child in node:
        tag = re.sub(r"{.*}", "", child.tag)
        if tag == "pc":
            continue

        text += extract_text(child) or ""
    
        if tag == "w":
            text += " "

    text += node.tail or ""
    return text


def get_verse_element(doc:ElementTree|Element, verse:str) -> Element|None:
    return find_element(doc, f".//ab[@n='{verse}']")


def get_verse_text(doc:ElementTree|Element, verse:str) -> str|None:
    verse_element = get_verse_element(doc, verse)
    if verse_element is None:
        return None
    
    return extract_text(verse_element).strip()
    

def add_witness_readings( readings:list[Element], siglum:str) -> None:
    for reading in readings:
        reading.attrib['wit'] += f" {siglum}"
        reading.attrib['wit'] = reading.attrib['wit'].strip()


def write_tei(doc:ElementTree, path:Path|str) -> None:
    doc.write(str(path), encoding="utf-8", xml_declaration=True, pretty_print=True)


def get_witness_list(apparatus:ElementTree|Element) -> Element:
    list_wit = find_element(apparatus, ".//listWit")
    if list_wit is None:
        raise ValueError("Could not find <listWit> element in the apparatus.")
    
    return list_wit


def add_siglum(apparatus:ElementTree|Element, siglum:str) -> Element:
    if isinstance(apparatus, ElementTree):
        apparatus = apparatus.getroot()

    """ Adds a <witness> element to the <listWit> element in the apparatus."""
    list_wit = get_witness_list(apparatus)
    
    # Check if the witness already exists
    witness_element = find_element(list_wit, f".//witness[@n='{siglum}']")
    if not witness_element:
        witness_element = ET.Element("witness", attrib={"n": siglum})
        list_wit.append(witness_element)

    return witness_element


def has_witness(apparatus:ElementTree|Element, siglum:str) -> bool:
    list_wit = get_witness_list(apparatus)
    return find_element(list_wit, f".//witness[@n='{siglum}']") is not None


def add_wit_detail(apps:Element|set[Element], siglum:str, detail:str) -> None:
    if isinstance(apps, Element):
        apps = set(apps)
    for app in apps:
        element = ET.SubElement(app, "witDetail", wit=siglum, resp="VorlageLLM")
        element.text = detail