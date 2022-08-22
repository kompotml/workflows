import os
import datetime
import numpy as np
import utilities as utils

from dbconnector import WorkflowsDB
from generate_flowchart_code import generate_flowchart_from_df

dirname = os.path.dirname(__file__)


file_path = f'{dirname}\\dbproperties.json'
flowcharts_path = 'C:\\xampp\\htdocs\\workflows\\sites\\default\\files\\flowcharts\\'
db_data = utils.load_json_from_pat(file_path)
wf = WorkflowsDB(db_data)
sp_name = wf.generate_webform_data()
df = wf.get_webform_data(sp_name)

for i in range(len(df)):
    timestamp = datetime.datetime.utcnow().strftime("%y_%m_%d_%H_%M_%S")
    df_row = df.iloc[[i]]
    df_row['1st_element_follows'] = 0
    df_row = df_row.replace('', np.nan)
    df_row = df_row.dropna(how='all', axis=1)
    df_row = df_row.reset_index()
    metadata = generate_flowchart_from_df(df_row, flowcharts_path, timestamp)
    wf.upsert_df_row(metadata, 'generatedworkflows')


