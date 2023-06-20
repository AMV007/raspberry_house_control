import os, sys
import sqlite3
from datetime import datetime, time as datetime_time, timedelta

import app_logger
from utils.common import get_time

# ---------------------------GLOBAL DATABASE----------------------------------------
watering_table_name = "watering_info"
water_level_table_name = "water_level_status"
co2_table_name = "co2_info"
particles_table_name = "particles_info"
temp_hum_table_name = "temp_hum_info"

create_watering_table = 'create table if not exists ' + watering_table_name + \
    ' (id INTEGER PRIMARY KEY, watering_date TIMESTAMP, watering_length INTEGER, description TEXT)'
create_water_level_table = 'create table if not exists ' + water_level_table_name + \
    ' (id INTEGER PRIMARY KEY, measure_date TIMESTAMP, water_status INTEGER)'
create_co2_table = 'create table if not exists ' + co2_table_name + \
    ' (id INTEGER PRIMARY KEY,  measure_date TIMESTAMP, co2 INTEGER, num_try INTEGER)'
create_particles_table = 'create table if not exists ' + particles_table_name + \
    ' (id INTEGER PRIMARY KEY,  measure_date TIMESTAMP, PM1 INTEGER, PM25 INTEGER, PM10 INTEGER)'
create_temp_hum = 'create table if not exists ' + temp_hum_table_name + \
    ' (id INTEGER PRIMARY KEY,  measure_date TIMESTAMP, temp REAL, humid REAL, num_try INTEGER)'

