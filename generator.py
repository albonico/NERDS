import os, shutil, sys
import argparse

import pandas as pd
from jinja2 import Template, Environment, FileSystemLoader


class SiteGenerator:
    def __init__(self, df, timetable, temp):
        self.talks = df
        self.schedule = timetable
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
        with open("public/abstracts.html", "w+") as file:
            html = template.render(title="Abstracts", talks=self.talks)
            file.write(html)

    def render_main_page(self):
        print("Rendering main page to static file.")
        if temp:
            template = self.env.get_template("template_main_temp.html")
        else:
            template = self.env.get_template("template_main.html")
        with open("public/index.html", "w+") as file:
            html = template.render(title="Index", schedule=self.schedule)
            file.write(html)


if __name__ == "__main__":
    # Create the parser
    my_parser = argparse.ArgumentParser(description="Write html body")

    # Add the arguments
    my_parser.add_argument("Year", metavar="year", type=int, help="Select year")

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

    # Execute the parse_args() method
    args = my_parser.parse_args()

    timetable_data = args.tfile
    talks_data = args.datafile
    year = args.Year
    temp = args.Temp

    df = pd.read_csv(talks_data)

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

    grouped_by_day = timetable.groupby("day")
    timetable_by_day = [grouped_by_day.get_group(day) for day in grouped_by_day.groups]

    current = df[df["Year"] == year]

    SiteGenerator(current, timetable_by_day, temp)
