-- Table: public.operation

-- DROP TABLE IF EXISTS public.operation;

CREATE TABLE IF NOT EXISTS public.operation
(
    operation_id character varying(128) COLLATE pg_catalog."default" NOT NULL,
    operation_log character varying(100) COLLATE pg_catalog."default",
    start_datetime character varying(20) COLLATE pg_catalog."default" NOT NULL,
    end_datetime character varying(20) COLLATE pg_catalog."default",
    total_duration character varying(20) COLLATE pg_catalog."default",
    operation_status character varying(20) COLLATE pg_catalog."default" NOT NULL,
    source_database_ip character varying(128) COLLATE pg_catalog."default" NOT NULL,
    destination_database_ip character varying(20) COLLATE pg_catalog."default" NOT NULL,
    total_tasks integer NOT NULL,
    total_passed_tasks integer
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.operation
    OWNER to postgres;

-- Table: public.operation_details

-- DROP TABLE IF EXISTS public.operation_details;

CREATE TABLE IF NOT EXISTS public.operation_details
(
    operation_id character varying(128) COLLATE pg_catalog."default" NOT NULL,
    task_id integer NOT NULL,
    task_name character varying(100) COLLATE pg_catalog."default" NOT NULL,
    task_description text COLLATE pg_catalog."default" NOT NULL,
    task_start_datetime character varying(20) COLLATE pg_catalog."default",
    task_end_datetime character varying(20) COLLATE pg_catalog."default",
    task_duration character varying(20) COLLATE pg_catalog."default",
    task_status character varying(20) COLLATE pg_catalog."default",
    remarks character varying(300) COLLATE pg_catalog."default",
    id_field_name character varying(100) COLLATE pg_catalog."default",
    ts_field_name character varying(100) COLLATE pg_catalog."default",
    db_name character varying(100) COLLATE pg_catalog."default" NOT NULL,
    archived_records bigint,
    deleted_records bigint,
    data_retention_days integer
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.operation_details
    OWNER to postgres;
-- Index: indx_operation_details_operation_id

-- DROP INDEX IF EXISTS public.indx_operation_details_operation_id;

CREATE INDEX IF NOT EXISTS indx_operation_details_operation_id
    ON public.operation_details USING btree
    (operation_id COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;