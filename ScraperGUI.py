"""Tkinter GUI for Python Web Scraper"""
 
import tkinter as tk
from tkinter import *
from tkinter import messagebox
import sys
import re
 
def create_gui():
    """Functon for creating the GUI"""
 
    #Initate tkinter windows class
    main_menu = tk.Tk()
 
    #Configures entire background window to be teal in color.
    main_menu.config(bg="#E3F2FD")
   
    #Create a greeting banner, pack it into the window.
    banner = tk.Label(text= "Welcome to our Python Web Scraper!", foreground="#B71C1C")
    banner.pack()
   
    ##Creates inner function.
    def get_url():
       
        #Before the tk.Entry(), we should have a box pop up with the URL entry field in it. Thoughts?
       
        #Create entry instance, pack into GUI.
        url_field = tk.Entry()
        url_field.pack()
   
        #Get the URL inputted by the user, store as a string.
        scrape_url = url_field.get()
 
        #Regex to confirm valid URL entry.
        reg_exp = "/((([A-Za-z]{3,9}:(?:\/\/)?)(?:[-;:&=\+\$,\w]+@)?[A-Za-z0-9.-]+|(?:www.|[-;:&=\+\$,\w]+@)[A-Za-z0-9.-]+)((?:\/[\+~%\/.\w-_]*)?\??(?:[-\+=&;%@.\w_]*)#?(?:[\w]*))?)/"
 
        #Check to confirm a matching URL against the above regex expression.
        if re.match(reg_exp, scrape_url):
           
            #Further logic will be developed as project evolves. Added this solely so the program runs without erroring.
            print("Valid URL presented. Scraping operation will proceed.")
   
        else:
            #Further logic will be developed as project evolves. Added this solely so the program runs without erroring.
            print("Invalid URL. Please try again or close the application. ")
   
   
    #Call BeautifulSoup functions after this to start scraping.
   
    #Search URL widget
    search_url_button = tk.Button(
       
        #Defines widget parameters.
        text = "Scrape URL",
        width = 20,
        height = 5,
        bg = "#00372E",
        fg = "#B71C1C",
        command = get_url
       
    )
   
    #Pack button
    search_url_button.pack()
   
    #Quit button widget
    quit_button = tk.Button(
       
        #Defines widget parameters.
        text = "Quit Program",
        width = 20,
        height = 5,
        bg = "#00372E",
        fg = "#B71C1C",
        command = quit_app
       
    )
   
    #Pack button into GUI.
    quit_button.pack()
   
    #Mainloop used to create the event loop. Must run for each window
    main_menu.mainloop()
 
   
 
def quit_app():
    """Quits application after quit button is clicked."""
   
    #We should probably add a quit message bow with Tkinter.
   
    sys.exit(0)
   
     
#Call main function
create_gui()