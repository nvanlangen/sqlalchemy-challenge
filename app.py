import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from datetime import datetime

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)

@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/YYYY-MM-DD<br/>"
        f"/api/v1.0/YYYY-MM-DD/YYYY-MM-DD<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data as json"""
    session = Session(engine)
    # Calculate the date 1 year ago from the last data point in the database
    max_date = session.query(func.max(Measurement.date)).first()
    min_date = str(int(str(max_date[0])[0:4])-1) + str(max_date[0])[4:10]

    # Perform a query to retrieve the data and precipitation scores
    precip_results = session.query(Measurement.date,func.avg(Measurement.prcp).label("prcp")).\
        filter(Measurement.date > min_date ).\
        group_by(Measurement.date).\
        order_by(Measurement.date).all()

    session.close()
    precipitation_data = []
    precip_dict = {}
    precip_dict["Result"] = "Daily Average Precipitation"
    precipitation_data.append(precip_dict)
    
    for result in precip_results:
        precip_dict = {}
        precip_dict["date"] = result.date
        precip_dict["prcp"] = result.prcp
        precipitation_data.append(precip_dict)

    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    """Return the station data as json"""
    session = Session(engine)
    station_results = session.query(Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation)

    session.close()
    station_data = []
    station_dict = {}
    station_dict["Result"] = "Station Information"
    station_data.append(station_dict)

    for result in station_results:
        station_dict = {}
        station_dict["station"] = result.station
        station_dict["name"] = result.name
        station_dict["latitude"] = result.latitude
        station_dict["longitude"] = result.longitude
        station_dict["elevation"] = result.elevation
        station_data.append(station_dict)

    return jsonify(station_data)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return the temperature data as json"""
    session = Session(engine)
    station_activity=session.query(Measurement.station,func.count(Measurement.station)).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).first()

    most_active_station = station_activity.station

    max_date = session.query(func.max(Measurement.date)).first()
    min_date = str(int(str(max_date[0])[0:4])-1) + str(max_date[0])[4:10]

    tobs_results = session.query(Measurement.date,Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date > min_date).\
        order_by(Measurement.date)

    session.close()
    tobs_data = []
    tobs_dict = {}
    tobs_dict["Result"] = "Temperature Observation for Station: " + most_active_station
    tobs_data.append(tobs_dict)

    for result in tobs_results:
        tobs_dict = {}
        tobs_dict["date"] = result.date
        tobs_dict["tobs"] = result.tobs
        tobs_data.append(tobs_dict)
        
    return jsonify(tobs_data)

@app.route("/api/v1.0/<start>")
def start_date(start):
    temp_stats = []
    try:
        datetime.strptime(start, '%Y-%m-%d')
    except ValueError:
        temp_dict = {}
        temp_dict["Error"] = "Date is not in a valid format"
        temp_stats.append(temp_dict)
        return jsonify(temp_stats)

    if (len(start) != 10):
        temp_dict = {}
        temp_dict["Error"] = "Date is not in a valid format"
        temp_stats.append(temp_dict)
        return jsonify(temp_stats)

    session = Session(engine)
    temp_results = session.query(Measurement.date,func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        group_by(Measurement.date).\
        order_by(Measurement.date).all()

    session.close()
    rec_count = len(temp_results)
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
        temp_dict = {}
        temp_dict["Result"] = "No information is available from " + start
        temp_stats.append(temp_dict)

    return jsonify(temp_stats)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start,end):
    temp_stats = []
    try:
        datetime.strptime(start, '%Y-%m-%d')
    except ValueError:
        temp_dict = {}
        temp_dict["Result"] = "Date is not in a valid format"
        temp_stats.append(temp_dict)
        return jsonify(temp_stats)
    try:
        datetime.strptime(end, '%Y-%m-%d')
    except ValueError:
        temp_dict = {}
        temp_dict["Result"] = "Date is not in a valid format"
        temp_stats.append(temp_dict)
        return jsonify(temp_stats)

    if (len(start) != 10 or len(end) != 10):
        temp_dict = {}
        temp_dict["Result"] = "Date is not in a valid format"
        temp_stats.append(temp_dict)
        return jsonify(temp_stats)

    session = Session(engine)
    temp_results = session.query(Measurement.date,func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).\
        group_by(Measurement.date).\
        order_by(Measurement.date).all()

    session.close()
    rec_count = len(temp_results)
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
        temp_dict = {}
        temp_dict["Result"] = "No information is available from " + start + " to " + end
        temp_stats.append(temp_dict)

    return jsonify(temp_stats)

if __name__ == "__main__":
    app.run(debug=True)
