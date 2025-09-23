-- Create additional database for AI data on first container start
-- This script is executed automatically by the official Postgres image
-- when mounted to /docker-entrypoint-initdb.d and the PGDATA dir is empty

-- Create database if it does not exist (idempotent)
DO $$
BEGIN
   IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'finance_ai_db') THEN
      EXECUTE 'CREATE DATABASE finance_ai_db OWNER ' || current_user;
   END IF;
END$$;


