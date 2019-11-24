import os, sys
import sqlite3
from datetime import datetime, time as datetime_time, timedelta

import my_logging
from utils.common import get_time

# ---------------------------WATERING----------------------------------------
watering_table_name = "watering_info"
create_watering_table = 'create table if not exists ' + watering_table_name + \
    ' (id INTEGER PRIMARY KEY, watering_date TIMESTAMP, watering_length INTEGER, description TEXT)'

pathname = os.path.dirname(sys.argv[0])
work_dir=os.path.abspath(pathname)
DATABASE_DIR = work_dir+"/database"
if not os.path.exists(DATABASE_DIR):
    os.makedirs(DATABASE_DIR)


def get_watering_log(start_date, end_date):
    db_conn = None
    res = {}
    try:
        db_conn = sqlite3.connect(
            'database/global.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        conn = db_conn.cursor()
        conn.execute(create_watering_table)
        conn.execute("SELECT * FROM "+watering_table_name +
                     " WHERE watering_date >=  ? AND watering_date <= ? ORDER BY  watering_date DESC", (start_date, end_date))
        rows = conn.fetchall()
        return rows
    except Exception as e:
        my_logging.logger.exception("message")
    finally:
        if(db_conn != None):
            db_conn.close()
    return res


def get_last_10_watering_info():
    db_conn = None
    res = ""
    try:
        db_conn = sqlite3.connect(
            'database/global.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        conn = db_conn.cursor()
        conn.execute(create_watering_table)
        conn.execute("SELECT * FROM "+watering_table_name +
                     " ORDER BY  watering_date DESC LIMIT 10")
        rows = conn.fetchall()

        for row in rows:
            date = row[1]
            length = row[2]
            reason = row[3]
            date_str = date.strftime('%Y-%m-%d %H:%M')
            res += date_str+", length: "+str(length)+", reason: "+reason+"\n"

        return res
    except Exception as e:
        my_logging.logger.exception("message")
    finally:
        if(db_conn != None):
            db_conn.close()
    return res


def get_latest_watering_info():
    db_conn = None
    try:
        db_conn = sqlite3.connect(
            'database/global.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        conn = db_conn.cursor()
        conn.execute(create_watering_table)
        conn.execute("SELECT * FROM "+watering_table_name +
                     " WHERE watering_date IN (SELECT max(watering_date) FROM "+watering_table_name+")")
        rows = conn.fetchall()
        if len(rows) == 0:
            return "no watering in history : 0"
        else:
            row = rows[0]
            date = row[1]
            length = row[2]
            reason = row[3]
            return "last watering done: "+get_time(date).replace(':',';') + "\nwatering duration: "+str(length)+" s\nwatering reason:  "+reason
    except Exception as e:
        my_logging.logger.exception("message")
    finally:
        if(db_conn != None):
            db_conn.close()


def get_latest_watering_date():
    db_conn = None
    try:
        db_conn = sqlite3.connect(
            'database/global.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        conn = db_conn.cursor()
        conn.execute(create_watering_table)
        conn.execute("SELECT * FROM "+watering_table_name +
                     " WHERE watering_date IN (SELECT max(watering_date) FROM "+watering_table_name+")")
        rows = conn.fetchall()
        if len(rows) == 0:
            return datetime.strptime('10-06-1990 12:00:00', '%d-%m-%Y %H:%M:%S')
        else:
            row = rows[0]
            date = row[1]
            return date
    except Exception as e:
        my_logging.logger.exception("message")
    finally:
        if(db_conn != None):
            db_conn.close()


def get_num_watering_time():
    db_conn = None
    try:
        db_conn = sqlite3.connect(
            'database/global.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        conn = db_conn.cursor()
        conn.execute(create_watering_table)
        conn.execute("SELECT Count(*) FROM "+watering_table_name)
        rows = conn.fetchall()
        if len(rows) == 0:
            return 0
        else:
            row = rows[0]
            return row[0]
    except Exception as e:
        my_logging.logger.exception("message")
    finally:
        if(db_conn != None):
            db_conn.close()


def add_watering_date(length_s, reason):
    db_conn = None
    date = datetime.now()
    try:
        db_conn = sqlite3.connect(
            'database/global.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        conn = db_conn.cursor()
        conn.execute(create_watering_table)
        conn.execute("INSERT INTO "+watering_table_name +
                     "(watering_date, watering_length, description) VALUES (?, ?, ?)", (date, length_s, reason))
        db_conn.commit()
    except Exception as e:
        my_logging.logger.exception("message")
    finally:
        if(db_conn != None):
            db_conn.close()


# ---------------------------------------------WATER_LEVEL-----------------------------------------
water_level_table_name = "water_level_status"
create_water_level_table = 'create table if not exists ' + water_level_table_name + \
    ' (id INTEGER PRIMARY KEY, measure_date TIMESTAMP, water_status INTEGER)'


def get_latest_water_level_status():
    db_conn = None
    try:
        db_conn = sqlite3.connect(
            'database/global.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        conn = db_conn.cursor()
        conn.execute(create_water_level_table)
        conn.execute("SELECT * FROM "+water_level_table_name +
                     " WHERE measure_date IN (SELECT max(measure_date) FROM "+water_level_table_name+")")
        rows = conn.fetchall()
        if len(rows) == 0:
            return None
        else:
            row = rows[0]
            return row[2]
    except Exception as e:
        my_logging.logger.exception("message")
    finally:
        if(db_conn != None):
            db_conn.close()


def add_water_level_status(status):
    db_conn = None
    date = datetime.now()
    try:
        db_conn = sqlite3.connect(
            'database/global.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        conn = db_conn.cursor()
        conn.execute(create_water_level_table)
        conn.execute("INSERT INTO "+water_level_table_name +
                     "(measure_date, water_status) VALUES (?, ?)", (date, status))
        db_conn.commit()
    except Exception as e:
        my_logging.logger.exception("message")
    finally:
        if(db_conn != None):
            db_conn.close()


# ----------------------------------------------------------CO2------------------------------------------
co2_table_name = "co2_info"
create_co2_table = 'create table if not exists ' + co2_table_name + \
    ' (id INTEGER PRIMARY KEY,  measure_date TIMESTAMP, co2 INTEGER, num_try INTEGER)'


def add_co2(co2):
    db_conn = None
    date = datetime.now()
    try:
        db_conn = sqlite3.connect(
            'database/global.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        conn = db_conn.cursor()
        conn.execute(create_co2_table)
        conn.execute("INSERT INTO "+co2_table_name +
                     "(measure_date, co2, num_try) VALUES (?, ?, ?)", (date, co2, 1))
        db_conn.commit()
    except Exception as e:
        my_logging.logger.exception("message")
    finally:
        if(db_conn != None):
            db_conn.close()


def get_co2(start_date, end_date):
    db_conn = None
    res = {}
    try:
        db_conn = sqlite3.connect(
            'database/global.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        conn = db_conn.cursor()
        conn.execute(create_co2_table)
        conn.execute("SELECT * FROM "+co2_table_name +
                     " WHERE measure_date >=  ? AND measure_date <= ? ORDER BY  measure_date ASC", (start_date, end_date))
        rows = conn.fetchall()
        return rows
    except Exception as e:
        my_logging.logger.exception("message")
    finally:
        if(db_conn != None):
            db_conn.close()
    return res


# ----------------------------------------------------------PARTICLES------------------------------------------
particles_table_name = "particles_info"
create_particles_table = 'create table if not exists ' + particles_table_name + \
    ' (id INTEGER PRIMARY KEY,  measure_date TIMESTAMP, PM1 INTEGER, PM25 INTEGER, PM10 INTEGER)'


def add_particles(data):
    db_conn = None
    date = datetime.now()
    try:
        db_conn = sqlite3.connect(
            'database/global.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        conn = db_conn.cursor()
        conn.execute(create_particles_table)
        pm1 = data['data']['8']
        pm25 = data['data']['10']
        pm10 = data['data']['12']
        conn.execute("INSERT INTO "+particles_table_name +
                     "(measure_date, PM1, PM25, PM10) VALUES (?, ?, ?, ?)", (date, pm1[1], pm25[1], pm10[1]))
        db_conn.commit()
    except Exception as e:
        my_logging.logger.exception("message")
    finally:
        if(db_conn != None):
            db_conn.close()


def get_particles(start_date, end_date):
    db_conn = None
    res = {}
    try:
        db_conn = sqlite3.connect(
            'database/global.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        conn = db_conn.cursor()
        conn.execute(create_particles_table)
        conn.execute("SELECT * FROM "+particles_table_name +
                     " WHERE measure_date >=  ? AND measure_date <= ? ORDER BY  measure_date ASC", (start_date, end_date))
        rows = conn.fetchall()
        return rows
    except Exception as e:
        my_logging.logger.exception("message")
    finally:
        if(db_conn != None):
            db_conn.close()
    return res


# ---------------------------------------------------------TEMPERATURE HUMIDITY----------------------------------------
temp_hum_table_name = "temp_hum_info"
create_temp_hum = 'create table if not exists ' + temp_hum_table_name + \
    ' (id INTEGER PRIMARY KEY,  measure_date TIMESTAMP, temp REAL, humid REAL, num_try INTEGER)'


def add_temp_humid(temp, humid, num_try):
    db_conn = None
    date = datetime.now()
    try:
        db_conn = sqlite3.connect(
            'database/global.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        conn = db_conn.cursor()
        conn.execute(create_temp_hum)
        conn.execute("INSERT INTO "+temp_hum_table_name +
                     "(measure_date, temp, humid, num_try) VALUES (?, ?, ?,?)", (date, temp, humid, num_try))
        db_conn.commit()
    except Exception as e:
        my_logging.logger.exception("message")
    finally:
        if(db_conn != None):
            db_conn.close()


def get_temp_humid(start_date, end_date):
    db_conn = None
    res = {}
    try:
        db_conn = sqlite3.connect(
            'database/global.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        conn = db_conn.cursor()
        conn.execute(create_temp_hum)
        conn.execute("SELECT * FROM "+temp_hum_table_name +
                     " WHERE measure_date >=  ? AND measure_date <= ? ORDER BY  measure_date ASC", (start_date, end_date))
        rows = conn.fetchall()
        return rows
    except Exception as e:
        my_logging.logger.exception("message")
    finally:
        if(db_conn != None):
            db_conn.close()
    return res
