from src.main.python.model.cdm import VisitOccurrence
from datetime import datetime
from src.main.python.util.create_record_source_value import create_challenge_visit_record_source_value


visit_type_map = {
    "outpatient": 9202,
    "inpatient": 9201,
    "emergency": 9203
}


def challenge_to_visit(wrapper) -> list:
    challenge_data = wrapper.get_challenge()

    records_to_insert = []
    patient_map = wrapper.patient_map
    # counter για το visit_occurrence_id
    visit_counter = 1

    for row in challenge_data:



        visit_start = datetime.strptime(row['visit_start_date'], "%Y-%m-%d")
        visit_end = datetime.strptime(row['visit_end_date'], "%Y-%m-%d")

        record = VisitOccurrence(
            visit_occurrence_id=visit_counter,
            person_id= patient_map.get(row['patient_id']),
            visit_concept_id= visit_type_map.get(row['visit_type']),  
            visit_start_date=visit_start.date(),
            visit_start_datetime=visit_start,
            visit_end_date=visit_end.date(),
            visit_end_datetime=visit_end,
            visit_type_concept_id= 32879,  # Registry
            provider_id= None, #row['provider_id'],
            care_site_id= None, #row['care_site_id'],
            visit_source_value= row['visit_id'],
            visit_source_concept_id=0,
            admitted_from_concept_id=0,
            discharge_to_concept_id=0,
            record_source_value= create_challenge_visit_record_source_value(row['patient_id'] , row['visit_type'])
        )
        records_to_insert.append(record)  





        visit_counter += 1

    return records_to_insert