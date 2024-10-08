# -*- coding: utf-8 -*-
"""Ops dashboard utilisation (product filter) - latest script

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1U6jHTpEC7e2xI0SSP7_2dN81x_-Qnsma
"""

!pip install gspread oauth2client

! pip install gspread df2gspread

from google.colab import drive

# Mounting drive so that we can to google sheet
drive.mount('/content/drive')

# Libraries required to connect to google sheet
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Define the scope
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# Provide the path to your credentials JSON file obtained from Google Developer Console
credentials = ServiceAccountCredentials.from_json_keyfile_name('/content/drive/MyDrive/cgxi-426308-9c147845f434.json', scope)

# Authenticate with Google Sheets
gc = gspread.authorize(credentials)

# Connect to the input raw data in google sheet
timesheet_mapping_ = gc.open_by_key('1orV_Qh5-2UL7eAqRQmbDSh5P2NLylQlpIQXTa8YuBu0') # Mapping File
timesheet_logger_ = gc.open_by_key('1wjx9tqAM_ShL-GRDRboD9xOO8JMFRZOaRLmm1gNthS0') # Timesheet Logger
timesheet_logger_1 = gc.open_by_key('1Z6CjKymnKcaK4TJnXztG-BAugT97KeWjdS4du8rvcxI') # Timesheet Logger Q3

# Select the worksheet by index (0 for the first worksheet)
timesheet_mapping = timesheet_mapping_.get_worksheet(0) # 0 Means we are picking first tab of the sheet
holiday_mapping = timesheet_mapping_.get_worksheet(8)
timesheet_logger = timesheet_logger_.get_worksheet(1)
timesheet_logger1 = timesheet_logger_1.get_worksheet(0)
non_billable_key_id = timesheet_mapping_.get_worksheet(7)

# Get all values from the worksheet
data = timesheet_logger.get_all_values() # To fetch the entire data of the tab
data_1 = timesheet_mapping.get_all_values()
data_2 = holiday_mapping.get_all_values()
data_4 = timesheet_logger1.get_all_values()
data_5 = non_billable_key_id.get_all_values()

# Importing pandas and numpy library
import pandas as pd
import numpy as np

# Convert data to a DataFrame
timesheet_data = pd.DataFrame(data[5:], columns=data[4]) # data[5:] - Pick tthe data from 6th Row, # columns=data[4] - Pick the column name from 5th row (To define the header)
timesheet_data_ = pd.DataFrame(data_4[5:], columns=data_4[4])
mapping_data = pd.DataFrame(data_1[1:], columns=data_1[0])
holiday_data = pd.DataFrame(data_2[1:], columns=data_2[0])
holiday_data = pd.DataFrame(data_2[1:], columns=data_2[0])
non_billable_key_ids = pd.DataFrame(data_5[1:], columns=data_5[0])

mapping_data

mapping_data['Role'] = mapping_data['Role'].astype(str).str.replace('Ex_', '', regex=False)
mapping_data.head()

def parse_date(date_str):
    formats = ['%m/%d/%Y', '%m/%d/%Y %H:%M:%S']
    for fmt in formats:
        try:
            return pd.to_datetime(date_str, format=fmt)
        except ValueError:
            pass
    # If none of the formats work, return NaT
    return pd.NaT

def parse_date_joining(date_str):
    if pd.isna(date_str) or date_str == '':
        return datetime(2024, 4, 1).date()

    formats = ['%d-%b-%Y', '%d-%b-%Y %H:%M:%S']
    for fmt in formats:
        try:
            return pd.to_datetime(date_str, format=fmt).date()
        except ValueError:
            pass
    # If none of the formats work, return 1st april 2024
    return datetime(2024, 4, 1).date()

def get_quarter_end_date():
    current_year = datetime.now().year
    current_quarter = (datetime.now().month - 1) // 3 + 1

    if current_quarter == 1:
        end_date = pd.to_datetime(f'{current_year}-03-31')
    elif current_quarter == 2:
        end_date = pd.to_datetime(f'{current_year}-06-30')
    elif current_quarter == 3:
        end_date = pd.to_datetime(f'{current_year}-09-30')
    else:
        end_date = pd.to_datetime(f'{current_year}-12-31')
    return end_date.date()

