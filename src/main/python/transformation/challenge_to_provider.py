from src.main.python.model.cdm import Provider
from datetime import datetime


def challenge_to_provider(wrapper) -> list:
    challenge_data = wrapper.get_challenge()

    records_to_insert = []
    provider_map = {}
    provider_counter = 1

    for row in challenge_data:
        provider_id = provider_counter

        record = Provider(
            provider_id=provider_id,
            provider_source_value=row.get('provider_id'),
            specialty_concept_id=0,
            gender_concept_id=0,
            gender_source_concept_id=0,

        )

        records_to_insert.append(record)
        provider_map[row['provider_id']] = provider_id
        provider_counter += 1

    # αποθηκεύουμε τον provider_map στο wrapper (όπως κάναμε με το patient_map)
    wrapper.provider_map = provider_map

    return records_to_insert
