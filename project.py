import pandas as pd
from pandas import Series, DataFrame
import datetime
from datetime import datetime as dt
import tkinter as tk
from tkinter import filedialog, Text
from tkinter import *
import os

root =tk.Tk()
root.title('MWH Converter')
root.geometry('600x600')
root.resizable(0, 0)
files = []

#function that takes string in HH:MM:SS format and converts it to a number representing hours
def stringToHours(hms):
    timeObj = dt.strptime(hms, '%H:%M:%S').time()
    return timeObj.hour + (timeObj.minute/60) + (timeObj.second/3600)

#function that programs functionality for add files button
def addFiles():
    for widget in frame.winfo_children():
        widget.destroy()
    
    filenames = filedialog.askopenfilenames(initialdir='/', title = "Select File")
    global files
    files = filenames
    for file in files:
        label = tk.Label(frame, text = os.path.basename(file).split('/')[-1], bg ='#E9E8D7')
        label.pack()

#clears hints from start and end time boxes
def startclick(*args):
    startEntry.delete(0, 'end')
def endclick(*args):
    endEntry.delete(0, 'end')
    
#resets everything   
def clear():
    startEntry.delete(0, END)
    endEntry.delete(0, END)
    global files
    files = []
    for widget in frame.winfo_children():
        widget.destroy()

#what happens when submit button is pressed
def submit():
    for widget in frame.winfo_children():
        widget.destroy()
    for file in files:
        ex = pd.read_csv(file)
        
        #setting up dataframe
        ex = ex.drop([0,1,2])
        ex.columns = ['time', 'value']
        ex = ex.dropna()
        ex = ex.reset_index()
        ex = ex.drop('index', axis = 1)
        
        # getting user input for time 
        startTimeStr = startEntry.get()
        endTimeStr = endEntry.get()
        startT = stringToHours(startTimeStr)
        endT = stringToHours(endTimeStr)
        if (startT > endT):
            for widget in frame.winfo_children():
                widget.destroy()
            label = tk.Label(frame, text = 'Invalid time entry, start time must be before end time', bg ='#E9E8D7')
            label.pack()
        elif (startT < stringToHours(ex.time[len(ex.time)-2])):
            for widget in frame.winfo_children():
                widget.destroy()
            label = tk.Label(frame, text = 'Invalid time entry, start time must be later', bg ='#E9E8D7')
            label.pack()
        elif (endT > stringToHours(ex.time[0])):
            for widget in frame.winfo_children():
                widget.destroy()
            label = tk.Label(frame, text = 'Invalid time entry, end time must be earlier', bg ='#E9E8D7')
            label.pack()
        else:    
            # computing integral
            times = ex.time
            integral = 0
            for i in range(len(times) -1):
                time = stringToHours(times[i])
                if (time >= startT and time <=endT):
                    nextTime = stringToHours(times[i+1])
                    deltaT = time - nextTime
                    integral += deltaT * float(ex.value[i])
            t ="File Name: " + os.path.basename(file).split('/')[-1] + "\noutput from " + startTimeStr + " to " +endTimeStr + ":       " + str(integral) + " MWH\n" 
            label = tk.Label(frame, text = t, bg ='#E9E8D7')
            label.pack()


#tkinter setup
canvas = tk.Canvas(master=root, height = 500, width = 500, bg = "#497A79")
canvas.pack_propagate(0)
canvas.pack(fill=tk.BOTH, expand=1)

frame = tk.Frame(master=root, bg = "#E9E8D7")
frame.place(relwidth = 0.8, relheight = 0.75, relx = 0.1, rely = 0.05)



openFile = tk.Button(root, text = "Open Files", padx = 10, pady = 5, fg ='#E9E8D7', bg = '#497A79', command = addFiles)
openFile.pack()

startEntry =tk.Entry(root)
startEntry.config(bg = "#FFFFFF", fg = "#08272A" )
startEntry.insert(0, "Start Time (HH:MM:SS)")
startEntry.config(width = 20)
startEntry.pack()
startEntry.bind("<Button-1>", startclick)

endEntry = tk.Entry(root)
endEntry.config(bg = "#FFFFFF", fg = "#08272A")
endEntry.insert(0, "End Time  (HH:MM:SS)")
endEntry.config(width = 20)
endEntry.pack()
endEntry.bind("<Button-1>", endclick)

submitButton = Button(root, text = "Submit", command = submit )
submitButton.pack(side= RIGHT)

clearButton = Button(root, text = "Clear Values", command = clear)
clearButton.pack(side= RIGHT)

root.mainloop()