'''
Generate a data-package.json for the dined data.
For now each resource is a table that should be a study
Each study has individuals as rows and measurements as fields

TODO: Packaging must be genericized to allow the transformation of different
tables coming from differnet sources and not necessarily standardize like dined data,
perhaps this package can also facilitate in this....perhaps is out of scope...

'''
from distutils.command import build

import sys
import os
from os import name

import json
from xmlrpc.client import Boolean

import pandas as pd
from frictionless import Package, Resource, validate, report
import re
from dined import FILE_ID_REGEX, load_studies_metadata


# We use this class to generate fields for each resource in
# the data package
class Field:
    '''
    A class to store field data.
    A field is the dictionary that must include the name property
    '''
    # Here we put only the required properties
    def __init__(self, name):
        self.name = name
        self.field = { "name": name }
    
    # add name to field dictionary
    def add_name(self, name):
        self.field['name'] = name

    def add_property(self, key, value):
        self.field[key] = value
    
    # get field dictionary
    def get_field(self):
        return self.field
    
    def get_field_serialized(self):
        return json.dumps(self.field)

    # get subfield
    def get_property(self, key):
        return self.field[key]

class DataPackage():
    '''A class to to create a data-package.json.'''
    def __init__(self, name):
        self.name = name
        self.package = { "name": name }
        
    def add_property(self, key, value):
        self.package[key] = value
    
    def get_property(self, key):
        return self.package[key]

def get_fields_from_metadata(metadata_path: str) -> list:
    '''Gets fields from the dined metadata used to describe dined data
    '''    
    # load metadata
    metadata = json.load(open(metadata_path))
    
    # Get fields value pairs
    fields = []

    # The first field for each resource (study)
    individual = Field('id')
    individual.add_property('type', 'integer')
    fields.append(individual.field)

    for group in metadata:
        for field_info in group['labels']:
            field = Field(field_info['name_en'])
            field.add_property('id', field_info['id'])

            # if there is no description, use the name
            if field_info['description_en'] == '' or field_info['description_en'] == None:
                field.add_property('description', field_info['name_en'])
            else:
                field.add_property('description', field_info['description_en'])
            
            field.add_property('type', "number")
            field.add_property('rdfType', 'https://schema.org/QuantitativeValue')
            field.add_property('unit', field_info['dimension'])
            # append only the Field.field dictionary not the entire object
            fields.append(field.field)
            
    return fields 

def load_fields(fields_path: str) -> list:
    '''Loads fields from a json file.'''
    with open(fields_path) as f:
        fields = json.load(f)
    return fields

def get_fields_from_file(file_path: str, dataset_fields: list) -> list:
    '''Procedure to get fields from a csv file to be later added to a Resource object.
    We read the columns and if the column name is in the list of fields generated,
    we return a list of fields
    '''
    # ignore file if it is not a csv
    if file_path.endswith('.csv'):
        # Read file and store in dataframe
        df = pd.read_csv(file_path)

        # Get fields from file
        # Pick the fields that match the column in the file
        fields = [ field for column in df.columns for field in dataset_fields if column == field['name']]        
        return fields
    else:
        print(f"File {file_path} is not a csv file, or contains columns that doesnt match the fields in the metadata")
    
def write_fields(fields: list, fields_path: str):
    '''Writes fields to a json file in the specified fields_path.'''
    with open(fields_path, 'w') as f:
        # write fields to file
        json.dump(fields, f, indent=4)

def make_study_name_unique(study_name: str, study_id: int) -> str:
    '''Modify study name to be unique by adding a number to the end
    >>> make_study_name_unique('My study name', 1)
    'My study name 1'
    '''
    return f"{study_name} (study id from original metadata is: {study_id}, this name is not unique) "

def check_study_file_regexp(study_file: str, regexp: str) -> bool:
    '''Returns true if the study file matches the study file regexp
    >>> check_study_file_regexp('id10_study_file.csv', 'id[0-9]+_')
    True
    '''
    try: return len(re.match(regexp, study_file).group(0)) > 0
    except AttributeError: return False

def check_study_name(study_file_name: str, studies_metadata: list) -> bool:
    '''Returns true if the study name matches the study name list'''
    # filter studies by file name
    study = [study for study in studies_metadata if study['name']]
    return len(study) > 0

