# Import the dependencies.
import datetime as dt
import numpy as np 
import pandas as pandas 
import sqlalchemy 
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)
most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
# one_year_ago = most_recent_date - dt.timedelta(days=365)
one_year_ago = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)
#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#Define Routes
@app.route("/")
def homepage():
    """List all available routes."""
    routes = [
        ("/api/v1.0/precipitation", "Precipitation Analysis (Last 12 Months)"),
        ("/api/v1.0/stations", "List of Stations"),
        ("/api/v1.0/tobs", "Temperature Observations (Last 12 Months)"),
        ("/api/v1.0/<start>", "Temperature Statistics (Start Date)"),
        ("/api/v1.0/<start>/<end>", "Temperature Statistics (Date Range)")
    ]
    links_html = ""
    for route, description in routes:
        links_html += f'<a href="{route}" target="_blank">{description}</a><br/>'

    return f"Available Routes:<br/>{links_html}"

# Define the route for precipitation data.
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Convert the query results from precipitation analysis to a dictionary and return JSON."""
    # # Calculate the date one year from the last date in the data set
    one_year_ago = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)

    # Query to retrieve the last 12 months of precipitation data
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).\
        order_by(Measurement.date).all()

    # Convert the query results to a dictionary
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}

    return jsonify(precipitation_dict)

# Define the route for station data.
@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    # Query to retrieve the list of stations
    station_list = session.query(Station.station).all()

    # Convert the query results to a list
    stations = [station[0] for station in station_list]

    return jsonify(stations)

# Define the route for temperature observation data.
@app.route("/api/v1.0/tobs")
def tobs():
    """Query the dates and temperature observations of the most-active station for the previous year of data."""
    # Use the most active station ID from the previous query
    most_active_station_id = 'USC00519281'

    # Query to retrieve the last 12 months of temperature observation data for the most active station
    temperature_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station_id).\
        filter(Measurement.date >= one_year_ago).\
        order_by(Measurement.date).all()

    # Convert the query results to a list of dictionaries
    temperature_list = [{"Date": date, "Temperature": tobs} for date, tobs in temperature_data]

    return jsonify(temperature_list)

# Define the route for temperature statistics with a specified start date.
@app.route("/api/v1.0/<start>")
def temp_start(start):
    """Return a JSON list of the minimum, average, and maximum temperatures for a specified start date."""
    try:
        # Query to calculate TMIN, TAVG, and TMAX for all dates greater than or equal to the start date
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).all()

        # Convert the query results to a list of dictionaries
        temp_stats = [{"Min Temperature": results[0][0], "Average Temperature": results[0][1], "Max Temperature": results[0][2]}]

        return jsonify(temp_stats)
    except Exception as e:
        return jsonify({"error": str(e)})

# Define the route for temperature statistics with a specified date range.
@app.route("/api/v1.0/<start>/<end>")
def temp_start_end(start, end):
    """Return a JSON list of the minimum, average, and maximum temperatures for a specified date range."""
    try:
    # Query to calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive
        results = session.query(
            func.min(Measurement.tobs), 
            func.avg(Measurement.tobs), 
            func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).\
            filter(Measurement.date <= end).all()

        # Convert the query results to a list of dictionaries
        temp_stats = [{"Min Temperature": results[0][0], "Average Temperature": results[0][1], "Max Temperature": results[0][2]}]

        return jsonify(temp_stats)
    except Exception as e:
        return jsonify({"error": str(e)})

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)