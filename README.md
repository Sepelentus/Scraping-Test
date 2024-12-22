# Scraping-Test
This is a project for a technical test that requires scraping from web pages.

# INSTALL AND USE GUIDE:

## Setup venv

Use venv for the python installs

> python venv venv/

If it doesnt work use -m parameter

> py -m venv venv/

## Install requirements

Activate your venv environment using the command

> cmd>venv/Scripts/activate

If it doesn't work, just use cd to move on the folders and type activate when you reach inside the Scripts folder

## Run Scrapper

Once you have the required installs, just start the server with this command

> python scrapper.py

This will start the server, allowing to use the endpoints.

## How to use

The endpoints work via URL, so open a program like Postman (or use curl) and use the endpoints this way:

### /scrape (POST)
IF USING POSTMAN, YOU NEED TO TYPE THE URL THIS WAY ON THE BODY (raw)
```
{
    "url": "your-url-here"
}
```
> Postman: http://127.0.0.1:5000/scrape
IF USING CURL, USE THIS (CHANGE THE URL TO THE DESIRED ONE)
> curl: curl -X POST http://127.0.0.1:5000/scrape -H "Content-Type: application/json" -d '{"url":"your-url-here"}'
