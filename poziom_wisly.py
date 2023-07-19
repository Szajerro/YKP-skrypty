# Data manipulation:
import numpy as np
import pandas as pd
import datetime as dt

# Data download:
import requests
from google.oauth2 import service_account
import gspread

# System manipulation:
import json
from os import environ


hydro = requests.get("http://danepubliczne.imgw.pl/api/data/hydro/").text
hydro_data = json.loads(hydro)
for item in hydro_data:
    if item['id_stacji'] == '152210170':
        bulwary_dict = item
bulwary_df = pd.DataFrame(pd.Series(bulwary_dict)).T
scopes = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive']
credentials_google = service_account.Credentials.from_service_account_file(
    environ['PERSONAL_GCLOUD_KEY'],scopes=scopes)
project_id = 'rtbhouse-business-apac'
gspread_client = gspread.Client(auth=credentials_google)
spreadsheet_id = '1eJSD3_ma89LpI38C4e_xYDUixB6cJ7d6IkVgM0kxVxQ'
worksheet_name = 'Poziom wody'

bulwary_df.fillna('',inplace=True)
spreadsheet = gspread_client.open_by_key(spreadsheet_id)
worksheet = spreadsheet.worksheet(worksheet_name)
spreadsheet_data = pd.DataFrame(worksheet.get_all_values()[1:],columns=worksheet.get_all_values()[0])

def to_spreadsheet_date(x):
    time = dt.datetime.strptime(x,'%Y-%m-%d %H:%M:%S')
    date_0 = dt.datetime(1899, 12, 30).date()
    hour = time.hour
    date = time.date()
    delta = (date - date_0).days + (hour / 24)
    return delta


bulwary_df['stan_wody_data_pomiaru'] = bulwary_df['stan_wody_data_pomiaru'].apply(lambda x: to_spreadsheet_date(x))
final_df = pd.concat([bulwary_df,spreadsheet_data],axis=0)
dataframe_to_update = final_df
worksheet.update([dataframe_to_update.columns.values.tolist()] + dataframe_to_update.values.tolist())



