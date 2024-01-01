
##Selenium is being used to fully load the websites page by either scrolling or clicking a button
##BS4 is being used to look the html and pull the desired information
import time
import cs50
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as BS

db = cs50.SQL("sqlite:///shows.db")

##function to convert month names to #s
def Month2Num(Month):

    match Month[:3]:
        case "Jan":
            return '01'
        case "Feb":
            return '02'
        case "Mar":
            return '03'
        case "Apr":
            return '04'
        case "May":
            return '05'
        case "Jun":
            return '06'
        case "Jul":
            return '07'
        case "Aug":
            return '08'
        case "Sep":
            return '09'
        case "Oct":
            return '10'
        case "Nov":
            return '11'
        case "Dec":
            return '12'
        case _:
            return


def Scrape_Bowery():
    ##clear all data from previous scrape form Bowery
    db.execute("DELETE FROM Shows WHERE Data_Source='The Bowery Presents'")

    ##start bot/WebDriver to click load more button at bottom of webpage and wait for initial page load
    service = Service(executeable_path="chromedriver")
    driver = webdriver.Chrome(service=service)
    driver.get("https://www.bowerypresents.com/")
    time.sleep(4)

    ##find this anchor tag on the page and click the link until all pages load
    ##<a "="" class="button black btShowMore">Show more</a>
    ##except happens when button cannot be clicked any longer (or page does not load)
    try:
        while True: 
            link = driver.find_element(By.LINK_TEXT, "Show more")
            link.click()
            time.sleep(2)
    except: 
        print("Web page fully loaded")

    ## get page html 
    html = driver.page_source

    ## Parse page html into bs4 object
    soup = BS(html, 'html.parser')

    ##Each show on the website is wrapped by this div class
    ##<div class="show-info-container">
    ##Get all instances of div container
    html_just_shows = soup.find_all('div', class_="show-info-container")

    ##type cast new variable as a string to make it parable again so that we can make a new soup object for just the shows
    soup_shows = BS(str(html_just_shows),"html.parser")

    ##Separte each show container in a list.  Due to how the webpage is setup there are some spacing divs that need to be ignored    
    Show_List = []
    for element in soup_shows.div.next_siblings:
        if ((element != ", ") and (element != "]")):
            Show_List.append(element)

    ##Create variable that we will use to store a list of dictionaries.  Each dict will be a row of a table 
    Show_Table_Data = []

    for i,show in enumerate(Show_List):

        ##the first container is a featured artist in a display at the top of the page.  The same event is listed in the page normally. Skip the first container to avoid duplication of a record
        if i == 0:
            continue
        
        ##per iteration create soup object for each individual container
        soup_cur_show = BS(str(show),'html.parser')

        ##Create empty dictionary to store the row values
        cur_show_dict = {}

        #Traverse soup object picking out desired elements and loading them into the dictionary 
        Main_Event = soup_cur_show.find('span',itemprop="name").get_text().strip()
        cur_show_dict['Main_Event'] = Main_Event

        Supporting_Event = soup_cur_show.find('span',itemprop="performer").get_text().strip()
        cur_show_dict['Supporting_Event'] = Supporting_Event

        Venue = soup_cur_show.find('strong',itemprop="name").get_text().strip()
        cur_show_dict['Venue'] = Venue

        ##Split date and event time text into desired parts so that they can be reformatted
        Event_Date_Time_Long = soup_cur_show.find('p', class_="list-date").get_text().replace('"',"").strip().partition("|")
        Event_Date_Long = Event_Date_Time_Long[0].strip()
        Event_Date_Parts_ALL = Event_Date_Long.partition(",")
        Event_Date_Parts_MDY = Event_Date_Parts_ALL[2].partition(",")
        Event_Date_Parts_MD = Event_Date_Parts_MDY[0].strip().partition(" ")
        Event_Year = Event_Date_Parts_MDY[2].strip()
        Event_Month = Event_Date_Parts_MD[0]
        Event_Day = Event_Date_Parts_MD[2]
        Event_DOW = Event_Date_Parts_ALL[0]

        cur_show_dict['Event_Year'] = Event_Year
        cur_show_dict['Event_Month'] = Month2Num(Event_Month)
        cur_show_dict['Event_Day'] = Event_Day
        if len(Event_Day)<2:
            Event_Date = '0'+str(Event_Date)
        cur_show_dict['Event_DOW'] = Event_DOW
        cur_show_dict['Event_Date'] = str(Event_Year)+"-"+str(Month2Num(Event_Month))+"-"+str(Event_Day)
        Event_Time = Event_Date_Time_Long[2].strip()
        cur_show_dict['Event_Time'] = Event_Time

        State = soup_cur_show.find('meta',itemprop="addressRegion")['content'].strip()
        cur_show_dict['State'] = State

        City = soup_cur_show.find('meta',itemprop="addressLocality")['content'].strip()
        cur_show_dict['City'] = City  

        Address_Long = soup_cur_show.find('meta',itemprop="streetAddress")['content'].partition(",")
        Address = Address_Long[0].strip()
        cur_show_dict['Address'] = Address 

        ZIP_Code = soup_cur_show.find('meta',itemprop="postalCode")['content'].strip()
        cur_show_dict['ZIP_Code'] = ZIP_Code

        ##Add the dictionary for this show to the main show list
        Show_Table_Data.append(cur_show_dict)


    ##Load show list into SQLITE3 table so that the data is stored in permanent memory and can be called a will
    for show in Show_Table_Data:
        db.execute("INSERT INTO Shows (Main_Event,Supporting_Event,Venue,Event_Date,Event_Year,Event_Month,Event_Day,Event_DOW,Event_Time,State,City,Street_Address, ZIP,Data_Source) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            show["Main_Event"],
            show["Supporting_Event"],
            show["Venue"],
            show["Event_Date"],
            show["Event_Year"],
            show["Event_Month"],
            show["Event_Day"],
            show["Event_DOW"],
            show["Event_Time"],
            show["State"],
            show["City"],
            show["Address"],
            show["ZIP_Code"],
            "The Bowery Presents",
        )        
    
    ##turn off bot/WebDriver
    driver.quit()
    


