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

# import csv
from datetime import date
import boto3
import os
import io
from botocore.exceptions import ClientError


# Amazon S3 constants
BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME")
OBJECT_NAME = "msu_covid.csv"


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
    current_data = read_current_s3()
    final_data = append_new_data(current_data, values_with_date)
    save_to_s3(final_data)


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
    r2 = requests.post(url, data={"sheet_id": sheetid},)

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


# def write_to_csv(values, filename):
#     """Write Tableau data values to a simple csv file.

#     Args:
#         values (List[str]): list of Tableau data values
#         filename (str): output filename
#     """
#     with open(filename, "a") as file:
#         csv_writer = csv.writer(file)
#         csv_writer.writerow(values)


def read_current_s3():
    """Retrieve latest covid data from Amazon s3 bucket and process as a csv fileobject.

    Returns:
        io.String: string object of covid data
    """
    s3_client = boto3.client("s3")
    bytes_buffer = io.BytesIO()

    s3_client.download_fileobj(
        Bucket=BUCKET_NAME, Key=OBJECT_NAME, Fileobj=bytes_buffer
    )
    byte_value = bytes_buffer.getvalue()
    str_value = byte_value.decode()
    return io.StringIO(str_value)


def save_to_s3(final_data):
    """Upload a file to an S3 bucket.

    Args:
        final_data: string fileobject of final data

    Returns:
        True if file was uploaded, else False
    """

    s3_client = boto3.client("s3")
    try:
        _ = s3_client.put_object(
            Bucket=BUCKET_NAME, Key=OBJECT_NAME, Body=final_data.getvalue()
        )
    except ClientError as e:
        print(e)
        return False
    return True


def append_new_data(current_data, values):
    """Write Tableau data values to a simple csv fileobject.

    Args:
        current_data: output fileobject
        values (List[str]): list of Tableau data values
    """
    string_to_write = ",".join(values) + "\n"
    current_data.seek(0, 2)
    current_data.write(string_to_write)
    current_data.seek(0)
    return current_data


if __name__ == "__main__":
    main(URL, FILENAME)
