# Copyright 2019 The Hyve
#
# Licensed under the GNU General Public License, version 3,
# or (at your option) any later version (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.gnu.org/licenses/
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# !/usr/bin/env python3
from pathlib import Path
import logging
from typing import Optional

from src.main.python.model import EtlWrapper
from src.main.python.model.SourceData import SourceData
from src.main.python.util import VariableConceptMapper
from src.main.python.model.cdm import *
from src.main.python.transformation import *
import enum

from src.main.python.transformation.challenge_to_person import challenge_to_person
from src.main.python.transformation.challenge_to_visit import challenge_to_visit
from src.main.python.transformation.challenge_to_stem_table import challenge_to_stem_table

logger = logging.getLogger(__name__)


class Wrapper(EtlWrapper):

    def __init__(self, database, source_folder, mapping_tables_folder):
        super().__init__(database=database, source_schema='')
        self.source_folder = Path(source_folder)
        self.variable_mapper = VariableConceptMapper(Path(mapping_tables_folder))
        self.person_id_lookup = None
        self.visit_occurrence_id_lookup = None
        self.episode_id_lookup = None
        self.event_field_concept_id_lookup = None
        self.stem_table_id_lookup = None
        #self.basedata_by_pid_lookup = None
        #self.enddata_by_pid_lookup = None
        self.challenge_by_pid_lookup = None
        #self.source_table_basedata = None
        #self.source_table_fulong = None
        #self.source_table_enddata = None
        self.source_table_challenge = None
        self.fulong_batch_number = 0
        self.FULONG_BATCH_SIZE = 5000

    def run(self):
        """Run PRIAS to OMOP V6.0 ETL"""
        self.start_timing()

        logger.info('{:-^100}'.format(' Source Counts '))
        self.log_tables_rowcounts(self.source_folder)

        logger.info('{:-^100}'.format(' Setup '))

        logger.info('Daimon config')
        # self.execute_sql_file('./postgres/30-source_source_daimon.sql')
        # self.execute_sql_file('./postgres/results_ddl_2.7.4.sql')
        self.execute_sql_query('SET search_path TO public;')

        # Prepare source
        self.drop_cdm()
        logger.info('Clinical CDM tables dropped')
        self.create_cdm()
        logger.info('CDM tables created')

        self.create_vocab_views()  # Views in public schema
        logger.info('Vocabulary views created')

        # Load custom concepts and stcm
        self.load_concept_from_csv('./resources/custom_vocabulary/2b_concepts.csv')
        """
        # Transformations
        logger.info('{:-^100}'.format(' ETL '))
        self.execute_transformation(basedata_to_person)
        self.execute_transformation(basedata_to_visit)
        self.execute_transformation(fulong_to_visit)
        self.execute_transformation(basedata_to_stem_table)
        while self.has_next_fulong_batch():
            self.execute_transformation(fulong_to_stem_table)
        self.execute_transformation(basedata_diagnosis_to_stem_table)
        self.execute_transformation(basedata_dre_to_stem_table)
        self.execute_transformation(fulong_dre_to_stem_table)
        self.execute_transformation(basedata_to_observation_period)
        self.execute_transformation(enddata_to_stem_table)
        self.execute_transformation(basedata_to_episode)
        self.execute_transformation(fulong_to_episode)
        """
        self.execute_transformation(challenge_to_person)
        self.execute_transformation(challenge_to_visit)
        self.execute_transformation(challenge_to_stem_table)

        logger.info('Stem table to domains')
        self.stem_table_to_domains()

        """
        logger.info('Episode event')
        self.execute_transformation(basedata_to_episode_event)
        self.execute_transformation(fulong_to_episode_event)
        self.execute_transformation(cdm_source)
        """

        self.log_summary()
        self.log_runtime()

    def stem_table_to_domains(self):
        post_processing_path = Path('src/main/python/post_processing')
        self.execute_sql_file(post_processing_path / 'stem_table_to_measurement.sql')
        self.execute_sql_file(post_processing_path / 'stem_table_to_condition_occurrence.sql')
        self.execute_sql_file(post_processing_path / 'stem_table_to_device_exposure.sql')
        self.execute_sql_file(post_processing_path / 'stem_table_to_drug_exposure.sql')
        self.execute_sql_file(post_processing_path / 'stem_table_to_observation.sql')
        self.execute_sql_file(post_processing_path / 'stem_table_to_procedure_occurrence.sql')
        self.execute_sql_file(post_processing_path / 'stem_table_to_specimen.sql')

    def drop_cdm(self):
        """Drops clinical tables, if they exist"""
        logger.info('Dropping OMOP CDM (non-vocabulary) tables if existing')
        self.db.base.metadata.drop_all(self.db.engine, tables=[
            clinical_data.ConditionOccurrence.__table__,
            clinical_data.DeviceExposure.__table__,
            clinical_data.DrugExposure.__table__,
            clinical_data.FactRelationship.__table__,
            clinical_data.Measurement.__table__,
            clinical_data.Note.__table__,
            clinical_data.NoteNlp.__table__,
            clinical_data.Observation.__table__,
            clinical_data.ObservationPeriod.__table__,
            clinical_data.Death.__table__,
            clinical_data.ProcedureOccurrence.__table__,
            clinical_data.Specimen.__table__,
            clinical_data.SurveyConduct.__table__,
            clinical_data.VisitOccurrence.__table__,
            clinical_data.VisitDetail.__table__,
            clinical_data.EpisodeEvent.__table__,
            clinical_data.Episode.__table__,
            derived_elements.DrugEra.__table__,
            derived_elements.DoseEra.__table__,
            derived_elements.ConditionEra.__table__,
            health_economics.PayerPlanPeriod.__table__,
            health_economics.Cost.__table__,
            clinical_data.Person.__table__,
            health_system_data.LocationHistory.__table__,
            health_system_data.Location.__table__,
            health_system_data.CareSite.__table__,
            health_system_data.Provider.__table__,
            clinical_data.StemTable.__table__,
            derived_elements.CdmSource.__table__
        ])

    def create_cdm(self):
        logger.info('Creating OMOP CDM (non-vocabulary) tables')
        self.db.base.metadata.create_all(self.db.engine)

    def create_person_lookup(self):
        """Initialize the person lookup"""
        with self.db.session_scope() as session:
            query = session.query(clinical_data.Person).all()
            self.person_id_lookup = {x.person_source_value: x.person_id for x in query}

    def lookup_person_id(self, person_source_value: str) -> int:
        if self.person_id_lookup is None:
            self.create_person_lookup()

        if person_source_value not in self.person_id_lookup:
            raise Exception('Person source value "{}" not found in lookup.'.format(person_source_value))

        return self.person_id_lookup[person_source_value]

    def create_visit_lookup(self):
        """ Initialize the visit lookup """
        with self.db.session_scope() as session:
            query = session.query(clinical_data.VisitOccurrence).all()
            self.visit_occurrence_id_lookup = {x.record_source_value: x.visit_occurrence_id for x in query}

    def lookup_visit_occurrence_id(self, visit_record_source_value):
        if self.visit_occurrence_id_lookup is None:
            self.create_visit_lookup()

        if visit_record_source_value not in self.visit_occurrence_id_lookup:
            logger.info('Visit record_source_value "{}" not found in lookup.'.format(visit_record_source_value))
            return None

        return self.visit_occurrence_id_lookup.get(visit_record_source_value)

    def create_episode_lookup(self):
        """ Initialize the episode lookup """
        with self.db.session_scope() as session:
            query = session.query(clinical_data.Episode).all()
            self.episode_id_lookup = {x.record_source_value: x.episode_id for x in query}

    def lookup_episode_id(self, episode_record_source_value):
        if self.episode_id_lookup is None:
            self.create_episode_lookup()

        if episode_record_source_value not in self.episode_id_lookup:
            raise Exception('Episode record source value "{}" not found in lookup.'.format(episode_record_source_value))

        return self.episode_id_lookup.get(episode_record_source_value)

    def domain_id_lookup(self, concept_id):
        """Initialize the domain lookup"""
        with self.db.session_scope() as session:
            query = session.query(Concept)
            result = query.filter_by(concept_id=concept_id).one()
            return result.domain_id

    def create_event_field_concept_id_lookup(self):
        event_field_concept_id_lookup = {
            'observation.observation_concept_id': 1147167,
            'measurement.measurement_concept_id': 1147140,
            'condition_occurrence.condition_concept_id': 1147129,
            'device_exposure.device_concept_id': 1147117,
            'drug_exposure.drug_concept_id': 1147096,
            'procedure_occurrence.procedure_concept_id': 1147084,
            'specimen.specimen_concept_id': 1147051,
            'visit_occurrence.visit_concept_id': 1147072
        }
        self.event_field_concept_id_lookup = event_field_concept_id_lookup

    def lookup_event_field_concept_id(self, concept_name):
        if self.event_field_concept_id_lookup is None:
            self.create_event_field_concept_id_lookup()

        if concept_name not in self.event_field_concept_id_lookup:
            logger.info('Event field concept "{}" could not be found in lookup.'.format(concept_name))
            return 0

        return self.event_field_concept_id_lookup.get(concept_name)

    def create_stem_table_lookup(self):
        """ Initialize the stem_table lookup """
        with self.db.session_scope() as session:
            query = session.query(clinical_data.StemTable).all()
            self.stem_table_id_lookup = {x.record_source_value: x.id for x in query}

    def lookup_stem_table_id(self, stem_table_record_source_value) -> Optional[int]:
        if self.stem_table_id_lookup is None:
            self.create_stem_table_lookup()

        if stem_table_record_source_value not in self.stem_table_id_lookup:
            logger.warning(f'Stem table record source value "{stem_table_record_source_value}" '
                           f'not found in lookup.')
            return None
        return self.stem_table_id_lookup.get(stem_table_record_source_value)

    def create_basedata_by_pid_lookup(self):
        """
        Initialize the basedata lookup
        Per person, get the person specific record
        :return:
        """
        self.basedata_by_pid_lookup = {x['p_id']: x for x in self.get_basedata()}

    def lookup_basedata_by_pid(self, p_id):
        if self.basedata_by_pid_lookup is None:
            self.create_basedata_by_pid_lookup()

        if p_id not in self.basedata_by_pid_lookup:
            raise Exception('Person id "{}" not found in lookup.'.format(p_id))

        return self.basedata_by_pid_lookup[p_id]
    
    def create_enddata_by_pid_lookup(self):
        """
        Initialize the enddata lookup
        Per person, get the person specific record
        :return:
        """
        self.enddata_by_pid_lookup = {x['p_id']: x for x in self.get_enddata()}

    def lookup_enddata_by_pid(self, p_id):
        if self.enddata_by_pid_lookup is None:
            self.create_enddata_by_pid_lookup()

        if p_id not in self.enddata_by_pid_lookup:
            return None
        return self.enddata_by_pid_lookup[p_id]
    
    def create_challenge_by_pid_lookup(self):
        self.challenge_by_pid_lookup = {int(x['patient_id']): x for x in self.get_challenge().data_dicts}

    def lookup_challenge_by_pid(self, patient_id):
        """Lookup challenge record by patient_id"""
        if self.challenge_by_pid_lookup is None:
            self.create_challenge_by_pid_lookup()
    
        return self.challenge_by_pid_lookup.get(patient_id, None)
    

    def gleason_sum(self, row, gleason_score1, gleason_score2):
        """
        :param row:
        :param gleason_score1:
        :param gleason_score2:
        :return variable, value:
        """
        variable = gleason_score1 + "_" + gleason_score2

        if row[gleason_score1] == '3' and row[gleason_score2] == '4':
            value = '3+4'
        elif row[gleason_score1] == '4' and row[gleason_score2] == '3':
            value = '4+3'
        else:
            value = int(row[gleason_score1]) + int(row[gleason_score2])
        return variable, value

    def pirads_score(self, value):
        value_lookup = {
            '1': 3,
            '2': 4,
            '3': 5
        }
        return value_lookup[value]

    def get_event_field_concept_id(self, concept_id):
        """
        :param concept_id:
        :return event_field_concept_id:
        """
        domain_id = self.domain_id_lookup(concept_id)
        domain_prefix = domain_id.split('_')[0]
        concept_name = domain_id + "." + domain_prefix + "_concept_id"
        concept_name = concept_name.lower()
        event_field_concept_id = self.lookup_event_field_concept_id(concept_name)
        return event_field_concept_id

    """
    def get_basedata(self):
        if not self.source_table_basedata:
            self.source_table_basedata = SourceData(self.source_folder / 'basedata.csv')

        return self.source_table_basedata

    def get_fulong(self):
        if not self.source_table_fulong:
            self.source_table_fulong = SourceData(self.source_folder / 'fulong.csv')

        return self.source_table_fulong
    """
    def get_challenge(self):
        if not self.source_table_challenge:
            self.source_table_challenge = SourceData(self.source_folder / 'omop_like_15.csv')

        return self.source_table_challenge

    def has_next_fulong_batch(self):
        if not self.source_table_fulong:
            self.source_table_fulong = SourceData(self.source_folder / 'fulong.csv')

        return self.fulong_batch_number * self.FULONG_BATCH_SIZE < len(self.source_table_fulong.data_dicts)

    def get_next_fulong_batch(self):
        if not self.source_table_fulong:
            self.source_table_fulong = SourceData(self.source_folder / 'fulong.csv')
        start_index = self.fulong_batch_number*self.FULONG_BATCH_SIZE
        end_index = (self.fulong_batch_number+1)*self.FULONG_BATCH_SIZE
        end_index = min(end_index, len(self.source_table_fulong.data_dicts))
        self.fulong_batch_number += 1
        return self.source_table_fulong.data_dicts[start_index:end_index]

    def get_enddata(self):
        if not self.source_table_enddata:
            self.source_table_enddata = SourceData(self.source_folder / 'enddata.csv')

        return self.source_table_enddata

    def create_vocab_views(self):
        self.execute_sql_query("""
        CREATE OR REPLACE VIEW concept AS (SELECT * FROM vocab.concept);
        CREATE OR REPLACE VIEW concept_ancestor AS (SELECT * FROM vocab.concept_ancestor);
        CREATE OR REPLACE VIEW concept_class AS (SELECT * FROM vocab.concept_class);
        CREATE OR REPLACE VIEW domain AS (SELECT * FROM vocab.domain);
        CREATE OR REPLACE VIEW vocabulary AS (SELECT * FROM vocab.vocabulary);
        """)

    # Set the different visit types
    class VisitType(enum.Enum):
        standard = 1
        mri = 2
