from flask import Flask, jsonify

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

    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    """Return the station data as json"""

    return jsonify(station_data)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return the temperature data as json"""

    return jsonify(tobs_data)

if __name__ == "__main__":
    app.run(debug=True)
