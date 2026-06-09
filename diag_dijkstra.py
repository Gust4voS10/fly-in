from parser.parser import Parser
from algorithms.dijkstra import Dijkstra

def zone_cost(zone):
    return 2 if zone.zone_type=='restricted' else 1

p = Parser('test.txt')
g = p.parse()
print('Zones:')
for name,z in g.zones.items():
    print(f" - {name}: type={z.zone_type}, max_drones={z.max_drones}")

D = Dijkstra(g)
path = D.find_path(g.start_zone, g.end_zone)
print('\nFound path:', ' -> '.join(path))
# compute total cost
cost = 0
for zname in path[1:]:
    cost += zone_cost(g.zones[zname])
print('Total cost:', cost)
