from src.main.python.model.cdm import StemTable
from datetime import datetime

# πρόχειροι χάρτες - ιδανικά θα έρθουν από unit_mapping / value_mapping
unit_map = {
    "g/dL": 8840,
    "mg/dL": 8753,
    "ng/mL": 8617,
    "mmHg": 8876,
    "mg/L": 8848,
    "U/L": 8842,
    "uIU/mL": 8751,
    "10^9/L": 8713,
    "kg/m2": 8510,
    "mmol/L": 8754
}

def challenge_to_stem_table(wrapper) -> list:
    challenge_data = wrapper.get_challenge()
    records_to_insert = []
    id_counter = 1
    patient_map = wrapper.patient_map

    for row in challenge_data:

        pid = patient_map.get(row['patient_id'])

        # --- Measurement ---
        if row.get('measurement_name'):
            measurement_date = datetime.strptime(row['measurement_date'], "%Y-%m-%d")
            rec = StemTable(
                id=id_counter,
                domain_id="Measurement",
                person_id=pid,
                concept_id=0,  # TODO: mapping από vocab
                start_date=measurement_date.date(),
                start_datetime=measurement_date,
                end_date=measurement_date.date(),
                end_datetime=measurement_date,
                type_concept_id=44818701,
                value_as_number=float(row['measurement_value']) if row['measurement_value'] else None,
                unit_concept_id=unit_map.get(row['measurement_unit'], 0),
                source_value=row['measurement_name'],
                unit_source_value=row['measurement_unit'],
                value_source_value=row['measurement_value'],
                record_source_value=f"{pid}-measurement-{row['measurement_name']}"
            )
            records_to_insert.append(rec)
            id_counter += 1

        # --- Condition ---
        if row.get('condition_name'):
            cond_start = datetime.strptime(row['condition_start_date'], "%Y-%m-%d")
            cond_end = None
            if row.get('condition_end_date'):
                cond_end = datetime.strptime(row['condition_end_date'], "%Y-%m-%d")
            rec = StemTable(
                id=id_counter,
                domain_id="Condition",
                person_id=pid,
                concept_id=0,
                start_date=cond_start.date(),
                start_datetime=cond_start,
                end_date=cond_end.date() if cond_end else None,
                end_datetime=cond_end,
                type_concept_id=32535,
                source_value=row['condition_name'],
                record_source_value=f"{pid}-condition-{row['condition_name']}"
            )
            records_to_insert.append(rec)
            id_counter += 1

        # --- Procedure ---
        if row.get('procedure_name'):
            proc_date = datetime.strptime(row['procedure_date'], "%Y-%m-%d")
            rec = StemTable(
                id=id_counter,
                domain_id="Procedure",
                person_id=pid,
                concept_id=0,
                start_date=proc_date.date(),
                start_datetime=proc_date,
                end_date=proc_date.date(),
                end_datetime=proc_date,
                type_concept_id=581412,
                source_value=row['procedure_name'],
                record_source_value=f"{pid}-procedure-{row['procedure_name']}"
            )
            records_to_insert.append(rec)
            id_counter += 1

        # --- Drug ---
        if row.get('drug_name'):
            drug_start = datetime.strptime(row['drug_exposure_start_date'], "%Y-%m-%d")
            drug_end = datetime.strptime(row['drug_exposure_end_date'], "%Y-%m-%d")
            rec = StemTable(
                id=id_counter,
                domain_id="Drug",
                person_id=pid,
                concept_id=0,
                start_date=drug_start.date(),
                start_datetime=drug_start,
                end_date=drug_end.date(),
                end_datetime=drug_end,
                type_concept_id=38000175,
                quantity=None,
                source_value=row['drug_name'],
                value_source_value=row['drug_dose'],
                record_source_value=f"{pid}-drug-{row['drug_name']}"
            )
            records_to_insert.append(rec)
            id_counter += 1

        # --- Observation ---
        if row.get('observation_name'):
            obs_date = datetime.strptime(row['observation_date'], "%Y-%m-%d")
            rec = StemTable(
                id=id_counter,
                domain_id="Observation",
                person_id=pid,
                concept_id=0,
                start_date=obs_date.date(),
                start_datetime=obs_date,
                type_concept_id=45905771,
                value_as_string=row['observation_value'],
                source_value=row['observation_name'],
                value_source_value=row['observation_value'],
                record_source_value=f"{pid}-observation-{row['observation_name']}"
            )
            records_to_insert.append(rec)
            id_counter += 1

    return records_to_insert
