from src.main.python.model.cdm import Person
from datetime import datetime

gender_map = {
            "Male": 8507,
            "Female": 8532
}
race_map = {
    "White": 8527,
    "Black": 8516,
    "Asian": 8515,
    "Other": 8522
}
ethnicity_map = {
    "Hispanic": 38003563,
    "Not_Hispanic": 38003564
}

def challenge_to_person(wrapper) -> list:
    challenge_data = wrapper.get_challenge()
    provider_map = wrapper.provider_map

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

        record = Person(
            person_id=person_counter,
            person_source_value=row['patient_id'],
            year_of_birth=birth_date.year,
            month_of_birth=birth_date.month,
            day_of_birth=birth_date.day,
            birth_datetime=birth_date,
            death_datetime=death_date,
            gender_concept_id = gender_map.get(row['gender']), 

            race_concept_id = race_map.get(row['race']),
            ethnicity_concept_id = ethnicity_map.get(row['ethnicity'], 0),
            gender_source_value = row['gender'],

            race_source_value = row['race'],
            ethnicity_source_value = row['ethnicity'],
            race_source_concept_id = 0,
            ethnicity_source_concept_id = 0,
            provider_id = provider_map.get(row['provider_id'])
            
            
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
