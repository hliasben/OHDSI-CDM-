# src/main/python/transformation/challenge_to_person.py
from src.main.python.model.cdm import Person
from datetime import datetime

def challenge_to_person(wrapper) -> list:
    source = wrapper.get_challenge()   # <-- εδώ πλέον παίρνουμε τα data
    records_to_insert = []

    for row in source:
        # birth_date
        birth_date = None
        if row['birth_date']:
            birth_date = datetime.strptime(row['birth_date'], "%Y-%m-%d")

        # death_date
        death_date = None
        if row.get('death_date'):
            death_date = datetime.strptime(row['death_date'], "%Y-%m-%d")

        # gender mapping (παράδειγμα με απλό dict)
        gender_map = {
            "Male": 8507,
            "Female": 8532
        }
        gender_concept_id = gender_map.get(row['gender'], 0)

        record = Person(
            person_id=int(row['patient_id']),
            person_source_value=row['patient_id'],
            year_of_birth=birth_date.year if birth_date else None,
            month_of_birth=birth_date.month if birth_date else None,
            day_of_birth=birth_date.day if birth_date else None,
            death_datetime=death_date,
            gender_concept_id=gender_concept_id,
            race_concept_id=0,  # μπορείς να προσθέσεις mapping αν έχεις
            ethnicity_concept_id=0,
            gender_source_concept_id=0,
            race_source_concept_id=0,
            ethnicity_source_concept_id=0
        )
        records_to_insert.append(record)

    return records_to_insert
