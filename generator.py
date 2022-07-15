import os, shutil, sys
import argparse

from datetime import datetime, timedelta, time
from icalendar import Calendar, Event
from jinja2 import Template, Environment, FileSystemLoader
import re
import numpy as np
import pandas as pd


class SiteGenerator:
    def __init__(self, df, timetable, temp, orgdata):
        self.talks = df
        self.schedule = timetable
        self.org_data = orgdata
        self.temp = temp
        self.env = Environment(loader=FileSystemLoader("template"))
        self.empty_public()
        self.copy_static()
        self.render_main_page()
        self.render_abs_page()

    def empty_public(self):
        """Ensure the public directory is empty before generating."""
        try:
            shutil.rmtree("./public")
            os.mkdir("./public")
        except:
            print("Error cleaning up old files.")

    def copy_static(self):
        """Copy static assets to the public directory"""
        try:
            shutil.copytree("template/static", "public/static")
        except:
            print("Error copying static files.")

    def render_abs_page(self):
        print("Rendering abstract page to static file.")
        template = self.env.get_template("template_abs.html")
        with open("public/abstracts.html", "w+", encoding="utf-8") as file:
            html = template.render(Year=year, talks=self.talks)
            file.write(html)

    def render_main_page(self):
        print("Rendering main page to static file.")
        if temp:
            template = self.env.get_template("template_main_temp.html")
        else:
            template = self.env.get_template("template_main.html")
        with open("public/index.html", "w+", encoding="utf-8") as file:
            html = template.render(Year=year, schedule=self.schedule, org=self.org_data)
            file.write(html)


class CalGenerator:
    def __init__(self, caldata, orgdata):
        self.cal_data = caldata
        self.org_data = orgdata
        self.dates = [
            datetime.strptime(d, "%d.%m.%Y")
            for d in self.org_data["dates"].values[0].split(",")
        ]
        self.calendar = Calendar()
        self.create_events()
        self.produce_ics()

    def create_events(self):
        """Create icalendar events with information from pd.dataframes and add them to calendar"""
        for i, row in self.cal_data.iterrows():
            # Create an event for each talk and add its information
            e = Event()
            e.add("summary", row["text"])
            e.add("description", row["title"])
            e.add("dtstamp", datetime.now())

            # Read time from string entry
            event_time = re.search(r"(?P<h>\d+)(\.(?P<m>\d+))?", row["time"])

            # Add start end and location for the event
            e.add(
                "dtstart",
                datetime.combine(
                    self.dates[row["day"] - 1],
                    time(
                        hour=int(event_time.group("h")),
                        minute=int(event_time.group("m"))
                        if event_time.group("m")
                        else 0,
                    ),
                ),
            )
            e.add(
                "dtend",
                datetime.combine(
                    self.dates[row["day"] - 1],
                    time(
                        hour=int(event_time.group("h")),
                        minute=int(event_time.group("m"))
                        if event_time.group("m")
                        else 0,
                    ),
                )
                + timedelta(minutes=45),
            )
            e.add("location", self.org_data["location"])

            # Finally add event to calendar
            self.calendar.add_component(e)

    def produce_ics(self):
        """Generate ics file from calendar"""
        print('Generating "cal.ics" file')
        os.makedirs("downloads", exist_ok=True)
        with open("downloads/cal.ics", "wb") as file:
            file.write(self.calendar.to_ical())


if __name__ == "__main__":
    # Create the parser
    my_parser = argparse.ArgumentParser(description="Write html body")

    # ---------- Add the arguments ---------------
    # Year of the edition
    my_parser.add_argument("Year", metavar="year", type=int, help="Select year")

    # Wether the main page is in temporary version (call for abstracts) or final (timetable)
    my_parser.add_argument("Temp", metavar="temp", type=int, help="Temporary version")

    my_parser.add_argument(
        "--tfile",
        "-t",
        metavar="input_timetable_path",
        type=str,
        default="NerdsTimetable.csv",
        help='define name of input file for timetable i.e. "NerdsTimetable.csv"',
    )

    my_parser.add_argument(
        "--datafile",
        "-d",
        metavar="input_data_path",
        type=str,
        default="NerdsData.csv",
        help='define name of input file for talk data i.e. "NerdsData.csv"',
    )

    my_parser.add_argument(
        "--orgdatafile",
        "-o",
        metavar="input_org_data_path",
        type=str,
        default="NerdsOrganizational.csv",
        help='define name of input file for organizational data i.e. "NerdsOrganizational.csv"',
    )

    # Execute the parse_args() method
    args = my_parser.parse_args()

    # Assign parsed arguments to variables
    timetable_data = args.tfile
    talks_data = args.datafile
    o_data = args.orgdatafile
    year = args.Year
    temp = args.Temp

    # Read the three csv files into pandas dataframes
    df = pd.read_csv(talks_data)

    org_data = pd.read_csv(
        o_data,
        dtype={
            # TO DO check dtype for list of dates/strings
            "email": str,
            "location": str,
        },
        # Convert string containing organizer names into list of names
        converters={"organizers": lambda x: x[1:-1].split(",")},
    )

    timetable = pd.read_csv(
        timetable_data,
        dtype={
            "day": int,
            "size": str,
            "kind": str,
            "flip": int,
            "timed": int,
            "non_empty": int,
            "time": str,
            "text": str,
            "ref": str,
            "title": str,
        },
    )

    # Create list of dataframes, one for each day of the conference
    grouped_by_day = timetable.groupby("day")
    timetable_by_day = [grouped_by_day.get_group(day) for day in grouped_by_day.groups]

    # Select the abstracts for the current edition
    current = df[df["Year"] == year]

    # Select data for ics file
    cal_data = timetable[
        np.logical_and(timetable["kind"] == "speaker", timetable["time"].notna())
    ][["day", "time", "text", "title"]]

    # Write ics file
    CalGenerator(cal_data, org_data)

    # Generate the html files by rendering the templates
    SiteGenerator(current, timetable_by_day, temp, org_data)
