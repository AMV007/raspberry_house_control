from flask import Flask
from flask import Markup
from flask import Flask
from flask import render_template
from flask import request
from flask import session
from datetime import datetime, time as datetime_time, timedelta, date as datetime_date
import _thread as thread
import dateparser
import traceback
import logging
import re

#my imports
from utils.common import get_time
import my_logging

import devices
import sensors
import controls
import database

def get_form_param():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    detailed = request.args.get('detailed')

    if detailed == None:
        detailed = False

    if start_date != None:
        if start_date.isdigit():
            start_date = datetime.now() - timedelta(days=int(start_date))
        else:
            try:
                start_date = dateparser.parse(start_date).date()
            except ValueError:
                return "Unable to understand date %s" % request.args.get('start_date'), 400
    else:
        start_date = datetime.now() - timedelta(days=7)

    if end_date != None:
        try:
            end_date = dateparser.parse(end_date).date()
        except ValueError:
            return "Unable to understand date %s" % request.args.get('end_date'), 400
    else:
        end_date = datetime.now()
    return (start_date, end_date, detailed)


def watering_chart():
    try:
        start_date, end_date, detailed = get_form_param()
        rows = database.get_watering_log(start_date, end_date)
        labels = []
        values = []
        values.append([])

        for row in rows:
            date = row[1]
            length = row[2]

            if detailed:
                date_str = date.strftime('%Y-%m-%d %H:%M')
            else:
                date_str = date.strftime('%Y-%m-%d %H:00')
            labels.append(date_str)
            values[0].append(length)

        legends = ["Watering time"]
        colors = ["rgba(23,118,229,0.8)"]
        return render_template('multi_chart.html', type="bar", title="Watering plants in room chart", legends=legends, labels=labels,
                               colors=colors, values=values,
                               start_date=start_date.strftime('%Y-%m-%d'), end_date=end_date.strftime('%Y-%m-%d'))
    except Exception as e:
        my_logging.logger.exception("watering_chart error")
        return "Unable to process watering_chart chart: " + traceback.format_exc(), 400
    finally:
        pass


def co2_chart():
    try:
        start_date, end_date, detailed = get_form_param()

        rows = database.get_co2(start_date, end_date)
        labels = []
        values = []
        values.append([])
        for row in rows:
            date = row[1]
            value = row[2]
            if value == None:
                value = 0
            if detailed:
                date_str = date.strftime('%Y-%m-%d %H:%M')
            else:
                date_str = date.strftime('%Y-%m-%d %H:00')
            if date_str in labels:
                continue
            labels.append(date_str)
            values[0].append(value)

        legends = ["CO2, ppm"]
        colors = ["rgba(23,220,174,0.8)"]
        return render_template('multi_chart.html', type="line",  title="CO2 in room chart", legends=legends, labels=labels,
                               colors=colors, values=values,
                               start_date=start_date.strftime('%Y-%m-%d'), end_date=end_date.strftime('%Y-%m-%d'))
    except Exception as e:
        my_logging.logger.exception("co2 chart error")
        return "Unable to process co2 chart: " + traceback.format_exc(), 400
    finally:
        pass


def watering_table():
    try:
        start_date, end_date, detailed = get_form_param()
        rows = database.get_watering_log(start_date, end_date)
        values_water = ""
        for row in rows:
            date = row[1]
            length = row[2]
            reason = row[3]
            date_str = date.strftime('%Y-%m-%d %H:%M')
            values_water += "<tr><td>"
            values_water += date_str+"</td><td>"
            values_water += str(length)+"</td><td>"
            values_water += reason+"</td></tr>"

        return render_template('watering_table.html', values_water=values_water,
                               start_date=start_date.strftime('%Y-%m-%d'), end_date=end_date.strftime('%Y-%m-%d'))
    except Exception as e:
        my_logging.logger.exception("index chart error")
        return "Unable to process index chart: " + traceback.format_exc(), 400
    finally:
        pass


