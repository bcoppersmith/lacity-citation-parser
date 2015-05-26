import argparse
import csv
import datetime
import os.path
import pyproj
import re
import sys
import time

ESRI_PROJ = "+proj=lcc +lat_1=34.03333333333333 +lat_2=35.46666666666667 +lat_0=33.5 +lon_0=-118 +x_0=2000000 +y_0=500000.0000000002 +ellps=GRS80 +datum=NAD83 +to_meter=0.3048006096012192 +no_defs"
EPSG_PROJ = "+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs"

# Hand-curated boundaries from clicking around on maps.google.com
SOUTHERN_BOUND = 33.695483
NORTHERN_BOUND = 34.336338
WESTERN_BOUND  = -118.531895
EASTERN_BOUND  = -117.908421

esri  = pyproj.Proj(ESRI_PROJ,preserve_units=True)
wgs84 = pyproj.Proj(EPSG_PROJ)

def is_valid_file(parser, filepath):
  if not os.path.exists(filepath):
    parser.error("The file %s is not valid" % filepath)
  else:
    return open(filepath, 'r')

def convert_geo(row):
  raw_lat = row['latitude']
  raw_lng = row['longitude']
  row['longitude'], row['latitude'] = pyproj.transform(esri, wgs84, raw_lat, raw_lng)
  return row

def normalize_ticket_time(raw_time):
  ticket_time = "00:00"
  if len(raw_time) == 4:
    ticket_time = re.sub('(\d{2})(\d{2})$', '\\1:\\2', raw_time)
  elif len(raw_time) == 3:
    ticket_time = re.sub('(\d{1})(\d{2})$', '0\\1:\\2', raw_time)
  return ticket_time

def convert_time(row):
  raw_ticket_time = row['issue_time']
  raw_ticket_date = row['issue_date']
  ticket_time = normalize_ticket_time(raw_ticket_time)
  ticket_date = re.sub('\s\d\d:\d\d:\d\d [AP]M', '', raw_ticket_date)
  raw_timestamp = ticket_date + ' ' + ticket_time
  try:
    timestamp = time.mktime(datetime.datetime.strptime(raw_timestamp, "%m/%d/%Y %H:%M").timetuple())
  except ValueError, TypeError:
    timestamp = "n/a"
  row['issue_time'] = timestamp
  return row

def is_valid_lat(lat):
  return float(lat) >= SOUTHERN_BOUND and float(lat) <= NORTHERN_BOUND

def is_valid_lng(lng):
  return float(lng) >= WESTERN_BOUND and float(lng) <= EASTERN_BOUND

def has_violation_description(desc):
  return desc is not None

def is_valid_row(row):
  return is_valid_lat(row['latitude']) and \
         is_valid_lng(row['longitude']) and \
         has_violation_description(row['violation_description'])

def process_row(writer, row):
  row = convert_geo(row)
  row = convert_time(row)
  if is_valid_row(row):
    writer.writerow(row)

parser = argparse.ArgumentParser()
parser.add_argument("--input", dest="filename",
                    required=True, help="Specify input CSV here.",
                    metavar="FILE", type=lambda filepath: is_valid_file(parser, filepath))

args = parser.parse_args()

with args.filename as csvfile:
  citation_reader = csv.DictReader(csvfile)
  for line_number, line in enumerate(citation_reader, 1):
    line = dict((k.lower(), v) for k,v in line.iteritems())
    line = dict((k.replace(' ', '_'), v) for k,v in line.iteritems())
    w    = csv.DictWriter(sys.stdout, line.keys())
    if line_number == 1:
      w.writeheader()
    process_row(w, line)
