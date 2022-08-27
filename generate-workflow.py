import os
import datetime
import numpy as np
from utilities import Utilities
from dbconnector import WorkflowsDB
from generate_flowchart_code import FlowChartGenerator


utils = Utilities()
flowcharts_path = utils.flowcharts_path
db_data = utils.load_db_properties()
wf = WorkflowsDB(db_data)
sp_name = wf.generate_webform_data()
df = wf.get_webform_data(sp_name)

for i in range(len(df)):
    fc_gen = FlowChartGenerator()
    timestamp = datetime.datetime.utcnow().strftime("%y_%m_%d_%H_%M_%S")
    df_row = df.iloc[[i]]
    df_row['1st_element_follows'] = 0
    df_row = df_row.replace('', np.nan)
    df_row = df_row.dropna(how='all', axis=1)
    df_row = df_row.reset_index()
    metadata = fc_gen.generate_flowchart_from_df(df_row, flowcharts_path, timestamp)
    wf.upsert_df_row(metadata, 'generatedworkflows')


