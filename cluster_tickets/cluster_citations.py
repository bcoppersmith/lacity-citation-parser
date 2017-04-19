import argparse
import json
import numpy
import pandas
import sys
from sklearn.cluster import DBSCAN
from geopy.distance import great_circle
from shapely.geometry import MultiPoint

kms_per_radian = 6371.0088
parser = argparse.ArgumentParser()

parser.add_argument(
  "--citations", dest="citations", required=True,
  help="Specify the location of pre-processed citation data to cluster",
  metavar="FILE"
)

parser.add_argument(
  "--violations", dest="violations", required=False,
  help="Specify which violations codes to cluster; provide as comma-delimited list.",
  type=str
)

def centroid(cluster):
  return (MultiPoint(cluster).centroid.x, MultiPoint(cluster).centroid.y)

args = parser.parse_args()

skinny_citations = pandas.read_table(
  args.citations,
  sep="\t",
  header=0,
  index_col=0,
  usecols=[0,2,8,9] # ticket ID, violation code, lat, lng
)

if args.violations:
  violation_codes = args.violations.split(",")
  skinny_citations = skinny_citations[skinny_citations.violation_code.isin(violation_codes)]

sys.stderr.write("Imported " + str(len(skinny_citations.index)) + " rows\n")

citation_points= skinny_citations.as_matrix(columns = ['longitude', 'latitude'])

db = DBSCAN(eps=0.0002, min_samples=1, algorithm='ball_tree', metric='haversine').fit(citation_points)
cluster_labels = db.labels_
num_clusters = len(set(cluster_labels))

clusters = pandas.Series([
  [citation_points[cluster_labels == n], skinny_citations.index[cluster_labels == n]]
  for n in range(num_clusters)
])

for n in range(num_clusters):
  points = citation_points[cluster_labels == n]
  ticket_ids = skinny_citations.index[cluster_labels == n].tolist()
  center = centroid(points)

  print json.dumps({
    "centroid": center,
    "points": points.tolist(),
    "ticket_ids": ticket_ids,
    "count": len(ticket_ids)
  })

sys.stderr.write('Estimated number of clusters: %d\n' % num_clusters)
sys.stderr.write('Estimated number of clustered tickets: %d\n' % len(cluster_labels))
