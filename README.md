# Web Scraper For Concerts/Events In NYC & New York State
#### Video Demo:  <URL https://youtu.be/i9AUHpCABd4>
#### Description: Web scraper leveraging the Python libraries of Beautiful Soup and Selenium for data collection, Flask for data display (in conjunction with an HTML webpage), and a sqlite3 database for permanent memory storage

For my project I decided that I wanted to aggregate event information for concert venues located around New York City.  I live in North Jersey, and I frequently purchase tickets for concerts taking place in the various boroughs of NYC and beyond.  I currently use an app called Song Kick as well as Spotify to keep me up to date with what concerts are coming up.  Unfortunately, both of those sources have a bit of a delay in sending out information, so I sometimes miss the initial ticket sales and have to purchase them second hand at a higher price.  In order to combat this, I have been manually looking through the websites of the various entertainment groups in hopes of being tipped off a bit earlier.  I came to realize that the majority of the popular venues are controlled by 3 major companies/conglomerates.  Those being DICE FM, Live Nation, & The Bowery Presents.  

My original plan was to scrape information from all 3 sources and then load it together in a single database to compare everything at once.  Realistically at the beginning of the project I knew close to nothing about web scraping, so I was starting in a hole.  Since there seems to be a package for everything in Python, I thought it would be a good choice for a beginner.  After looking around for a bit, Beautiful Soup/BS4 seemed to be the right tool for the job. I pip installed the package and with some reading I got the main page of the Bowery website parsed into what I would call a soup object. I was happy...then I realized that the page only loads a couple of records at a time.  From there I spent several hours trying to figure out how to use BS4 to load more of the page, but I soon realized that it was incapable of doing that.  I was back to being stuck.

An hour or so later I came across a package called Selenium which, among other things, can autonomously manipulate webpages.  I tried reading the documentation and coding some things up, but I couldn't get anything to work.  Eventually I realized that I needed to separately install a WebDriver in order for it to do anything.  I got the driver working and eventually got the whole webpage loaded and parsed by beautiful soup.  In terms of the scraping there were not anymore hard roadblocks.  It was all trial and error from that point on.  The general gist of my web scraping function is as follows:

1. Initialize the Selenium WebDriver and load the webpage
2. Have the bot continually click the webpages show more button until it is fully loaded
3. Pass the html from the webpage into beautiful soup so that I can search using the built in functions
4. Separate the show containers from the rest of the webpage information. The show container essentially has all the information for each event nested within it.
5. Iterate over the current blob of data and append each instance of a container to its own unique spot in a list
6. Create an empty container that is going to house a list of dictionaries. Each dictionary will be a row of our soon to be show database.
7. Iterate over the list of containers.  For each container initialize an empty dictionary.  Use the BS4 html search features to find the relevant show data such as date, venue, and artist.  As the information is found add the key value pairs to the dictionary.  At the end of each loop append the dictionary to the Main Table data list.
8. After all the containers have been looped through load the rows into the preconfigured Sqlite3 database.

Next, I moved on to Live Nation.  Finding the right page to scrape was not as simple as the Bowery but after some searching, I found a similar page though it was more specified to a particular area.  As a side note, for the Bowery I pulled all their information because most of their venues are in the general tri-state area.  Live Nation’s venues are geographically dispersed over the US and as such I did not try to get everything for them.  Getting back on topic, the procedure was generally the same as the previous site but there were a few differences.  

1. As opposed to their being a load more button the page just "infinitely" loaded on scroll.  As such I had to change the script for the bot to scroll instead of click. 
2. This website did not have as much information as the Bowery.  For example, there was no address listed, there was no ZIP code listed, and the opening act was indiscernible from the main event.
3. New html searches had to be created to account for how their Html was written.

At this point scraping the 3rd website was going to be less about coding and more about sitting and analyzing the way their html was written so I opted to move on to the next part of the project.  Up to this point I was checking everything by passing it into a pandas data frame.  In the spirit of doing things just to try them I started creating a display of the data using html and Flask.  My Flask application was designed to do three things:

1. Provide an interface to trigger both web scraping functions without going through the command line.
2. Display a basic table of the important information regarding each event
3. Allow for a few filters to be applied to the data showing up in the table by using a couple of preset SQL statements.

The filter and web scraping were enabled through two separate forms and a series of if statements depending on which form was submitted.  I mainly checked if a forms variables were returned as None to verify which form was submitted and which fields were filled in.  Even though there is only a single html page it took me a long time to adjust all of the divs to be adequately positioned within the bootstrap grid.  It might not look like much now but it's an improvement to what it started off as. At the end of the day, everything works but I have a couple of things that I want to continue to improve on in the future.

1. After looking around at some of the data there are some instances of both companies supporting the same events so there are several duplicate events for certain venues.  I would like to build some validation into the initial data scrape so that I can prevent this type of double up.
2. Rather than trying to scrape the address and zip code information from the website itself it might be better to keep a secondary table where I look this information up off google based on the name of the venue.  This way there are no empty data fields.
3. As well as the information for DICE I’d like to pull some of the information for several of the small independent venues in the city.
4. I would like to make the information more interactive by bringing in links to the ticketing webpages as well as images for each record.  I don't want to be too overzealous with the ticketing websites though, they are known for banning IPs if they suspect that you are using a bot to navigate.
5. If other sites that I incorporate in the future mix the main act with the supporting act  within the data lines then I am going to remove the additional column and present the everything together.

