import requests
import pandas as pd
import numpy as np
import sqlite3
from bs4 import BeautifulSoup
from datetime import datetime


#Task1: define a log process function
def log_progress(message):
    '''This function logs the mentioned message at a given stage of the
    code execution to a log file. Function returns nothing.'''
    timestamp_format='%Y-%h-%d-%H:%M:%S'
    now=datetime.now()
    timestamp=now.strftime(timestamp_format)
    with open ('code_log.txt','a') as f:
        f.write(timestamp+' : '+message+'\n')

#Task2: Define an extract info function
def extract(url, table_attributes):
    page=requests.get(url).text
    data=BeautifulSoup(page,'html.parser')
    df=pd.DataFrame(columns=table_attributes)
    tables=data.find_all('tbody')
    rows=tables[0].find_all('tr')
    for row in rows:
        col=row.find_all('td')
        if len(col)!=0:
            data_dict={
                'Name':col[1].find_all('a')[1]['title'],
                'MC_USD_Billion':float(col[2].contents[0][:-1])
            }


            df1=pd.DataFrame(data_dict,index=[0])
            df=pd.concat([df,df1],ignore_index=True)
    return(df)

#Task3: Transformation of Data
def transform(df,file_to_process):
    ''' This function accesses the CSV file for exchange rate
    information, and adds three columns to the data frame, each
    containing the transformed version of Market Cap column to
    respective currencies'''
    dataframe=pd.read_csv(file_to_process)
    exchange_rate = dataframe.set_index('Currency').to_dict()['Rate']
       
    df['MC_GBP_Billion'] = [np.round(x*exchange_rate['GBP'],2) for x in df['MC_USD_Billion']]
    df['MC_EUR_Billion'] = [np.round(x*exchange_rate['GBP'],2) for x in df['MC_USD_Billion']]
    df['MC_INR_Billion'] = [np.round(x*exchange_rate['GBP'],2) for x in df['MC_USD_Billion']]
   
    return(df) 

def load_to_csv(df, csv_path):
    ''' This function saves the final data frame as a CSV file in
    the provided path. Function returns nothing.'''
    df.to_csv(csv_path)

def load_to_db(df, sql_connection, table_name):
    ''' This function saves the final dataframe to as a database table
    with the provided name. Function returns nothing.'''
    df.to_sql(table_name,sql_connection,if_exists='replace', index=False)

def run_query(query_statement, sql_connection):
    ''' This function runs the query on the database table and
    prints the output on the terminal. Function returns nothing. '''
     
    print(query_statement)
    query_output = pd.read_sql(query_statement, sql_connection)
    print(query_output)

alternative_url="https://web.archive.org/web/20240108121928/https://en.wikipedia.org/wiki/List_of_largest_banks"
url="https://en.wikipedia.org/wiki/List_of_largest_banks"
csv_path="Largest_banks_data.csv"
table_attributes=["Name","MC_USD_Billion"]
final_attributes=["Name", "MC_USD_Billion", "MC_GBP_Billion", "MC_EUR_Billion", "MC_INR_Billion"]
table_name="Largest_banks"
file_to_process='exchange_rate.csv'

log_progress('Preliminaries complete. Initiating ETL process')

df = extract(url, table_attributes)

log_progress('Data extraction complete. Initiating Transformation process')

df = transform(df,file_to_process)

log_progress('Data transformation complete. Initiating loading process')

log_progress('Data saved to CSV file') 

sql_connection = sqlite3.connect('Banks.db')

log_progress('SQL Connection initiated.')

load_to_db(df, sql_connection, table_name)

log_progress('Data loaded to Database as table. Running the query')
query_statement = f"SELECT Name from Largest_banks LIMIT 5"

log_progress('Process Complete.')
sql_connection.close()