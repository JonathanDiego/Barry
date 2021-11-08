# -*- coding: utf-8 -*-
"""
Created on Mon Nov  1 22:35:04 2021

@author: Jonathan
"""
from pystray import MenuItem as item
from datetime import datetime
from threading import Timer
from tkinter import ttk
from PIL import Image 
import tkinter as tk
import pandas as pd
import pystray

#from tkinter.messagebox import showinfo

class FORM1:    
    #Paths of resources
    configPath = "DataBase\\config.json"
    dataPath = "DataBase\\data.json"
    icoName = "resource\\barry.ico"
        
    standardFontLbl = ("Dubai", 14)
    standardFontEntry = ("Dubai", 10)    
    SecondsCount = 1    
    
    def __init__(self):    
        try:            
            self.window = tk.Tk()
            self.window.title("Barry - quick activity reports")
            self.window.iconbitmap(self.icoName)
            self.window.configure(background='black')        
            self.window.resizable(False, False)
            self.window.attributes("-topmost", True)
            self.window.bind("<Key>", self.key_pressed)
    
            self.RecalcCenterScreen(600, 500)
    
            self.LoadConfig()
            self.Visible = True
            
            #powered
            self.lblPowered = tk.Label(self.window, text="Created by JD", fg='white', font=self.standardFontLbl, bg = 'black')
            self.lblPowered.place(x=460, y=470)
        
            #Product
            self.lblProduct = tk.Label(self.window, text="Product", fg='white', font=self.standardFontLbl, bg = 'black')
            self.lblProduct.place(x=6, y=10)
        
            self.comboProduct = ttk.Combobox(self.window, values=self.Products, font=self.standardFontEntry, state="readonly")                
            self.comboProduct.current(0)
            self.comboProduct.place(x=10, y=40)        
            
            #Activity
            self.lblActivity = tk.Label(self.window, text="Activity", fg='white', font=self.standardFontLbl, bg = 'black')
            self.lblActivity.place(x=176, y=10) 
        
            self.comboActivity = ttk.Combobox(self.window, values=self.Activities, font=self.standardFontEntry, state="readonly", width = 56)                
            self.comboActivity.current(0)
            self.comboActivity.place(x=180, y=40)    
            
            #Description
            self.lblDescription = tk.Label(self.window, text="Description", fg='white', font=self.standardFontLbl, bg = 'black')
            self.lblDescription.place(x=6, y=80) 
        
            self.txtDescription = tk.Entry(self.window, text="Description", bd=1, width = 96, font=self.standardFontEntry)
            self.txtDescription.place(x=10, y=110)
            self.txtDescription.delete(0, tk.END)
            self.txtDescription.insert(0,"")
            
            #Write
            self.btnWrite = tk.Button(self.window, text="Write", fg='black', font=self.standardFontEntry, command = self.btnWriteClick, width = 8)
            self.btnWrite.place(x=510, y=150)  
            
            #Data View            
            self.style = ttk.Style()
            self.style.theme_use('default') 
            self.style.configure("Treeview", background = "#D3D3D3", foreground="black", rowheight=25, fieldbackground = "#D3D3D3")
            self.style.map("Treeview", background = [('selected', '#347083')])
                        
            self.tree_frame = tk.Frame(self.window)            
            self.tree_frame.place(x=10, y=190)             
            
            self.tree_scroll = tk.Scrollbar(self.tree_frame)
            self.tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)            
            
            self.columns = ('Date', 'Product', 'Activity', 'Description')    
            
            self.DataTree = ttk.Treeview(self.tree_frame, columns=self.columns, show='headings', yscrollcommand=self.tree_scroll.set, selectmode = "extended")
            self.DataTree.pack()    
                      
            self.DataTree.heading('Date', text='Date')
            self.DataTree.heading('Product', text='Product')
            self.DataTree.heading('Activity', text='Activity')
            self.DataTree.heading('Description', text='Description')
            
            self.DataTree.column('Date', width = 140)
            self.DataTree.column('Product', width = 110)
            self.DataTree.column('Activity', width = 150)
            self.DataTree.column('Description', width = 160)
            
            self.DataTree.bind('<<TreeviewSelect>>', self.item_selected)
            
            self.LoadData()
            
            #Time
            self.timeStr = tk.StringVar()
            self.timeStr.set("Time: " + str(self.SecondsCount) + " second(s)")
            self.lblTime = tk.Label(self.window, textvariable = self.timeStr, fg='red', font=self.standardFontLbl, bg = 'black')
            self.lblTime.place(x=10, y=470)
            
            self.Clock = Timer(1.0, self.timeout)
            self.Clock.start()
            
        except Exception as e:
            print ("erro: " + str(e))
                
    def item_selected(self, event):
        for selected_item in self.DataTree.selection():
            item = self.DataTree.item(selected_item)
            record = item['values']
                        
            
            prd = self.Products.index(record[1])
            act = self.Activities.index(record[2])
            desc = record[3]
            
            self.comboProduct.current(prd)
            self.comboActivity.current(act)
            
            self.txtDescription.delete(0, tk.END)
            self.txtDescription.insert(0, desc)
            
            #print(record)
            # show a message
            #showinfo(title='Information', message=','.join(record))
            
    def ClearData(self):
        for row in self.DataTree.get_children():
            self.DataTree.delete(row)
            
    def WriteDate(self):
        date = datetime.now()
        date_f = date.strftime('%d/%m/%Y %H:%M:%S')
        
        d = {
                "Date": date_f,
                "Product": self.comboProduct.get(),
                "Activity": self.comboActivity.get(),
                "Description": self.txtDescription.get()
            }
        
        serie = pd.Series([d])
        NewDataFrame = self.DataFrame["Data"].append(serie, ignore_index=True)        
        
        out = "{\"Data\":\n" + (" " * 4)
        out += NewDataFrame.to_json(orient='records')[0:].replace("\"},{\"", "\"},\n\n" +  (" " * 4) + "{\"").replace("\",\"", "\",\n" +  (" " * 4) + "\"")
        out += "\n}"
        
        with open(self.dataPath, 'w') as f:
            f.write(out)
            
    def key_pressed(self, event):
        if (event.char == '\r'): #enter key
            self.btnWriteClick()
            
        if (event.char == '\x1b'): #esc key
            self.hide_window()
    
    def LoadData(self):
        def sort(e):
            return e[0]        
        
        self.ClearData()
        
        self.DataFrame = pd.read_json(self.dataPath)
        
        self.DataTable = [(x["Date"], x["Product"], x["Activity"], x["Description"]) for x in self.DataFrame["Data"]]
        self.DataTable.sort(key = sort, reverse = True)
            
        for t in self.DataTable:
            self.DataTree.insert('', tk.END, values = t)
            
        self.FocusLast()
            
    def FocusLast(self):
        if len(self.DataTable) > 0:
            child_id = self.DataTree.get_children()[0]
            self.DataTree.focus(child_id)
            self.DataTree.selection_set(child_id)
        
    def LoadConfig(self):
        try:
            df = pd.read_json(configPath)    
            self.Products = [prd.strip() for prd in df["Config"]["Products"].split(',')]
            self.Activities = [prd.strip() for prd in df["Config"]["Activities"].split(',')]
            self.TimeCycle = df["Config"]["Time (minutes)"] * 60
            self.SecondsCount = self.TimeCycle
        except:
            self.Products = ["Products empty"]
            self.Activities = ["Activities empty"]
            self.TimeCycle = 99999
            self.SecondsCount = self.TimeCycle
        
    # function for quit the window
    def quit_window(self, icon, item):
        icon.stop()
        self.Clock.cancel()
        self.window.destroy()
        
    # function to show the window again
    def show_window(self, icon, item):
        if (self.Visible == False):
            self.icon.stop()
            self.window.after(0, self.window.deiconify())        
            self.FocusLast()
            self.RecalcCenterScreen(600, 500)
            self.Visible = True
        
    # Hide the window and show on the system taskbar
    def hide_window(self):
        self.window.withdraw()
        
        image = Image.open(self.icoName)
        
        menu = (item('Report', self.show_window), item('Quit', self.quit_window))
        self.icon = pystray.Icon("name", image, "Barry - quick activity reports", menu)        
        self.Visible = False
        self.icon.run()          
        
    def RecalcCenterScreen(self, width, height):
        window_height = height
        window_width = width
        
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        x_cordinate = int((screen_width/2) - (window_width/2))
        y_cordinate = int((screen_height/2) - (window_height/2))
        
        self.window.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))
        
    def Start(self):       
        self.window.protocol('WM_DELETE_WINDOW', self.hide_window)
        self.window.mainloop()
        
    def btnWriteClick(self):
        self.WriteDate()
        self.LoadData()
        self.hide_window()
        
    def timeout(self):
        self.SecondsCount -= 1
        
        if (self.SecondsCount == 0):
            self.SecondsCount = self.TimeCycle 
            self.show_window(self.icon, 'foo')
            
        self.Clock.cancel()
        self.Clock = Timer(1.0, self.timeout)
        self.Clock.start()
        
        self.timeStr.set("Time: " + str(self.SecondsCount) + " second(s)")
        
form1 = FORM1()
form1.Start()       

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        