-- operation definition

DROP TABLE operation;

CREATE TABLE operation(
	operation_id VARCHAR(128) NOT NULL,
	operation_log varchar(100),
	start_datetime	varchar(20) NOT NULL,
	end_datetime	varchar(20),
	total_duration varchar(20),
	operation_status	VARCHAR(20) NOT NULL,
	source_database_ip VARCHAR(128) NOT NULL,
	destination_database_ip VARCHAR(20) NOT null,
	total_tasks		INTEGER NOT NULL,
	total_passed_tasks	INTEGER
);


-- operation_details definition

DROP TABLE operation_details;


CREATE TABLE IF NOT EXISTS public.operation_details
(
    operation_id varchar(128) NOT NULL,
    task_id integer NOT NULL,
    task_name varchar(100)  NOT NULL,
    task_description text  NOT NULL,
    task_start_datetime varchar(20),
    task_end_datetime varchar(20),
    task_duration varchar(20),
    task_status varchar(20),
    remarks varchar(300),
    id_field_name varchar(100),
    ts_field_name varchar(100),
    db_name varchar(100) NOT NULL,
    archived_records bigint,
    deleted_records bigint,
    data_retention_days bigint
);

CREATE INDEX indx_operation_details_operation_id
ON operation_details(operation_id);

