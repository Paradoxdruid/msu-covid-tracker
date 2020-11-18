# msu-covid-tracker

![gpl3.0](https://img.shields.io/github/license/Paradoxdruid/msu-covid-tracker.svg "GPL 3.0 Licensed")  [![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/Paradoxdruid/msu-covid-tracker.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/Paradoxdruid/academia-admin-automation/context:python)  [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black) 

## Description
Collects daily [MSU Denver covid dashboard](https://www.msudenver.edu/safe-return-to-campus/) data and publishes it in a plotly dash dashboard at:

**[msu-covid-tracker.herokuapp.com](msu-covid-tracker.herokuapp.com)**

## Workflow
This app relies on [Github actions](https://github.com/features/actions) to grab updated data, commit them to this repository, and then push those changes to dynamic python hosting on heroku.com.

## Authors
This script is developed as academic software by [Dr. Andrew J. Bonham](https://github.com/Paradoxdruid) at the [Metropolitan State University of Denver](https://www.msudenver.edu). It is licensed under the GPL v3.0.