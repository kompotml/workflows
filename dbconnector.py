import os

import mysql.connector as mc
from utilities import Utilities

import pandas as pd


class WorkflowsDB:
    def __init__(self, connection_data: dict):
        self.utils = Utilities()
        self.dirname = os.path.dirname(__file__)
        self.connection = mc.connect(**connection_data)
        mc.connect()
        self.build_database()
        print(f"Connected to {connection_data['database']}.")

    def query_to_df(self, sql_query: str) -> pd.DataFrame:
        try:
            self.connection.reconnect()
            crs = self.connection.cursor()
            crs.execute(sql_query)
            records = pd.DataFrame(crs.fetchall())
            records.columns = crs.column_names
            return records
        except Exception as ex:
            print(f"Failed loading query from database: {ex}")

    def run(self, sql_query: str):
        try:
            crs = self.connection.cursor()
            crs.execute(sql_query)
            return "Success"
        except Exception as ex:
            print(f"Failed running query: {ex}")

    def close(self):
        try:
            self.connection.close()
            print("MySQL Connection closed!")
        except Exception as ex:
            print(f"Failed closing database connection: {ex}")

    def status(self):
        print(f"Connected: {self.connection.is_connected()}")

    def get_db_name(self):
        self.connection.reconnect()
        crs = self.connection.cursor()
        crs.execute("select database();")
        record = crs.fetchone()[0]
        return record

    def generate_webform_data(self):
        procedure_name = "get_workflows_submissions"
        db_name = self.get_db_name()
        sp_code = f"""
        CREATE OR REPLACE PROCEDURE {db_name}.{procedure_name}()
        BEGIN
            set @sql = null;
            SELECT
              GROUP_CONCAT(DISTINCT
                           CONCAT('MAX(IF(`element` = "', `element`,'", `value`,"")) AS "',`element`,'"')
                          ) into @sql
            from workflows.vw_concat;
            SET @sql = CONCAT('SELECT  FROM_UNIXTIME(b.`changed`) changed_date, s.`sid`,  ', @sql, ' FROM workflows.vw_concat s join workflows.workflowsapp_webform_submission b on s.`sid` = b.`sid` 
                            where FROM_UNIXTIME(b.`changed`) >= CURRENT_TIMESTAMP - INTERVAL 3 MINUTE
                            GROUP BY b.`changed`, b.`uid`, s.`sid` ORDER BY s.`sid` ');
            PREPARE stmt FROM @sql;
            EXECUTE stmt;
        end
        """
        status = self.run(sp_code)
        print(status)
        return f"call {db_name}.{procedure_name}()"

    def upsert_df_row(self, df_row: pd.DataFrame, target_table: str) -> None:
        self.connection.reconnect()
        series = df_row.to_records(index=False)[0]
        sql = f"""
            REPLACE INTO workflows.{target_table} (changed_date, sid, workflow_name, submitted_by, submitted_by_role, implemented, 
            decoded_data, saved_path) VALUES{series}; 
        """
        crs = self.connection.cursor()
        crs.execute(sql)
        crs.execute("commit;")

    def get_webform_data(self, stored_procedure_name: str) -> pd.DataFrame:
        try:
            new_df = self.query_to_df(stored_procedure_name)
            return new_df
        except Exception as ex:
            print(f"Failed getting webform data: {ex}")

    def build_database(self):
        try:
            with open(f"{self.utils.filepath}\\config.sql") as file:
                config_file = file.read()
            self.run(config_file)
        except Exception as ex:
            print(f"Failed building items. {ex}")
