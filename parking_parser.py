import argparse
import csv
import datetime
import pyproj
import re
import time
import json
from point_in_polygons import PointInPolygons
from shapely.geometry import Point

UNCHANGED_FIELDS = [
  "Ticket number",
  "Violation Description",
  "Violation code",
  "Fine amount",
  "Location"
]

ESRI_PROJ = "+proj=lcc +lat_1=34.03333333333333 +lat_2=35.46666666666667 +lat_0=33.5 +lon_0=-118 +x_0=2000000 +y_0=500000.0000000002 +ellps=GRS80 +datum=NAD83 +to_meter=0.3048006096012192 +no_defs"
EPSG_PROJ = "+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs"

header = [
  "ticket_number",
  "violation_description",
  "violation_code",
  "fine_amount",
  "location",
  "issue_date",
  "issue_timestamp",
  "issue_day_of_month",
  "latitude",
  "longitude",
  "raw_meterid"
]
esri  = pyproj.Proj(ESRI_PROJ, preserve_units = True)
wgs84 = pyproj.Proj(EPSG_PROJ)

def convert_geo(geom):
  return pyproj.transform(esri, wgs84, geom[0], geom[1])

def augment_meter_id(meter_id, zone):
  if re.match('^[0-9]+', meter_id):
    return zone + meter_id
  else:
    return meter_id

def sanitize_time(time):
  ticket_time = ""
  if len(time) == 4:
    ticket_time = re.sub('(\d{2})(\d{2})$', '\\1:\\2', time)
  elif len(time) == 3:
    ticket_time = re.sub('(\d{1})(\d{2})$', '0\\1:\\2', time)
  return ticket_time

def sanitize_date(date):
  return re.sub('\s\d\d:\d\d:\d\d [AP]M', '', date)

def generate_timestamp(date, time_of_day):
  raw_timestamp = date + ' ' + time_of_day
  try:
    return int(time.mktime(datetime.datetime.strptime(raw_timestamp, "%m/%d/%Y %H:%M").timetuple()))
  except ValueError:
    return ""

def grab_day_of_month(date):
  return re.sub('\d{2}\/(\d{2})\/\d{4}', '\\1', date)

parser = argparse.ArgumentParser()

parser.add_argument(
  "--citations", dest="citations", required=True,
  help="Specify citation data here.", metavar="FILE"
)

parser.add_argument(
  "--neighborhoods", dest="neighborhoods_geojson", required=False,
  help="Specify the neighborhoods geoJSON file here.", metavar="FILE"
)

parser.add_argument(
  "--meters", dest="meter_zone_geojson", required=False,
  help="Specify the meter zones geoJSON file here.", metavar="FILE"
)

args = parser.parse_args()

meter_zones = None
if args.meter_zone_geojson:
  meter_zones = PointInPolygons(args.meter_zone_geojson, 'PMZ_CODE')
  header.extend(["meterid", "meter_zone"])

neighborhoods = None
if args.neighborhoods_geojson:
  neighborhoods = PointInPolygons(args.neighborhoods_geojson, 'name')
  header.extend(["neighborhood"])

print "\t".join(header)

citations = open(args.citations)
reader = csv.DictReader(citations)
for row in reader:
  output = [row[field] for field in UNCHANGED_FIELDS]

  date = sanitize_date(row['Issue Date'])
  time_of_day = sanitize_time(row['Issue time'])
  timestamp = generate_timestamp(date, time_of_day)
  day_of_month = grab_day_of_month(date)
  output.extend([date, timestamp, day_of_month])

  geometry = convert_geo([row['Latitude'], row['Longitude']])
  point = Point(geometry)

  raw_meter_id = row['Meter Id']
  output.extend([geometry[1], geometry[0], raw_meter_id])

  if meter_zones:
    meter_zone = meter_zones.search(point)
    meter_id = augment_meter_id(raw_meter_id, meter_zone)
    output.extend([meter_id, meter_zone])

  if neighborhoods:
    neighborhood = neighborhoods.search(point)
    output.extend([neighborhood])

  print '	'.join(str(field) for field in output)

citations.close()
