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


def PlotDryVsWet(df, savename, ylim=None, norm=False):
    """For a single compression test, plot dry vs wet tests.
    df --> pandas dataframe containing test data
    savename --> file name to save plot as
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

    for i, (test, marker) in enumerate(zip(['dry', 'wet'], ['o', '.'])):
        for j, cyl in enumerate([1, 2, 3, 4]):

            name = '{}{}'.format(cyl, test) #data key name
            if norm:
                #key for data normalized by its maximum
                name = '{}norm'.format(name)

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

def PlotDryVsWetDelta(df, ylim=None, norm=1):
    """For a single compression test, plot wet - dry delta.
    df --> pandas dataframe containing test data
    ylim --> boundaries of y-axis ([ymin, ymax])
    norm --> normalization factor (1 for none, max dry values otherwise)
    """



    if max(norm) == 1:
        norm = np.ones(4)
        ylbl = 'Wet - Dry [psi]'
        legtitle = '$\\Delta P$'
    else:
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
    # SavePlot(savename)


def main(path, name, ylim=None):
    """Plot dry and wet tests of all cylinders together against stroke number
    """

    ### LOAD TEST DATA
    df = ReadCompTestData(path)

    ####################################################################
    ### PLOT DRY VS WET RESULTS ########################################
    ####################################################################

    savename = 'Results/CompTest{}.png'.format(name)
    PlotDryVsWet(df, savename, ylim)




    # ####################################################################
    # #FIRST TEST
    #     #Cammy mk3, 1/7/2017
    # #dry and wet test data
    # # filename = 'Data/CompTest_2016-01-07_1st_1999Camry.dat'
    # filename = 'Data/CompTest_2016-01-07_1st_Retest2_1999Camry.dat'
    # key = 1
    # keys.append(key)
    # df = ReadCompTestData(path)
    # savename = 'Results/CompTest{}.png'.format(name)
    # PlotDryVsWet(df, savename, ylim)

    # ####################################################################
    # #SECOND TEST
    #     #Cammy mk3, 1/7/2017
    # # filename = 'Data/CompTest_2016-01-07_2nd_1999Camry.dat'
    # filename = 'Data/CompTest_2016-01-07_2nd_Low3_1999Camry.dat'
    #     #includes low value for first stroke pressure
    # key = 2
    # keys.append(key)
    # dfs[key] = ReadCompTestData(filename)
    # savename = 'Results/CompTest{}.png'.format(key)
    # PlotDryVsWet(dfs[key], savename, [50, 275])

    # ####################################################################
    # #THIRD TEST
    #     #Cammy mk3, 2/11/2017, after Seafoam treatment
    # filename = 'Data/CompTest_2016-02-11_1st_1999Camry.dat'
    # key = 3
    # keys.append(key)
    # dfs[key] = ReadCompTestData(filename)
    # savename = 'Results/CompTest{}.png'.format(key)
    # PlotDryVsWet(dfs[key], savename, [50, 275])

    # print(dfs[key])


    # ####################################################################
    # #COROLLA TEST
    #     #Grant's corrolla, 2/12/2017
    # filename = 'Data/CompTest_2016-02-12_1st_1996Corolla.dat'
    # key = 'rolla'
    # keys.append(key)
    # dfs[key] = ReadCompTestData(filename)
    # savename = 'Results/CompTest{}.png'.format(key)
    # PlotDryVsWet(dfs[key], savename, [50, 275])

    # print(dfs[key])

    ####################################################################
    ### DELTAS AND MAXIMA ########################
    ####################################################################

    cyls = [1, 2, 3, 4]
    tests = ['dry', 'wet']

    #GET MAXIMA AND NORMALIZE

    maxs = { 'dry' : [], 'wet' : []}
    for cyl in cyls:
        for test in tests:
            curkey = '{}{}'.format(cyl, test)
            #Get Local Maximum for Each Cylinder
            maxs[test].append(max( df[curkey] ))
            #Normalize Current Cylinder by Maximum
            df['{}norm'.format(curkey)] = df[curkey] / maxs[test][-1]

    #PLOT NORMALIZED DRY VS WET TESTS
    savename = 'Results/CompTest{}_norm.png'.format(name)
    PlotDryVsWet(df, savename, None, norm=True)



    #Save Maxima for current test
    maxima = pd.DataFrame( {
                                'cyl' : cyls,
                                'drymax' : maxs['dry'],
                                'wetmax' : maxs['wet']
                            })

    #CALC FRACTIONAL DIFFERENCE FROM MAX CYLINDER
        #lower pressure is worse.  Calc percent difference of lower
        #max pressures from greatest max pressure.
    maxcyl = max(maxima['drymax'])
    maxima['diff'] = (maxima['drymax'] - maxcyl) / maxcyl

    #Print Differences
    print('Test {} % diff:'.format(name) )
    print( maxima['diff'] * 100 )


    #CALCULATE WET-DRY DELTAS
    for cyl in cyls:
        for test in tests:
            #FILL MISSING STROKE DATA WITH LAST RECORDED VALUE
            curkey = '{}{}'.format(cyl, test)
            #Get last value (non-NaN)
            lastval = df[curkey].dropna().iloc[-1]
            #Replace NaN values with last value
            df[curkey] = df[curkey].fillna(lastval)

        #Subtract dry test pressure from wet test pressure
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
    tmpdf = main(filename, key, ylimit, )
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