def get_db_conn():
    if not os.path.isdir('database'):
        os.mkdir("database")
    db_conn = sqlite3.connect(
            'database/global.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    conn = db_conn.cursor()
    conn.execute(create_watering_table)
    conn.execute(create_water_level_table)
    conn.execute(create_co2_table)
    conn.execute(create_particles_table)
    conn.execute(create_temp_hum)
    return db_conn, conn

def free_db_conn(db_conn):
    if(db_conn != None):
        db_conn.commit()
        db_conn.close()

# ---------------------------WATERING----------------------------------------
def get_watering_log(start_date, end_date):
    db_conn = None
    res = []
    try:
        db_conn, conn = get_db_conn()
        conn.execute("SELECT * FROM "+watering_table_name +
                     " WHERE watering_date >=  ? AND watering_date <= ? ORDER BY  watering_date DESC", (start_date, end_date))
        rows = conn.fetchall()
        res=rows
    except Exception as e:
        app_logger.exception("message")
    finally:
        free_db_conn(db_conn)
    return res

def get_last_10_watering_info():
    db_conn = None
    res = "unknown"
    try:
        db_conn, conn = get_db_conn()
        conn.execute("SELECT * FROM "+watering_table_name +
                     " ORDER BY  watering_date DESC LIMIT 10")
        rows = conn.fetchall()

        for row in rows:
            date = row[1]
            length = row[2]
            reason = row[3]
            date_str = date.strftime('%Y-%m-%d %H:%M')
            res += date_str+", length: "+str(length)+", reason: "+reason+"\n"
    except Exception as e:
        app_logger.exception("message")
    finally:
        free_db_conn(db_conn)
    return res


def get_latest_watering_info():
    db_conn = None
    res = "unknown"
    try:
        db_conn, conn = get_db_conn()
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
            res= "last watering done: "+get_time(date).replace(':',';') + "\nwatering duration: "+str(length)+" s\nwatering reason:  "+reason
    except Exception as e:
        app_logger.exception("message")
    finally:
        free_db_conn(db_conn)
    return res


def get_latest_watering_date():
    db_conn = None
    res = "unknown"
    try:
        db_conn, conn = get_db_conn()
        conn.execute("SELECT * FROM "+watering_table_name +
                     " WHERE watering_date IN (SELECT max(watering_date) FROM "+watering_table_name+")")
        rows = conn.fetchall()
        if len(rows) == 0:
            res=datetime.strptime('10-06-1990 12:00:00', '%d-%m-%Y %H:%M:%S')
        else:
            row = rows[0]
            date = row[1]
            res=date
    except Exception as e:
        app_logger.exception("message")
    finally:
        free_db_conn(db_conn)
    return res


def get_num_watering_time():
    db_conn = None
    res = "unknown"
    try:
        db_conn, conn = get_db_conn()
        conn.execute("SELECT Count(*) FROM "+watering_table_name)
        rows = conn.fetchall()
        if len(rows) == 0:
            res=0
        else:
            row=rows[0]
            res=row[0]
    except Exception as e:
        app_logger.exception("message")
    finally:
        free_db_conn(db_conn)
    return res

def add_watering_date(length_s, reason):
    db_conn = None
    try:
        db_conn, conn = get_db_conn()
        conn.execute("INSERT INTO "+watering_table_name +
                     "(watering_date, watering_length, description) VALUES (?, ?, ?)", (datetime.now(), length_s, reason))
    except Exception as e:
        app_logger.exception("message")
    finally:
        free_db_conn(db_conn)


# ---------------------------------------------WATER_LEVEL-----------------------------------------
def add_water_level_status(status):
    db_conn = None
    try:
        db_conn, conn = get_db_conn()
        conn.execute("INSERT INTO "+water_level_table_name +
                     "(measure_date, water_status) VALUES (?, ?)", (datetime.now(), status))
    except Exception as e:
        app_logger.exception("message")
    finally:
        free_db_conn(db_conn)

def get_latest_water_level_status():
    db_conn = None
    res = "unknown"
    try:
        db_conn, conn = get_db_conn()
        conn.execute("SELECT * FROM "+water_level_table_name +
                     " WHERE measure_date IN (SELECT max(measure_date) FROM "+water_level_table_name+")")
        rows = conn.fetchall()
        if len(rows) > 0:
            row = rows[0]
            res=row[2]
    except Exception as e:
        app_logger.exception("message")
    finally:
        free_db_conn(db_conn)
    return res

# ----------------------------------------------------------CO2------------------------------------------
def add_co2(co2):
    db_conn = None
    try:
        db_conn, conn = get_db_conn()
        conn.execute("INSERT INTO "+co2_table_name +
                     "(measure_date, co2, num_try) VALUES (?, ?, ?)", (datetime.now(), co2, 1))
    except Exception as e:
        app_logger.exception("message")
    finally:
        free_db_conn(db_conn)


def get_co2(start_date, end_date):
    db_conn = None
    res = []
    try:
        db_conn, conn = get_db_conn()
        conn.execute("SELECT * FROM "+co2_table_name +
                     " WHERE measure_date >=  ? AND measure_date <= ? ORDER BY  measure_date ASC", (start_date, end_date))
        rows = conn.fetchall()
        res=rows
    except Exception as e:
        app_logger.exception("message")
    finally:
        free_db_conn(db_conn)
    return res


# ----------------------------------------------------------PARTICLES------------------------------------------
def add_particles(data):
    db_conn = None
    try:
        db_conn, conn = get_db_conn()
        pm1 = data['data']['8']
        pm25 = data['data']['10']
        pm10 = data['data']['12']
        conn.execute("INSERT INTO "+particles_table_name +
                     "(measure_date, PM1, PM25, PM10) VALUES (?, ?, ?, ?)", (datetime.now(), pm1[1], pm25[1], pm10[1]))
    except Exception as e:
        app_logger.exception("message")
    finally:
        free_db_conn(db_conn)


def get_particles(start_date, end_date):
    db_conn = None
    res = []
    try:
        db_conn, conn = get_db_conn()
        conn.execute("SELECT * FROM "+particles_table_name +
                     " WHERE measure_date >=  ? AND measure_date <= ? ORDER BY  measure_date ASC", (start_date, end_date))
        rows = conn.fetchall()
        res=rows
    except Exception as e:
        app_logger.exception("message")
    finally:
        free_db_conn(db_conn)
    return res


# ---------------------------------------------------------TEMPERATURE HUMIDITY----------------------------------------
def add_temp_humid(temp, humid, num_try):
    db_conn = None
    try:
        db_conn, conn = get_db_conn()
        conn.execute("INSERT INTO "+temp_hum_table_name +
                     "(measure_date, temp, humid, num_try) VALUES (?, ?, ?,?)", (datetime.now(), temp, humid, num_try))
    except Exception as e:
        app_logger.exception("message")
    finally:
        free_db_conn(db_conn)


def get_temp_humid(start_date, end_date):
    db_conn = None
    res = []
    try:
        db_conn, conn = get_db_conn()
        conn.execute("SELECT * FROM "+temp_hum_table_name +
                     " WHERE measure_date >=  ? AND measure_date <= ? ORDER BY  measure_date ASC", (start_date, end_date))
        rows = conn.fetchall()
        res=rows
    except Exception as e:
        app_logger.exception("message")
    finally:
        free_db_conn(db_conn)
    return res
