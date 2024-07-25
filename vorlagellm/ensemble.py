from lxml.etree import _ElementTree as ElementTree

from .tei import find_elements, extract_text, reading_has_witness, add_witness_readings, remove_witnesss_readings

def do_ensemble(apparatuses:list[ElementTree], witness:str) -> ElementTree:
    assert len(apparatuses) >= 2, f"Needs multiple apparatus objects to perform ensemble"
    apparatus_readings_list = [find_elements(apparatus, ".//rdg") for apparatus in apparatuses]
    
    # Make sure that each apparatus has the same number of readings
    apparatus_readings_count = None
    for apparatus_readings in apparatus_readings_list:
        if apparatus_readings_count is None:
            apparatus_readings_count = len(apparatus_readings)
        else:
            assert apparatus_readings_count == len(apparatus_readings)

    for readings in zip(*apparatus_readings_list):
        readings_with_witness = 0
        # Make sure that each reading is the same
        readings_text = None
        for reading in readings:
            if readings_text is None:
                readings_text = extract_text(reading)
            else:
                assert readings_text == extract_text(reading)

            readings_with_witness += int(reading_has_witness(reading, witness))
        
        majority_has_witness = (2 * readings_with_witness >= len(apparatuses))

        # modify first apparatus
        reading = readings[0]
        if majority_has_witness == reading_has_witness(reading, witness):
            continue
        elif majority_has_witness:
            add_witness_readings(reading, witness)
        else:
            remove_witnesss_readings(reading, witness)
        
    # TODO Get justifications
    # TODO add to header

    return apparatuses[0]

