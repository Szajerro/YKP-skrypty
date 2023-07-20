# Data manipulation:
import pandas as pd
import datetime as dt

# Data download:
import requests
from google.oauth2 import service_account
import gspread

# System manipulation:
import json
from os import environ

scopes = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive']
credentials_google = service_account.Credentials.from_service_account_file(
    environ['PERSONAL_GCLOUD_KEY'],scopes=scopes)
gspread_client = gspread.Client(auth=credentials_google)
spreadsheet_id = '1eJSD3_ma89LpI38C4e_xYDUixB6cJ7d6IkVgM0kxVxQ'

worksheet_name = 'Parametry pomostu'
spreadsheet = gspread_client.open_by_key(spreadsheet_id)
worksheet = spreadsheet.worksheet(worksheet_name)
pomost_df = pd.DataFrame(worksheet.get_all_values()[1:],columns=worksheet.get_all_values()[0])
pomost_df.set_index('Key',inplace=True)
pomost_dict = dict(pomost_df['Value'])

hydro = requests.get("http://danepubliczne.imgw.pl/api/data/hydro/").text
hydro_data = json.loads(hydro)
for item in hydro_data:
    if item['id_stacji'] == '152210170':
        bulwary_dict = item | pomost_dict
bulwary_df = pd.DataFrame(pd.Series(bulwary_dict)).T
bulwary_df.fillna('',inplace=True)

def to_spreadsheet_date(x):
    time = dt.datetime.strptime(x,'%Y-%m-%d %H:%M:%S')
    date_0 = dt.datetime(1899, 12, 30).date()
    hour = time.hour
    date = time.date()
    delta = (date - date_0).days + (hour / 24)
    return delta


worksheet_name = 'Poziom wody'
spreadsheet = gspread_client.open_by_key(spreadsheet_id)
worksheet = spreadsheet.worksheet(worksheet_name)
spreadsheet_data = pd.DataFrame(worksheet.get_all_values()[1:],columns=worksheet.get_all_values()[0])

final_df = pd.concat([bulwary_df,spreadsheet_data],axis=0)
final_df.fillna('',inplace=True)

final_df['stan_wody_data_pomiaru'] = final_df['stan_wody_data_pomiaru'].apply(lambda x: to_spreadsheet_date(x) if x != '' else '')
final_df['zjawisko_zarastania_data_pomiaru'] = final_df['zjawisko_zarastania_data_pomiaru'].apply(lambda x: to_spreadsheet_date(x) if x != '' else '')
final_df['stan_wody'] = final_df['stan_wody'].apply(lambda x: int(x) if x != '' else '')
final_df['zjawisko_zarastania'] = final_df['zjawisko_zarastania'].apply(lambda x: int(x) if x != '' else '')

final_df['temperatura_wody_data_pomiaru'] = final_df['temperatura_wody_data_pomiaru'].apply(lambda x: to_spreadsheet_date(x) if x != '' else '')
final_df['zjawisko_lodowe_data_pomiaru'] = final_df['zjawisko_lodowe_data_pomiaru'].apply(lambda x: to_spreadsheet_date(x) if x != '' else '')
final_df['temperatura_wody'] = final_df['temperatura_wody'].apply(lambda x: int(x) if x != '' else '')
final_df['zjawisko_lodowe'] = final_df['zjawisko_lodowe'].apply(lambda x: int(x) if x != '' else '')


dataframe_to_update = final_df
worksheet.update([dataframe_to_update.columns.values.tolist()] + dataframe_to_update.values.tolist())

formatting = {
    'numberFormat': {
        "type":"DATE",
        "pattern": "yyyy-mm-dd HH:MM:SS"
    }
}

worksheet.format('F2:F995',formatting)
worksheet.format('H2:H995',formatting)
worksheet.format('J2:J995',formatting)
worksheet.format('L2:L995',formatting)
