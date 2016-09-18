# lacity-citation-parser
A simple script to parse parking citation data from the City of Los Angeles and transform it into a more usable format by adding translating geocodes, cleaning/standardizing time/money fields, and adding in neighborhood context.

The geo transform parts are cribbed from CMBleakley's parser (https://github.com/CMBleakley/citation-formatter)

## Usage
Do this:
```
python parking_parser.py \
  --citations [csv of ticket data] \
  --neighborhoods [geojson of LA Time neighborhood polygons] \
  --meters [geojson of LA City meter zones]
```
or 
```
python parking_parser.py --help
```
## Where to get the Data
* City of LA Parking Tickets: https://data.lacity.org/A-Well-Run-City/Parking-Citations/t4h6-r362
* City of LA Meter Zones: http://geohub.lacity.org/datasets/71c26db1ad614faab1047cc8c3686ece_28
* LA Times Neighborhood Polygons: http://boundaries.latimes.com/sets/

## Sample Viz:
Here's a blog post that uses this data (and CartoDB): https://ben-coppersmith.cartodb.com/viz/96aab120-06ff-11e5-a99e-0e018d66dc29/public_map
