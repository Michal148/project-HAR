import dash
from dash.dependencies import Output, Input
from dash import dcc, html
from datetime import datetime
import json
import plotly.graph_objs as go
from collections import deque
from flask import Flask, request
import pyodbc

#fill in tcp address, database and credentials; can be retrieved at azure website
cnxn = pyodbc.connect("Driver={ODBC Driver 17 for SQL Server};Server=tcp:,1433;Database=;Uid=;Pwd=;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;")
cursor = cnxn.cursor()

server = Flask(__name__)
app = dash.Dash(__name__, server=server)

MAX_DATA_POINTS = 1000
UPDATE_FREQ_MS = 100

time = deque(maxlen=MAX_DATA_POINTS)
accel_x = deque(maxlen=MAX_DATA_POINTS)
accel_y = deque(maxlen=MAX_DATA_POINTS)
accel_z = deque(maxlen=MAX_DATA_POINTS)

app.layout = html.Div(
	[
		dcc.Markdown(
			children="""
			# Live Sensor Readings
			Streamed from Sensor Logger: tszheichoi.com/sensorlogger
		"""
		),
		dcc.Graph(id="live_graph"),
		dcc.Interval(id="counter", interval=UPDATE_FREQ_MS),
	]
)


@app.callback(Output("live_graph", "figure"), Input("counter", "n_intervals"))
def update_graph(_counter):
	data = [
		go.Scatter(x=list(time), y=list(d), name=name)
		for d, name in zip([accel_x, accel_y, accel_z], ["X", "Y", "Z"])
	]

	graph = {
		"data": data,
		"layout": go.Layout(
			{
				"xaxis": {"type": "date"},
				"yaxis": {"title": "Acceleration ms<sup>-2</sup>"},
			}
		),
	}
	if (
		len(time) > 0
	):  #  cannot adjust plot ranges until there is at least one data point
		graph["layout"]["xaxis"]["range"] = [min(time), max(time)]
		graph["layout"]["yaxis"]["range"] = [
			min(accel_x + accel_y + accel_z),
			max(accel_x + accel_y + accel_z),
		]

	return graph


@server.route("/data", methods=["POST"])
def data():  # listens to the data streamed from the sensor logger
	if str(request.method) == "POST":
		data = json.loads(request.data)
		for d in data['payload']:
			if (
				d.get("name", None) == "accelerometer"
			):  #  modify to access different sensors
				ts = datetime.fromtimestamp(d["time"] / 1000000000)
				if len(time) == 0 or ts > time[-1]:
					time.append(ts)
					# modify the following based on which sensor is accessed, log the raw json for guidance
					accel_x.append(d["values"]["x"])
					accel_y.append(d["values"]["y"])
					accel_z.append(d["values"]["z"])
					x_ac = float(d["values"]["x"])
					y_ac = float(d["values"]["y"])
					z_ac = float(d["values"]["z"])

			if (
				d.get("name", None) == "gyroscope"
			):  # data just for streaming to db
				ts = datetime.fromtimestamp(d["time"] / 1000000000)
				if len(time) == 0 or ts > time[-1]:
					x_gyr = float(d["values"]["x"])
					y_gyr = float(d["values"]["y"])
					z_gyr = float(d["values"]["z"])

			if (
				d.get("name", None) == "magnetometer"
			):  # data just for streaming to db
				ts = datetime.fromtimestamp(d["time"] / 1000000000)
				if len(time) == 0 or ts > time[-1]:
					x_mag = float(d["values"]["x"])
					y_mag = float(d["values"]["y"])
					z_mag = float(d["values"]["z"])

		#edit table name/columns for streaming workload
		query = f"INSERT INTO [dbo].[test] (x_ac, y_ac, z_ac, x_gyr, y_gyr, z_gyr, x_mag, y_mag, z_mag) VALUES ({x_ac}, {y_ac}, {z_ac}, " \
				f"{x_gyr}, {y_gyr}, {z_gyr}, {x_mag}, {y_mag}, {z_mag})"
		#print(query)
		cursor.execute(query)
		cnxn.commit()
	return "success"


if __name__ == "__main__":
	app.run_server(port=8000, host="0.0.0.0")
