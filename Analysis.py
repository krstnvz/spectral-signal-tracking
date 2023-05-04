from cProfile import label
from dataclasses import dataclass
import numpy as np
import matplotlib.pyplot as p
import pandas as pd

##----VISUALIZATION OF DATA----##

fig, ax = p.subplots()
fig2, ax2 = p.subplots()
pickedIslands = []

#data array - array of row arrays
#xlow, xhigh, ylow, yhigh - end values for the x and y axis
def drawColormap(dataArray, xlow, xhigh, ybot, ytop):
    print("Drawing colormap...")

    #use pyplot image show to draw colormap, non interpolated, origin point is bottom left
    colormap = ax.imshow(dataArray, interpolation = 'none', cmap = p.cm.jet, origin = 'lower', aspect='auto', extent = [xlow, xhigh, ybot, ytop])

    #add colorbar
    p.colorbar(colormap)
    fig.show()

def visualizeIsland(path_coords, islandId):
    #convert to numpy array so i can extraxt data easily
    path_coords = np.array(path_coords)
    #extraxt coordinates (y is first because first column is depth)
    y,x = path_coords.T
    #draw a scatter plot of the path into the colormap
    ax.plot(x,y, c="lime", ms=7, picker = 10, label=islandId)

    #subscribe the on_pick function to the pick event callback
    fig.canvas.callbacks.connect('pick_event', on_pick)

    fig.show()

def pathFigureShow(freqPath, xmin, xmax, ybot, ytop):
    #convert to numpy array so i can extraxt data easily
    freqPath = np.array(freqPath)
    #extraxt coordinates (y is first because first column is depth)
    y,x = freqPath.T
    #draw a scatter plot of the deth/freqs
    ax2.scatter(x,y, c="red", s=7)
    ax2.set_xlim([xmin,xmax])
    ax2.set_ylim([ybot,ytop])

    fig2.show()


def plotInterpolation(data, ogData, xmin, xmax, ymin, ymax):   
    #plot interpolated data into same axes
    ax2.scatter(data['freq'], data['depth'], c="black", s=7)

    #plot the original data over it
    pathFigureShow(ogData, xmin, xmax, ymin, ymax)

    fig2.show()


##----INTERACTING----##

def on_pick(event):
    if int(event.artist._label) not in pickedIslands:
        pickedIslands.append(int(event.artist._label))
        print("You added island number " + str(event.artist._label))
        event.artist.set_color("white")
        fig.show()
    else:
        pickedIslands.remove(int(event.artist._label))
        print("You removed island number " + str(event.artist._label))
        event.artist.set_color("lime")
        fig.show()

    print("Currently selected islands: " + str(pickedIslands))

def getCurrentIslands():
    return pickedIslands


##----SIGNIFICANCE ISLAND IDETIFICATION----##


#helper function - checks if a given cell can be included in DFS
def isSafeToVisit(i, j, visited, dataArray, limit):
    # row number is in range, column number
    # is in range and value is >= 0.9
    # and not yet visited
    return (i >= 0 and i < len(visited) and
            j >= 0 and j < len(visited[0]) and
            not visited [i][j] and dataArray.iloc[i,j] >= limit)

#helper function for identifying all significance islands - visits adjuscent cells and either adds them to the island or not
#returns wether it finished exploring the island or not
def DFS(i, j, visited, dataArray, depth, islands, currentIsland, limit):
    #increment depth, which keeps track of how deep in recursion we are
    depth += 1

    #initialize row and col arrays with indexes of surrounding cells
    rowNbr = [-1,-1,-1,0,0,1,1,1]
    colNbr = [-1,0,1,-1,1,-1,0,1]

    #mark current cell as visited
    visited[i][j] = True

    #add cell to the current island
    islands[currentIsland].append([i,j])

    valid_neighbors = 0

    #run a loop from 0 - 8 to traverse the neighbor
    for n in range(8):
        #if neigbor is safe to visit and is not visited
        if isSafeToVisit(i + rowNbr[n], j + colNbr[n], visited, dataArray, limit):
            #check how deep we are in recursion, if too deep leave the next cell for the next batch
            if (depth >= 900):
                return False, i + rowNbr[n], j + colNbr[n];

            valid_neighbors += 1

            #call DFS recursively on the neighbor
            finished, lasti, lastj = DFS(i + rowNbr[n], j + colNbr[n], visited, dataArray, depth, islands, currentIsland, limit)
            if not finished:
                return finished, lasti, lastj

    return True, i + rowNbr[n], j + colNbr[n];

