import os, json
import sqlite3 as sqlite
import datefuncs.dt as dt
from util import check_file

class JSONTemps(object):
    
    def __init__(self, filename, db=None):
        self._curjson = None
        self._empty()
        self.db = db
        self._filename = None
        # Property will raise an exception if theres a problem here
        self.filename = filename
        with open(self.filename, 'r') as f:
            try:
                self._curjson = json.loads(f.read())
            except ValueError:
                self._curjson = []

    def _empty(self):
        self._curjson = {'plotdata':[]}
        
    def add_val(self, time, val):
        ''' Add a value to the json file

        Arguments:
        time should be a timestamp of the reading, same form as time.time()
        val is the value of the reading to be added
        '''

        # JSON is only for today, if we are tring to add a value for another
        # day discard it
        if not dt.is_today(time):
            return
        # if We've moved into a new day empty the values
        if not self._sameday():
            self._empty()
        # Get all of todays readings so far if we currently have none
        if len(self._curjson['plotdata']) == 0:
            self._curjson = {'plotdata':self._get_today()}
        # Now we can finally add the value to the json
        self._curjson['plotdata'].append([int(time * 1000), val])
        self.__writejson()

    def _sameday(self):
        ''' Check if today is the same date as the last reading in the json '''

        # No point going any further if the list is empty, lets bail
        if len(self._curjson) == 0: return

        today = dt.utc_now()
        last = dt.utc(self._curjson['plotdata'][-1][0] / 1000.0)
        return (today.day == last.day and
                today.month == last.month and
                today.year == last.year)

    def _get_today(self):
        ''' retrieve all of the readings for today formatted for json file'''
        
        if self.db is None: return
        res = []
        today = dt.timestamp_day(dt.now())
        with sqlite.connect(os.environ['PIMMS_DB']) as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM readings "
                        "WHERE timestamp  > {ts} AND timestamp < {te} "
                        "ORDER BY timestamp ASC;".format(ts = today.start,
                                                         te = today.end))
            res = cur.fetchall()
        return JSONTemps.dbval2json(res)

    @staticmethod
    def dbval2json(res):
        ''' Format a list of times / temperatures suitable for the json file

        returns a new list
        '''
        return [[int(r[0] * 1000), r[1] / 1000.0] for r in res]

    
    def __writejson(self):
        ''' Write the current json vals to the file '''
        with open(self.filename, 'w') as f:
            f.write(json.dumps(self._curjson))

    @property
    def filename(self):
        return self._filename
    @filename.setter
    def filename(self, filename):
        check_file(filename)
        self._filename = filename
