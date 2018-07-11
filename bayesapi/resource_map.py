from bayesapi.resources import peers
from bayesapi.resources import anomalies
from bayesapi.resources import explanation
from bayesapi.resources import tabledata
from bayesapi.resources import associated_columns

resources = [
    { 'path': '/find-peers',
      'resource_class': peers.PeersResource },
    { 'path': '/find-anomalies',
      'resource_class': anomalies.AnomaliesResource },
    { 'path': '/last-query',
      'resource_class': explanation.LastQueryResource },
    { 'path': '/table-data',
      'resource_class': tabledata.TableDataResource },
    { 'path': '/peer-heatmap-data',
      'resource_class': explanation.PeerHeatmapDataResource },
    { 'path': '/anomaly-scatterplot-data',
      'resource_class': explanation.AnomalyScatterplotDataResource },
    { 'path': '/find-associated-columns',
      'resource_class': associated_columns.AssociatedColumnsResource }
]
