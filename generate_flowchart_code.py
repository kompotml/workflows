import os
from collections import defaultdict
import pandas as pd
import numpy as np
import json
from pyflowchart import StartNode, SubroutineNode, ConditionNode, InputOutputNode, OperationNode, Flowchart, EndNode
from selenium import webdriver
from typing import Tuple
import base64
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

dirname = os.path.dirname(__file__)
os.environ["PATH"] += os.pathsep + f"{dirname}\\chromedriver.exe"
with open(f'{dirname}\\rules.json') as rules:
    rules_dict = json.load(rules)

with open(f'{dirname}\\regex_rules.json') as regex:
    regex_rules = json.load(regex)


def convert_row_to_dict(data_frame: pd.DataFrame) -> Tuple[dict, pd.DataFrame]:
    try:
        converted_dataframe = {}
        metadata = data_frame[
            ['changed_date', 'sid', 'workflow_name_', 'submit_as_', 'your_role__', 'final_element_', 'implemented_']]
        for key, value in regex_rules.items():
            elements = []
            columns = data_frame.filter(regex=value).columns
            data_frame[columns].replace(r'^\s*$', 0, regex=True).apply(lambda x: elements.append(x[0]))
            converted_dataframe[key] = [*elements]
    except TypeError as te:
        print(f"Query has returned 0 rows.: {te}")
    except AttributeError as ae:
        print(f"Query returned an empty dataframe: {ae}")
    except Exception as ex:
        print(f"Could not convert DataFrame to dict: {ex}")
        raise
    return converted_dataframe, metadata


def transpose_dict(values: dict) -> dict:
    try:
        transposed_dict = defaultdict(dict)
        for key, _ in regex_rules.items():
            i = len(values[key])
            for j in range(i):
                transposed_dict[f"element{j}"][key] = values[key][j]
    except Exception as ex:
        print(f"Could not transpose dictionary: {ex}")
        raise
    return transposed_dict


def add_function_to_element_type(transposed_dict: dict) -> dict:
    try:
        for k, v in transposed_dict.items():
            transposed_dict[k]['function'] = rules_dict[v['element_type']]["function"]
    except ValueError as ve:
        print(f"Value error, could not add function to element type: {ve}")
        raise
    except Exception as ex:
        print(f"Could not add function to element type: {ex}")
        raise
    return transposed_dict


def create_flowchart_code(dict_object: dict, fe: str) -> str:
    try:
        created_elements = defaultdict(dict)
        st = StartNode("Workflow")
        e = EndNode('Workflow')
        for item, value in dict_object.items():
            created_elements[int(value['element_order'])][item] = value['element_type']
            if (value['function']) != "skip":
                exec(f"global {item}; {item} = {value['function']}'{value['element_description']}')")
            else:
                exec(f"global {item}; {item} = element{int(value['element_order']) - 1}")

        sorted_dict = dict(sorted(created_elements.items()))
        for key, value in sorted_dict.items():
            for subitem, subval in value.items():
                if key == 0:
                    exec(f"st.connect(element{key})")
                elif subval == 'condyes':
                    for element in dict_object.items():
                        if int(element[1]['element_order']) == int(subitem[-1:]) + 1:
                            exec(f"element{key}.connect_yes({element[0]})")
                elif subval == 'condno':
                    for element in dict_object.items():
                        if int(element[1]['element_order']) == int(subitem[-1:]) + 1:
                            exec(f"element{key}.connect_no({element[0]})")
                else:
                    exec(f"element{key - 1}.connect({subitem})")
        exec(f"element{int(fe) - 1}.connect(e)")
        fc = Flowchart(st)
    except Exception as ex:
        print(f"Error in creating Flowchart code: {ex}")
    return fc.flowchart()


def generate_flowchart(fc_code, fc_path, timestamp):
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        driver = webdriver.Chrome(executable_path=f"{dirname}\\chromedriver.exe", chrome_options=options)
        driver.get('https://flowchart.js.org/')

        elements = driver.find_element(By.CLASS_NAME, "ace_text-input")
        elements.clear()
        elements.send_keys(fc_code)

        diagram = driver.find_element(By.XPATH, "/html/body/div[1]/section/table/tbody/tr/td[2]")
        driver.set_window_size(1200, 1200)
        ActionChains(driver).scroll_to_element(diagram).perform()

        sb64 = diagram.screenshot_as_base64
        decoded_data = base64.b64decode(sb64)
        flowchart_saved_path = f"{fc_path}workflow_{timestamp}.png"
        img_file = open(flowchart_saved_path, 'wb')
        img_file.write(decoded_data)
        img_file.close()
        driver.close()
        return sb64, flowchart_saved_path

    except Exception as ex:
        print(f"Failed to generate flowchart png: {ex}")


def generate_flowchart_from_df(df: pd.DataFrame, flowcharts_path: str, timestamp: str) -> pd.DataFrame:
    try:
        conversion, metadata = convert_row_to_dict(df)
        final_element = metadata.filter(regex="final_element_$").columns
        fe = int(metadata[final_element].values[0][0])
        transposed = transpose_dict(conversion)
        final_object = add_function_to_element_type(transposed)
        pseudocode = create_flowchart_code(final_object, fe)
        decoded_data, flowchart_saved_path = generate_flowchart(pseudocode, flowcharts_path, timestamp)
        metadata = metadata.drop(['final_element_'], axis=1)
        metadata['decoded_data'] = decoded_data
        metadata['flowchart_saved_path'] = flowchart_saved_path
        return metadata
    except Exception as ex:
        print(f"error in generate_flowchart_from_df: {ex}")

