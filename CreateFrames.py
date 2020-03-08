from datetime import date, datetime, timedelta
import os
import requests

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import pandas as pd
import numpy as np

GITHUB_BASE_URL = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/'

FILE_CONFIRMED = 'time_series_19-covid-Confirmed.csv'
FILE_DEATH = 'time_series_19-covid-Deaths.csv'
FILE_RECOVERED = 'time_series_19-covid-Recovered.csv'


def read_temporal_data():
    '''
    Reads all the csv files from github
    '''

    # Confirmed Cases
    print('Fetching confirmed cases')
    r = requests.get(GITHUB_BASE_URL+FILE_CONFIRMED)
    if r.status_code == 200:
        with open(f'./data/{FILE_CONFIRMED}', 'wb') as code:
            code.write(r.content)
            code.close()

    # Death Cases
    print('Fetching death cases')
    r = requests.get(GITHUB_BASE_URL+FILE_DEATH)
    if r.status_code == 200:
        with open(f'./data/{FILE_DEATH}', 'wb') as code:
            code.write(r.content)
            code.close()

    # Recovered Cases
    print('Fetching recovered cases')
    r = requests.get(GITHUB_BASE_URL+FILE_RECOVERED)
    if r.status_code == 200:
        with open(f'./data/{FILE_RECOVERED}', 'wb') as code:
            code.write(r.content)
            code.close()


def add_text(df, ax=None, current_date=date.today(), column=0, config=None):
    fontname = 'Open Sans'
    fontsize = 28

    # Positions for the date and counter
    date_x = -53
    date_y = -50
    date_spacing = 65

    # Date text
    ax.text(date_x, date_y,
            f"{current_date.strftime('%b %d, %Y')}",
            color='white',
            fontname=fontname, fontsize=fontsize*1.3,
            transform=ccrs.PlateCarree())

    # Case Counter
    ax.text(date_x + date_spacing, date_y,
            f"{config['display_text']}", color='#ff6600',
            fontname=fontname, fontsize=fontsize,
            transform=ccrs.PlateCarree())
    ax.text(date_x + date_spacing*1.7, date_y,
            f"{df[df.columns[column]].sum():,}",
            color='#ff6600', ha='left',
            fontname=fontname, fontsize=fontsize*1.3,
            transform=ccrs.PlateCarree())

    # Prepare the top 10 table
    # new sorted dataset. Thsi could be propably done mor concise,
    # but i leave it like this for clarity
    tt = df.copy()

    # Condense the regions just to the countries
    tt = tt.groupby(tt.columns[1]).sum()

    # Reset the index so we can easily access the columns by number
    tt = tt.reset_index()

    tt = tt.sort_values(df.columns[column], ascending=False)
    tt = tt.head(10)  # top 10

    # Province, Country, Number of the current column
    # -1 cause we lost one column during groupby
    tt = tt[[tt.columns[0], tt.columns[column-1]]]
    tt = tt.replace(np.nan, '', regex=True)  # replace NaN

    # Print the columns
    # I did not use axes.table, beacause I was not able to overlay
    # the table over the axes. Therefore I created it manually
    tab_x = -140
    tab_y = -60
    delimiter = '\n'

    # Country
    ax.text(tab_x, tab_y,
            delimiter.join(tt[tt.columns[0]].to_list()),
            color='white', horizontalalignment='right',
            fontname=fontname, fontsize=12,
            transform=ccrs.PlateCarree())

    # Cases
    ax.text(tab_x + 15, tab_y,
            # use map to convert int to string => convert to list to join
            delimiter.join(list(map(str, tt[tt.columns[1]].to_list()))),
            color='white', horizontalalignment='right',
            fontname=fontname, fontsize=12,
            transform=ccrs.PlateCarree())


