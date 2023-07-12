import pandas as pd
from pandas import Series, DataFrame
import datetime
from datetime import datetime as dt
import tkinter as tk
from tkinter import filedialog, Text
from tkinter import *
import os

#tkinter setup
root =tk.Tk()
root.title('MWH Converter')
root.geometry('700x700')
root.resizable(0, 0)

#global vars
files = []
singleFile = IntVar()


#function that takes string in HH:MM:SS format and converts it to a number representing hours
def stringToHours(hms):
    timeObj = dt.strptime(hms, '%H:%M:%S').time()
    return timeObj.hour + (timeObj.minute/60) + (timeObj.second/3600)

#Function that takes string in date-time format and converts it a string only containing HH:MM:SS
def dateToHrs(dateStr):
    return dateStr.split(" ")[-1]
    

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
def startDayClick(*args):
    startDate.delete(0, 'end')
def endDayClick(*args):
    endDate.delete(0, 'end')
    
#resets everything   
def clear():
    startEntry.delete(0, END)
    endEntry.delete(0, END)
    startDate.delete(0, END)
    endDate.delete(0, END)
    global files
    files = []
    for widget in frame.winfo_children():
        widget.destroy()
    startEntry.insert(0, "Start Time (HH:MM:SS)")
    endEntry.insert(0, "End Time  (HH:MM:SS)")
    startDate.insert(0, "Start (MM/DD/YYYY)")
    endDate.insert(0, "End (MM/DD/YYYY)")

#Allows input to date depending on state of singleFile    
def changeEntry():
    if (singleFile.get() == 0):
        startDate.config(state='disabled')
        endDate.config(state='disabled')
    else:
        startDate.config(state='normal')
        endDate.config(state='normal')
        
#performs integral calculation for mva and mw        
def mvaIntegral(startT, endT, ex):
    times = ex.time
    integral = 0
    for i in range(len(times) -1):
        time = stringToHours(dateToHrs(times[i]))
        if (time >= startT and time <=endT):
            nextTime = stringToHours(dateToHrs(times[i+1]))
            deltaT = time - nextTime
            integral += deltaT * float(ex.value[i]) 
    return integral

#performs integral calculation for amps
def ampsIntegral(startT, endT, ex, multiplier):
    ex.value = ex.value.astype(float)
    ex.value *=((1.73*multiplier)/1000000)
    return mvaIntegral(startT, endT, ex)

#what happens when submit button is pressed
def submit():
    #Clears what was previously on screen
    for widget in frame.winfo_children():
        widget.destroy()
    #Multi file mode    
    if (singleFile.get() == 0):
        for file in files:
            #setting up dataframe
            ex = pd.read_csv(file, on_bad_lines='skip')
            unit = ex.columns[1].split(' ')[-1]
            multiplier = 0
            if (unit == "AMPS.MV"):
                if ("W" in ex.columns[1].split(" ")[1]):
                    multiplier = 13800
                if ("L" in ex.columns[1].split(" ")[1]):
                    multiplier = 13200
            ex = ex.drop([0,1])
            ex.columns = ['time', 'value']
            ex = ex.dropna()
            ex = ex.reset_index()
            ex = ex.drop('index', axis = 1)
            # getting user input for time 
            startTimeStr = startEntry.get()
            endTimeStr = endEntry.get()
            startT = stringToHours(startTimeStr)
            endT = stringToHours(endTimeStr)
            #Incorrect usage checks
            if (startT > endT):
                for widget in frame.winfo_children():
                    widget.destroy()
                label = tk.Label(frame, text = 'Invalid time entry, start time must be before end time', bg ='#E9E8D7')
                label.pack()
            elif (startT < stringToHours(dateToHrs(ex.time[len(ex.time)-2]))):
                for widget in frame.winfo_children():
                    widget.destroy()
                label = tk.Label(frame, text = 'Invalid time entry, start time must be later', bg ='#E9E8D7')
                label.pack()
            elif (endT > stringToHours(dateToHrs(ex.time[0]))):
                for widget in frame.winfo_children():
                    widget.destroy()
                label = tk.Label(frame, text = 'Invalid time entry, end time must be earlier', bg ='#E9E8D7')
                label.pack()
            #If correctly used, continue    
            else:    
                # computing integral
                integral = 0
                if (unit == "MW.MV" or unit == "MVA.MV"):
                    integral = mvaIntegral(startT, endT, ex)
                elif (unit == "AMPS.MV"):
                    print(multiplier)
                    integral = ampsIntegral(startT, endT, ex, multiplier)
                else:
                    print("Unsupported format, only MVA, MW, and AMPS are supported as of now")
                t ="File Name: " + os.path.basename(file).split('/')[-1] + "\noutput from " + startTimeStr + " to " +endTimeStr + ":       " + str(integral) + " MWH\n" 
                label = tk.Label(frame, text = t, bg ='#E9E8D7')
                label.pack() 
    # else:


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

startDate = tk.Entry(root)
startDate.config(bg = "#FFFFFF", fg = "#08272A")
startDate.insert(0, "Start (MM/DD/YYYY)")
startDate.config(width = 20)
startDate.config(state='disabled')
startDate.pack(side = 'left')
startDate.bind('<Button-1>',startDayClick)

endDate = tk.Entry(root)
endDate.config(bg = "#FFFFFF", fg = "#08272A")
endDate.insert(0, "End (MM/DD/YYYY)")
endDate.config(width = 20)
endDate.config(state='disabled')
endDate.pack(side = LEFT)
endDate.bind('<Button-1>',endDayClick)

submitButton = Button(root, text = "Submit", command = submit )
submitButton.pack(side= RIGHT)

clearButton = Button(root, text = "Clear Values", command = clear)
clearButton.pack(side= RIGHT)


checkBox = Checkbutton(root, text="Single File Mode (Use for 1 file with multiple dates)", variable= singleFile, command = changeEntry)
checkBox.pack(side = TOP)

root.mainloop()