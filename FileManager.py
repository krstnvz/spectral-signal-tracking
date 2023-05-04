from tkinter import filedialog

#function to open a csv file and put it into a dataframe
def openFile_csv(empty_ehaResults):
    #open file dialog and get the chosen file path
    file_path = filedialog.askopenfilename()
    empty_ehaResults.assignPath(file_path)

def exportFile():
    filename = filedialog.asksaveasfilename(filetypes = [('All types(*.*)', '*.*'),('csv file(*.csv)', '*.csv')], 
                                            defaultextension = [('csv file(*.csv)', '*.csv')])

    return filename