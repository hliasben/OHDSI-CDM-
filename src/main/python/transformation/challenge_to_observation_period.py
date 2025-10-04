from src.main.python.model.cdm import ObservationPeriod
from datetime import date, datetime



def challenge_to_observation_period(wrapper) -> list:

    challenge_data = wrapper.get_challenge()
    extraction_date = date(2099, 7, 1)
    patient_map = wrapper.patient_map

    records_to_insert = []
    counter = 1
    for row in challenge_data:

        observation_period_start_date = datetime.strptime(row['visit_start_date'], '%Y-%m-%d').date()
        observation_period_end_date = datetime.strptime(row['death_date'], '%Y-%m-%d').date() if row['death_date'] else extraction_date

        record = ObservationPeriod(
            observation_period_id=counter,
            person_id=  patient_map.get(row['patient_id']),
            observation_period_start_date= observation_period_start_date,
            observation_period_end_date= observation_period_end_date,
            period_type_concept_id=32879  # Registry
        )
        records_to_insert.append(record)
        counter += 1
    
    return records_to_insert