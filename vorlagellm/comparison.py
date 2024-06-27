from enum import Enum
from lxml.etree import _ElementTree as ElementTree
from lxml.etree import _Element as Element
from collections import Counter

from .tei import readings_for_witness, find_elements

class WitnessComparison(Enum):
    MISSING = 0
    UNAMBIGUOUS_DISAGREEMENT = 1
    AMBIGUOUS_AGREEMENT = 2
    UNAMBIGUOUS_AGREEMENT = 3



def get_app_witness_agreements(app:Element, siglum1:str, siglum2:str) -> WitnessComparison:
    readings1 = readings_for_witness(app, siglum1)
    if len(readings1) == 0:
        return WitnessComparison.MISSING    

    readings2 = readings_for_witness(app, siglum2)
    if len(readings2) == 0:
        return WitnessComparison.MISSING    

    intersection = readings1 & readings2
    if len(intersection) == 0:
        return WitnessComparison.UNAMBIGUOUS_DISAGREEMENT
    
    if len(readings1) == 1 and len(readings2) == 1:
        return WitnessComparison.UNAMBIGUOUS_AGREEMENT
    
    return WitnessComparison.AMBIGUOUS_AGREEMENT



def get_all_witness_agreements(apparatus:ElementTree|Element, siglum1:str, siglum2:str) -> Counter[WitnessComparison]:
    """Aggregates the types of witness agreements across multiple apparatus entries in an XML document.

    Args:
        apparatus (ElementTree or Element): The root XML element or element tree representing the entire document.
        siglum1 (str): The siglum of the first witness.
        siglum2 (str): The siglum of the second witness.

    Returns:
        Counter: A counter with the counts of each type of witness agreement.
    """
    counter = Counter()
    for app in find_elements(apparatus, ".//app"):
        counter.update( [get_app_witness_agreements(app, siglum1, siglum2)] )
    return counter