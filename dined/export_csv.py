'''
Convert results from sql queries to csv files given the current dined database schemas
The result is a dir with csv viles where each file is a study.
Each study is a table consiting of "individuals"(rows) and "measurements" per individuals(columns)
'''
import sys

import os 
from os import environ as env

import mysql.connector
from mysql.connector import Error

import numpy as np
import pandas as pd
import json
import sqlalchemy


if 'DB_PWD' in os.environ:
    del os.environ['DB_PWD']

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine

uri = f'mysql+mysqlconnector://{env["DB_USER"]}:{env["DB_PWD"]}@{env["DB_HOST"]}/{env["DB_NAME"]}'

def query_to_df(db, query: str) -> pd.DataFrame:
    ''' Generic function to query the database and return a dataframe
    '''
    with db.connect() as connection:
        result = pd.read_sql_query(query, connection)
        return pd.DataFrame(result)

def load_measures_spec(representation : json):
    """Load the measures.json specification file into a flat list of dictionaries 
    containing the measure id, name and unit"""
    with open(representation) as json_file:
        data = json.load(json_file)
        # flatten dictionary
        flat = []
        # Flatten the measures
        for measure in data:
            for measure_group in measure['labels']:
                flat.append(measure_group)

        # sort id in ascending order by id
        flat = sorted(flat, key=lambda x: int(x['id']))
        return flat

def print_measures_code(data):
    """Quick check to traverse the measures.json specification and getting. 
    The names associated with the ids
    """
    for measures_group in data:
        for measure in measures_group['labels']:
                print("This is the id:", measure['id'], "This is the measure name:" ,measure['name_en'])

def write_measures_to_txt(data):
    with open('measures,txt', 'w') as f:
        for measures_group in data:
            for measure in measures_group['labels']:
                f.write("This is the id: " + measure['id'] + " This is the measure name: " + measure['name_en'] + "\n")

# QUERIES 
def get_tables(db):
    query = 'SHOW TABLES'
    return query_to_df(db, query)

def get_measurements(db: sqlalchemy.engine.base.Engine, study_id=None) -> pd.DataFrame:
    '''Gets measurement from the database, it can take a study id as an argument'''
    query = 'SELECT * FROM measurements'
    if study_id != None:
        query += ' WHERE study_id = ' + study_id
    return query_to_df(db, query)

def write_to_csv(data, filename):
    data.to_csv(filename, index=False)

def get_studies_names(studies_metadata: str) -> list:
    '''Returns a listh with the study id as key and the study name as value
    Example:
    [{'study_id': '1', 'study_name': 'Study 1'}, {'study_id': '2', 'study_name': 'Study 2'}]
    '''
    # assert that studies_metadata is a string and json
    
    with open(studies_metadata) as json_file:
        data = json.load(json_file)

        # Return a list of dictionaries with the study id and its name  
        simplified_metadata = [{'study_id': study['id'], 'study_name': study['name']} for study in data]
        
        return simplified_metadata

def count_studies(db):
    ''' Returns amount of studies in the database
    '''
    query = 'SELECT COUNT(DISTINCT study_id) FROM measurements'    
    return query_to_df(db, query)

def measurements_per_individual(data: pd.DataFrame, measures_spec: list) -> pd.DataFrame:
    '''Returns a dataframe that groups measurement_id in columns and individuales in rows
    Example:
    individual_id | measure_id_1 | measure_id_2 | measure_id_3     | ...
    1             | value        | value        | value            | ...
    2             | value        | value        | value            | ...    
    '''

    # Load specs
    measures_spec = load_measures_spec(measures_spec)

    # Create columns for each measure_id
    columns_names = []
    columns_ids = []
    for measure_id in np.unique(data['measure_id']):
        # Get the measure spec that matches the measure_id
        
        measure = [measure for measure in measures_spec if int(measure['id']) == measure_id]
        columns_ids.append(measure_id)
        columns_names.append(str(measure[0]['name_en']))
    
    # Create individuals ids for rows using numpy
    rows = np.unique(data['individual_id'])

    # Create dataframe
    df = pd.DataFrame(index=rows, columns=columns_ids)
    
    # Fill dataframe with values
    for measurement in data.iterrows():
        df.at[measurement[1]['individual_id'], measurement[1]['measure_id']] = measurement[1]['value']
    # replace columns_names with columns_ids
    df.columns = columns_names
    return df

def export_raw_csv(db, studies_metadata: str, target_dir: str):
    '''For each study writes a csv file
    target_dir: directory where the csv files will be written
    '''
    # Count distinct studies
    query = 'SELECT DISTINCT study_id FROM measurements'
    studies = query_to_df(db, query)

    metadata = get_studies_names(studies_metadata)

    # For each study write a csv file
    for study_id in studies.study_id:
        study_id = str(study_id) # Make sure we compare the same types
        # get the study name
        study = [study for study in metadata if str(study['study_id']) == str(study_id)]
        study_name = study[0]['study_name']
        
        data = get_measurements(db, study_id)
        
        # Create studies directory if it doesnt exist
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        
        write_to_csv(data, f'{target_dir}/{study_name}.csv')

# Write formated data where each individual is a row
def export_formatted_csv(db, studies_metadata, measures_spec, target_dir:str) -> None:
    '''For each study writes a csv file'''
    # Count distinct studies
    query = 'SELECT DISTINCT study_id FROM measurements'
    studies = query_to_df(db, query)

    metadata = get_studies_names(studies_metadata)

    # For each study write a csv file
    for study_id in studies.study_id:
        study_id = str(study_id) # Make sure we compare the same types
        # get the study name
        study = [study for study in metadata if str(study['study_id']) == str(study_id)]
        study_name = study[0]['study_name'
        ]
        # Avoid file name collisions
        study_name = study_name.replace(' ', '_')
        study_name = study_name.lower()
        
        data = get_measurements(db, study_id)
        df = measurements_per_individual(data, measures_spec)
    
        # Create studies directory if it doesnt exist
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        # Create dataframe with measurements per individual
        write_to_csv(df, f'{target_dir}/{study_name}.csv')

# function to read csv study file
def read_csv_study(filename:str) -> pd.DataFrame:
    '''Reads a csv file and returns a dataframe'''
    return pd.read_csv(filename)    
    
    
def main():
    db = create_engine(uri, echo=True)
    # For each study write a csv file
    export_formatted_csv(db, './metadata/studies.json', './metadata/measures.json', './data')
        

if __name__ == '__main__':
    main()
