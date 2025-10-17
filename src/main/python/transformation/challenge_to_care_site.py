from src.main.python.model.cdm import CareSite

def challenge_to_care_site(wrapper) -> list:
    challenge_data = wrapper.get_challenge()

    records_to_insert = []
    care_site_map = {}
    care_site_counter = 1

    for row in challenge_data:
        care_site_id = care_site_counter

        record = CareSite(
            care_site_id=care_site_id,
            care_site_source_value=row.get('care_site_id'),
            place_of_service_concept_id=0,
        )

        records_to_insert.append(record)
        care_site_map[row['care_site_id']] = care_site_id
        care_site_counter += 1

    wrapper.care_site_map = care_site_map
    return records_to_insert