def findSignificanceIslands(dataArray, limit):
    print("Identifying island...")

    #initialize a matrix for storing all the islands
    islands = []

    #get the size of the matrix
    rows = len(dataArray.index)
    cols = len(dataArray.columns)
    
    #initialize boolean matrix to false in the same size to store if cell was visited
    visited = [[False for j in range(cols)]for i in range(rows)]

    #initialize count = 0, to store number of islands
    count = 0

    #traverse a loop from 0 to ROW
    for i in range(rows):
        #traverse a nested loop from 0 to COL
        for j in range(cols):
            #if the value of the current cell in the matrix is >= limit and is not visited
            if visited[i][j] == False and dataArray.iloc[i,j] >= limit:
                #append a new island to the islands array
                islands.append([])

                #call DFS function to visit all cells in this island
                finished, lasti, lastj = DFS(i, j, visited, dataArray, 0, islands, count, limit)

                #check if island finished, if not, call DFS to do the next batch until it does finish
                while not finished:
                    finished, lasti, lastj = DFS(lasti, lastj, visited, dataArray, 0, islands, count, limit)

                #increment count by 1
                count += 1

                print("Island " + str(count) + " explored.")

    print("Finished exploring. Number of islands identified: " + str(count))

    #return the islands
    return islands


##----INTER AND EXTRAPLOATION----##


#function that produces the interpolated and/or extrapolated data based on initial path
def interExtrapolate(path, extraBool, xmin, xmax, ymin, ymax):
    #first add names to the dataframe columns
    col_names = ['depth', 'freq']
    path_df = path
    path_df.columns = col_names

    if extraBool:
        #get depth max and min for resampling
        dMin = ymax
        dMax = ymin
    else:
        #get depth max and min for resampling
        dMin = float(path_df.iloc[0,0])
        dMax = float(path_df.iloc[-1,0])

    #calculate number of samples after interpolation
    span = round(dMax - dMin,1)
    step = round(float(path_df.iloc[-1,0]) - float(path_df.iloc[-2,0]), 2)
    i = int(span/step)
    num = i + 1

    #create a new depthAxis for resampling (that goes from deepest to shallowes)
    depth_resampled = np.linspace(dMin, dMax, num)

    #create a dataframe with resampled depth
    path_resampled = pd.DataFrame(depth_resampled, columns=['depth'])

    #temporarily converting the depth column ito strings with 1 decimal so that it is possible to merge the two dfs
    path_resampled['depth'] = path_resampled['depth'].map(lambda x: '{0:.1f}'.format(x))
    path_df['depth'] = path_df['depth'].map(lambda x: '{0:.1f}'.format(x))

    #right join table, there should now be the existing values as well as nans at new depths
    path_resampled = pd.merge(path_df, path_resampled, on=['depth'], how='right')

    #convert back to floats
    path_resampled['depth'] = path_resampled['depth'].astype(float)
    path_df['depth'] = path_df['depth'].astype(float)

    #now interpolate over nans
    path_interpol = path_resampled
    path_interpol['freq'] = path_interpol['freq'].interpolate()

    path_resampled.to_csv("D:/resampled.csv")
    path_interpol.to_csv("D:/interpol.csv")

    plotInterpolation(path_interpol, path, xmin, xmax, ymin, ymax)

    return path_interpol
