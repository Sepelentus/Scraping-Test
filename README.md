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

### /process (POST)

This endpoint receives a text input, processes it using an AI model (summarization), and returns the summarized result in JSON Format

IF USING POSTMAN, YOU NEED TO TYPE THE INPUT TEXT ON THE BODY (raw)
```
{
    "text": "your-text-here"
}
```
> Postman: http://127.0.0.1:5000/process

IF USING CURL, USE THIS (CHANGE "your-text-here" to the desired input text)

> curl: curl -X POST http://127.0.0.1:5000/process -H "Content-Type: application/json" -d '{"text":"your-text-here"}'

Example of JSON Response (success):
```
Input:
{
    "text": "El equipo Red Bull de Fórmula 1 anunció que Sergio Checo Pérez no correrá con ellos en la temporada 2025, pero seguirá en el equipo en un rol menos protagónico, lejos de las competencias de la F1. Christian Horner, jefe de equipo, mencionó que Pérez participará en algunos eventos como show runs. Esta decisión se tomó debido a la presión y expectativas que enfrentaba el piloto mexicano cada fin de semana. Liam Lawson será el nuevo compañero de Max Verstappen en Red Bull para la Fórmula 1 2025. "
}
```

```
Output:
{
    "status": "success",
    "summary": "Sergio Checo Pérez no correrá con Red Bull en la temporada 2025 . El piloto mexicano permanecerá en el equipo en un papel menos importante lejos de las competiciones F1. Liam Lawson será el nuevo socio de Max Verstappen en Red Bull para F1 2025 ."
}

```

### /combined (POST)

This endpoint integrates both scraping and text processing. It scrapes the content from the provided URL, processes the scraped text using the AI Model and returns the original scraped text along with its summary in JSON Format

IF USING POSTMAN, YOU NEED TO TYPE THE URL THIS WAY ON THE BODY (raw)
```
{
    "url": "your-url-here"
}
```
> Postman: http://127.0.0.1:5000/combined

IF USING CURL, USE THIS (CHANGE "your-url-here" to the desired URL):
> curl: curl -X POST http://127.0.0.1:5000/combined -H "Content-Type: application/json" -d '{"url":"your-url-here"}'

EXAMPLE OF JSON Response (success):
```
INPUT:
{
    "url": "https://www.villalemana.cl/2024/12/municipalidad-de-villa-alemana-reconoce-la-labor-de-carabineros-con-emotiva-jornada-navidena/"
}
```
```
OUTPUT:
{
    "original_text": "Ley del Lobby Ley de Transparencia Ley de Transparencia Comparte esta Noticia En una cálida muestra de agradecimiento y unión,el Municipio de Villa Alemana reconoció la destacada labor de Carabineros de la Sexta Comisaria,en una ceremonia llena de emotividad y espíritu navideño. El evento, realizado en las afueras de la unidad policial, contó con la participación de un coro de villancicos quienes deleitaron a los presentes con un repertorio cargado de alegría y esperanza. Durante la ceremonia, el alcalde de Villa Alemana, Nelson Estay, reafirmó su compromisode seguir generando instancias que promuevan el reconocimiento y colaboración entre instituciones.‘’Carabineros cumple una ardua labor de resguardo y seguridad con todos nosotros. Este es un momento único, no se había realizado nunca y es un reconocimiento en estas fiestas tan importantes para el mundo cristiano.’’",
    "status": "success",
    "summary": "La Municipalidad de Villa Alemana reconoció la destacada labor de Carabineros del Sexto Comisionado. Un coro de villancicos encantó a los presentes con un repertorio lleno de alegría y esperanza. Carabineros lleva a cabo una ardua tarea de salvaguardia y seguridad con todos nosotros. Villa Alemana, Nelson Estay, reafirmó su compromiso de seguir generando instancias que promuevan el reconocimiento y la colaboración entre las instituciones."
}
```