def Scrape_Live_Nation():  
    ##clear all data from previous scrape form Live Nation
    db.execute("DELETE FROM Shows WHERE Data_Source='Live Nation'")

    ##start bot/WebDriver to continually scroll until the entire webpage is loaded and wait for initial page load
    service = Service(executeable_path="chromedriver")
    driver = webdriver.Chrome(service=service)
    driver.get("https://www.livenation.com/events?utm_source=lngifts&utm_medium=internal&utm_campaign=LNMP-internal-lngifts-main-subnav-events&type=upcoming&start=2024-01-01&end=2025-01-31")
    time.sleep(1)

    ##make web window wider for bot - The larger the page the more elements load at once
    driver.maximize_window()

    ##Disclaimer: I partially appropriated this scrolling loop from someone.  
    ##It makes the bot scroll to the bottom of the window and check if the window grew inside.  If it did I scroll down again, if it didn't it stops 
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    ## get page html 
    html = driver.page_source

    ## Parse page html into bs4 object
    soup = BS(html, 'html.parser')

    ##Each show on the website is wrapped by this div class
    html_just_shows = soup.find_all('div', class_="css-zzrm1w")

    soup_shows = BS(str(html_just_shows),"html.parser")

    Show_List = []

    for element in soup_shows.div.next_siblings:
        if ((element != ", ") and (element != "]")):
            Show_List.append(element)

    Show_Table_Data = []

    ##from this point forward, it is extremely similar to the scraping of the previous website.  There is less available data though.  
    ##I am getting the same information as I just am looking it up from different places compared to the previous website.
    for show in Show_List:

        soup_cur_show = BS(str(show),'html.parser')
        cur_show_dict = {}

        Main_Event = soup_cur_show.find('h3',class_="css-v0o9zs").get_text()
        cur_show_dict['Main_Event'] = Main_Event

        ##All Supporting act not separately listed in live nation data
        ##Supporting_Event = 
        ##cur_show_dict['Supporting_Event'] = 

        ven_city_state = soup_cur_show.find('p',class_="chakra-text css-qz18t2").get_text().partition("|")
        city_state = ven_city_state[2].partition(",") 
        Venue = ven_city_state[0].strip()
        cur_show_dict['Venue'] = Venue

        Event_Date_Time_Long = soup_cur_show.find_all('time',role="presentation")
        Event_Date_Time_Parts = Event_Date_Time_Long[1].get_text().partition(" ")
        Event_M_DYT = Event_Date_Time_Parts[2].partition(" ")
        Event_D_YT = Event_M_DYT[2].partition(",")
        Event_Y_T = Event_D_YT[2].strip().partition(" ")

        Event_Year = Event_Y_T[0].strip()
        Event_Month = Event_M_DYT[0].strip()
        Event_Day = Event_D_YT[0].strip()
        if len(Event_Day)<2:
            Event_Day = '0'+str(Event_Day)
        Event_DOW = Event_Date_Time_Parts[0].strip()

        cur_show_dict['Event_Year'] = Event_Year
        cur_show_dict['Event_Month'] = Month2Num(Event_Month)
        cur_show_dict['Event_Day'] = Event_Day
        cur_show_dict['Event_DOW'] = Event_DOW
        cur_show_dict['Event_Date'] = str(Event_Year)+"-"+str(Month2Num(Event_Month))+"-"+str(Event_Day)
        cur_show_dict['Event_Time'] = Event_Y_T[2].strip()

        State = city_state[2].strip()
        cur_show_dict['State'] = State

        City = city_state[0].strip()
        cur_show_dict['City'] = City  

        ##No Address Data on Live Nation Listings
        ##Address_Long = 
        ##Address = 
        ##cur_show_dict['Address'] = 

        ##No ZIP Data on Live Nation Listings
        ##ZIP_Code = 
        ##cur_show_dict['ZIP_Code'] = 

        Show_Table_Data.append(cur_show_dict)

    for show in Show_Table_Data:
            db.execute("INSERT INTO Shows (Main_Event,Venue,Event_Date,Event_Year,Event_Month,Event_Day,Event_DOW,Event_Time,State,City,Data_Source) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                show["Main_Event"],
                show["Venue"],
                show["Event_Date"],
                show["Event_Year"],
                show["Event_Month"],
                show["Event_Day"],
                show["Event_DOW"],
                show["Event_Time"],
                show["State"],
                show["City"],
                "Live Nation",
            )        
        
    driver.quit()


##If you want to manually run the scrapers uncomment the below two lines
##Scrape_Bowery()
##Scrape_Live_Nation()
