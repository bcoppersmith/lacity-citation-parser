# Geo Clustering Ticket Data

This script uses the DBSCAN clustering algorithm (from scikit-learn) to cluster ticket data, as processed using the script in the parent directory.

## Usage

Here's an example run-command:

``` bash
$> python cluster_citations.py --citations ../{parsed-tickets}.tab --violations 8702,22514#
```

## Output

The script will output newline-separated JSON for each cluster. It includes the centroid of the cluster, all points in the cluster, the ticket IDs in the cluster, and the number of tickets/points that were clustered. Here's an example:

``` json
{
  "count": 2,
  "points": [
    [-118.267567418, 34.0288392786],
    [-118.267567418, 34.0288392786]
  ],
  "centroid": [-118.267567418, 34.0288392786],
  "ticket_ids": ["1102878873", "1102878921"]
}
```
