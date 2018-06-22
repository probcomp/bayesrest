from bayesapi.resources import peers
from bayesapi.resources import anomalies

resources = [
    { 'path': '/find-peers',
      'resource_class': peers.PeersResource },
    { 'path': '/find-anomalies',
      'resource_class': anomalies.AnomaliesResource }
]