def parse_date_exit(date_str):
    if pd.isna(date_str) or date_str == '':
        # Handle NaN or empty string values by returning the end date of the current quarter
        return get_quarter_end_date()

    formats = ['%d-%b-%Y', '%d-%b-%Y %H:%M:%S']
    for fmt in formats:
        try:
            # Parse the date and return as a date object
            return pd.to_datetime(date_str, format=fmt, errors='coerce').date()
        except ValueError:
            # Continue trying other formats
            continue

    # If none of the formats work, return the end date of the current quarter
    return get_quarter_end_date()

from datetime import datetime, timedelta

mapping_data['Date of Joining'] = mapping_data['Date of Joining'].apply(parse_date_joining)
mapping_data['Date of Exit'] = mapping_data['Date of Exit'].apply(parse_date_exit)
mapping_data['Date of Joining'] = pd.to_datetime(mapping_data['Date of Joining'])
mapping_data['Date of Exit'] = pd.to_datetime(mapping_data['Date of Exit'])

# Selecting the column required from resource mapping file
mapping_data = mapping_data[['Resource Name', 'CTN ID', 'Role', 'Location', 'Channel', 'Date of Joining', 'Date of Exit', 'Dedicated/Non Dedicated']]
mapping_data.head() # To see the data of 5 row

# timesheet_data = timesheet_data[timesheet_data['Channel'].isin(['Email', 'Studio Services', 'Data', 'Strategic Services', 'Tech', 'Technology', 'ASO', 'HPP', 'MOps', '', 'N/A', 'NA'])]

# Drop 'Role' and 'Country' columns from timesheet log
timesheet_data.drop(columns = ['Role', 'Country'], axis = 1, inplace = True) # Axis 1 means vertical i.e columns and Axis 0 Horizontal i.e rows represent
timesheet_data_.drop(columns = ['Role', 'Country'], axis = 1, inplace = True)

# Unpivot timesheet data
id_cols = ['Estimate ID', 'Request ID', 'Key ID', 'Campaign Details',
           'Product Line', 'Channel', 'Campaign Name', 'Deliverable Name',
           'Request Type', 'Resource']

df_unpivoted = pd.melt(timesheet_data, id_vars=id_cols, var_name='Date', value_name='Minutes')
df_unpivoted = df_unpivoted[df_unpivoted['Minutes'].astype(str).str.match(r'^\d*\.?\d+$')]
df_unpivoted['Minutes'] = df_unpivoted['Minutes'].astype('float')
df_unpivoted.reset_index(inplace = True, drop = True)

# Unpivot timesheet data
id_cols = ['Estimate ID', 'Request ID', 'Key ID', 'Campaign Details',
           'Product Line', 'Channel', 'Campaign Name', 'Deliverable Name',
           'Request Type', 'Resource']

df_unpivoted1 = pd.melt(timesheet_data_, id_vars=id_cols, var_name='Date', value_name='Minutes')
df_unpivoted1 = df_unpivoted1[df_unpivoted1['Minutes'].astype(str).str.match(r'^\d*\.?\d+$')]
df_unpivoted1['Minutes'] = df_unpivoted1['Minutes'].astype('float')
df_unpivoted.reset_index(inplace = True, drop = True)

df_unpivoted = pd.concat([df_unpivoted, df_unpivoted1], ignore_index = True) # To union different data sets

# Grouping timesheet data
timesheet_data = df_unpivoted.groupby(['Estimate ID', 'Request ID', 'Key ID', 'Campaign Details', 'Product Line', 'Channel', 'Campaign Name', 'Deliverable Name',
                              'Request Type', 'Resource', 'Date']).agg({'Minutes' : 'sum'})
timesheet_data.reset_index(inplace = True)
timesheet_data

# Selecting required columns from timesheet data
timesheet_data = timesheet_data[['Estimate ID', 'Request ID', 'Key ID', 'Campaign Details','Product Line', 'Campaign Name', 'Deliverable Name','Request Type', 'Resource', 'Date', 'Minutes']]

# Removing rows from timesheet data that don't have continuum id present
timesheet_data = timesheet_data[~((timesheet_data['Request ID'] == 'Request ID') | (timesheet_data['Resource'] == '') | (timesheet_data['Key ID'] == ''))]

# Applying regular expression to filter out those rows which doesn't have numeric "Minutes" entries in timesheet data
timesheet_data = timesheet_data[timesheet_data['Minutes'].astype(str).str.match(r'^\d*\.?\d+$')]

