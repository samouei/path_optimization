#!/usr/bin/env python3

from util import read_osm_data, great_circle_distance, to_local_kml_url

# NO ADDITIONAL IMPORTS!


ALLOWED_HIGHWAY_TYPES = {
    'motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'unclassified',
    'residential', 'living_street', 'motorway_link', 'trunk_link',
    'primary_link', 'secondary_link', 'tertiary_link',
}


DEFAULT_SPEED_LIMIT_MPH = {
    'motorway': 60,
    'trunk': 45,
    'primary': 35,
    'secondary': 30,
    'residential': 25,
    'tertiary': 25,
    'unclassified': 25,
    'living_street': 10,
    'motorway_link': 30,
    'trunk_link': 30,
    'primary_link': 30,
    'secondary_link': 30,
    'tertiary_link': 25,
}


def build_auxiliary_structures(nodes_filename, ways_filename):
    """
    Create any auxiliary structures you are interested in, by reading the data
    from the given filenames (using read_osm_data)
    ways = {way_id: {'nodes': [id, id], 'tags':{'maxspeed_mph':x, 'oneway':y, 'highway': z}}}
    nodes = {node_id: {'neighbors': {id, id}, 'lat': #, 'lon': #}}
    """

    ways = {} # ways = {way_id: {'nodes': [id, id], 'tags':{x:y, u:z}}}
    nodes = {} # nodes = {node_id: {'neighbors': {id, id}, 'lat': #, 'lon': #}}
    max_speed_dic = {}
    
    # Make data structure for allowed highways
    for w in read_osm_data(ways_filename):        
        if 'highway' in w['tags'] and w['tags']['highway'] in ALLOWED_HIGHWAY_TYPES:
            
            ways[w['id']] = {
                            'nodes': w['nodes'], 
                            'tags': {'maxspeed_mph': w['tags'].get('maxspeed_mph', DEFAULT_SPEED_LIMIT_MPH[w['tags']['highway']] ),
                                      'oneway': w['tags'].get('oneway', None),
                                      'highway': w['tags'].get('highway', None)}
                            }
    
            i = w['id']
        
            for j in range(len(ways[i]['nodes'])): # go through the nodes connected by that way
                # Initialize all the nodes
                if ways[i]['nodes'][j] not in nodes:
                    nodes[ways[i]['nodes'][j]] = {'neighbors': set(), 'lat': None, 'lon': None}
      
                  
            for j in range(len(ways[i]['nodes']) - 1): # go through the nodes connected by that way
                # One-way roads
                # If one-way key exists and is yes
                if 'oneway' in ways[i]['tags'] and ways[i]['tags']['oneway'] == 'yes':   
                    nodes[ways[i]['nodes'][j]]['neighbors'].add(ways[i]['nodes'][j + 1])
                    
                    
                    max_speed_dic[( w['nodes'][j], w['nodes'][j + 1] )] = ways[i]['tags']['maxspeed_mph']
                    
                    
                # Two-way roads
                else:
                    nodes[ways[i]['nodes'][j]]['neighbors'].add(ways[i]['nodes'][j + 1])  
                    nodes[ways[i]['nodes'][j + 1]]['neighbors'].add(ways[i]['nodes'][j])
                    
                    max_speed_dic[( w['nodes'][j], w['nodes'][j + 1] )] = ways[i]['tags']['maxspeed_mph']
                    max_speed_dic[( w['nodes'][j + 1], w['nodes'][j] )] = ways[i]['tags']['maxspeed_mph']

    # Get nodes' lat and lon
    for n in read_osm_data(nodes_filename):  
        if n['id'] in nodes:
            nodes[n['id']]['lat'] = n['lat']
            nodes[n['id']]['lon'] = n['lon']
                
    return nodes, ways, max_speed_dic



def find_nearest_node_id(aux_structures, loc):
    """
    Returns the node ID for the nearest node next to loc (chosen from all the valid nodes).
    loc: tuple of 2 floats: (latitude, longitude)
    """
    nodes, ways, max_speed_dic = aux_structures
    distances = {}
    
    # Map node IDs to distances
    for n in nodes:
        lat, lon = nodes[n]['lat'],nodes[n]['lon']
        distances[n] = great_circle_distance(loc, (lat, lon))
     
    # Find min distance
    min_distance = min(distances.values())
    
    # Get node ID with min distance
    for node_id, distance in distances.items():
        if distance == min_distance:
            return node_id


def map_node_id_to_coordinates(aux_structures, node):
    """
    Maps node IDs to lat and lon.
    Returns a dictionary of the format: {node_id: (lat, lon)}
    """    
    nodes, ways, max_speed_dic = aux_structures

    return (nodes[node]['lat'], nodes[node]['lon'])


