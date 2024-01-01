import cs50
from flask import Flask, render_template, request
from scraper import Scrape_Bowery,Scrape_Live_Nation

app = Flask(__name__)

db = cs50.SQL("sqlite:///shows.db")

##load data from sqlite3 on launch
All_Show_Data = db.execute("SELECT * FROM Shows WHERE State = 'NY' AND Event_Date >= '2023-12-01' ORDER BY Event_Date")
Unique_Venues_NY = db.execute("SELECT DISTINCT(Venue) AS 'Venues' FROM Shows WHERE State = 'NY' ORDER BY Venue")

@app.route("/", methods=["GET", "POST"])
def main_page():
    if request.method == "POST":
        ##There are two submission forms of the webpage being used to display the information
        ##One is used to call each web scraper if you want updated information
        ##Calling the scraper will delete all of the previous information in the database and replace it with the new data
        ##the other is used to filter the and return data from the sqlite3 database

        ##radio yes for rescrape of Bowery data
        if(request.form.get("Bow") == "Yes"):
            Scrape_Bowery()

        ##radio yes for rescrape of Live Nation data
        if(request.form.get("Live") == "Yes"):
            Scrape_Live_Nation()

        ##If the form for the scraper is not called, checking for its inputs will return None
        ##In this case the filter form must have been called
        if(request.form.get("Bow") == None):
            ##There are 4 different filters:
            ##1. Artist - A typed field that searches if a text string is contained anywhere in the event names stored in either the Main or Supporting Events columns
            ##   If nothing is entered for this field the filter will lookup all artists/events
            ##2. Venue - A progenerated list of all of the venues in the database that are in NY state.  You can filter on one at a time
            ##   If nothing is entered for this field all venues will be show 
            ##3. & 4. From Date/To Date - This will show any dates between the specified ranges.  
            ##   If nothing is entered for From it will default to 12/1/23.
            ##   If nothing is entered for To it will default to 12/31/29.
            if (request.form.get("Artist") != None):
                Artist_Filter = request.form.get("Artist")
            else:
                Artist_Filter = ""

            Venue_Filter = request.form.get("Venue")

            if ((request.form.get("From Date") != "") and (request.form.get("From Date") != None)) :
                print("why")
                From_Date_Filter = request.form.get("From Date")
            else:
                From_Date_Filter = "2023-12-01"

            if ((request.form.get("To Date") != "") and (request.form.get("To Date") != None)):
                print("why")
                To_Date_Filter = request.form.get("To Date")
            else:
                To_Date_Filter = "2029-12-31"

            if (Venue_Filter != None):
                Current_Data = db.execute("SELECT * FROM Shows WHERE State = 'NY' AND (Main_Event LIKE ? OR Supporting_Event LIKE ?) AND Venue = ? AND Event_Date >= ? AND Event_Date <= ? ORDER BY Event_Date","%"+Artist_Filter+"%","%"+Artist_Filter+"%", Venue_Filter,From_Date_Filter,To_Date_Filter)
            else:
                Current_Data = db.execute("SELECT * FROM Shows WHERE State = 'NY' AND (Main_Event LIKE ? OR Supporting_Event LIKE ?) AND Event_Date >= ? AND Event_Date <= ? ORDER BY Event_Date","%"+Artist_Filter+"%","%"+Artist_Filter+"%",From_Date_Filter,To_Date_Filter)
        else:
            Current_Data = db.execute("SELECT * FROM Shows WHERE State = 'NY' ORDER BY Event_Date")       

    #Intial load and refresh of page will default data back to starting state       
    if request.method == "GET":    
        Current_Data = db.execute("SELECT * FROM Shows WHERE State = 'NY' AND Event_Date >= '2023-12-01' ORDER BY Event_Date")

    return render_template("index.html", Show_Data=Current_Data,Uni_Venues=Unique_Venues_NY)
    