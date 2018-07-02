from bayesapi.resources import peers
from bayesapi.resources import anomalies
from bayesapi.resources import explanation
from bayesapi.resources import tabledata

resources = [
    { 'path': '/find-peers',
      'resource_class': peers.PeersResource },
    { 'path': '/find-anomalies',
      'resource_class': anomalies.AnomaliesResource },
    { 'path': '/last-query',
      'resource_class': explanation.LastQueryResource },
    { 'path': '/table-data',
      'resource_class': tabledata.TableDataResource }
]