def make_map(df, ax=None, fig=None, resolution='low', column=0, config=None):
    '''
    Paints the data on the map
    '''

    # Create a date Object from the column name
    current_date = datetime.strptime(df.columns[column], '%m/%d/%y').date()
    print('\tWorking on ' + str(current_date))

    # Load the background image
    ax.background_img(name='BM', resolution=resolution)
    ax.set_extent([-179, 179, -70, 70], crs=ccrs.PlateCarree())

    # Iterate each row and plot the data on the graph
    for index, row in df.iterrows():
        # print(index, column, row[column])
        if int(row[column]) > 0:  # only the ones with confirmed cases
            # print('\t\t', index, row[1], row[2], row[3], row[column])
            ax.scatter(row[3], row[2], s=row[column]*config['scale_factor'],
                       color='#ff6600', alpha=0.8, transform=ccrs.PlateCarree())

    add_text(df, ax=ax, current_date=current_date,
             column=column, config=config)


def create_images(df, config=None):
    '''
    Reads all the file from ./data and plots it on the map
    Images are stored in ./frames

    The data columns are:
       0: Province/State
       1: Country/Region
       2: Lat 
       3: Long
    4-..: Dates with the cases
    '''
    # Set this environment variable, so that cartopy finds the background image
    # Seems only to work with absolute paths
    os.environ['CARTOPY_USER_BACKGROUNDS'] = '/Users/sascha/git/covid_19/background'

    # fig.savefig needs the directory already created
    try:
        os.mkdir('frames')  # try to creaet the frames directory
    except:
        pass

    try:
        # try ro create the current sub-directory
        os.mkdir(config['frames_dir'])
    except:
        pass

    # Set Up the Image Object
    # We do that outside the loop and just clear the axes and reuse them
    # The figure is saved with 100 DPI. Thus with a size of 19.2x10.8 this leads
    # to a resolution of 1980x1080px
    # For projecting the "round" earth on a 2D canvas I use the Mercator projection
    fig = plt.figure(figsize=(19.2, 10.8))
    ax = plt.axes(projection=ccrs.Mercator(min_latitude=-70,
                                           max_latitude=70))

    # Loop over each column and create one image for a column (which represents
    # a single day). The first data column is #4
    for i in range(4, len(df.columns)):
        # CHeck if the file already exists. If yes,it was rendered before
        # so we don't render it again. Assuming, that there ar no changes
        # in history :-)
        if not os.path.isfile(f"{config['frames_dir']}/frame_{i:06d}.png"):

            make_map(df, ax=ax, fig=fig, resolution='high',
                     column=i, config=config)

            # Zoom in to remove black borders around the image
            fig.tight_layout(pad=-1)
            fig.savefig(f"{config['frames_dir']}/frame_{i:06d}.png", dpi=100,
                        frameon=False, facecolor='black')

            ax.clear()


if __name__ == '__main__':
    # First read the datasets from Hopkins
    read_temporal_data()

    # Confirmed Cases
    print('\nProcessing Confirmed Cases')

    config = {
        'frames_dir': 'frames/confirmed',
        'display_text': 'CONFIRMED',
        'scale_factor': 0.1  # define the size of the plot
    }

    df = pd.read_csv('./data/' + FILE_CONFIRMED)

    create_images(df, config)

    # Active Cases
    print('\nProcessing Active Cases')

    config = {
        'frames_dir': 'frames/active',
        'display_text': '       ACTIVE',
        'scale_factor': 0.1  # define the size of the plot
    }

    confirmed = pd.read_csv('./data/' + FILE_CONFIRMED)
    recovered = pd.read_csv('./data/' + FILE_RECOVERED)

    # Use Pandas to create a new data frame of the activ cases (confirmed - recovered)
    df = confirmed.set_index(['Province/State', 'Country/Region', 'Lat', 'Long']).subtract(
        recovered.set_index(['Province/State', 'Country/Region', 'Lat', 'Long']))

    # remove the index we created in the statement before. Otherwise the dynamic counter based
    # on the for loop cross the columns doesn't work correctly (it assumes the first date column
    # to be #4)
    df.reset_index(inplace=True)

    create_images(df, config)