def get_nearest_node_id(aux_structures, nodes, n1):
    """
    Returns the node ID for the nearest node next to n1 from a set of nodes.
    n1: node ID.
    nodes: set containing node IDs.
    """    
    id_coordinate_map = map_node_id_to_coordinates(aux_structures)
    distances = {}
    
    # Map node IDs to distances
    for n in nodes:
        distances[n] = great_circle_distance(loc, id_coordinate_map[n])

    # Find min distance
    min_distance = min(distances.values())
    
    # Get node ID with min distance
    for node_id, distance in distances.items():
        if distance == min_distance:
            return node_id   

        
def calculate_distance(aux_structures, start, end):
    """
    Returns the distance between two nodes.
    start and end are node IDs.
    """   
    
    start_id_to_coordinate = map_node_id_to_coordinates(aux_structures, start)
    end_id_to_coordinate = map_node_id_to_coordinates(aux_structures, end)
    
    distance = great_circle_distance(start_id_to_coordinate, end_id_to_coordinate)
    return distance


            

#def get_speed(aux_structures, start, end):
#    """
#    Returns the speed limit between two nodes.
#    start and end are node IDs.
#    """   
#        
##    ways = {way_id: {'nodes': [id, id], 'tags':{'maxspeed_mph':x, 'oneway':y, 'highway': z}}}
##    nodes = {node_id: {'neighbors': {id, id}, 'lat': #, 'lon': #}}
#    
#    nodes, ways, max_speed_dic = aux_structures
#    costs = set()
#    for w in ways:
#        if start in ways[w]['nodes'] and end in ways[w]['nodes']:
#            
#            # Check for 'maxspeed_mph' value
#            if ways[w]['tags']['maxspeed_mph'] != None:
#                costs.add(calculate_distance(aux_structures, start, end) / ways[w]['tags']['maxspeed_mph'])
#            
#            # If no 'maxspeed_mph' tag, get default value
#            else:
#                costs.add(calculate_distance(aux_structures, start, end) / DEFAULT_SPEED_LIMIT_MPH[ways[w]['tags']['highway']])
#
#    return min(costs)
    

    
def get_lowest_cost_path(paths):
    """
    Gets the path with the lowest cost from a set of paths.
    paths is a set of format: {((node_1,..., node_n), cost)}.
    Returns path with format: ((node, node, node), cost).
    """  
    
    return min(paths, key = lambda t: t[1])


def construct_path(aux_structures, node_ids):
    """
    Given a tuple of node IDs, creates a path with corresponding lat, lon values.
    Returns a list of (latitude, longitude) tuples representing the path.
    """  
    nodes, ways, max_speed_dic = aux_structures
    path = []
    for id_ in node_ids:
        path.append(map_node_id_to_coordinates(aux_structures, id_))
    return path

            

def find_short_path(aux_structures, loc1, loc2, speed = False):
    """
    Return the shortest path between the two locations

    Parameters:
        aux_structures: the result of calling build_auxiliary_structures:        
            ways = {way_id: {'nodes': [id, id], 'tags':{'maxspeed_mph':x, 'oneway':y, 'highway': z}}}
            nodes = {node_id: {'neighbors': {id, id}, 'lat': #, 'lon': #}}
        loc1: tuple of 2 floats: (latitude, longitude), representing the start
              location
        loc2: tuple of 2 floats: (latitude, longitude), representing the end
              location

    Returns:
        a list of (latitude, longitude) tuples representing the shortest path
        (in terms of distance) from loc1 to loc2.
    """
#################
    
# Heuristics:
    
# agenda = { ((n_1,), calculate_distance(aux_structures, n_1, n_2)) } 
# agenda.add((path_ids+(child,) , cost 
#                                + calculate_distance(aux_structures, term_vertex, child) 
#                                + calculate_distance(aux_structures, child, n_2))
#                                ) 

#################


    nodes, ways, max_speed_dic = aux_structures 


    n_1 = find_nearest_node_id(aux_structures, loc1) #id
    n_2 = find_nearest_node_id(aux_structures, loc2) #id

    
    agenda = { ((n_1,), 0) } 
    expanded = set() 

#    counter = 0    
    while agenda:
        
        # Remove the path with lowest cost from agenda
        lowest_cost_path = get_lowest_cost_path(agenda)    
        path_ids, cost = lowest_cost_path
        agenda.remove(lowest_cost_path)
