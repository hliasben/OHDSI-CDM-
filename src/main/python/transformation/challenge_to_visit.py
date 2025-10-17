from src.main.python.model.cdm import VisitOccurrence
from datetime import datetime
from src.main.python.util.create_record_source_value import create_challenge_visit_record_source_value



def challenge_to_visit(wrapper) -> list:
    challenge_data = wrapper.get_challenge()

    records_to_insert = []
    patient_map = wrapper.patient_map
    provider_map = wrapper.provider_map
    care_site_map = wrapper.care_site_map
    # counter για το visit_occurrence_id
    visit_counter = 1

    for row in challenge_data:

        visit_target = wrapper.variable_mapper.lookup("visit_type", row["visit_type"])
        visit_concept_id = visit_target.concept_id

        visit_start = datetime.strptime(row['visit_start_date'], "%Y-%m-%d")
        visit_end = datetime.strptime(row['visit_end_date'], "%Y-%m-%d")

        record = VisitOccurrence(
            visit_occurrence_id=visit_counter,
            person_id= patient_map.get(row['patient_id']),
            visit_concept_id= visit_concept_id,  
            visit_start_date=visit_start.date(),
            visit_start_datetime=visit_start,
            visit_end_date=visit_end.date(),
            visit_end_datetime=visit_end,
            visit_type_concept_id= 32879,  # Registry
            visit_source_value= row['visit_id'],
            visit_source_concept_id=0,
            admitted_from_concept_id=0,
            discharge_to_concept_id=0,
            record_source_value= create_challenge_visit_record_source_value(row['patient_id'] , row['visit_type']),

            provider_id= provider_map.get(row['provider_id']),
            care_site_id= care_site_map.get(row['care_site_id'])
        )
        records_to_insert.append(record)  





        visit_counter += 1

    return records_to_insert