# OMOP Data Engineering Challenge
ETL scripts to convert the Prostate cancer Research International: Active Surveillance (PRIAS) datasets to a PIONEER modification of [OMOP CDM v6.x](https://github.com/thehyve/ohdsi-omop-pioneer/tree/master/pioneer_omop_cdm). 
+ [Oncology WG extensions](https://github.com/OHDSI/OncologyWG/wiki).

## Mapping Document
The mapping document can be found [here](https://thehyve.github.io/ohdsi-etl-prias/).

## Prerequisites
- Docker Desktop
- Visual Studio Code (VS Code)
- PostgreSQL (local install or via Docker)
- pgAdmin (recommended for database exploration)

## Vocabulary

You download the vocabulary files that you wish to use from Athena. The downloaded .zip folder containing the .csv vocabulary files needs to be renamed to *vocabulary.zip* and placed in the postgres folder. 

## Docker
First you navigate to your postgres directory

`cd postgres`

And build the Docker image of postgres

`docker build -t thehyve/ohdsi_postgresql`

Then you navigate back to your main project directory

`cd ..`

And start your container

`docker-compose up -d` will start the following containers:
* postgresql
* broadsea-webtools
* broadsea-methods-library
* jupyter
* etl

To view the progress of the database setup and etl, view the logs:
* To check the postgres database:
`docker-compose logs -f postgresql`
or in the Docker Desktop.

To run ETL again: `docker-compose up -d --build etl` and check the etl logs.

## Target
The resulting OMOP CDM is written to the `public` schema.



## Junior challenge dataset

This repository includes a small, synthetic dataset for the junior challenge:

- Folder: `resources/test_datasets/junior_challenge_15/`
- File: `omop_like_15.csv`
- Size: 15 patients, ~30 columns covering demographics (gender, nationality), visit info (outpatient/inpatient/emergency), measurements, conditions, procedures, drug exposures, and observations.

This dataset is intentionally different from the default PRIAS source files so that you can design your own transformations.

### How to run the ETL against this dataset

Option A — Docker (recommended):
1. Edit `docker-compose.yml` and set the ETL source folder to the challenge dataset folder:
   - `ETL_SOURCE=/app/resources/test_datasets/junior_challenge_15`
2. Start or rebuild the ETL service:
```
docker compose up -d --build etl
docker compose logs -f etl
```

Troubleshooting on Windows: If you see an error like:

```
/bin/sh^M: bad interpreter: No such file or directory
```

This is caused by Windows CRLF line endings in `postgres/10-init-vocabulary.sh`.
Fix:
- Open the file in Notepad++
- Convert line endings to UNIX (LF): Edit -> EOL Conversion -> Unix (LF)
- Save the file and rebuild: `docker compose up --build`

### Where to change the path (for Docker)
In `docker-compose.yml` under the `etl` service, update the `ETL_SOURCE` environment variable to point to the challenge folder.

### Important: the default transformations expect PRIAS files

The current ETL expects three PRIAS-style source files in the source folder:
- `basedata.csv`
- `fulong.csv`
- `enddata.csv`

Your `omop_like_15.csv` is a single wide file and does not match that structure. You must follow the approach below:

1) Write a custom transformation (preferred challenge):
   - Add a new module under `src/main/python/transformation/` (e.g. `challenge_to_stem_table.py`) that reads `omop_like_15.csv` and writes to the OMOP `stem_table` model, similar to how `basedata_to_stem_table.py` and `fulong_to_stem_table.py` do.
   - Wire your function into the pipeline in `src/main/python/wrapper.py` before the post-processing steps that move the stem table into domain tables.

## What the transformation scripts do (high level)

- `basedata_to_person.py`: Creates `person` records from `basedata.csv` (person_id, birth year, death date if applicable, gender, etc.).
- `basedata_to_visit.py` and `fulong_to_visit.py`: Create `visit_occurrence` (baseline visits and MRI visits) from `basedata.csv` and `fulong.csv`.
- `basedata_to_stem_table.py`, `fulong_to_stem_table.py`, `enddata_to_stem_table.py`: Populate an intermediate `stem_table` with measurements/observations/conditions/procedures/drugs using mapping tables from `resources/mapping_tables/`.
- Post-processing SQL in `src/main/python/post_processing/*.sql`: Moves rows from `stem_table` into OMOP domain tables (`measurement`, `condition_occurrence`, `procedure_occurrence`, `drug_exposure`, `observation`, `specimen`).

## What you (the challenger) need to do

Pick an approach and implement it:

Approach  — Custom transformation:
- Create `src/main/python/transformation/challenge_to_stem_table.py` with a function, e.g. `def challenge_to_stem_table(wrapper) -> list:` that:
  - Reads `resources/test_datasets/junior_challenge_15/omop_like_15.csv` (use `SourceData` to read a CSV).
  - Maps columns to OMOP concepts and fills the `stem_table` ORM model.
  - Returns a list of ORM records to be inserted (follow the pattern in existing `*_to_stem_table.py`).
- Edit `src/main/python/wrapper.py` to call your function in `run()` before `stem_table_to_domains()`.
- Optionally skip or comment out original PRIAS-specific transformations while testing your custom pipeline.

Tips:
- `SourceData` lowercases headers and uses Windows-1252 encoding by default.
- Use the mapping tables under `resources/mapping_tables/` to map names/values/units to standard concepts, or hardcode concept_ids for this exercise.
- Keep `record_source_value` fields meaningful for traceability.

## Verifying your results
- After the ETL run, check row counts in `public.person`, `public.visit_occurrence`, `public.measurement`, `public.condition_occurrence`, `public.procedure_occurrence`, `public.drug_exposure`, `public.observation`.
- Confirm your 15 patients appear in `person` and that downstream domain tables have rows consistent with your input.