#        counter += 1

        # Ignore path's terminal vertex if in expanded set 
        term_vertex = path_ids[-1]
        if term_vertex in expanded:
            continue
        
        # Check if path's terminal vertex satisfies the goal 
        # Otherwise, add its terminal vertex to expanded
        if term_vertex == n_2:
#            print(counter)
            return construct_path(aux_structures, path_ids)         
        else:
            expanded.add(term_vertex)
                 
        # For each of the children of path's terminal vertex
        for child in nodes[term_vertex]['neighbors']:  
            
            # Skip if in expanded 
            if child in expanded:
                continue
            
            # Add path and cost to agenda
            else:
                if speed:
                    agenda.add((path_ids+(child,) , cost +  calculate_distance(aux_structures, term_vertex, child) / max_speed_dic[(term_vertex, child)])) 
                else:
                    agenda.add((path_ids+(child,) , cost + calculate_distance(aux_structures, term_vertex, child))) 
            
    return None

def find_short_path(aux_structures, loc1, loc2, speed = False):
    """
    Return the shortest path between the two locations

    Parameters:
        aux_structures: the result of calling build_auxiliary_structures:        
            ways = {way_id: {'nodes': [id, id], 'tags':{'maxspeed_mph':x, 'oneway':y, 'highway': z}}}
            nodes = {node_id: {'neighbors': {id, id}, 'lat': #, 'lon': #}}
        loc1: tuple of 2 floats: (latitude, longitude), representing the start
              location
        loc2: tuple of 2 floats: (latitude, longitude), representing the end
              location

    Returns:
        a list of (latitude, longitude) tuples representing the shortest path
        (in terms of distance) from loc1 to loc2.
    """
#################
    
# Heuristics:
    
# agenda = { ((n_1,), calculate_distance(aux_structures, n_1, n_2)) } 
# agenda.add((path_ids+(child,) , cost 
#                                + calculate_distance(aux_structures, term_vertex, child) 
#                                + calculate_distance(aux_structures, child, n_2))
#                                ) 

#################


    nodes, ways, max_speed_dic = aux_structures 


    n_1 = find_nearest_node_id(aux_structures, loc1) #id
    n_2 = find_nearest_node_id(aux_structures, loc2) #id

    
    agenda = { ((n_1,), 0) } 
    expanded = set() 

#    counter = 0    
    while agenda:
        
        # Remove the path with lowest cost from agenda
        lowest_cost_path = get_lowest_cost_path(agenda)    
        path_ids, cost = lowest_cost_path
        agenda.remove(lowest_cost_path)
#        counter += 1

        # Ignore path's terminal vertex if in expanded set 
        term_vertex = path_ids[-1]
        if term_vertex in expanded:
            continue
        
        # Check if path's terminal vertex satisfies the goal 
        # Otherwise, add its terminal vertex to expanded
        if term_vertex == n_2:
#            print(counter)
            return construct_path(aux_structures, path_ids)         
        else:
            expanded.add(term_vertex)
                 
        # For each of the children of path's terminal vertex
        for child in nodes[term_vertex]['neighbors']:  
            
            # Skip if in expanded 
            if child in expanded:
                continue
            
            # Add path and cost to agenda
            else:
                if speed:
                    agenda.add((path_ids+(child,) , cost +  calculate_distance(aux_structures, term_vertex, child) / max_speed_dic[(term_vertex, child)])) 
                else:
                    agenda.add((path_ids+(child,) , cost + calculate_distance(aux_structures, term_vertex, child))) 
            
    return None

def find_fast_path(aux_structures, loc1, loc2):
    """
    Return the shortest path between the two locations, in terms of expected
    time (taking into account speed limits).

    Parameters:
        aux_structures: the result of calling build_auxiliary_structures:
            ways = {way_id: {'nodes': [id, id], 'tags':{'maxspeed_mph':x, 'oneway':y, 'highway': z}}}
            nodes = {node_id: {'neighbors': {id, id}, 'lat': #, 'lon': #}}
        loc1: tuple of 2 floats: (latitude, longitude), representing the start
              location
        loc2: tuple of 2 floats: (latitude, longitude), representing the end
              location

    Returns:
        a list of (latitude, longitude) tuples representing the shortest path
        (in terms of time) from loc1 to loc2.
    """

    return find_short_path(aux_structures, loc1, loc2, speed = True)




if __name__ == '__main__':
    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used, for example, to generate the results for the online questions.
    pass

    
  #######################################################

    #### 2.1 Test 1: Printing out nodes and ways ####

