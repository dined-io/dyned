'''
Exports data from sql dined database into a dataset of csv files.

In order to work with this script you need access to an instance of dined
database.

- We use mysql.connector package to connect to the database
- sql alchemy is required to use pandas with sql.
- The `measures.json` file contains a description of the measures which we use 
to create more descriptive csv files later 
'''
import sys

import os 
from os import environ as env

import mysql.connector
from mysql.connector import Error

from dotenv import load_dotenv
load_dotenv()

import json
from sqlalchemy import create_engine

import numpy as np
import pandas as pd


uri = f'mysql+mysqlconnector://{env["DB_USER"]}:{env["DB_PWD"]}@{env["DB_HOST"]}/{env["DB_NAME"]}'
db = create_engine(uri, echo=True)

def read_measures_spec(path):
    with open (path) as file:
        # TODO: Add check or asert
        return json.loads(file.read())


def get_data(query="""SELECT * FROM studies;"""):
    '''Do sql query'''
    try:
        connection = mysql.connector.connect(host=env['DB_HOST'],
                                            database=env['DB_NAME'],
                                            user=env['DB_USER'],
                                            password=env['DB_PWD'])
        if connection.is_connected():
            db_info = connection.get_server_info()
            print("Connected to MsQL Server version ", db_info)
            cursor = connection.cursor()
            cursor.execute(query)
            records = cursor.fetchall()
            return records

    except Error as error:
        print("Error while connecting to MySQL", error)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

def sql_to_df(query):
    with db.connect() as connection:
        result = pd.read_sql_query(query, connection)
        return pd.DataFrame(result)

def mk_template(path):
    ''' Makes a template for an individual based on the measures.json data'''
    measures = read_measures_spec(path)

    df = pd.DataFrame()
    for measures_group in measures:
        for measure in measures_group['labels']:
                measure = pd.DataFrame([], columns={ measure['id']})
                df = pd.concat([df, measure],ignore_index=True, axis=0)
    
    df.insert(0, 'individual_id', pd.Series)
    return df    

def write(query, path, columns=None):
    '''Write query results to csv '''
    records = get_data(query)
    
    # Create dir if doesnt exist
    if not os.path.exists(path):
        dir ='/'.join(list(path.split('/')[:-1]))
        os.makedirs(dir)
        print("Created dir: ", path)

    df = pd.DataFrame(records, columns=columns)
    df.to_csv(path, index=False)
    print("Data written to csv file")
    print(df.head())


if __name__ == "__main__":
    # Turn sql query result into pandas dataframe measurements
    m = sql_to_df("SELECT * FROM measurements LIMIT 100;")
    # Chop dataframe for testing

    # Create the new dataframe with all the data
    individuals = pd.DataFrame()

    # Set individual id start
    i_id = 0

    # Makes individual empty dataframe to be populated
    new_i = mk_template('../experiments/measures.json') # new individual
    new_i.loc[len(new_i)] = np.nan
    # Go through all the measurements to create dataframe
    for i, row in m.iterrows():
        if int(row['individual_id']) != i_id:
            # print(new_i)
            if i_id > 0:
                individuals = pd.concat([individuals, new_i], 
                                        ignore_index=True, axis=0)
                # clean the new_i dataframe to append to the aggregate indivduals
                new_i.loc[len(new_i)] = np.nan
                print(f'New Individual has id: {row["individual_id"]}')
            i_id += 1

        elif int(row['individual_id']) == i_id:
            for col in new_i.columns:
                if str(int(row['measure_id'])) == col: 
                    new_i[col] = row['value']
        


    # df = new_i.dropna(axis=1, how='all')
    # print(df)
    df = individuals.dropna(axis=1, how='all')
    print(df)


    # This function is deprecated as it is
    # write(sys.argv[1], sys.argv[2])
    

# Test conversion creation of dataframe for each individual