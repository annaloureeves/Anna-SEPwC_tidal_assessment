"""Anna Reeves' version of tidal analysis for SEPwC"""
#!/usr/bin/env python3
# Removing line too long errors due to URLs
# pylint: disable=line-too-long
# import the modules you need here
import argparse
import glob
import pandas as pd
import numpy as np
from scipy.stats import linregress
from matplotlib.dates import date2num
import uptide


# From https://stackoverflow.com/questions/41938549/how-to-replace-all-non-numeric-entries-with-nan-in-a-pandas-dataframe
def isnumber(x):
    """Custom function for determining if feature is a number."""
    try:
        float(x)
        return True
    except ValueError:
        return False
    except TypeError:
        return False

def read_tidal_data(filename):
    """Reads in selected file name of standard formatting and exports to a data frame"""
    # Read the CSV file into a DataFrame, skipping specific rows and using whitespace as the delimiter
    # References: https://www.geeksforgeeks.org/how-to-read-space-delimited-files-in-pandas/
    # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html
    # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html
    data = pd.read_csv(filename, skiprows=[
                    0, 1, 2, 3, 4, 5, 6, 7, 8, 10], sep=r'\s+')
    # Rename column to "Sea Level"
    data.rename(columns={data.columns[3]: "Sea Level"}, inplace=True)
    # Combine "Date" and "Time" to "datetimes"
    # References: https://stackoverflow.com/questions/17978092/combine-date-and-time-columns-using-pandas
    # https://pandas.pydata.org/docs/reference/api/pandas.DatetimeIndex.html
    data['datetime'] = pd.to_datetime(data['Date'] + ' ' + data['Time'])
    # Set "datetime" column as the index of the df
    # https://stackoverflow.com/questions/27032052/how-do-i-properly-set-the-datetimeindex-for-a-pandas-datetime-object-in-a-datafr
    data = data.set_index('datetime')
    # Filter to only include rows where all the elements are numbers
    data = data[data.map(isnumber)]
    # Convert "Sea Level" to float type
    # https://stackoverflow.com/questions/16729483/converting-strings-to-floats-in-a-dataframe
    data["Sea Level"] = data["Sea Level"].astype(float)
    # Convert "Residual" to float type
    data["Residual"] = data["Residual"].astype(float)
    # Replace values in column 'A' that end with 'M' with NaN
    # https://github.com/jhill1/SEPwC_tidal_assessment
    data.replace(to_replace=".*M$",value={'A':np.nan},regex=True,inplace=True)
    # Replace values in column 'A' that end with 'N' with NaN
    data.replace(to_replace=".*N$",value={'A':np.nan},regex=True,inplace=True)
    # Replace values in column 'A' that end with 'T' with NaN
    data.replace(to_replace=".*T$",value={'A':np.nan},regex=True,inplace=True)
    return data

def extract_single_year_remove_mean(year, data):
    """Extracts single year and subtracts the mean from each row"""
    # Function based on work from:
    # https://www.dataquest.io/blog/datetime-in-pandas/
    # Create a string representing the start of the year in 'YYYYMMDD' format
    year_string_start = str(year)+"0101"
     # Create a string representing the end of the year in 'YYYYMMDD' format
    year_string_end = str(year)+"1231"
    # Select "Sea Level" data from the DataFrame 'data' for a given year
    year_data = data.loc[year_string_start:year_string_end, ['Sea Level']]
    # Find the mean and remove it
    # https://jhill1.github.io/SEPwC.github.io/Mini_courses.html#tidal-analysis-in-python
    # Calculate the mean of the "Sea Level" for the selected year
    mmm = np.mean(year_data['Sea Level'])
    # Subtract the mean 'Sea Level' from the 'Sea Level' column
    year_data['Sea Level'] -= mmm
    return year_data

def extract_section_remove_mean(start, end, data):
    """Extracts single year and subtracts the mean from each row"""
    # https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html
    year1946_1947 = data.loc[start:end].copy()
    year1946_1947['Sea Level'] = year1946_1947['Sea Level'] - np.mean(year1946_1947['Sea Level'])
    return year1946_1947


def join_data(data1, data2):
    """Joins data frames in chronological order"""
    # Concatenate data1 and data2 DataFrames vertically
    joined_data = pd.concat([data1, data2])
    # Sort the concatenated DataFrame by its index in ascending order
    # https://stackoverflow.com/questions/40262710/sorting-a-pandas-dataframe-by-its-index
    joined_data.sort_index(ascending=True, inplace=True)
    return joined_data

def convert_date_to_number(x):
    """Convert date to a number"""
    return date2num(x)

def sea_level_rise(data):
    """Linear Regression of Sea Level Against Time"""
    # https://www.w3schools.com/python/python_ml_multiple_regression.asp
    # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.dropna.html
    # Assign the DataFrame 'data' to the variable 'df'
    df = data
    # Convert datetime index to numerical format using date2num
    df['datetime_as_number'] = df.index.map(convert_date_to_number)
    # Drop rows with missing values in 'Sea Level'
    df.dropna(subset=["Sea Level"], inplace=True)
    # Assign new datetime values to 'x' and 'Sea Level' values to 'y'
    x = df["datetime_as_number"]
    y = df['Sea Level']
    # Perform linear regression
    slope, _, _, pvalue, _ = linregress(x, y)
    return slope, pvalue

def tidal_analysis(data, constituents, start_datetime):
    """Harmonic Analysis of Sea Level Data Using Tidal Constituents"""
    # using uptide package as described
    # https://github.com/stephankramer/uptide
    # Drop 'Sea Level" rows with missing values
    data = data.dropna(subset=["Sea Level"])
    # https://stackoverflow.com/questions/16628819/convert-pandas-timezone-aware-datetimeindex-to-naive-timestamp-but-in-certain-t
    # Putting this here because otherwise if we put it in read data, the tests fail
    # Convert the index to a datetime format using UTC timezone
    data.index = pd.to_datetime(data.index, utc=True)
    # Tides object with specified constituents
    tide = uptide.Tides(constituents)
    # Set initial time to given start_datetime
    tide.set_initial_time(start_datetime)
    # Perform harmonic analysis
    amp, pha = uptide.harmonic_analysis(tide, data["Sea Level"],
                                        (data.index - start_datetime).total_seconds())
    return amp, pha

def get_longest_contiguous_data(data):
    """"Extract Longest Continuous Segment of Sea Level Data"""
    # https://stackoverflow.com/questions/41494444/pandas-find-longest-stretch-without-nan-values
    a = data["Sea Level"].values
    # Create a mask for NaN
    m = np.concatenate(( [True], np.isnan(a), [True] ))
    ss = np.flatnonzero(m[1:] != m[:-1]).reshape(-1,2)
    start,stop = ss[(ss[:,1] - ss[:,0]).argmax()]
    data = data.reset_index()
    datarange = data.iloc[start:stop]
    datarange = datarange.set_index('datetime')
    return datarange

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