#    nodes = 0
#    for node in read_osm_data('resources/cambridge.nodes'):
#        nodes += 1
#    print("Number of Nodes:",nodes)
    
    
#    counter = 0
#    for node in read_osm_data('resources/cambridge.nodes'):
#        if 'name' in node['tags']:
#            counter += 1
#    print("Number of Nodes with Names:",counter)
    
    
#    for node in read_osm_data('resources/cambridge.nodes'):
#        if 'name' in node['tags'] and node['tags']['name'] == '77 Massachusetts Ave':
#            print("ID Number:",node['id'])
    

#    ways = 0
#    for way in read_osm_data('resources/cambridge.ways'):
#        ways += 1
#    print("Number of Ways:",ways)  
    
    
#    one_way_streets = 0
#    for way in read_osm_data('resources/cambridge.ways'):
#        if 'oneway' in way['tags'] and way['tags']['oneway'] == 'yes':
#            one_way_streets += 1
#        continue
#    print("Number of Oneway Streets:",one_way_streets)
    
  #######################################################

    #### *3.1.1 Test 1: Number of Allowed Highways ####

#    highways = 0
#    for way in read_osm_data('resources/cambridge.ways'):
#        if 'highway' in way['tags'] and way['tags']['highway'] in ALLOWED_HIGHWAY_TYPES:
#            highways += 1
#    print("Number of Allowed Highways:",highways) 
    
  #######################################################

    #### 3.1.3 Test 1: Testing great_circle_distance ####
    
#    loc_1 = (42.363745, -71.100999)
#    loc_2 = (42.361283, -71.239677)
#    print("Distance is:",great_circle_distance(loc_1, loc_2))

    #### 3.1.3 Test 2: Testing great_circle_distance on midwest dataset ####
    
#    id_1 = 233941454
#    id_2 = 233947199
#    for node in read_osm_data('resources/midwest.nodes'):
#        if node['id'] == id_1:
#            loc_1 = (node['lat'], node['lon'])
#        if node['id'] == id_2:
#            loc_2 = (node['lat'], node['lon'])   
#    print("Distance is:",great_circle_distance(loc_1, loc_2))      
    
    #### 3.1.3 Test 3: Testing great_circle_distance on ID number 21705939 ####
    
#    id_1 = 21705939
#    nodes = []
#    locations = [(41.447604, -89.393558), (41.447601, -89.394215), 
#                 (41.447611, -89.395527), (41.447611, -89.396958), 
#                 (41.447607, -89.402144), (41.447677, -89.403083),
#                 (41.447795, -89.404006), (41.447801, -89.404476), 
#                 (41.447801, -89.404946), (41.447773, -89.407548)]
#    distance = 0
#    for way in read_osm_data('resources/midwest.ways'):
#        if way['id'] == id_1:
#            nodes.append(way['nodes'])
#            print("Nodes are:",way['nodes'])
#            
#    for n in read_osm_data('resources/midwest.nodes'):          
#        if n['id'] == 21705939:               
#            locations.append((n['lat'], n['lon']))
#            
#    for i in range(1, len(locations)):
#        distance += great_circle_distance(locations[i - 1], locations[i])
#    print(distance)   

  #######################################################
    
    #### 3.1.4 Test 1: Finding ID of the nearest node to (41.4452463, -89.3161394) ####
    
#    loc = (41.4452463, -89.3161394)
#    nodes_filename = 'resources/midwest.nodes'
#    ways_filename = 'resources/midwest.ways'
#    aux_structures = build_auxiliary_structures(nodes_filename, ways_filename)
#    print("Nearest node ID is:", find_nearest_node_id(aux_structures, loc))

  #######################################################
    
    #### 4.2 Test 1: Testing the Heuristic ####
    
#    loc1 = (42.3858, -71.0783)
#    loc2 = (42.5465, -71.1787)
#    nodes_filename = 'resources/cambridge.nodes'
#    ways_filename = 'resources/cambridge.ways'
#    aux_structures = build_auxiliary_structures(nodes_filename, ways_filename)  
#    find_short_path(aux_structures, loc1, loc2)
    print("with heuristics:", 76773)
    print("without heuristics:", 386255)
    
     
    
    
    
    
  #######################################################

    #### * Test 1: Number of Oneway Allowed Highways ####

#    ways = {}    
#    for w in read_osm_data('resources/cambridge.ways'):        
#        if 'highway' in w['tags'] and w['tags']['highway'] in ALLOWED_HIGHWAY_TYPES:
#            ways[w['id']] = {'nodes': w['nodes'], 'tags': w['tags']}
#    oneway = []
#    for i in ways:
#        if 'oneway' in ways[i]['tags']:
#            oneway.append(i)
#    print("Number of oneway allowed highways:",len(oneway))
    
    
    
            
