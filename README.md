# dyned

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/dined-io/dyned/HEAD)

A toolkit to work with antropometric data


## Project motivation
Advanced DINED research workflows using python based stacks and solutions to facilitate the development of new research tools and methods by researchers. We want to standardized antropometric data and build tools around the standards in a decoupled and modular way.

## Project status
:construction: This project is under active development

## Wish list
- :heavy_check_mark: Standardize antropometric data 
- :heavy_check_mark: Frictionless data-package that captures dataset relevant metadata
- :x: Archive new data-package in a data repository
- :x: Dyned 1D standards
    - :x: measure
    - :x: study
    - :x: individual/subject
- :x: Python package to work with antropometric data that extends pandas using frictionless metadata standards to perform common antropometric analysis
- :x: Validation of tabular data using dined standards
- :x: Open API to access antropometric data programmatically
- :x: Python based we application/dashboard to visualize antropometric data that can work with local standardized tabular data or data from the Open API
- :x: **Service to store and find antropometric data and metadata:** This would be the backend of the open API using document database to allow flexibility for the storage of data.

## Current features
- export of dined database to csv
- packaging of csv files using frictionless data standards

## Running the dined package
- I am using python virtual environments:
```sh
# Create environment for project
python3 -m venv .env

# Activate environment
source .env/bin/activate
```
- To reproduce the environment dependencies, I am relying on `setup.py`
- In development mode I install packages using `pip install -e .[dev]`. With pip3 this should work: `pip3 install "-e.[dev]"`
(`[dev]` will install the development dependencies.)
- You can run the test by running `pytest` in the comand line.