def get_study_id_from_file(study_file_name: str) -> int:
    '''Returns the study id from the file name'''
    file_id_regex = FILE_ID_REGEX
    # assert check_study_file_regexp(study_file, file_id_regex), f'Study file name {study_file} does not match regexp {file_id_regex}'
    
    if not check_study_file_regexp(study_file_name, file_id_regex):
        raise(f'Study file name {study_file_name} does not match regexp {file_id_regex}')
    else:
        try:
            study_id_from_file = re.findall(fr'{file_id_regex}', study_file_name)[0]
            study_id_from_file = re.findall(r'[0-9]+', study_id_from_file)
            study_id_from_file = study_id_from_file[0]
            return int(study_id_from_file)
        except ValueError as e:
            print(f'Error getting study id from file {study_file_name}')
            raise(e)

def get_study_id_from_metadata(studies_metadata: dict, id: int) -> int:
    '''Returns the study id from the metadata'''
    # check that id is in metadata
    study = [study for study in studies_metadata if study['id'] == id]
    if len(study) == 0:
        return f'No study with id {id} in metadata'
    else:
        return study[0]['id']

def get_study_metadata_from_id(study_id: int, studies_metadata: list) -> dict:
    '''Returns a dictionary with the metadata of the study with the given id 
    >>> get_study_metadata_from_id(1, [{'name': 'My first study, 1'}])
    '''
    # filter studies by file name
    study = [study for study in studies_metadata if study['id'] == study_id]
    # if study name is duplicate throw an error
    if len(study) == 0:
        raise ValueError(f'Study: {study_id} not found in metadata')
    else:
        return study[0]

def get_duplicate_study_name(study_file: str ,studies_metadata: list) -> str:
    '''Returns a modified name iif a duplicate name is found in the metadata
    >>> get_duplicate_study_name('id10_study_file.csv', [{'name': 'My Duplicate Study Name',
                                                            'id' : 10}, {'name': 'My Duplicate Study Name',
                                                            'id' : 11}])}])
    '''
    # filter studies by file name
    study_id = get_study_id_from_file(study_file)
    try:
        study_name = [study['name'] for study in studies_metadata if study['id'] == study_id][0]
        duplicate_names = [study['name'] for study in studies_metadata if study['name'] == study_name]
        if len(duplicate_names) > 1:
            print(f'Duplicate study name {study_name} related to file {study_file}')
            return make_study_name_unique(study_name, study_id)
        else:
            return study_name
    except:
        print(f' Study name extracted from: {study_file} not found in studies metadata ')
        # Here we should get the study name with the id from the file name
        return get_study_metadata_from_id(study_id, studies_metadata)['name']
        
def check_study_match(study_file_name: str, study_name: str, study_id: int) -> bool:
    '''Check if the file name matches the study name.
    Given that the file name was generated from the study name in the metadata by lowercasing and adding _ to spaces,
    and adding an prefix the file name with its id, we can check if the file name matches the study name.
    Input example:
    >>> check_study_match('id1_my_first_study.csv', 'My first study, 1')
    True
    '''
    file_id_regex = FILE_ID_REGEX
    
    if not check_study_file_regexp(study_file_name, file_id_regex):
        return False
    else:
        study_id_from_file = get_study_id_from_file(study_file_name)

        # Remove .csv extension from as well as _ from file name
        file_name = study_file_name.split('.')[0].lower()
        # Remove the following regexp pattern from the file name /ID[0-9]+_/
        file_name = re.sub(rf'{file_id_regex}','_', file_name)[1:]
        
        file_name = rf"{file_name.replace('_', ' ')}"
        study_name = rf"{study_name.lower()}"
        
        try:
            full_match = file_name == study_name and int(study_id_from_file) == int(study_id)
            id_match = int(study_id_from_file) == int(study_id)
            
            # Sometimes file name might not be the same as the study name, but the id is the same 
            if full_match == False and id_match == True:
                print(f'Study file name {study_file_name} does matches id but does not match study name {study_name}')
                return True
            elif full_match and id_match:
                return True
        except:
            if file_name != study_name:
                print (f'File name {file_name} does not match study name {study_name}')
                print(f'Study id from file is {study_id_from_file} and study id is {study_id}')
            elif study_id_from_file != study_id:
                print(f'Study id {study_id_from_file} does not match study id {study_id}')
            return False

def get_study_metadata(study_file_name: str, studies_metadata: list) -> dict:
    '''Returns a dictionary with the metadata of the study with the given file name 
    >>> get_study_metadata('id1_my_first_study.csv', [{'name': 'My first study, 1'}])
    '''
    
    studies = load_studies_metadata(studies_metadata)

    # filter studies by file name
    study = [study for study in studies if check_study_match(study_file_name, study['name'], study['id'])]
    # if study name is duplicate throw an error
    if len(study) == 0:
        raise ValueError(f'Study: {study_file_name} not found in metadata')
    else:
        return study[0]