def temp_hum_chart():
    try:
        start_date, end_date, detailed = get_form_param()

        rows = database.get_temp_humid(start_date, end_date)
        labels = []
        values = []
        values.append([])
        values.append([])

        for row in rows:
            date = row[1]
            if detailed:
                date_str = date.strftime('%Y-%m-%d %H:%M')
            else:
                date_str = date.strftime('%Y-%m-%d %H:00')

            if date_str in labels:
                continue
            labels.append(date_str)
            values[0].append(row[2])
            values[1].append(row[3])

        legends = ["Temperature, °C", "Humidity, %"]
        colors = ["rgba(238,74,41,0.4)", "rgba(125,125,231,0.8)"]
        return render_template('multi_chart.html', type="line", title="Temperature and humidity in room", legends=legends, colors=colors,
                               labels=labels, values=values,
                               start_date=start_date.strftime('%Y-%m-%d'), end_date=end_date.strftime('%Y-%m-%d'))
    except Exception as e:
        my_logging.logger.exception("index chart error")
        return "Unable to process index chart: " + traceback.format_exc(), 400
    finally:
        pass


def particles_chart():
    try:
        start_date, end_date, detailed = get_form_param()

        rows = database.get_particles(start_date, end_date)
        labels = []
        values = []
        values.append([])
        values.append([])
        values.append([])

        for row in rows:
            date = row[1]
            if detailed:
                date_str = date.strftime('%Y-%m-%d %H:%M')
            else:
                date_str = date.strftime('%Y-%m-%d %H:00')

            if date_str in labels:
                continue

            labels.append(date_str)

            values[0].append(row[2])
            values[1].append(row[3])
            values[2].append(row[4])

        legends = ["P1, μg/m³", "P2.5, μg/m³", "P10, μg/m³"]
        colors = ["rgba(162,251,49, 0.4)",
                  "rgba(220,190,23, 0.55)", "rgba(220,95,23, 0.75)"]
        return render_template('multi_chart.html', type="line", title="PM dust chart", legends=legends, values=values, colors=colors, labels=labels,
                               start_date=start_date.strftime('%Y-%m-%d'), end_date=end_date.strftime('%Y-%m-%d'))
    except Exception as e:
        my_logging.logger.exception("index chart error")
        return "Unable to process index chart: " + traceback.format_exc(), 400
    finally:
        pass


def status_info():
    try:
        CO2 = sensors.get(sensors.CO2)[0].read_val()
        temperature, humidity, num_cycles_wrong = sensors.get(sensors.TempHum)[0].read_val()
        particles = sensors.get(sensors.Particles_pms7003)[0].read_val()
        info_data = re.split('\n|:',controls.get_status_str()+sensors.get_status_str())
        info_data = list(filter(None, info_data))
        res_info = "<trt><td>Update time</td><td>" + \
            get_time(datetime.now())+"</td></tr>"
        for counter in range(0, len(info_data)-1, 2):
            res_info += "<tr>"
            res_info += "<td>"+info_data[counter]+"</td>"
            res_info += "<td>"+info_data[counter+1].replace(';', ':')+"</td>"
            res_info += "</tr>"

        out_particles = []
        out_particles.append(particles['data']['8'])
        out_particles.append(particles['data']['10'])
        out_particles.append(particles['data']['12'])

        return render_template('status_info.html', temp=str("%.1f" % temperature), hum=str("%.1f" % humidity), co2=str(CO2),
                               particles=out_particles,
                               status_info=res_info)
    except Exception as e:
        my_logging.logger.exception("status_info chart error")
        return "Unable to process status_info chart: " + traceback.format_exc(), 400
    finally:
        pass


def index():
    try:
        return render_template('index.html')
    except Exception as e:
        my_logging.logger.exception("index chart error")
        return "Unable to process index chart: " + traceback.format_exc(), 400
    finally:
        pass


routes = [
    dict(route="/", page="index", func=index),
    dict(route="/temp_hum_chart", page="temp_hum_chart", func=temp_hum_chart),
    dict(route="/particles_chart", page="particles_chart", func=particles_chart),
    dict(route="/co2_chart", page="co2_chart", func=co2_chart),
    dict(route="/watering_chart", page="watering_chart", func=watering_chart),
    dict(route="/watering_table", page="watering_table", func=watering_table),
    dict(route="/status_info", page="status_info", func=status_info),
    dict(route="/about", page="about", func=index)
]


def flaskThread():
    global app
    app.run(host='0.0.0.0', port=8080)


def run(_name):
    global app
    logging.getLogger("werkzeug").setLevel(logging.ERROR)
    if _name == "__main__":
        app = Flask(_name)
        for route in routes:
            app.add_url_rule(
                route["route"],  # I believe this is the actual url
                # this is the name used for url_for (from the docs)
                route["page"]
            )
            app.view_functions[route["page"]] = route["func"]
        thread.start_new_thread(flaskThread, ())
