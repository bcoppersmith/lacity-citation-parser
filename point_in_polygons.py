import json
from shapely.geometry import shape

class PointInPolygons:

  def __init__(self, file_name, return_value):
    with open(file_name, 'r') as f:
      js = json.load(f)

    self.polygons = {}
    for feature in js['features']:
      polygon = shape(feature['geometry'])
      self.polygons[feature['properties'][return_value]] = polygon

  def search(self, point):
    for value, polygon in self.polygons.items():
      if polygon.contains(point):
        return value
    return ''
