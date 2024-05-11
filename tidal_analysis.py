#!/usr/bin/env python3

# import the modules you need here
import argparse
import pandas as pd
import pylint 
import numpy as np

#From https://stackoverflow.com/questions/41938549/how-to-replace-all-non-numeric-entries-with-nan-in-a-pandas-dataframe
def isnumber(x):
    """Custom function for determining if feature is a number."""
    try:
        float(x)
        return True
    except:
        return False
    
def read_tidal_data(filename):
    tidal_file = "data/1947ABE.txt"
    # Read data, separate columns by spaces, ignore first 10 , rename data column as "Sea Level"
    # References: https://www.geeksforgeeks.org/how-to-read-space-delimited-files-in-pandas/ 
    # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html 
    # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html 
    data = pd.read_csv(filename, skiprows=[
                    0, 1, 2, 3, 4, 5, 6, 7, 8, 10], sep=r'\s+')
    data.rename(columns={data.columns[3]: "Sea Level"}, inplace=True)
    # Combine "Date" and "Time" to "datetimes" 
    # References: https://stackoverflow.com/questions/17978092/combine-date-and-time-columns-using-pandas
    # https://pandas.pydata.org/docs/reference/api/pandas.DatetimeIndex.html
    data['datetime'] = pd.to_datetime(data['Date'] + ' ' + data['Time'])
    data = data.set_index('datetime')
    data = data[data.map(isnumber)]
    data["Sea Level"] = data["Sea Level"].astype(float)
    data["Residual"] = data["Residual"].astype(float)
    data.replace(to_replace=".*M$",value={'A':np.nan},regex=True,inplace=True)
    data.replace(to_replace=".*N$",value={'A':np.nan},regex=True,inplace=True)
    data.replace(to_replace=".*T$",value={'A':np.nan},regex=True,inplace=True)
    return data
    
def extract_single_year_remove_mean(year, data):
    #Function based on work from:
    # https://www.dataquest.io/blog/datetime-in-pandas/
    year_string_start = str(year)+"0101"
    year_string_end = str(year)+"1231"
    year_data = data.loc[year_string_start:year_string_end, ['Sea Level']]
    # Find the mean and remove it
    # https://jhill1.github.io/SEPwC.github.io/Mini_courses.html#tidal-analysis-in-python
    mmm = np.mean(year_data['Sea Level'])
    year_data['Sea Level'] -= mmm
    return year_data

def extract_section_remove_mean(start, end, data):
    year1946_1947 = data.loc[start:end].copy()
    year1946_1947['Sea Level'] = year1946_1947['Sea Level'] - np.mean(year1946_1947['Sea Level'])
    return year1946_1947



def join_data(data1, data2):
    joined_data = pd.concat([data1, data2])
    # https://stackoverflow.com/questions/40262710/sorting-a-pandas-dataframe-by-its-index
    joined_data.sort_index(ascending=True, inplace=True)
    return joined_data



def sea_level_rise(data):

                                                     
    return 

def tidal_analysis(data, constituents, start_datetime):


    return 

def get_longest_contiguous_data(data):


    return 

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
                     prog="UK Tidal analysis",
                     description="Calculate tidal constiuents and RSL from tide gauge data",
                     epilog="Copyright 2024, Jon Hill"
                     )

    parser.add_argument("directory",
                    help="the directory containing txt files with data")
    parser.add_argument('-v', '--verbose',
                    action='store_true',
                    default=False,
                    help="Print progress")

    args = parser.parse_args()
    dirname = args.directory
    verbose = args.verbose
    


