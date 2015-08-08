import os
import yaml
import pymongo
import datetime
from flask import Flask, redirect
from flask_restful import Resource, Api, abort, reqparse

app = Flask(__name__)
api = Api(app)

config = None
with open("/etc/l2-sensors/conf.yml", 'r') as f:
    config = yaml.load(f.read())
if config is None:
    raise ValueError("Failed to load configuration.")

client = pymongo.MongoClient(
    os.environ['DB_PORT_27017_TCP_ADDR'],
    int(os.environ['DB_PORT_27017_TCP_PORT']),
    
)
client.particule.authenticate(config['db']['mongo']['username'], config['db']['mongo']['password'])

db = client.particule

@app.route("/")
def index():
    return """
<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8">
    <title>Temperature, pressure and humidity at level2</title>
    <script type='text/javascript' src='//code.jquery.com/jquery-1.9.1.js'></script>
    <script src="//code.highcharts.com/stock/highstock.js"></script>
    <script src="//code.highcharts.com/stock/modules/exporting.js"></script>
    <script type='text/javascript'>//<![CDATA[

$(function () {

    $.getJSON('/temperature', function (data) {
        var newdata = []
        for(var i in data['data']){
            var date = new Date(data['data'][i]['date']);
            newdata.push([date.getTime(), data['data'][i]['value']])
        }
        // Create the chart
        $('#container').highcharts('StockChart', {


            rangeSelector : {
                selected : 1
            },

            title : {
                text : 'Temperature °C'
            },

            series : [{
                name : 'Temperature',
                data : newdata,
                tooltip: {
                    valueDecimals: 2
                }
            }]
        });
    });

});

$(function () {

    $.getJSON('/pressure', function (data) {
        var newdata = []
        for(var i in data['data']){
            var date = new Date(data['data'][i]['date']);
            newdata.push([date.getTime(), data['data'][i]['value']])
        }
        // Create the chart
        $('#containerPressure').highcharts('StockChart', {


            rangeSelector : {
                selected : 1
            },

            title : {
                text : 'Pressure hPa'
            },

            series : [{
                name : 'Pressure',
                data : newdata,
                tooltip: {
                    valueDecimals: 2
                }
            }]
        });
    });

});
$(function () {

    $.getJSON('/humidity', function (data) {
        var newdata = []
        for(var i in data['data']){
            var date = new Date(data['data'][i]['date']);
            newdata.push([date.getTime(), data['data'][i]['value']])
        }
        // Create the chart
        $('#containerHumidity').highcharts('StockChart', {


            rangeSelector : {
                selected : 1
            },

            title : {
                text : 'Humidity %'
            },

            series : [{
                name : 'Humidity',
                data : newdata,
                tooltip: {
                    valueDecimals: 0
                }
            }]
        });
    });

});

//]]>
    </script>
</head>
<body>
    <div id="container" style="height: 400px; min-width: 310px"></div>
    <div id="containerPressure" style="height: 400px; min-width: 310px"></div>
    <div id="containerHumidity" style="height: 400px; min-width: 310px"></div>
</body>
</html>
"""

parser = reqparse.RequestParser()
parser.add_argument('year', type=int, help='Year')
parser.add_argument('month', type=int, help='Month')
parser.add_argument('day', type=int, help='Day')


class GenericResource(Resource):
    name = None

    def _get_cursor(self, begin=None, end=None):
        req = {"name": self.name}

        if not isinstance(begin, (datetime.datetime, type(None))):
          raise TypeError("begin must be datetime")
        if not isinstance(end, (datetime.datetime, type(None))):
          raise TypeError("end must be datetime")

        if begin is not None and end is not None:
          req['_date'] = { "$lte": end, "$gte": begin }

        return db.measure.find(req).sort("_date", 1)

    def value_filter(self, value):
        return value

    def get(self):
        args = parser.parse_args()

        begin, end = None, None
        if args['year'] and args['month'] and args['day']:
            try:
                selected_date = datetime.datetime(args['year'], args['month'], args['day'])
                begin = selected_date
                end = begin + datetime.timedelta(1)
            except Exception as e:
                abort(400, message="Date incorrect")

        cursor = self._get_cursor(begin, end)
        if not cursor.count():
            abort(404, message="No data found for this date")

        data = [
            {
                "date":i['_date'].isoformat(),
                "value": self.value_filter(i['result'])
            } for i in cursor
        ]
        return {"data": data}


class TemperatureResource(GenericResource):
    name = "temperatureC"

    def value_filter(self, value):
        return round(value, 3)


class PressureResource(GenericResource):
    name = "pressure"

    def value_filter(self, value):
        return round(value, 3)


class HumidityResource(GenericResource):
    name = "humidity"

    def value_filter(self, value):
        return round(value)


api.add_resource(TemperatureResource, '/temperature')
api.add_resource(PressureResource, '/pressure')
api.add_resource(HumidityResource, '/humidity')

if __name__ == "__main__":
    app.run()

