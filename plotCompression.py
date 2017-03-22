"""COMPRESSION TEST VISUALIZATION TOOL
Logan Halstrom
CREATED: 08 JAN 2017
MODIFIY: 08 JAN 2017

DESCRIPTION:  Visualize data for compression tests of internal combustion
engines.  Compare pressure history of each cylinder as well as differences
between dry and wet (oil added to cylinder) tests.

NOTE:
Data files are made by pasting Google sheet columns into Sublime text,
then using column editing to separate with commas to fixed width with
no space between commas and next column.

IMPROVMENTS:
Normalize pressures by max value (for intratest comparison)
Extend tests with less total strokes by repeating the last value
Plot dry/wet deltas normalized by cylinder maximum or greatest maximum
"""

import numpy as np
import pandas as pd

#CUSTOM PLOTTING PACKAGE
import matplotlib.pyplot as plt
import sys
sys.path.append('/Users/Logan/lib/python')
from lutil import df2tex
from lplot import *
from seaborn import color_palette
import seaborn as sns
UseSeaborn('xkcd') #use seaborn plotting features with custom colors
colors = sns.color_palette() #color cycle
markers = bigmarkers         #marker cycle




def ReadCompTestData(filename):
    """Reads compression test data from csv file into pandas dataframe.
    filename --> path to data file to read
    """

    columnnames = ['Stroke', '1dry', '2dry', '3dry', '4dry',
                             '1wet', '2wet', '3wet', '4wet']

    #Read data, assign columnnames
    df = pd.read_csv(filename, sep=',', names=columnnames)
    #Replace whitespace (blanks) with NaNs
    df = df.replace(r'\s+', np.nan, regex=True)
    #Make all value float
    df = df.apply(pd.to_numeric)
    return df


def PlotDryVsWet(df, savename, ylim=None):
    """For a single compression test, plot dry vs wet tests.
    """
    _,ax = PlotStart(None, 'Engine Stroke',
                            'Cylinder Pressure [psi]', figsize=[6, 6])

    mhandles = [] #dry/wet
    mlabels = []
    nhandles = [] #cyl number
    nlabels = []

    for i, (test, marker) in enumerate(zip(['dry', 'wet'], ['o', '.'])):
        for j, cyl in enumerate([1, 2, 3, 4]):

            name = '{}{}'.format(cyl, test) #data key name
            # print(df['Stroke'][:len(df[name])]) #print strokes for each test
            h, = ax.plot(df['Stroke'].values, df[name].values,
                        label=name, color=colors[j],
                        linestyle='-', marker=marker, markersize=8
                        )
            if j == 0:
                mhandles.append(h)
                mlabels.append(str(test))
            if i == 0:
                nhandles.append(h)
                nlabels.append(str(cyl))
    ax.set_xlim([0, max(df['Stroke'])])
    plt.xticks(np.arange(1, max(df['Stroke'])+1, 2.0))
    if ylim != None:
        ax.set_ylim(ylim)

    leg1 = PlotLegendLabels(ax, mhandles, mlabels,
                            loc='lower center', title='Test')
    leg2 = PlotLegendLabels(ax, nhandles, nlabels,
                            loc='lower right', title='Cyl')
    plt.gca().add_artist(leg1)

    SavePlot(savename)

def PlotDryVsWetDelta(df, savename=None, ylim=None):
    """For a single compression test, plot wet - dry delta.
    """
    _,ax = PlotStart(None, 'Engine Stroke',
                            'Cylinder Pressure [psi]', figsize=[6, 6])


    for j, cyl in enumerate([1, 2, 3, 4]):

        name = '{}del'.format(cyl) #data key name
        h, = ax.plot(df['Stroke'].values, df[name].values,
                    label=name, color=colors[j],
                    linestyle='-', marker='o', markersize=8
                    )

    ax.set_xlim([0, max(df['Stroke'])])
    # plt.xticks(np.arange(0, max(df['Stroke'])+1, 1.0))
    if ylim != None:
        ax.set_ylim(ylim)

    leg1 = PlotLegend(ax, loc='lower center', title='$\\Delta P$')

    return ax
    # SavePlot(savename)



