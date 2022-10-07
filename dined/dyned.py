import os
from importlib.resources import path
import json

import pandas as pd
import frictionless as fl


class DinedSeries(pd.Series):
    '''
    A DinedSeiries is a subclass of pandas.Series that constructs individual measures
    It must belong to a study
    '''
    @property
    def _constructor(self):
        return DinedSeries

    @property
    def _constructor_expanddim(self):
        return DinedDataFrame


class DinedDataFrame(pd.DataFrame):
    '''
    DinedDataFrame is a subclass of pandas.DataFrame that aggregates DinedSeries

    '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    @staticmethod
    def _validate(self):
        if 'Popliteal height, sitting X' not in self.columns:
            raise AttributeError("Must have 'Popliteal height, sitting X'.")

    def _read_csv(self, path):
        if os.path.exists(path):
            self = pd.read_csv(path)
            return self
        else:
            raise ValueError('Path does not exist')
    
    @property
    def _set_metadata(self):
        # set metadata
        pass

def load_dataset_metadata(path: str):
    return fl.Package(descriptor=path)

    
# load study creates a dataframe with the study data extended with the study metadata
def load_study(path: str, package=None):
    '''Procedure to create a DinedDataFrame from a study csv file and a data package description'''
    study = DinedDataFrame()
    study = study._read_csv(path)
    study_metadata = []
    # identify study filename and id in package
    if package is not None:
        package = fl.Package(descriptor=package)
        # remove the directory path 
        study_name = os.path.basename(path)
        study_metadata = [r for r in package.resources if r['path'] == f'./data/{study_name}'][0]
        print(study_metadata)
    
    # add study metadata to dataframe
    for key, value in study_metadata.items():
        if key != 'schema':
            setattr(study, key, value)

    return study


    