# Converting "Date" column datatype to datetime, errors='coerce' - if the date is not in the required format then replace that date with NAT
timesheet_data['Date'] = pd.to_datetime(timesheet_data['Date'], format='%m/%d/%Y', errors='coerce')
timesheet_data

import datetime
# Only pick timesheet entries from 1st April, 2024 onwards till today
timesheet_data = timesheet_data[(timesheet_data['Date'] >= '2024-04-01 00:00:00')]
timesheet_data = timesheet_data[(timesheet_data['Date'] <= datetime.datetime.today().strftime('%Y-%m-%d'))]

# Creating calendar date dataframe excluding weekend dates
import datetime

# Define the start date
start_date = datetime.date(2024, 4, 1)  # Change this to your desired start date

# Define the end date as today's date
end_date = datetime.date.today() - datetime.timedelta(days=1)

# Generate a range of dates
date_range = pd.date_range(start=start_date, end=end_date)

# Create a DataFrame with the date range
df = pd.DataFrame({'Date': date_range})

# Filter out Saturdays and Sundays
df_till_today = df[df['Date'].dt.dayofweek < 5]  # 0: Monday, 1: Tuesday, ..., 4: Friday

# Reset index
df_till_today.reset_index(drop=True, inplace=True)

# Display the DataFrame
# df_till_today['total_hours'] = 8
df_till_today

df_till_today = df_till_today.loc[df_till_today.index.repeat(2)].reset_index(drop=True)
import numpy as np
mask = np.arange(len(df_till_today)) % 2 == 0

df_till_today.loc[mask, 'category'] = 'billable'
df_till_today.loc[~mask, 'category'] = 'non_billable'

df_till_today

# Join "df_till_today" with resource mapping file
df_till_today = df_till_today.merge(mapping_data[['Resource Name', 'CTN ID', 'Role', 'Location', 'Channel', 'Date of Joining', 'Date of Exit', 'Dedicated/Non Dedicated']],
                      how='cross')

df_till_today.rename(columns = {'CTN ID' : 'Resource'}, inplace = True)
df_till_today

df_till_today = df_till_today[(df_till_today['Date'] <= df_till_today['Date of Exit']) & (df_till_today['Date'] >= df_till_today['Date of Joining'])].reset_index(drop = True)
df_till_today

# Trimming extra space character from "Resource" column
timesheet_data['Resource'] = timesheet_data['Resource'].str.strip()

# Converting Resource to lowercase in timesheet data
timesheet_data['Resource'] = timesheet_data['Resource'].apply(lambda x: x.lower())

# Converting "Minutes" column datatype to float and creating a new column "Hours" with that
timesheet_data['Minutes'] = timesheet_data['Minutes'].astype('float')
timesheet_data['Hours'] = timesheet_data['Minutes'].div(60).fillna(0)

timesheet_data['Hours'].sum()

timesheet_data.reset_index(drop = True, inplace= True)
timesheet_data.head()

merged_df = timesheet_data.copy()

# Drop the "Minutes" column
merged_df.drop(['Minutes'], axis=1, inplace=True)

# Create a "category" column
merged_df['category'] = 'billable'

# Filling category column with non_billable entries based on "Key ID"
merged_df.loc[merged_df['Key ID'].isin(non_billable_key_ids['Key ID'].unique()), 'category'] = 'non_billable'

# Creating column "utilisation_hours"
merged_df['utilisation_hours'] = 0
merged_df.loc[~(merged_df['Key ID'].isin(['NW-40021', 'L-85909', 'H-78953'])), 'utilisation_hours'] = merged_df['Hours']

merged_df[~(merged_df['Key ID'].isin(['NW-40021', 'L-85909', 'H-78953']))]['Hours'].sum()

merged_df

# Getting role from resource mapping file
merged_df = df_till_today.merge(merged_df, how='left', left_on= ['Date', 'Resource', 'category'], right_on=['Date', 'Resource', 'category'])

merged_df = merged_df[~(merged_df['Key ID'] == 'H-78953')]
merged_df.head()

# Fill null "Role" values with empty string
merged_df['Role'].fillna("", inplace=True)

# # Fill garbage values in "category" column with empty values
# merged_df['category'].replace(['N/A', 'NA', 'na', 'n/a', ' ', '#N/A', np.nan], "", inplace=True)

merged_df['utilisation_hours'].sum()

