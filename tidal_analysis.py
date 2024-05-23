"""Anna Reeves' version of tidal analysis for SEPwC"""
#!/usr/bin/env python3
# Removing line too long errors due to URLs
# pylint: disable=line-too-long
# import the modules you need here
import argparse
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress
from matplotlib.dates import date2num
import uptide


#From https://stackoverflow.com/questions/41938549/how-to-replace-all-non-numeric-entries-with-nan-in-a-pandas-dataframe
def isnumber(x):
    """Custom function for determining if feature is a number."""
    try:
        float(x)
        return True
    except:
        return False
  
def read_tidal_data(filename):
    """Reads in selected file name of standard formatting and exports to a data frame"""
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
    # https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html 
    year1946_1947 = data.loc[start:end].copy()
    year1946_1947['Sea Level'] = year1946_1947['Sea Level'] - np.mean(year1946_1947['Sea Level'])
    return year1946_1947


def join_data(data1, data2):
    joined_data = pd.concat([data1, data2])
    # https://stackoverflow.com/questions/40262710/sorting-a-pandas-dataframe-by-its-index
    joined_data.sort_index(ascending=True, inplace=True)
    return joined_data


def sea_level_rise(data):
    # https://www.w3schools.com/python/python_ml_multiple_regression.asp 
    # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.dropna.html 
    df = data
    df['datetime_as_number'] = df.index.map(lambda x: date2num(x))
    df.dropna(subset=["Sea Level"], inplace=True)
    x = df["datetime_as_number"]
    y = df['Sea Level']
    res = linregress(x, y)
    return res.slope, res.pvalue

def tidal_analysis(data, constituents, start_datetime):
    # using uptide package as described
    # https://github.com/stephankramer/uptide 
    data = data.dropna(subset=["Sea Level"])
    # https://stackoverflow.com/questions/16628819/convert-pandas-timezone-aware-datetimeindex-to-naive-timestamp-but-in-certain-t 
    # Putting this here because otherwise if we put it in read data, the tests fail
    data.index = pd.to_datetime(data.index, utc=True)
    tide = uptide.Tides(constituents)
    tide.set_initial_time(start_datetime)
    amp, pha = uptide.harmonic_analysis(tide, data["Sea Level"], (data.index - start_datetime).total_seconds())
    return amp, pha

def get_longest_contiguous_data(data):
    # https://stackoverflow.com/questions/41494444/pandas-find-longest-stretch-without-nan-values 
    a = data["Sea Level"].values  # Extract out relevant column from dataframe as array
    m = np.concatenate(( [True], np.isnan(a), [True] ))  # Mask
    ss = np.flatnonzero(m[1:] != m[:-1]).reshape(-1,2)   # Start-stop limits
    start,stop = ss[(ss[:,1] - ss[:,0]).argmax()]
    data = data.reset_index()
    range = data.iloc[start:stop]
    range = range.set_index('datetime')
    return range

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
    file_list = glob.glob(dirname + "/*.txt")
    files = pd.DataFrame()
    for file in file_list:
        if verbose:
            msg = "Reading in " + file
            print(msg)
        temp_data = read_tidal_data(file)
        files = join_data(files, temp_data)
    print(files.head(25))
    print(get_longest_contiguous_data(files))
    print(sea_level_rise(files))
