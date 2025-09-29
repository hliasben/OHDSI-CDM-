# src/main/python/transformation/challenge_to_visit.py
from src.main.python.model.cdm import VisitOccurrence
from datetime import datetime

visit_type_map = {
        "outpatient": 9201,  
        "inpatient": 9202,
        "emergency": 9203
}

def challenge_to_visit(wrapper) -> list:
    source = wrapper.get_challenge()
    records_to_insert = []

    

    for row in source:
        visit_start = datetime.strptime(row['visit_start_date'], "%Y-%m-%d")
        visit_end = datetime.strptime(row['visit_end_date'], "%Y-%m-%d")

        visit_concept_id = visit_type_map.get(row['visit_type'].lower(), 0)

        record = VisitOccurrence(
            person_id=int(row['patient_id']),
            visit_concept_id=visit_concept_id,
            visit_source_concept_id=0,
            visit_start_date=visit_start.date(),
            visit_start_datetime=visit_start,
            visit_end_date=visit_end.date(),
            visit_end_datetime=visit_end,
            visit_type_concept_id=32879,  # Registry type
            discharge_to_concept_id=0,
            admitted_from_concept_id=0,
            care_site_id=row.get('care_site_id'),
            provider_id=row.get('provider_id'),
            record_source_value=row['visit_id'],
            visit_source_value=row['visit_id']
        )
        records_to_insert.append(record)

    return records_to_insert
