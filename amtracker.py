#!/usr/bin/env python
# Author: E.G. Galano
# Jan 13 2014

import argparse
from datetime import datetime
import sys

from bs4 import BeautifulSoup
import requests

DESTINATIONS = \
{
    "LAX": "Los Angeles - Union Station, CA (LAX)",
    "IRV": "Irvine, CA (IRV)"
}

def get_date_string(year, month, day):
    if len(str(year)) < 2:
        year = str(year).zfill(2)
    if len(str(month)) < 2:
        month = str(month).zfill(2)
    input_datetime = datetime.strptime("{}-{}-{}".format(year, month, day),
                                                         "{}-{}-{}".format("%Y" if len(str(year)) > 2 else "%y",
                                                                          "%m" if len(str(month)) == 2 else "%b",
                                                                          "%d"))
    output_datetime = input_datetime.strftime("%a, %b %d, %Y")
    return output_datetime

def get_amtrak_data(origin, dest, date_string, train_num="optional"):
    url = "http://tickets.amtrak.com/itd/amtrak"

    headers = {"Accept-Encoding": "gzip,deflate,sdhc",
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "text/html,application/xhtml+xml,application/xml",
                # Unused headers
                #"Origin": "http://tickets.amtrak.com",
                #"Host": "tickets.amtrak.com",
                #"Accept-Language": "en-US,en",
                #"Cache-Control": "max-age=0",
                #"Referer": "http://tickets.amtrak.com/itd/amtrak",
                #"Connection": "keep-alive"
                }

    payload = {"requestor": "amtrak.presentation.handler.page.AmtrakCMSNavigationTabPageHandler",
            "/sessionWorkflow/productWorkflow[@product='Rail']/tripRequirements/journeyRequirements[1]/departDate.date": date_string,
            "xwdf_trainNumber": "/sessionWorkflow/productWorkflow[@product='Rail']/tripRequirements/journeyRequirements[1]/segmentRequirements[1]/serviceCode",
            "wdf_trainNumber": train_num,
            "xwdf_origin": "/sessionWorkflow/productWorkflow[@product='Rail']/travelSelection/journeySelection[1]/departLocation/search",
            "wdf_origin": DESTINATIONS[origin.upper()],
            "xwdf_destination": "/sessionWorkflow/productWorkflow[@product='Rail']/travelSelection/journeySelection[1]/arriveLocation/search",
            "wdf_destination": DESTINATIONS[dest.upper()],
            "xwdf_SortBy": "/sessionWorkflow/productWorkflow[@product='Rail']/tripRequirements/journeyRequirements[1]/departDate/@radioSelect",
            "wdf_SortBy": "arrivalTime",
            "/sessionWorkflow/productWorkflow[@product='Rail']/tripRequirements/journeyRequirements[1]/departTime.hourmin": "",
            "_handler=amtrak.presentation.handler.request.rail.AmtrakRailTrainStatusSearchRequestHandler/_xpath=/sessionWorkflow/productWorkflow[@product='Rail']": "",
    # Not sure what these 2 params are for but they dont seem to be necessary
    #       "_handler=amtrak.presentation.handler.request.rail.AmtrakRailTrainStatusSearchRequestHandler/_xpath=/sessionWorkflow/productWorkflow[@product='Rail'].x": "23",
    #       "_handler=amtrak.presentation.handler.request.rail.AmtrakRailTrainStatusSearchRequestHandler/_xpath=/sessionWorkflow/productWorkflow[@product='Rail'].y": "12"
            }

    amtrak_response = requests.post(url, headers=headers, data=payload)
    amtrak_html = amtrak_response.text
    return amtrak_html

def parse_response(amtrak_html):
    soup = BeautifulSoup(amtrak_html)
    result_table = soup.find(id="status_results")
    try:
        pairs = result_table.find_all("tbody")
    except AttributeError:
        print("No train found with the supplied filters")
        sys.exit(1)
    trains = []
    for pair in pairs:
        first_train = {}
        second_train = {}

        rows = pair.find_all("tr", {"class": "status_result"})
        first = rows[0]
        first_train["route"] = first.find("div", {"class":"route_num"}).text
        first_train["name"] = first.find("div", {"class": "route_name"}).text
        first_train["city"] = first.find("td", {"class": "city"}).text.strip()
        first_train["action"] = set(set(first["class"]) & set(("departs", "arrives"))).pop()
        first_train["scheduled"] = first.find("td", {"class": "scheduled"})
        first_train["time"] = first_train["scheduled"].find("div", {"class": "time"}).text
        first_train["date"] = first_train["scheduled"].find("div", {"class": "date"}).text
        first_train["est"] = first.find("td", {"class", "act_est"})
        first_train["msg"] = first_train["est"].next_sibling.next_sibling.text.strip() # See sibling docs. Two sibs to skip the newline

        second = rows[1]
        second_train["name"] = first_train["name"]
        second_train["route"] = first_train["route"]
        second_train["city"] = second.find("td", {"class": "city"}).text.strip()
        second_train["action"] = set(set(second["class"]) & set(("departs", "arrives"))).pop()
        second_train["scheduled"] = second.find("td", {"class": "scheduled"})
        second_train["time"] = second_train["scheduled"].find("div", {"class": "time"}).text
        second_train["date"] = second_train["scheduled"].find("div", {"class": "date"}).text
        second_train["est"] = second.find("td", {"class", "act_est"})
        second_train["msg"] = second_train["est"].next_sibling.next_sibling.text.strip() # See sibling docs. Two sibs to skip the newline

        print()
        print("{name} - {route} - {action} from {city} at {time} - {date}\n{msg}".format(**first_train))
        print("".ljust(60,"-"))
        print("{name} - {route} - {action} from {city} at {time} - {date}\nNotes: {msg}".format(**second_train))
        print("".ljust(60,"-"))
        print()


def main():
    # The default parser and args
    now = datetime.now()
    parser = argparse.ArgumentParser(description= "Command-line access to the Amtrak train schedules and status page")

    parser.add_argument("-y", "--year", help="The year filter", type=str)
    parser.add_argument("-m", "--month", help="The month filter", type=str)
    parser.add_argument("-d", "--day", help="The day filter", type=str)
    parser.add_argument("-t", "--train", help="The train number for filtering results", type=str, default="optional")
    parser.add_argument("-o", "--origin", help="The train's origin (3-char code)", type=str, required=True)
    parser.add_argument("--dest", help="The train's destination (3-char code)", type=str, required=True)
    parser.add_argument( "-D", "--debug", help="Enable debug logging", action="store_true", required=False)

    args = parser.parse_args()

    date_string = get_date_string(now.year if not args.year else args.year, now.month if not args.month else args.month, now.day if not args.day else args.day)

    data = get_amtrak_data(args.origin, args.dest, date_string, args.train)
    if data:
        parse_response(data)


if __name__ == "__main__":
    main()
