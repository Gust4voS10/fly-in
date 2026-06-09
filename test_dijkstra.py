from core.graph import Graph
from core.zone import Zone
from core.connection import Connection
from algorithms.dijkstra import Dijkstra

g = Graph()

g.add_zone(Zone(name='start', x=0, y=0))

g.add_zone(Zone(name='A', x=1, y=0, zone_type='restricted'))

g.add_zone(Zone(name='B', x=0, y=1))

g.add_zone(Zone(name='C', x=1, y=1))

g.add_zone(Zone(name='end', x=2, y=0))

# Conexoes

g.add_connection(Connection(zone1='start', zone2='A'))

g.add_connection(Connection(zone1='A', zone2='end'))


g.add_connection(Connection(zone1='start', zone2='B'))

g.add_connection(Connection(zone1='B', zone2='C'))

g.add_connection(Connection(zone1='C', zone2='end'))

# Executar Dijkstra

d = Dijkstra(g)
path = d.find_path('start','end')
print('Found path:', ' -> '.join(path))