merged_df.head(2)

merged_df['category'].unique()

# Fill garbage values in "Product Line" column with empty values
merged_df['Product Line'].replace(['N/A', 'NA', 'na', 'n/a', ' ', '#N/A', np.nan], "", inplace=True)

# Where category non billable, fill "Product Line" column with empty values
merged_df.loc[(merged_df['category'] == 'non_billable'), 'Product Line'] = ''

# Grouping the data based on required columns
timesheet_utilization = merged_df.groupby(['Resource Name', 'Resource', 'Location', 'Channel', 'Date', 'Role', 'category', 'Product Line', 'Dedicated/Non Dedicated']).agg({'utilisation_hours' : 'sum'})
timesheet_utilization.reset_index(inplace = True)

timesheet_utilization['utilisation_hours'].sum()

# Creating merged_df_leave dataframe based on "Key ID"
merged_df_leave = merged_df[merged_df['Key ID'] == 'L-85909']

# Grouping "merged_df_leave" dataframe
merged_df_leave = merged_df_leave.groupby(['Resource','Date']).agg({'Key ID' :'count', 'Hours' : 'sum'})

# Assumption for entries greater than 4 hours should be called leave
merged_df_leave = merged_df_leave[merged_df_leave['Hours'] >= 4]

merged_df_leave.drop('Hours', axis = 1, inplace = True)
merged_df_leave.reset_index(inplace = True)
merged_df_leave['category'] = 'non_billable'
merged_df_leave

# Joining the time sheet data with "merged_df_leave" to get the leaves column
timesheet_utilization = timesheet_utilization.merge(merged_df_leave,
                      how='left', left_on=['Resource', 'Date', 'category'], right_on=['Resource', 'Date', 'category'])

timesheet_utilization.rename(columns = {'Key ID' : 'Leaves'}, inplace = True)

# timesheet_utilization_ = timesheet_utilization_[timesheet_utilization_['country_code'].isnull()]
# timesheet_utilization_.drop(columns = ['country_code', 'holiday_date'], inplace = True)
timesheet_utilization

holiday_data['holiday_date'] = pd.to_datetime(holiday_data['holiday_date'], format='%m-%d-%Y', errors='coerce')

holiday_data.info()

# Removing holiday rows from data
timesheet_utilization_ = timesheet_utilization.merge(holiday_data, how='left', left_on=['Location', 'Date'], right_on=['country_code', 'holiday_date'])
timesheet_utilization_.head()

timesheet_utilization_.shape

# Removing holiday rows from data
timesheet_utilization_temp = timesheet_utilization_[~timesheet_utilization_['country_code'].isna()].groupby(['Date', 'Resource']).agg({'utilisation_hours' : 'sum'})
timesheet_utilization_temp.reset_index(inplace = True)
timesheet_utilization_temp.rename(columns = {'utilisation_hours' : 'utilisation_hours_temp'}, inplace = True)
timesheet_utilization_ = timesheet_utilization_.merge(timesheet_utilization_temp,
                      how='left', left_on=['Resource', 'Date'], right_on=['Resource', 'Date'])
timesheet_utilization_ = timesheet_utilization_[timesheet_utilization_['utilisation_hours_temp'] != 0].drop(columns = ['country_code', 'holiday_date', 'utilisation_hours_temp'])
timesheet_utilization_

# Importing libraries that are required to push the datframe to google sheet
from google.colab import auth
from google.auth import default
from df2gspread import df2gspread as dfg
from oauth2client.client import GoogleCredentials

auth.authenticate_user()
creds, _ = default()
gc = gspread.authorize(creds)

# Creating a object where we want to push the data
worksheet = gc.open("timesheet_utilization")
Sheet1 = worksheet.worksheet("timesheet_new")

# Adjustment done in final output data so that we can push the data to google sheet
timesheet_utilization_['Date'] = timesheet_utilization_['Date'].dt.strftime('%Y-%m-%d')
timesheet_utilization_ = timesheet_utilization_.replace([np.nan, np.inf, -np.inf], None)

timesheet_utilization_

# Code for final data push to google sheet
Sheet1.clear()
Sheet1.update([timesheet_utilization_.columns.values.tolist()]+timesheet_utilization_.values.tolist())

# timesheet_utilization_(final output file)

# timesheet_utilization_.to_csv('timesheet_utilization.csv', index=False)

