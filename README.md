# NERDS

Generator.py is a program that can be used to produce html files for the website of the NERDS Conference held yearly within students of the Mathematical Physics group at the MI in Oxford. The program uses jinja2 templates for both the main page and the abstract page. The repository contains:

- template : a folder containing the templates for the html pages as well as css files

- NerdsData.csv, NerdsOrganizational.csv and NerdsTimetable.csv : data to appear on the website

- generator.py : the python program that renders the jinja2 templates into html files using the data from the csv files. It also generate the ics file.

- public : the folder containing the output of the python program, i.e. the html and css files necessary to produce the website

## How to use the program

To run the programm, you only need to ensure you have python 3.4 or above installed on your computer. Ideally you should run the programm in a virtual environment, which is activated on OS and Linux as follows:

```
python3 -m venv ./myvenv
source myvenv/bin/activate
```

Either in the virtual environment or on your computer, install the required packages via:

```
pip3 install -r requirements.txt
```

Then run the generator.py script to produce the html files (as detailed further down)

```
python3 generator.py [-h] year temp [-t timetable-path] [-d data-path] [-o org-path]
```

If you're using venv, don't forget to deactivate and delete the environment:

```
deactivate
rm -r myvenv
```

## Talks data

Every year, the "database" of talks should be updated with the new submissions. This data is contained in the file "NerdsData.csv" and structured as follows:

- Id : of the form "{name}{year}", it is used as the reference id of the abstract from the timetable

- Speaker : (first) name of the speaker

- Title : title of the talk

- Keywords : this entry should be a list of strings containing keywords for the talk (the main purpose of this entry is future analysis)

- Year : edition of the conference (in case of several editions in one year, use "year_n")

- Abstract : text of the abstract


## Timetable

The timetable data should be in a csv file (e.g. "NerdsTimetable.csv") which should be compiled yearly. The data should be entered in a sheet of the format provided, where the columns stand for the following:

- day : numbers days of conference

- defsize : setsize or setsize-double for single or double height

- kind : date or speaker (date is for smaller font: day, breaks)

- flip : wether the slot should flip when hovering

- timed : wether the slot has a time <span>  

- non_empty : wether the slot has a text <span>

- text : the description appearing in the text <span>

- ref : aref to abstract in abstracts page

- title : title of the talk on the back of the flip card

- month : int(month)

- date : int(day)

- location : str(room)

## Organizational data

The organizational data is cast in a csv file containing:

- email : email address to contact organizers

- location : where the talks will be held

- dates : dates of the talks in format dd.mm.yyyy


### Temporary page

Before the speakers have submitted their topics, there is the option to generate a temporary main page with an empty table and a call for abstracts.

## Generator.py

```
python3 generator.py [-h] year temp [-t timetable-path] [-d data-path] [-o org-path]
```

The required arguments are:

- year : the year of the current edition to be displayed on the website

- temp : wether you wish to generate the temporary page (1) or the timetable (0)

The optional arguments are :

- timetable-path : the path to the csv file containing the timetable (default: 'NerdsTimetable.csv'). If you're generating the temporary page, this should be 'EmptyTimetable.csv'

- data-path : the path to the csv file containing the details of the talks (default: 'NerdsData.csv').

- org-path : the path to the csv file containing the organizational info (default: 'NerdsOrganizational.csv').

