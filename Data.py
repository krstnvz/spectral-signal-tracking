from queue import Empty
import pandas as pd
import Analysis as an
import numpy as np
import FileManager as fm

# class to contain the original eha results and other metadata
class EHAresult:
    pathStr = ""
    ehaData = pd.DataFrame()
    significanceIslands = []
    plottedPath = []
    interpolatedPath = []
    on_dataLoaded = []
    on_pathPlotted = []
    on_pathInterpol = []

    xmin = 0
    xmax = 0
    ymin = 0
    ymax = 0

    def assignPath(self, path):
        # assign the file path
        self.pathStr = path

        # load the file into a pandas dataframe
        self.ehaData = pd.read_csv(self.pathStr, header = 0, index_col = 0)

        #order dataframe so that the first column is the deepest
        self.ehaData = self.ehaData[self.ehaData.columns[::-1]]

        #transpose so that the depth is vertical
        self.ehaData = self.ehaData.transpose()

        #extract axes limit data for further analysis purposes
        self.extractAxisLimits()

        #notify listeners that data is fully loaded
        self.fireLoaded()

        print("File loaded.")

        #call function to draw the colormap
        an.drawColormap(self.ehaData, self.xmin, self.xmax, self.ymin, self.ymax)

    def extractAxisLimits(self):
        #extract values for edge values no both axis
        self.xmin = self.ehaData.columns[0]
        self.xmax = self.ehaData.columns[-1]
        self.ymin = float(self.ehaData.index[0])
        self.ymax = float(self.ehaData.index[-1])

    def traceFreqs(self, limitInput):
        print("Tracing started.")
        
        #extract significance limit from imput field
        limit = float(limitInput.get())

        #find significance islands
        self.significanceIslands = np.array(an.findSignificanceIslands(self.ehaData, limit), dtype=object)

        i = 0
        #visualize each of them
        for island in self.significanceIslands:
            print("Calculating path for island number " + str(i+1) + ".")
            islandPath = self.getIslandPath(island)

            print("Visualizing island number " + str(i+1) + ".")
            an.visualizeIsland(islandPath, i)
            i += 1


    def add_listener_toLoaded(self, listener):
        self.on_dataLoaded.append(listener)

    def add_listener_toPlotted(self, listener):
        self.on_pathPlotted.append(listener)

    def add_listener_toInterpol(self, listener):
        self.on_pathInterpol.append(listener)

    def fireLoaded(self):
        for listener in self.on_dataLoaded:
            listener()

    def firePlotted(self):
        for listener in self.on_pathPlotted:
            listener()

    def fireInterpol(self):
        for listener in self.on_pathInterpol:
            listener()

    #returns path in depth and freq coordinates!!!
    def getIslandPath(self, island):
        #convert island to np array so it is easily filtered
        island = np.array(island, dtype = object)

        #initialize path
        path = []

        #get the row n of the first and last entry
        f_row = island[0][0]
        l_row = island[-1][0]

        #get first column (which specifies row) so i can use it for filtering later
        f_col = island[:,0]

        #get each row of an island
        row = f_row
        while row <= l_row:
            #filter to only get rows where the id = row
            filter = np.asarray([row])
            mask = np.in1d(f_col, filter)
            this_row = island[mask]

            #get the middle value of this row, and get the discrete value
            mid = int(np.median(this_row, axis = 0)[1])

            #add it to the path
            path.append([row, mid])

            #increment the row count
            row += 1

        coor_path = []
        #convert path to coordinates for plotting
        for entry in path:
            depth = float(self.ehaData.index[entry[0]])
            freq = self.ehaData.columns[entry[1]]
            coor_path.append([depth, freq])

        #return path
        return coor_path

    #a function that prepares data of chosen islands and sends them for plotting
    def plotChosenIslands(self):
        print("Plotting chosen islands...")

        #get the ids of the chosen islands
        ids = an.getCurrentIslands()

        #check if there are selected islands
        if not ids:
            print("Nothing to plot!")
            return

        #save all the selected islands into the frequency path
        freqPath = []
        #for each island
        for idx in ids:
            #get Island path in depth and freq coordinates
            freqPath.extend(self.getIslandPath(self.significanceIslands[idx]))

        #make sure the path is ordered from deepest to shallowest
        freqPath.sort(key=lambda x: x[0])

        #send values for plotting
        an.pathFigureShow(freqPath, self.xmin, self.xmax, self.ymin, self.ymax)

        #save plotted path for later use
        self.plottedPath = pd.DataFrame(freqPath)

        self.firePlotted()
    
    #function that sends data for interpolation
    def fillData(self, extraVar):
        extra = extraVar.get()
        if extra:
            print("Interpolating and extrapolating ...")

        else:
            print("Interpolating ...")
        
        #send for interpolaiton
        self.interpolatedPath = an.interExtrapolate(self.plottedPath, extra, self.xmin, self.xmax, self.ymin, self.ymax)

        #notify listeners that data has been interpolated
        self.fireInterpol()

    #fucntion that takes care of exporting different datasets
    def exportData(self, dataIntVar):
        #first get a path to the saved file
        filePath = fm.exportFile()

        #see what file to export, the export // 1 -- pure path // 2 -- interpolated path || index = False because we don't need the row index exported
        num = dataIntVar.get()
        if num == 1:
            self.plottedPath.to_csv(filePath, index = False)
        elif num == 2:
            self.interpolatedPath.to_csv(filePath, index = False)
        else:
            print("Invalid export selection!")


