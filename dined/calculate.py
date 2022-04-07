#!/usr/bin/env python
'''
This module contains the functions that calculate the design parameters
'''
import os
import numpy as np
import pandas as pd


def load_specs(path) -> pd.core.frame.DataFrame:
    """
    Loads a design specifications file

    Parameters:
    -----------
    path: string
        The path to the design specifications file
    """
    # Assert that the file exists
    assert os.path.isfile(path), "The file does not exist"

    specs = pd.read_csv(path)
    assert "Dimensions" in specs.columns, 'Missing column "Dimensions" in the dataframe'
    assert (
        "Target percentile" in specs.columns
    ), 'Missing column "Target percentile" in the dataframe'
    assert (
        specs.dtypes["Target percentile"] == int
    ), '"Target percentile" column must contain integers'
    assert "Clearance" in specs.columns, "Missing column 'Clearance' in the dataframe"
    assert specs.dtypes["Clearance"] == int, '"Clearance" column must contain floats'
    return specs


def get_design_param(
    dimension: pd.core.series.Series, target_perc: int, clearance: float
) -> float:
    """
    Returns a float number that specifies the dimension according to a target percentile

    get_design_param(df["Stature (mm)"], 5, 10 ) will target the Stature dimension to be 5% of the population
    with a clearance of 10mm.

    Parameters:
    -----------
    dimension: pd.core.series.Series
        The dimension of interest

    target_perc: string with a percentage value
        The target percentile

    clearance: float
        The clearance of the dimension

    """
    assert isinstance(
        dimension, pd.core.series.Series
    ), "The dimension must be a series"

    percentages = np.array([target_perc])
    target_dim = dimension.describe(percentiles=percentages * 0.01)
    target_dim = target_dim[str(f"{target_perc}%")]

    return round(target_dim, 1) + clearance


def get_design_params(
    specs: pd.core.frame.DataFrame, *populations: pd.core.frame.DataFrame
) -> pd.core.frame.DataFrame:
    """
    Returns a dictionary of design parameters

    Parameters:
    -----------
    specs: pandas.core.frame.DataFrame
        A dataframe containing the list of dimensions, their corresponding percentages and the clearance
    populations: list
        a list of populations stored as datafa
    """
    assert "Dimensions" in specs.columns, "Missing column 'Dimensions' in the dataframe"
    assert (
        "Target percentile" in specs.columns
    ), "Missing column 'Target percentile' in the dataframe"
    assert "Clearance" in specs.columns, "Missing column 'Clearance' in the dataframe"

    not_found = (
        []
    )  # TODO: We use later this this to warn the user that some dimensions were not found
    results = []
    for pop in populations:
        assert isinstance(
            pop, pd.core.frame.DataFrame
        ), "The populations must be a dataframe"
        for dim in specs["Dimensions"]:
            # Check if dimension name exists in the population dataframe
            if dim in pop.columns:

                if dim in not_found:
                    not_found.remove(dim)

                # Get target percentile
                target_perc = specs.loc[
                    specs["Dimensions"] == dim, "Target percentile"
                ].values[0]

                # Get clearance
                clearance = specs.loc[specs["Dimensions"] == dim, "Clearance"].values[0]
                results.append(
                    float(get_design_param(pop[dim], target_perc, clearance))
                )
            else:
                not_found.append(dim)

    specs["Design specifications"] = results
    return specs
