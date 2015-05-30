# lacity-citation-parser
A simple script to parse parking citation data from the City of Los Angeles.

This script is for those who have already found CMBleakley's first parser (https://github.com/CMBleakley/citation-formatter), but are not yet brave enough to use Node.

Usage:
`python parking_parser.py --input [raw csv]`

This parser is destructive, in that it places the parsed/coerced values into the column from which they were originally derived.

Sample visualization, with CartoDB: https://ben-coppersmith.cartodb.com/viz/96aab120-06ff-11e5-a99e-0e018d66dc29/public_map
