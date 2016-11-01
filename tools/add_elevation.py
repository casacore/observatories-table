#!/usr/bin/env python3

import argparse
import json
import os
import urllib.request

# The following function was used to retrieve the elevation.
# Get the API key from https://maps.googleapis.com/
def get_elevation(longitude, latitude, api_key):
    url="https://maps.googleapis.com/maps/api/elevation/json?" + \
    "locations={longitude},{latitude}&key={key}"
    response = urllib.request.urlopen(url.format(longitude=longitude,
                                                 latitude=latitude,
                                                 key=api_key))
    data = json.loads(str(response.read().decode()))
    return int(data['results'][0]['elevation'])

default_file = "observatories.json"

parser = argparse.ArgumentParser(
    usage = 'casacore-update-observatories [options]',
    description = 'Update casacore Observatory table from json input')
parser.add_argument('-f', '--file',
                    help='JSON input file (default: {})'
                    .format(default_file),
                    default=default_file)
parser.add_argument('-k', '--api-key',
                    help='Google maps API key. Get it from https://developers.google.com/maps/documentation/elevation/start')
args = parser.parse_args()

if not args.api_key:
    print('API key required. Get it from https://maps.googleapis.com')
    exit(1)
    
with open(args.file) as f:
    obstable = json.load(f)

found = False
for row in obstable:
    if 'elevation' not in row:
        found = True
        row['elevation'] = get_elevation(row['latitude'], row['longitude'],
                                         args.api_key)

if found:
    with open(args.file + '.new', 'w') as f:
        json.dump(obstable, f, indent=4, sort_keys=True)

    if not os.path.exists(args.file + '.old'):
        os.rename(args.file, args.file + '.old')
    os.rename(args.file + '.new', args.file)
