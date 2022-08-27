import json
import os


class Utilities:

    def __init__(self):
        self.filepath = f"{os.path.dirname(__file__)}\\utilities"
        self.flowcharts_path = "C:\\xampp\\htdocs\\workflows\\sites\\default\\files\\flowcharts\\"

    def load_json_from_path(self, file_name: str) -> dict:
        try:
            with open(f"{self.filepath}\\{file_name}") as json_file:
                data = json.load(json_file)
        except Exception as ex:
            print(f"Couldn't load json from: {self.filepath}. Reason: {ex}")
        return data

    def get_chromedriver_path(self) -> str:
        chromedriver_path = ""
        try:
            chromedriver_path = f"{self.filepath}/chromedriver.exe"
        except Exception as ex:
            print(f"Could not return filepath: {ex}")
        return chromedriver_path

    def load_db_properties(self) -> dict:
        db_properties_name = "dbproperties.json"
        db_props = self.load_json_from_path(db_properties_name)
        return db_props

    def load_flowchart_rules(self) -> dict:
        flow_chart_rules_name = "rules.json"
        flowchart_rules = self.load_json_from_path(flow_chart_rules_name)
        return flowchart_rules

    def load_regex_rules(self) -> dict:
        regex_rules_name = "regex_rules.json"
        regex_rules_dict = self.load_json_from_path(regex_rules_name)
        return regex_rules_dict

