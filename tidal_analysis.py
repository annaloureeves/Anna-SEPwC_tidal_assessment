#!/usr/bin/env python3

# import the modules you need here
import argparse
import pandas as pd



def read_tidal_data(filename):
    # Read data, separate columns by spaces, ignore first 10 , rename data column as "Sea Level"
    # References: https://www.geeksforgeeks.org/how-to-read-space-delimited-files-in-pandas/ 
    # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html 
    data = pd.read_csv(filename, sep='\s+', skiprows=[0,1,2,3,4,5,6,7,8,9,10], names=['Cycle', 'Date', 'Time', 'Sea Level', 'Residual'])
    # Combine "Date" and "Time" to "datetimes"
    pd.to_datetime(data['Date'] + ' ' + data['Time'])
    return data
    
def extract_single_year_remove_mean(year, data):
   

    return 


def extract_section_remove_mean(start, end, data):


    return 


def join_data(data1, data2):

    return 



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
    


