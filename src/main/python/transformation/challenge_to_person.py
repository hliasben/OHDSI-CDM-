from src.main.python.model.cdm import Person
from datetime import datetime


def challenge_to_person(wrapper) -> list:



    challenge_data = wrapper.get_challenge()
    provider_map = wrapper.provider_map
    care_site_map = wrapper.care_site_map

    records_to_insert = []
    patient_map = {}
    # counter για το person_id
    person_counter = 1

    for row in challenge_data:


        # 
        birth_date = datetime.strptime(row['birth_date'], "%Y-%m-%d")

        #
        death_date = None
        if row.get('death_date'):
            death_date = datetime.strptime(row['death_date'], "%Y-%m-%d")

        # mapping patient_id -> internal person_id
        patient_map[row['patient_id']] = person_counter

        gender_target = wrapper.variable_mapper.lookup("gender", row["gender"])
        gender_concept_id = gender_target.concept_id

        # Race
        race_target = wrapper.variable_mapper.lookup("race", row["race"])
        race_concept_id = race_target.concept_id
     

        # Ethnicity
        ethnicity_target = wrapper.variable_mapper.lookup("ethnicity", row["ethnicity"])
        ethnicity_concept_id = ethnicity_target.concept_id 

        record = Person(
            person_id=person_counter,
            person_source_value=row['patient_id'],
            year_of_birth=birth_date.year,
            month_of_birth=birth_date.month,
            day_of_birth=birth_date.day,
            birth_datetime=birth_date,
            death_datetime=death_date,
            gender_concept_id = gender_concept_id, 

            race_concept_id = race_concept_id,
            ethnicity_concept_id = ethnicity_concept_id,
            gender_source_value = row['gender'],

            race_source_value = row['race'],
            ethnicity_source_value = row['ethnicity'],
            race_source_concept_id = 0,
            ethnicity_source_concept_id = 0,
            provider_id = provider_map.get(row['provider_id']),
            care_site_id = care_site_map.get(row['care_site_id'])
            
            
        )
        records_to_insert.append(record)

        person_counter += 1
    wrapper.patient_map = patient_map

    return records_to_insert


if __name__ == '__main__':
    from src.main.python.database.database import Database
    from src.main.python.wrapper import Wrapper

    db = Database(f'postgresql://postgres@localhost:5432/postgres')  # A mock database object
    w = Wrapper(db, '../../../../resources/source_data', '../../../../resources/mapping_tables')

    for x in challenge_to_person(w):
        print(x.__dict__)
