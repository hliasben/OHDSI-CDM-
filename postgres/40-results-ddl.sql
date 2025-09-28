-- Create results schema and tables
CREATE SCHEMA IF NOT EXISTS prias_results;
SET search_path TO prias_results;

-- Copy the entire content of results_ddl_2.7.4.sql here
-- Or keep it as a separate file and just reference it:
\i /docker-entrypoint-initdb.d/results_ddl_2.7.4.sql