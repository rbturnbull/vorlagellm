from lxml import etree as ET
from collections import Counter
from vorlagellm.agreements import WitnessComparison, get_app_witness_agreements, count_witness_agreements

def test_witness_missing():
    xml_data = '''<app>
        <rdg wit="SIGLUM2">Text 1</rdg>
    </app>'''
    root = ET.fromstring(xml_data)
    result = get_app_witness_agreements(root, 'SIGLUM1', 'SIGLUM2')
    assert result == WitnessComparison.MISSING

def test_unambiguous_disagreement():
    xml_data = '''<app>
        <rdg wit="SIGLUM1">Text 1</rdg>
        <rdg wit="SIGLUM2">Text 2</rdg>
    </app>'''
    root = ET.fromstring(xml_data)
    result = get_app_witness_agreements(root, 'SIGLUM1', 'SIGLUM2')
    assert result == WitnessComparison.UNAMBIGUOUS_DISAGREEMENT

def test_unambiguous_agreement():
    xml_data = '''<app>
        <rdg wit="SIGLUM1 SIGLUM2">Text 1</rdg>
    </app>'''
    root = ET.fromstring(xml_data)
    result = get_app_witness_agreements(root, 'SIGLUM1', 'SIGLUM2')
    assert result == WitnessComparison.UNAMBIGUOUS_AGREEMENT

def test_ambiguous_agreement():
    xml_data = '''<app>
        <rdg wit="SIGLUM1">Text 1</rdg>
        <rdg wit="SIGLUM1 SIGLUM2">Text 2</rdg>
        <rdg wit="SIGLUM2">Text 3</rdg>
    </app>'''
    root = ET.fromstring(xml_data)
    result = get_app_witness_agreements(root, 'SIGLUM1', 'SIGLUM2')
    assert result == WitnessComparison.AMBIGUOUS_AGREEMENT


def test_all_witness_agreements():
    xml_data = '''<root>
        <app>
            <rdg wit="SIGLUM1">Text 1</rdg>
        </app>
        <app>
            <rdg wit="SIGLUM2">Text 1</rdg>
        </app>
        <app>
            <rdg wit="SIGLUM1">Text 1</rdg>
            <rdg wit="SIGLUM2">Text 2</rdg>
        </app>
        <app>
            <rdg wit="SIGLUM1 SIGLUM2">Text 3</rdg>
        </app>
        <app>
            <rdg wit="SIGLUM1">Text 4</rdg>
            <rdg wit="SIGLUM2">Text 5</rdg>
            <rdg wit="SIGLUM1 SIGLUM2">Text 6</rdg>
        </app>
    </root>'''
    root = ET.fromstring(xml_data)
    result = count_witness_agreements(root, 'SIGLUM1', 'SIGLUM2')
    expected = Counter({
        WitnessComparison.UNAMBIGUOUS_DISAGREEMENT: 1,
        WitnessComparison.UNAMBIGUOUS_AGREEMENT: 1,
        WitnessComparison.AMBIGUOUS_AGREEMENT: 1,
        WitnessComparison.MISSING: 2,
    })
    assert result == expected