def main():
    """Plot dry and wet tests of all cylinders together against stroke number
    """

    dfs = {}
    keys = []


    ####################################################################
    ### PLOT DRY VS WET RESULTS FOR EACH TEST ##########################
    ####################################################################

    ####################################################################
    #FIRST TEST
        #Cammy mk3, 1/7/2017
    #dry and wet test data
    # filename = 'Data/CompTest_2016-01-07_1st_1999Camry.dat'
    filename = 'Data/CompTest_2016-01-07_1st_Retest2_1999Camry.dat'
    key = 1
    keys.append(key)
    dfs[key] = ReadCompTestData(filename)
    savename = 'Results/CompTest{}.png'.format(key)
    PlotDryVsWet(dfs[key], savename, [50, 275])

    ####################################################################
    #SECOND TEST
        #Cammy mk3, 1/7/2017
    # filename = 'Data/CompTest_2016-01-07_2nd_1999Camry.dat'
    filename = 'Data/CompTest_2016-01-07_2nd_Low3_1999Camry.dat'
        #includes low value for first stroke pressure
    key = 2
    keys.append(key)
    dfs[key] = ReadCompTestData(filename)
    savename = 'Results/CompTest{}.png'.format(key)
    PlotDryVsWet(dfs[key], savename, [50, 275])

    ####################################################################
    #THIRD TEST
        #Cammy mk3, 2/11/2017, after Seafoam treatment
    filename = 'Data/CompTest_2016-02-11_1st_1999Camry.dat'
    key = 3
    keys.append(key)
    dfs[key] = ReadCompTestData(filename)
    savename = 'Results/CompTest{}.png'.format(key)
    PlotDryVsWet(dfs[key], savename, [50, 275])




    ####################################################################
    #COROLLA TEST
        #Grant's corrolla, 2/12/2017
    filename = 'Data/CompTest_2016-02-12_1st_1996Corolla.dat'
    key = 'rolla'
    keys.append(key)
    dfs[key] = ReadCompTestData(filename)
    savename = 'Results/CompTest{}.png'.format(key)
    PlotDryVsWet(dfs[key], savename, [50, 275])


    ####################################################################
    ### DELTAS AND MAXIMA ########################
    ####################################################################

    cyls = [1, 2, 3, 4]

    #GET MAXIMA
    maxima = {}

    for k in keys:
        maxs = { 'dry' : [], 'wet' : []}
        for cyl in cyls:
            for test in ['dry', 'wet']:
                curkey = '{}{}'.format(cyl, test)
                #Get Local Maximum for Each Cylinder
                maxs[test].append(max( dfs[k][curkey] ))
        #Save Maxima for current test
        maxima[k] = pd.DataFrame( {
                                    'cyl' : cyls,
                                    'drymax' : maxs['dry'],
                                    'wetmax' : maxs['wet']
                                })



    #CALCULATE WET-DRY DELTAS

    for k in keys:
        print('\nTest: {}\n\n'.format(k))

        cyls = [1, 2, 3, 4]

        for cyl in cyls:
            print('Cyl: {}'.format(cyl))
            for test in ['dry', 'wet']:
                #FILL MISSING STROKE DATA WITH LAST RECORDED VALUE
                curkey = '{}{}'.format(cyl, test)
                #Get last value (non-NaN)
                lastval = dfs[k][curkey].dropna().iloc[-1]
                #Replace NaN values with last value
                dfs[k][curkey] = dfs[k][curkey].fillna(lastval)

            #Subtract dry test pressure from wet test pressure
            dfs[k]['{}del'.format(cyl)] = (dfs[k]['{}wet'.format(cyl)]
                                         - dfs[k]['{}dry'.format(cyl)])



    key = 'rolla'
    print(maxima[key])
    ax = PlotDryVsWetDelta(dfs[key])
    savename = 'Results/CompTest{}_delta.png'.format(key)
    SavePlot(savename)






    ####################################################################
    ### COMPARE DIFFERENT TESTS OF SIMILAR TYPE ########################
    ####################################################################





if __name__ == "__main__":


    main()
