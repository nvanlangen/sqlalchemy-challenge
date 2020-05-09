# Import libraries
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from datetime import datetime

from flask import Flask, jsonify

# Connect to Database, Map Tables
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)

# Index Route - Displays URLs
@app.route("/")
def welcome():
    return (
        f"<center><strong>Welcome to the Climate API!<br><br/><hr><br />"
        f"Available Routes:</strong><br /><br />"
        f"/api/v1.0/precipitation<br /><br />"
        f"/api/v1.0/stations<br /><br />"
        f"/api/v1.0/tobs<br /><br />"
        f"/api/v1.0/YYYY-MM-DD<br /><br />"
        f"/api/v1.0/YYYY-MM-DD/YYYY-MM-DD<br /></center>"
    )

# Precipitation Route, Returns Avg Daily Precipitation for the last year of collected data
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data as json"""
    session = Session(engine)
    # Calculate the date 1 year ago from the last data point in the database
    max_date = session.query(func.max(Measurement.date)).first()
    min_date = str(int(max_date[0][0:4])-1) + max_date[0][4:10]

    # Perform a query to retrieve the date and precipitation scores
    precip_results = session.query(Measurement.date,func.avg(Measurement.prcp).label("prcp")).\
        filter(Measurement.date > min_date ).\
        group_by(Measurement.date).\
        order_by(Measurement.date).all()

    session.close()

    # Create a list and dictionary
    precipitation_data = []
    precip_dict = {}

    # Add a Result element to a temp dictionary and append dictionary to the list
    precip_dict["Result"] = "Daily Average Precipitation"
    precipitation_data.append(precip_dict)
    
    # Loop through each record returned
    for result in precip_results:
        # Add data to a temp dictionary and append dictionary to the list
        precip_dict = {}
        precip_dict["date"] = result.date
        precip_dict["prcp"] = result.prcp
        precipitation_data.append(precip_dict)

    # Return data as JSON
    return jsonify(precipitation_data)

# Stations Route, Returns information about each station
@app.route("/api/v1.0/stations")
def stations():
    """Return the station data as json"""
    session = Session(engine)

    # Perform a query to retrieve the station data
    station_results = session.query(Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation)

    session.close()

    # Add a Result element to a temp dictionary and append dictionary to the list
    station_data = []
    station_dict = {}
    station_dict["Result"] = "Station Information"
    station_data.append(station_dict)

    # Loop through each record returned
    for result in station_results:
        # Add data to a temp dictionary and append dictionary to the list
        station_dict = {}
        station_dict["station"] = result.station
        station_dict["name"] = result.name
        station_dict["latitude"] = result.latitude
        station_dict["longitude"] = result.longitude
        station_dict["elevation"] = result.elevation
        station_data.append(station_dict)

    # Return data as JSON
    return jsonify(station_data)

# TOBS Route, Returns temperature information for the last year of collected data from the station with the most observations
@app.route("/api/v1.0/tobs")
def tobs():
    """Return the temperature data as json"""
    session = Session(engine)

    # Perform a query to find the station with the most observations
    station_activity=session.query(Measurement.station,func.count(Measurement.station)).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).first()

    most_active_station = station_activity.station

    # Identify the date range to use
    max_date = session.query(func.max(Measurement.date)).first()
    min_date = str(int(max_date[0][0:4])-1) + max_date[0][4:10]

    # Perform a query to find the temperature for each date from the most active station
    tobs_results = session.query(Measurement.date,Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date > min_date).\
        order_by(Measurement.date)

    session.close()

    # Add a Result element to a temp dictionary and append dictionary to the list    
    tobs_data = []
    tobs_dict = {}
    tobs_dict["Result"] = "Temperature Observation for Station: " + most_active_station
    tobs_data.append(tobs_dict)

    # Loop through each record returned
    for result in tobs_results:
        # Add data to a temp dictionary and append dictionary to the list
        tobs_dict = {}
        tobs_dict["date"] = result.date
        tobs_dict["tobs"] = result.tobs
        tobs_data.append(tobs_dict)
        
    # Return data as JSON
    return jsonify(tobs_data)

# Start Date Route, Returns the Min, Max, and Avg temperature for every day starting with the date submitted through the last date that data was collected
@app.route("/api/v1.0/<start>")
def start_date(start):
    temp_stats = []

    # Validate that the date is a valid date 
    try:
        datetime.strptime(start, '%Y-%m-%d')
    except ValueError:
        # Invalid date - Add an error message to a dictionary, append the dictionary to a list and return as JSON
        temp_dict = {}
        temp_dict["Result"] = "Date is not valid"
        temp_stats.append(temp_dict)
        return jsonify(temp_stats)

    # Validate that the length of the date entered is 10. This is so the string can be compared to the values in the database.
    if (len(start) != 10):
        # Invalid date format- Add an error message to a dictionary, append the dictionary to a list and return as JSON
        temp_dict = {}
        temp_dict["Result"] = "Date is not in a valid format"
        temp_stats.append(temp_dict)
        return jsonify(temp_stats)

    session = Session(engine)

    # Perform a query to find the Min, Max, and Avg temperature for every date greater than or equal to the entered date
    temp_results = session.query(Measurement.date,func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        group_by(Measurement.date).\
        order_by(Measurement.date).all()

    session.close()

    # Get the number of records returned
    rec_count = len(temp_results)

    # If Records were found, add the data to the dictionary and list
    if rec_count > 0:
        temp_dict = {}
        temp_dict["Result"] = "Information is available from " + start
        temp_stats.append(temp_dict)

        for result in temp_results:
            temp_dict = {}
            temp_dict["date"] = result[0]
            temp_dict["TMIN"] = result[1]
            temp_dict["TAVG"] = result[3]
            temp_dict["TMAX"] = result[2]
            temp_stats.append(temp_dict)

    else:
        # No Records were found, add a no information found message to the dictionary and list
        temp_dict = {}
        temp_dict["Result"] = "No information is available from " + start
        temp_stats.append(temp_dict)

    # Return data as JSON
    return jsonify(temp_stats)

# Start and End Date Route, Returns the Min, Max, and Avg temperature for every day between the dates entered
@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start,end):
    temp_stats = []

    # Validate that both dates are valid 
    try:
        datetime.strptime(start, '%Y-%m-%d')
    except ValueError:
        # Invalid date - Add an error message to a dictionary, append the dictionary to a list and return as JSON
        temp_dict = {}
        temp_dict["Result"] = "Start Date is not valid"
        temp_stats.append(temp_dict)
        return jsonify(temp_stats)
    try:
        datetime.strptime(end, '%Y-%m-%d')
    except ValueError:
        # Invalid date - Add an error message to a dictionary, append the dictionary to a list and return as JSON
        temp_dict = {}
        temp_dict["Result"] = "End Date is not valid"
        temp_stats.append(temp_dict)
        return jsonify(temp_stats)

    # Validate that the length of both dates entered is 10. This is so the string can be compared to the values in the database.
    if (len(start) != 10 or len(end) != 10):
        # Invalid date format- Add an error message to a dictionary, append the dictionary to a list and return as JSON
        temp_dict = {}
        temp_dict["Result"] = "Start or End Date is not in a valid format"
        temp_stats.append(temp_dict)
        return jsonify(temp_stats)

    session = Session(engine)

    # Perform a query to find the Min, Max, and Avg temperature for every date in the range entered
    temp_results = session.query(Measurement.date,func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).\
        group_by(Measurement.date).\
        order_by(Measurement.date).all()

    session.close()

    # Get the number of records returned
    rec_count = len(temp_results)

    # If Records were found, add the data to the dictionary and list
    if rec_count > 0:
        temp_dict = {}
        temp_dict["Result"] = "Information is available from " + start + " to " + end
        temp_stats.append(temp_dict)

        for result in temp_results:
            temp_dict = {}
            temp_dict["date"] = result[0]
            temp_dict["TMIN"] = result[1]
            temp_dict["TAVG"] = result[3]
            temp_dict["TMAX"] = result[2]
            temp_stats.append(temp_dict)

    else:
        # No Records were found, add a no information found message to the dictionary and list
        temp_dict = {}
        temp_dict["Result"] = "No information is available from " + start + " to " + end
        temp_stats.append(temp_dict)

    # Return data as JSON
    return jsonify(temp_stats)

if __name__ == "__main__":
    app.run(debug=True)
