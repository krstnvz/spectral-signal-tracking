from cgitb import text
import tkinter as tk
import FileManager as fm
import Data as dt
import Analysis as an

#create an EHAresult
ehaRes = dt.EHAresult()
baseButtons = []                #buttons to be enabled after data is loaded
manipulateElements = []         #elements to be enabled once a chose path is plotted
interpolElements = []           #elements to be enbaled once interpolation is finnished

def main():
    #create the main window
    root = tk.Tk()

    #add a listener to the results - the listener is notified when the data is fully loaded and visualized
    #I am using this to enable the basic analysis buttons only after the data has fully loaded
    ehaRes.add_listener_toLoaded(enableAnalysisButtons)
    ehaRes.add_listener_toPlotted(enablePathManipulation)
    ehaRes.add_listener_toInterpol(enableAfterInterpolation)

    #add open file button (two callbacks - one to a file dialog and one to change the frame)
    openButton = tk.Button(root, text ="Open file", command= lambda: [ analysisDialog(root), fm.openFile_csv(ehaRes)])
    openButton.pack(pady = 40)

    #run the main window
    root. mainloop()

def analysisDialog(root):
    #erase everything from the entry frame
    for widget in root.winfo_children():
        widget.destroy()

    #input field for significance limit for signal tracing
    limitInput = tk.Entry(root)
    limitInput.grid(row = 0, column= 0, padx = 5, pady = 5)

    #button to find signal chunks
    traceButton = tk.Button(root, text ="Trace signal", command= lambda: [ehaRes.traceFreqs(limitInput), disableButton(traceButton), enableButton(plotButton)])
    #disable until the data is loaded
    traceButton["state"] = "disabled"
    traceButton.grid(row = 0, column = 1, padx=5, pady=5)

    #button to plot chosen islands
    plotButton = tk.Button(root, text = "Plot islands", command= ehaRes.plotChosenIslands)
    #disable until the islands are identified
    plotButton["state"] = "disabled"
    plotButton.grid(row = 1, columnspan= 2, padx=5, pady=5)

    #checkboxes - should we also extrapolate?
    extraVar = tk.BooleanVar(root)
    extraCheck = tk.Checkbutton(root, text = "Extrapolate", variable = extraVar)
    extraCheck["state"] = "disabled"
    extraCheck.grid(row = 2, column = 0, padx=5, pady=5)

    #button to inter and extrapolate the chosen path
    fillButton = tk.Button(root, text = "Interpolate", command= lambda: [ehaRes.fillData(extraVar)])
    #disable until a path is chosen
    fillButton["state"] = "disabled"
    fillButton.grid(row = 2, column = 1, padx=5, pady=5)

    #radiobuttons to select which data should be exported
    selected = tk.IntVar(root)
    radio_pure = tk.Radiobutton(root, text="Pure Path", variable=selected, value=1)
    radio_inter = tk.Radiobutton(root, text="Interpolation", variable=selected, value=2)
    radio_pure.grid(row = 3, column = 0, padx = 5, pady = 2)
    radio_inter.grid(row = 4, column = 0, padx = 5, pady = 2)
    radio_pure["state"] = "disabled"
    radio_inter["state"] = "disabled"

    #export data into a file button
    exportButton = tk.Button(root, text = "Export", command = lambda: [ehaRes.exportData(selected)])
    exportButton.grid(row = 3, column = 1, rowspan = 2, padx = 5, pady = 5)
    exportButton["state"] = "disabled"

    #add trace button to array of basic buttons to be enabled on load
    baseButtons.append(traceButton)
    #add manipulation elements to an array to be enabled when the path is plotted
    manipulateElements.append(extraCheck)
    manipulateElements.append(fillButton)
    #add export elems to be enabled once path is plotted
    manipulateElements.append(exportButton)
    manipulateElements.append(radio_pure)
    #add export elems to be enabled after interpolation
    interpolElements.append(radio_inter)

#function to enable analysis buttons - is a listener of the ehaResult class
def enableAnalysisButtons():
    for button in baseButtons:
        enableButton(button)

#function that enables elements that are used for path manipulation - called once the path is plotted
def enablePathManipulation():
    for elem in manipulateElements:
        enableButton(elem)

def enableAfterInterpolation():
    for elem in interpolElements:
        enableButton(elem)

#function that disables any button, takes the button as an input
def disableButton(button):
    button["state"] = "disabled"

#function that enables any button, takes the button as an input
def enableButton(button):
    button["state"] = "normal"

if __name__ == "__main__":
    main()


