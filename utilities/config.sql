create view if not EXISTS workflows.vw_concat as
select sid, concat(name, "_", property) element, value from workflows.workflowsapp_webform_submission_data wwsd
where webform_id = 'create_workflow';

CREATE TABLE IF NOT EXISTS workflows.GeneratedWorkflows (
  changed_date TIMESTAMP,
  sid int AUTO_INCREMENT PRIMARY KEY,
  workflow_name varchar(45) DEFAULT NULL,
  submitted_by varchar(45) NOT NULL,
  submitted_by_role varchar(25) not null,
  decoded_data blob not null,
  saved_path varchar(255) not null,
  implemented varchar(5) not null,
  load_timestamp TIMESTAMP default CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);