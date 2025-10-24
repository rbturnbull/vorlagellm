from lxml import etree as ET
from lxml.etree import _ElementTree as ElementTree
from rich.progress import track

from .tei import (
    find_elements, 
    extract_text, 
    reading_has_witness, 
    add_witness_readings, 
    remove_witnesss_readings, 
    find_element, 
    add_responsibility_statement,
)

def do_ensemble(xml_files:list[ElementTree], witness:str) -> ElementTree:
    assert len(xml_files) >= 2, f"Needs multiple apparatus objects to perform ensemble"
    apparatus_apps_list = [find_elements(apparatus, ".//app") for apparatus in xml_files]
    
    # Add responsibility statements from other files
    collation_xml_file = xml_files[0]
    title_stmt = find_element(collation_xml_file, ".//titleStmt")
    for xml_file in xml_files[1:]:
        for resp_stmt in find_elements(xml_file, ".//respStmt"):
            title_stmt.append(resp_stmt)

    # Add VorlageLLM Ensemble information into the TEI header and include all the relevant information about each apparatus
    _, responsibility_statement_id = add_responsibility_statement(
        xml_files[0], 
        "VorlageLLM-Ensemble", 
        f"Ensembled from {len(xml_files)} files using VorlageLLM.",
    )

    # Make sure that each apparatus has the same number of readings
    apps_count = None
    for app_list in apparatus_apps_list:
        if apps_count is None:
            apps_count = len(app_list)
        else:
            assert apps_count == len(app_list), f"Each apparatus must have the same number of <app> elements, expected {apps_count} and found {len(app_list)}"

    for app_in_each_file in track(zip(*apparatus_apps_list), total=apps_count, description="Ensembling <app> elements"):
    # for app_in_each_file in zip(*apparatus_apps_list):
        assert len(app_in_each_file) == len(xml_files)
        readings_list = [find_elements(app, ".//rdg") for app in app_in_each_file]

        # Make sure that each apparatus has the same number of readings
        readings_count = None
        for readings in readings_list:
            if readings_count is None:
                readings_count = len(readings)
            else:
                assert readings_count == len(readings), f"Each apparatus must have the same number of <rdg> elements in each <app>, expected {readings_count} and found {len(readings)}"

        for readings in zip(*readings_list):
            assert len(readings) == len(xml_files)
            readings_with_witness = 0

            # Make sure that each reading is the same
            readings_text = None
            for reading in readings:
                if readings_text is None:
                    readings_text = extract_text(reading)
                else:
                    assert readings_text == extract_text(reading)

                readings_with_witness += int(reading_has_witness(reading, witness))
            
            majority_has_witness = (2 * readings_with_witness >= len(xml_files))

            # modify first apparatus
            reading = readings[0]
            if majority_has_witness == reading_has_witness(reading, witness):
                continue
            elif majority_has_witness:
                add_witness_readings(reading, witness)
            else:
                remove_witnesss_readings(reading, witness)
    
        # Find witDetail element in each apparatus
        wit_details = [find_element(app, f".//witDetail[@wit='" + witness + "']") for app in app_in_each_file]
        
        # Create new witDetail in first apparatus
        ensenble_app = app_in_each_file[0]
        ensemble_wit_detail = ET.SubElement(ensenble_app, "witDetail", wit=witness, resp=responsibility_statement_id)
        for wit_detail in wit_details:
            if wit_detail is not None:
                ensemble_wit_detail.append(wit_detail)

    return xml_files[0]

