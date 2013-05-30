""" pimms.py Entry point for PI.M.M.S application. Does all the web rendering.

Copyright 2013 Will Bickerstaff <will.bickerstaff@gmail.com>

This file is part of Pi.M.M.S.

    Pi.M.M.S is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Foobar is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
"""

import sqlite3 as sqlite
import datetime
import time
import os
from collections import namedtuple
from flask import Flask, request
from jinja2 import Environment, FileSystemLoader

templatedir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'templates')
env = Environment(loader = FileSystemLoader(templatedir))

app = Flask(__name__)
app.config['DEBUG'] = True

def now():
    """ Datetime object representing now """
    return datetime.date.fromtimestamp(time.time())

def reading_extents_offset():
    """ Get the timedelta from now of the earliest and most recent readings
    returns a namedtuple  with start and end
    start being a timedelta difference from now to the earliest reading
    end being a timedelta difference from now to the most recent reading
    """

    Deltatype = namedtuple('Deltatype', 'start end')
    n = now()

    with sqlite.connect(os.environ['PIMMS_DB']) as con:
        cur = con.cursor()
        cur.execute("SELECT MIN(timestamp) FROM readings;")
        starttime = datetime.date.fromtimestamp(cur.fetchone()[0])
        cur.execute("SELECT MAX(timestamp) FROM readings;")
        endtime = datetime.date.fromtimestamp(cur.fetchone()[0])

    return (Deltatype(n - starttime, n - endtime if endtime < n else n - n))

def join_date(delim, *args):
    """ Join with delim a list of args into a string """

    return delim.join([str(x) for x in args])

def valid_year(year): return year > 1900 and year < 2300
def valid_month(month): return month > 0 and month < 13
def valid_day(day): return day > 0 and day < 31
def valid_date(year, month, day):
    if valid_year(year) and valid_month(month) and valid_day(day):
        return True
    return False

def make_day(year, month, day):
    """ Create a namedtuple with 2 datetime objects spaning a day """

    Daytype = namedtuple('DayType', 'start end')
    daystart = datetime.datetime(year, month, day)
    dayend = datetime.datetime(year, month, day, 23, 59, 59)
    return Daytype(daystart, dayend)

def get_readings(day):
    """ Get all readings for the given day
    @see make_day
    """

    res = []
    plotdate = (time.mktime(day.start.timetuple()),
                time.mktime(day.end.timetuple()))
    with sqlite.connect(os.environ['PIMMS_DB']) as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM readings WHERE timestamp > {start:f} AND timestamp < {end:f};".format(
                start=plotdate[0], end=plotdate[1]))
        res = cur.fetchall()
    return res

@app.route('/', methods=["GET", "POST"])
def index():
    plotdate = datetime.date.fromtimestamp(time.time()).__str__()
    if request.method == 'POST':
        if 'dateselected' in request.form:
            pdate = request.form['dateselected']
            psplit = [int(x) for x in pdate.split('/')]
            if (len(psplit) == 3 and
                   valid_date(psplit[2], psplit[0], psplit[1])):
                plotdate = join_date('-', psplit[2], psplit[0], psplit[1])

    plotdate = [int(x) for x in plotdate.split('-')]
    datestr = join_date('/', plotdate[2], plotdate[1], plotdate[0])
    temps = []
    day = make_day(plotdate[0], plotdate[1], plotdate[2])
    res = get_readings(day)
    for r in res:
        temps.append([str(datetime.datetime.utcfromtimestamp(r[0])).split('.')[0], float(r[1])/1000])

    deltas = reading_extents_offset()

    template = env.get_template('default.html')
    return template.render(start = 0 - deltas.start.days,
                           end = deltas.end.days,
                           readings=temps, plotdate=datestr, day=day )

if __name__ == '__main__':
    app.run()
