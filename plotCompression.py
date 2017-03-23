"""COMPRESSION TEST VISUALIZATION TOOL
Logan Halstrom
CREATED: 08 JAN 2017
MODIFIY: 22 MAR 2017

DESCRIPTION:  Visualize data for compression tests of internal combustion
engines.  Compare pressure history of each cylinder as well as differences
between dry and wet (oil added to cylinder) tests.

NOTE:
Data files are made by pasting Google sheet columns into Sublime text,
separating with columns, and trimming whitespace in numerical entries.
NaNs are filled with whitespace that is later replaced by NaN in script.

FUTURE IMPROVMENTS:
Add threshold percentage value for deviation from max and print warning
dry only or dry and wet option

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


def PlotPressHist(df, ylim=None, norm=False,
                    tests=['dry', 'wet'], cyls=[1, 2, 3, 4] ):
    """For a single compression test, plot cylinder pressure history.
    Plot dry vs wet tests if data is available for both
    df --> pandas dataframe containing test data
    ylim --> boundaries of y-axis ([ymin, ymax])
    norm --> plot normalized values instead (must calculate beforehand)
    """

    ylbl = 'Cylinder Pressure [psi]'
    if norm:
        ylbl = 'Norm. Cyl. Pressure [N.D.]'
    _,ax = PlotStart(None, 'Engine Stroke', ylbl, figsize=[6, 6])

    mhandles = [] #dry/wet
    mlabels = []
    nhandles = [] #cyl number
    nlabels = []

    for i, (test, marker) in enumerate(zip(tests, ['o', '.'])):
        for j, cyl in enumerate(cyls):

            name = '{}{}'.format(cyl, test) #data key name
            if norm:
                #key for data normalized by its maximum
                name = '{}norm'.format(name)

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

    #Cylinder Legend
    leg1 = PlotLegendLabels(ax, nhandles, nlabels,
                            loc='lower right', title='Cyl')
    if len(tests) > 1:
        #Test Type Legend
        leg2 = PlotLegendLabels(ax, mhandles, mlabels,
                                loc='lower center', title='Test')
        plt.gca().add_artist(leg1)

    return ax

def PlotDryVsWetDelta(df, ylim=None, norm=1):
    """For a single compression test, plot wet - dry delta.
    df --> pandas dataframe containing test data
    ylim --> boundaries of y-axis ([ymin, ymax])
    norm --> normalization factor (1 for none, max dry values otherwise)
    """

    if max(norm) == 1:
        #Non-normalized plot
        norm = np.ones(4)
        ylbl = 'Wet - Dry [psi]'
        legtitle = '$\\Delta P$'
    else:
        #Normalize each delta by max pressure of that cylinder
        ylbl = 'Norm. Wet - Dry'
        legtitle = '$\\Delta P / P_{dry,max}$'

    _,ax = PlotStart(None, 'Engine Stroke', ylbl, figsize=[6, 6])


    for j, cyl in enumerate([1, 2, 3, 4]):

        name = '{}del'.format(cyl) #data key name
        h, = ax.plot(df['Stroke'].values, df[name].values / norm[j],
                    label=cyl, color=colors[j],
                    linestyle='-', marker='o', markersize=8
                    )

    ax.set_xlim([0, max(df['Stroke'])])
    plt.xticks(np.arange(1, max(df['Stroke'])+1, 2.0))
    if ylim != None:
        ax.set_ylim(ylim)

    leg1 = PlotLegend(ax, loc='lower center', title=legtitle)

    return ax


def main(path, name, ylim=None, thresh=15,
            tests=['dry', 'wet'], ncyl=4):
    """
    Calculate maximum pressure of each cylinder in each test
    Determine pressure variation between cylinders, evaluate with threshold
    Plot cylinder pressure histories, raw and normalized
    Co-plot dry and wet tests if data is available
    Plot dry and wet test pressure differences if data is available

    path --> path to data file
    name --> name for current test
    ylim --> y-axis plotting range (e.g. [ymin, ymax] or None)
    thresh --> percentage threshold for poor cylinder performance
                (assessed as negative in code)
    tests --> types of tests performed ('dry' only or both 'dry' and 'wet')
    ncyl  --> number of cylinders in engine
    """


    ####################################################################
    ### LOAD TEST DATA #################################################
    ####################################################################

    cyls = np.arange(1, ncyl+1, 1) #List of cylinder numbers
    df = ReadCompTestData(path)    #Load compression test pressure data

    ####################################################################
    ### MAXIMA ANALYSIS ################################################
    ####################################################################


    #CALCULATE MAXIMA AND NORMALIZE PRESSURE
    maxima = pd.DataFrame( {'cyl' : cyls})

    for test in tests:
        maxs = []
        for cyl in cyls:
            curkey = '{}{}'.format(cyl, test)
            #Get Local Maximum for Each Cylinder
            maxs.append(max( df[curkey] ))
            #Normalize Current Cylinder by Maximum
            df['{}norm'.format(curkey)] = df[curkey] / maxs[-1]

        maxima['{}max'.format(test)] = maxs

    #CALC FRACTIONAL DIFFERENCE FROM MAX CYLINDER (DRY TEST ONLY)
        #lower pressure is worse.  Calc percent difference of lower
        #max pressures from greatest max pressure.
    maxcyl = max(maxima['drymax'])
    maxima['diff'] = (maxima['drymax'] - maxcyl) / maxcyl #fractional diff
    maxima['percdiff'] = maxima['diff'] * 100 #percent difference

    #Print Differences
    print('\n**********************************')
    print('Compression Test {}, % difference:'.format(name) )
    print( maxima[['cyl', 'percdiff']])
    #Determine if any cylinders are outside of success threshold
    failures = maxima[maxima['percdiff'] < -thresh]
    if not failures.empty:
        print('WARNING: FOLLOWING CYLINDERS ARE ' \
                'BELOW {}% OF MAXIMUM (FAIL)!!!'.format(thresh))
        print( failures[['cyl', 'percdiff']])
    else:
        print('ALL MAXIMUM CYLINDER PRESSURES ARE ' \
                'WITHIN THRESHOLD (PASS)!!!')



    ####################################################################
    ### PLOT PRESSURE HISTORIES ########################################
    ####################################################################

    #PLOT COMPRESSION TEST PRESSURE HISTORIES (DRY VS WET IF AVAILABLE)
    PlotPressHist(df, ylim, tests=tests, cyls=cyls)
    savename = 'Results/CompTest{}.png'.format(name)
    SavePlot(savename)

    #PLOT NORMALIZED PRESSURE HISTORIES (DRY VS WET IF AVAILABLE)
    PlotPressHist(df, None, norm=True, tests=tests, cyls=cyls)
    savename = 'Results/CompTest{}_norm.png'.format(name)
    SavePlot(savename)

    ####################################################################
    ### WET-DRY DELTAS #################################################
    ####################################################################

    #CALCULATE DIFFERENCE BETWEEN WET AND DRY TESTS
    for cyl in cyls:
        for test in tests:
            #FILL MISSING STROKE DATA WITH LAST RECORDED VALUE
            curkey = '{}{}'.format(cyl, test)
            #Get last value (non-NaN)
            lastval = df[curkey].dropna().iloc[-1]
            #Replace NaN values with last value
            df[curkey] = df[curkey].fillna(lastval)

        #SUBTRACT DRY TEST PRESSURE FROM WET TEST PRESSURE
        df['{}del'.format(cyl)] = (df['{}wet'.format(cyl)]
                                     - df['{}dry'.format(cyl)])

    #PLOT DELTAS AS FRACTION OF MAX DRY PRESSURE FOR EACH CYLINDER
    ax = PlotDryVsWetDelta(df, None, norm=maxima['drymax'])
    savename = 'Results/CompTest{}_delta_norm.png'.format(name)
    SavePlot(savename)



    return df, maxima



if __name__ == "__main__":


    ####################################################################
    ### RUN MAIN FOR SEPARATE COMPRESSION TESTS ########################
    ####################################################################

    keys = []   #Key for each test
    dfs = {}    #Store processed data for each test
    maxima = {} #Store maxima of each test

    ylimit = [50, 275] #Limits for plots

    ####################################################################
    #FIRST TEST
        #Cammy mk3, 1/7/2017
    #dry and wet test data
    # filename = 'Data/CompTest_2016-01-07_1st_1999Camry.dat'
    filename = 'Data/CompTest_2016-01-07_1st_Retest2_1999Camry.dat'
    key = 1
    #CALCULATIONS AND PLOTS FOR CURENT TEST
    tmpdf = main(filename, key, ylimit)
    #Save Data
    dfs[key], maxima[key] = tmpdf
    keys.append(key)

    ####################################################################
    #SECOND TEST
        #Cammy mk3, 1/7/2017
    # filename = 'Data/CompTest_2016-01-07_2nd_1999Camry.dat'
    filename = 'Data/CompTest_2016-01-07_2nd_Low3_1999Camry.dat'
        #includes low value for first stroke pressure
    key = 2
    tmpdf = main(filename, key, ylimit, )
    #Save Data
    dfs[key], maxima[key] = tmpdf
    keys.append(key)

    ####################################################################
    #THIRD TEST
        #Cammy mk3, 2/11/2017, after Seafoam treatment
    filename = 'Data/CompTest_2016-02-11_1st_1999Camry.dat'
    key = 3
    tmpdf = main(filename, key, ylimit, )
    #Save Data
    dfs[key], maxima[key] = tmpdf
    keys.append(key)

    ####################################################################
    #COROLLA TEST
        #Grant's corrolla, 2/12/2017
    filename = 'Data/CompTest_2016-02-12_1st_1996Corolla.dat'
    key = 'rolla'
    tmpdf = main(filename, key, ylimit, )
    #Save Data
    dfs[key], maxima[key] = tmpdf
    keys.append(key)





