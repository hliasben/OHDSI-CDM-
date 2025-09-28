# !/usr/bin/env python3
from src.main.python.model.cdm import StemTable
from datetime import date, datetime
from src.main.python.util.create_record_source_value import create_basedata_visit_record_source_value
from src.main.python.util.create_record_source_value import create_basedata_stem_table_record_source_value
import logging


def challenge_to_stem_table(wrapper) -> list:
    """
    Transform the challenge CSV into StemTable records
    """
    challenge_data = wrapper.get_challenge()

    records_to_insert = []

    operator_concept_id = None

    for row in challenge_data:

        # Handle measurements
        if row['measurement_name'] and row['measurement_value']:
            variable = row['measurement_name']
            value = row['measurement_value']
            # Lookup concept mapping
            target = wrapper.variable_mapper.lookup(variable, value)
            concept_id = target.concept_id
            value_as_concept_id = target.value_as_concept_id
            value_as_number = target.value_as_number
            unit_concept_id = target.unit_concept_id if target.unit_concept_id else None
            source_value = target.source_value
            value_source_value = target.value_source_value

            # Lookup visit occurrence ID
            visit_record_source_value = create_basedata_visit_record_source_value(
                row['patient_id'], row['visit_type'])
            visit_occurrence_id = wrapper.lookup_visit_occurrence_id(visit_record_source_value)

            # StemTable record source value
            stem_table_record_source_value = create_basedata_stem_table_record_source_value(
                row['patient_id'], variable)

            record = StemTable(
                person_id=int(row['patient_id']),
                visit_occurrence_id=visit_occurrence_id,
                start_date=datetime.strptime(row['visit_start_date'], "%Y-%m-%d").date(),
                start_datetime=datetime.strptime(row['visit_start_date'], "%Y-%m-%d"),
                concept_id=concept_id if concept_id else 0,
                value_as_concept_id=value_as_concept_id,
                value_as_number=value_as_number,
                unit_concept_id=unit_concept_id,
                source_value=source_value,
                value_source_value=value_source_value,
                operator_concept_id=operator_concept_id,
                type_concept_id=32879,
                record_source_value=stem_table_record_source_value
            )
            records_to_insert.append(record)

        # Handle conditions
        if row['condition_name']:
            variable = row['condition_name']
            value = 1
            target = wrapper.variable_mapper.lookup(variable, value)
            concept_id = target.concept_id
            visit_record_source_value = create_basedata_visit_record_source_value(
                row['patient_id'], row['visit_type'])
            visit_occurrence_id = wrapper.lookup_visit_occurrence_id(visit_record_source_value)
            stem_table_record_source_value = create_basedata_stem_table_record_source_value(
                row['patient_id'], variable)

            record = StemTable(
                person_id=int(row['patient_id']),
                visit_occurrence_id=visit_occurrence_id,
                start_date=datetime.strptime(row['condition_start_date'], "%Y-%m-%d").date() if row['condition_start_date'] else None,
                start_datetime=datetime.strptime(row['condition_start_date'], "%Y-%m-%d") if row['condition_start_date'] else None,
                concept_id=concept_id if concept_id else 0,
                value_as_concept_id=None,
                value_as_number=None,
                unit_concept_id=None,
                source_value=variable,
                value_source_value=None,
                operator_concept_id=operator_concept_id,
                type_concept_id=32879,
                record_source_value=stem_table_record_source_value
            )
            records_to_insert.append(record)

        # Handle procedures
        if row['procedure_name']:
            variable = row['procedure_name']
            value = 1
            target = wrapper.variable_mapper.lookup(variable, value)
            concept_id = target.concept_id
            visit_record_source_value = create_basedata_visit_record_source_value(
                row['patient_id'], row['visit_type'])
            visit_occurrence_id = wrapper.lookup_visit_occurrence_id(visit_record_source_value)
            stem_table_record_source_value = create_basedata_stem_table_record_source_value(
                row['patient_id'], variable)

            record = StemTable(
                person_id=int(row['patient_id']),
                visit_occurrence_id=visit_occurrence_id,
                start_date=datetime.strptime(row['procedure_date'], "%Y-%m-%d").date() if row['procedure_date'] else None,
                start_datetime=datetime.strptime(row['procedure_date'], "%Y-%m-%d") if row['procedure_date'] else None,
                concept_id=concept_id if concept_id else 0,
                value_as_concept_id=None,
                value_as_number=None,
                unit_concept_id=None,
                source_value=variable,
                value_source_value=None,
                operator_concept_id=operator_concept_id,
                type_concept_id=32879,
                record_source_value=stem_table_record_source_value
            )
            records_to_insert.append(record)

        # Handle drugs
        if row['drug_name']:
            variable = row['drug_name']
            value = row['drug_dose']
            target = wrapper.variable_mapper.lookup(variable, value)
            concept_id = target.concept_id
            visit_record_source_value = create_basedata_visit_record_source_value(
                row['patient_id'], row['visit_type'])
            visit_occurrence_id = wrapper.lookup_visit_occurrence_id(visit_record_source_value)
            stem_table_record_source_value = create_basedata_stem_table_record_source_value(
                row['patient_id'], variable)

            record = StemTable(
                person_id=int(row['patient_id']),
                visit_occurrence_id=visit_occurrence_id,
                start_date=datetime.strptime(row['drug_exposure_start_date'], "%Y-%m-%d").date() if row['drug_exposure_start_date'] else None,
                start_datetime=datetime.strptime(row['drug_exposure_start_date'], "%Y-%m-%d") if row['drug_exposure_start_date'] else None,
                concept_id=concept_id if concept_id else 0,
                value_as_concept_id=None,
                value_as_number=None,
                unit_concept_id=None,
                source_value=variable,
                value_source_value=value,
                operator_concept_id=operator_concept_id,
                type_concept_id=32879,
                record_source_value=stem_table_record_source_value
            )
            records_to_insert.append(record)

        # Handle observations
        if row['observation_name']:
            variable = row['observation_name']
            value = row['observation_value']
            target = wrapper.variable_mapper.lookup(variable, value)
            concept_id = target.concept_id
            visit_record_source_value = create_basedata_visit_record_source_value(
                row['patient_id'], row['visit_type'])
            visit_occurrence_id = wrapper.lookup_visit_occurrence_id(visit_record_source_value)
            stem_table_record_source_value = create_basedata_stem_table_record_source_value(
                row['patient_id'], variable)

            record = StemTable(
                person_id=int(row['patient_id']),
                visit_occurrence_id=visit_occurrence_id,
                start_date=datetime.strptime(row['observation_date'], "%Y-%m-%d").date() if row['observation_date'] else None,
                start_datetime=datetime.strptime(row['observation_date'], "%Y-%m-%d") if row['observation_date'] else None,
                concept_id=concept_id if concept_id else 0,
                value_as_concept_id=target.value_as_concept_id,
                value_as_number=target.value_as_number,
                unit_concept_id=target.unit_concept_id if target.unit_concept_id else None,
                source_value=target.source_value,
                value_source_value=target.value_source_value,
                operator_concept_id=operator_concept_id,
                type_concept_id=32879,
                record_source_value=stem_table_record_source_value
            )
            records_to_insert.append(record)

    return records_to_insert


if __name__ == '__main__':
    from src.main.python.database.database import Database
    from src.main.python.wrapper import Wrapper

    db = Database('postgresql://postgres@localhost:5432/postgres')
    w = Wrapper(db, '../../../../resources/test_datasets/junior_challenge_15', '../../../../resources/mapping_tables')
    for x in challenge_to_stem_table(w):
        print(x.__dict__)
