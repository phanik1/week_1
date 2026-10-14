# Week 1: My First Data Pipeline

**Goal:** get live data from an API into a database, on your own machine, today.

## Run it (5 minutes)

1. Make sure Python 3 is installed: `python3 --version`
2. Put `pipeline.py` in a new folder, for example `de-project`
3. In that folder run:

```
python3 pipeline.py
```

You should see each city fetched, then a table of readings printed from the database.

4. Run it again a few minutes later. New observation times mean new rows. Same observation time means no duplicates (that's the idempotency part).

## Look inside the database

```
sqlite3 weather.db
```

Then try:

```sql
SELECT * FROM readings;
SELECT city, temperature_c FROM readings ORDER BY temperature_c DESC;
```

(If `sqlite3` isn't installed, use the free "DB Browser for SQLite" app and open `weather.db`.)

## What you just built

- **Extract:** `extract()` calls the Open-Meteo API
- **Transform:** `transform()` picks fields and shapes a row
- **Load:** `load()` writes into SQLite

That is ETL, the core of data engineering, in about 80 lines.

## Your Week 1 challenges (do them in order)

1. **Add your own cities** to the `CITIES` list and rerun.
2. **Add a new field.** Open-Meteo also has `precipitation` and `apparent_temperature`. Add one to the API URL, the transform, the table, and the print.
3. **Break it on purpose.** Put a wrong latitude like `999`. See what error you get and how the script survives it.
4. **Switch the API.** Pick one you care about (cricket scores, crypto prices, job postings, NASA data) and rebuild extract + transform for it.
5. **Push it to GitHub** with this README. Your first portfolio project.

## Next (Week 2)

SQL on the data you've collected: averages per city, hottest hour, changes over time. You will learn SQL by answering questions about your own data.
