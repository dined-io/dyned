import pandas as pd
import pytest

from dined.calculate import *

@pytest.fixture
def pop_door():
    '''Loads a sample population 1'''
    path = "./dined/tests/fixtures/pop_door.csv"
    return pd.read_csv(path)

@pytest.fixture
def specs_door():
    '''Sample door handle specs'''
    return load_specs("./dined/tests/fixtures/specs_door.csv")    

def test_load_specs():
    '''Tests if the specs are loaded correctly'''

    with pytest.raises(AssertionError):
        # If this passess it means we are catching the errors we are looing for
        load_specs("./tests/fixtures/broken_specs_door.csv") 


def test_load_pop_door(pop_door):
    '''Tests if the sample population is loaded correctly'''
    assert type(pop_door) == pd.core.frame.DataFrame, "The population must be a dataframe" 

def test_get_design_param(pop_door):
    '''Test if design parameter is calaculated based on the dimension data provided,
    the target percentilem and clearance'''

    param = get_design_param(pop_door["Stature (mm)"], 5, 10 )
    
    assert param == pytest.approx(1589.0)

    # Except if dimension is not a series
    with pytest.raises(AssertionError):
        param = get_design_param(1,10,20)



def test_get_design_params(specs_door, pop_door):
    '''
    This will check that design parameters are calculated correctly

    Given that the specs are loaded correctly, 
    and the population is loaded dataframe contains the dimension values, 
    and column names as stated in the specs,
    this test will check if the design parameters are calculated correctly
    '''
    design = get_design_params(specs_door, pop_door)
    assert design["Design specifications"].equals(design["Desired Outcomes"])

def test_dined_data():
    '''
    This will check that data from dined is loaded correctly

    '''
    pass

def test_dined_standardize():
    '''
    '''
    pass




