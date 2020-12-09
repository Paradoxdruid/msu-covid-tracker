#!/usr/bin/env python
# coding: utf-8

"""Module to grab underlying Tableu data values from a page with embedded Tableau output.

Examples:
    $ python update.py

"""

__version__ = "0.1"

# Built from https://stackoverflow.com/questions/62095206/how-to-scrape-a-public-tableau-dashboard

# imports
import requests
from bs4 import BeautifulSoup
import json
import re
import csv
from datetime import date

# import pandas as pd
# import plotly.graph_objects as go

#  and output filename
# URL: str = "https://public.tableau.com/views/COVIDTracker_16021924036240/Dashboard2"
URL: str = "https://public.tableau.com/views/COVIDTracker_16039090369530/Dashboard2"
"""Default url: MSU Denver COVID Dashboard"""

FILENAME: str = "./msu_covid.csv"
""""Default output filename"""

# URL options from embedded Tableau code:
# :embed=y&:showVizHome=no&:host_url=https%3A%2F%2Fpublic.tableau.com%2F&
# :embed_code_version=3&:tabs=no&:toolbar=no&:animate_transition=yes&
# :display_static_image=no&:display_spinner=no&:display_overlay=yes&:display_count=yes&
# :language=en&publish=yes&:loadOrderID=0


def main(url, filename):
    """Wrapper to retrieve data, write updated csv, and use it to write updated graph

    Args:
        url (str): url of Tableau dashboard to parse
        filename (str): output csv filename
    """
    get_data_process_and_write_csv(url, filename)
    # make_covid_graph(filename)
    return


def get_data_process_and_write_csv(url, filename):
    """Wrapper to run all module functions.

    Args:
        url (str): url of page with embedded Tableau display
        filename (str): output .csv file to which we will append data
    """
    url_data = get_tableau_url(url)
    data_url, data_dict = parse_tableau_config_return_data_url(url_data)
    values = parse_tableau_data(data_url, data_dict)
    values_with_date = prepend_date(values)
    write_to_csv(values_with_date, filename)
    return


def get_tableau_url(url):
    """Retrieve requests data from Tableau display page.

    Args:
        url (str): url of Tableau display page

    Returns:
        requests.Response: HTTP response from the site
    """
    # Pull the dashboard website
    r = requests.get(
        url,
        params={
            ":embed": "y",
            ":showVizHome": "no",
            ":embed_code_version": "3",
            ":tabs": "no",
            ":toolbar": "no",
            ":display_static_image": "yes",
            ":display_spinner": "no",
            ":display_overlay": "yes",
            ":display_count": "yes",
            ":language": "en",
            "publish": "yes",
            ":loadOrderID": "0",
        },
    )
    return r


def parse_tableau_config_return_data_url(request_data):
    """Grabs hidden text config options from response data, and uses them to generate
       a url to the actual Tableau data.

    Args:
        request_data (requests.Response): HTTP response from Tableau display page

    Returns:
        str: url to access underlaying Tableau data
    """
    # Parse and grab embedded Tableau data
    soup = BeautifulSoup(request_data.text, "html.parser")
    tableauData = json.loads(soup.find("textarea", {"id": "tsConfigContainer"}).text)
    sheet_id = tableauData["sheetId"]

    # Use that data to build a direct data access URL
    data_url = (
        f'https://public.tableau.com/{tableauData["vizql_root"]}/'
        f'bootstrapSession/sessions/{tableauData["sessionid"]}'
    )
    return data_url, sheet_id


def parse_tableau_data(url, sheetid):
    """Request HTTP response with underlaying Tableau data and extract primary values.

    Args:
        url (str): url to access underlaying Tableau data

    Returns:
        List[str]: list of Tableau data values
    """
    # Grab the data and parse it
    r2 = requests.post(
        url,
        data={"sheet_id": sheetid},
    )

    dataReg = re.search(r"\d+;({.*})\d+;({.*})", r2.text, re.MULTILINE)

    _ = json.loads(dataReg.group(1))
    data = json.loads(dataReg.group(2))

    finaldata = data["secondaryInfo"]["presModelMap"]["dataDictionary"][
        "presModelHolder"
    ]["genDataDictionaryPresModel"]["dataSegments"]["0"]["dataColumns"]

    final_values = finaldata[0]["dataValues"]
    final_values[0] += 80  # correction for data source change
    return final_values


def prepend_date(values):
    """Add current date to beginning of values list.

    Args:
        values (List[str]): list of Tableau data values

    Returns:
        List[str]: modified list of Tableau data values
    """
    # Add the date and write out daily values to a csv file, appending new data
    today = date.today()
    values.insert(0, today.strftime("%m/%d/%Y"))
    return values


def write_to_csv(values, filename):
    """Write Tableau data values to a simple csv file.

    Args:
        values (List[str]): list of Tableau data values
        filename (str): output filename
    """
    with open(filename, "a") as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(values)
    return


# def make_covid_graph(csv_filename):
#     """Create a dataframe from covid csv file and output a dated .png image.

#     Args:
#         css_filename (str): filename of .csv to process
#     """
#     df, date = read_covid_csv(csv_filename)
#     make_graph(df, date)
#     return


# def read_covid_csv(csv_filename):
#     """Read in a .csv file with covid case data and return a dataframe and current date.

#     Args:
#         csv_filename (str): filename of .csv to process

#     Returns:
#         Tuple[pd.DataFrame, str]: dataframe of .csv file info and string of current date.
#     """

#     df = pd.read_csv(csv_filename, header=0)
#     df["Date"] = pd.to_datetime(df["Date"])
#     date = df["Date"].iloc[-1].strftime("%Y_%m_%d")
#     return df, date


# def make_graph(df, date):
#     """Take in a dataframe and current date and write a pretty .png image.

#     Args:
#         df (pd.DataFrame): covid data dataframe
#         date (str): latest date in string format
#     """

#     fig = go.Figure()
#     fig.add_trace(
#         go.Scatter(
#             x=df["Date"],
#             y=df["Case"],
#             mode="lines+markers+text",
#             name="Total Cases",
#             text=df["Case"],
#             textposition="top center",
#         )
#     )
#     fig.add_trace(
#         go.Scatter(
#             x=df["Date"],
#             y=df["New"],
#             mode="lines+markers+text",
#             name="New Cases",
#             text=df["New"],
#             textposition="top center",
#         )
#     )

#     fig.update_layout(
#         title="COVID Cases at MSU Denver",
#         xaxis_title="Date",
#         yaxis_title="Cases",
#         template="ggplot2",
#         # color_discrete_sequence=colors.sequential.Rainbow_r,
#         #     height=500,
#         #     width=900,
#         legend=dict(orientation="v", yanchor="bottom", y=0.4, xanchor="right", x=1),
#     )

#     fig.update_xaxes(showline=True, linewidth=1, linecolor="black")
#     fig.update_yaxes(showline=True, linewidth=1, linecolor="black")

#     fig.update_xaxes(dtick="D1", tickformat="%b %d")

#     fig.write_image("./assets/msu_covid.png")
#     return


if __name__ == "__main__":
    main(URL, FILENAME)
