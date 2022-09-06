''' Functions that are needed for the data extraction and processing modules
'''

import json

# When creating the package we prefix the study_id with 'id' to avoid file name collisions
# This is the regex pattern that describes the prefix
FILE_ID_REGEX = 'id[0-9]+_'

def load_measures_metadata(measures_json : json) -> dict:
    """Load the measures.json specification file into a flat list of dictionaries 
    containing the measure id, name and unit"""
    with open(measures_json) as json_file:
        data = json.load(json_file)
        # flatten measures.json dictionary g is groups and gg is subgroup of g
        flat = [ gg for g in data for gg in g['labels'] ]
        flat = sorted(flat, key=lambda x: int(x['id']))
        return flat

def load_studies_metadata(studies_json: json) -> dict:
    """Load the studies.json specification file into a flat list of dictionaries 
    containing the study id, name and unit"""
    with open(studies_json) as json_file:
        return json.load(json_file) 
