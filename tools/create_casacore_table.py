#!/usr/bin/env python3

import argparse
import datetime
import dateutil.parser
import json

from casacore import tables

default_version = "1.1"
default_date = "2016-11-01T11:42"

default_input = "observatories.json"
default_path = "Observatories"

parser = argparse.ArgumentParser(
    usage = 'casacore-update-observatories [options]',
    description = 'Update casacore Observatory table from json input')
parser.add_argument('-i', '--input-file',
                    help='JSON oinput file (default: {})'
                    .format(default_input),
                    default=default_input)
parser.add_argument('-o', '--output-path',
                    help='output table path (default: {})'
                    .format(default_path),
                    default=default_path)
parser.add_argument('-v', '--version',
                    help='Set version number in table (default: {})'
                    .format(default_version),
                    default=default_version)
parser.add_argument('-d', '--date',
                    help='Set version date in database (default: {})'
                    .format(default_date),
                    default=default_date)
args = parser.parse_args()

with open(args.input_file) as f:
    obstable = json.load(f)

# Create data table
columns = [
    tables.makescacoldesc('MJD', 0., valuetype='double',
                          keywords={'UNIT':'d'}),
    tables.makescacoldesc('Name', '', valuetype='string'),
    tables.makescacoldesc('Type', '', valuetype='string'),
    tables.makescacoldesc('Long', 0., valuetype='double',
                          keywords={'UNIT':'deg'}),
    tables.makescacoldesc('Lat', 0., valuetype='double',
                          keywords={'UNIT':'deg'}),
    tables.makescacoldesc('Height', 0., valuetype='double',
                          keywords={'UNIT':'m'}),
    tables.makescacoldesc('X', 0., valuetype='double',
                          keywords={'UNIT':'m'}),
    tables.makescacoldesc('Y', 0., valuetype='double',
                          keywords={'UNIT':'m'}),
    tables.makescacoldesc('Z', 0., valuetype='double',
                          keywords={'UNIT':'m'}),
    tables.makescacoldesc('Source', '', valuetype='string'),
    tables.makescacoldesc('Comment', '', valuetype='string'),
]

t = tables.table(args.output_path, tables.tablecreatedesc(columns),
                 len(obstable))
t.putinfo({'type': 'IERS', 'subType': 'observatory'})
t.putkeywords({
    'MJD0': 0,
    'dMJD': 0.0,
    'VS_VERSION': '{:04d}.{:04d}'.format(*(int(i)
                                           for i in args.version.split('.'))),
    'VS_CREATE': dateutil.parser.parse(args.date).strftime('%Y/%m/%d/%H:%M'),
    'VS_DATE': dateutil.parser.parse(args.date).strftime('%Y/%m/%d/%H:%M'),
    'VS_TYPE': 'List of Observatory positions'
})

tablerows = t.row()
for i, row in enumerate(obstable):
    [[x, y, z ]] =  tables.taql("calc meas.position('itrf',{}deg,{}deg,{}m,"
                                "'wgsll')".format(row['longitude'],
                                                  row['latitude'],
                                                  row['elevation']))
    tablerows.put(i, {
        'MJD': 0.0,
        'Name': str(row['Id']),
        'Type': 'WGS84',
        'Long': row['longitude'],
        'Lat':  row['latitude'],
        'Height':  row['elevation'],
        'X': x,
        'Y': y,
        'Z': z,
        'Source': row.get('Reference', 'Wikipedia')
    })