# FRICTIONLESS METADATA GENERATION AND VALIDATION
def build_resource_descriptor(file_path: str, 
                             studies_metadata_path: str, 
                             measures_metadata: str) -> Resource:
    '''Builds a resource descriptor for a file.
    Returns a frictionless Resource object.
    >>> build_resource_descriptor('id1_my_first_study.csv', './studies.json', './measures.json.c')
    '''
    # Get file name without extension
    file_name = file_path.split('/')[-1].split('.')[0]
    extracted_name = os.path.basename(os.path.normpath(file_path))
    extracted_name = extracted_name.split('.')[0]
    
    studies_metadata = load_studies_metadata(studies_metadata_path)
    # This should be from id not name
    study_metadata = get_study_metadata(extracted_name, studies_metadata_path)

    # Check that study name is unique
    unique_study_name = get_duplicate_study_name(file_name, studies_metadata)
    
    # metadata fields means all the fields in all the studies
    metadata_fields = get_fields_from_metadata(measures_metadata)

    # resource_fields are the fields that are in the file
    resource_fields = get_fields_from_file(file_path, metadata_fields) 

    if study_metadata != None:
        resource = Resource(
            path=f"{file_path}",
            name=unique_study_name,
            description=study_metadata['description'],
            profile='tabular-data-resource',
            encoding='utf-8',
            schema={
                'fields': resource_fields
            }
        )
        return resource
    else:
        print(f'Error: not able to build resource descriptor for {file_name}')
        return None

def build_dined_data_package(measures_metadata: str,
                             studies_metadata: str,  
                             data_dir='./data') -> Package:
    '''Builds a data package for the dined data.'''
    # Get fields from metadata
    pkg = Package(
        name='dined-tables',
        title='Dined tabular Data',
        description='A data package consisting of tables describing 1D dimensional anthropometric data.',
    ) 

    pkg.resources = [] # we do this after creating the package to keep a more convenient output format
    
    files = os.listdir(data_dir)
    for file in files:
        # ignore files that are not csv
        if file.endswith('.csv'):
            # Create a resource for each file
            # Check that study name is not duplicate in original dined metadata
            resource = build_resource_descriptor(f'{data_dir}/{file}', 
                                                studies_metadata , measures_metadata)
            pkg.resources.append(resource)
    
    return pkg

def write_data_package(data_package: Package, package_metadata_path: str, package_name="data-package.json") -> None:
    '''writes the data package'''
    # Write table descriptor to file
    with open(f"{package_metadata_path}/{package_name}", 'w') as f:
        json.dump(data_package, f, indent=4)

def validate_package(package_metadata) -> report.Report:
    '''
    Checks for errors in the package using the frictionless 
    matadata spec for data-package
    '''    
    # Load package descriptor as a frictionless package
    pkg = Package(package_metadata)
    
    # Validate each file in the data directory with map function in pkg.rsources
    return validate(package_metadata)

def validate_resources(package_metadata='data-package/json') -> list:
    # Map and reduce function to validate each resource
    # return list(map(lambda resource: validate(resource), package_metadata))
    validate_resource = lambda resource: validate(resource)
    
    pkg = Package(package_metadata)
    return list(map(validate_resource, pkg.resources))

if __name__ == '__main__':
    PACKAGE_METADATA = "./data-package.json"
    if len(sys.argv) > 2 : 
        PACKAGE_DIR = sys.argv[1]
        MEASURES_METADATA = sys.argv[2]
        STUDIES_METADATA = sys.argv[3]
    
    else: 
        PACKAGE_DIR = "./data" 
        MEASURES_METADATA = './metadata/measures.json'
        STUDIES_METADATA = './metadata/studies.json'

    # Build the data package
    data_package = build_dined_data_package(MEASURES_METADATA, STUDIES_METADATA, PACKAGE_DIR)
    write_data_package(data_package, PACKAGE_DIR, 'data-package.json')
    # r =  validate_resources(f"{PACKAGE_DIR}/{PACKAGE_METADATA}")
    report = validate_package(f"{PACKAGE_DIR}/{PACKAGE_METADATA}")
    if report['valid'] == False:
        print(report.to_summary())
    else:
        print(f"Valid package")
    print('Done.')








    
    