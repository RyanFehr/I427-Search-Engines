from math import sqrt

import pickle
from operator import attrgetter
from queue import Queue

from geopy.geocoders import Nominatim

ROADS_ADJACENCY_LIST = dict()
CITIES = dict()


class City(object):
    # constructor for Node objects
    def __init__(self, name, parent):
        self.name = name
        self.parent = parent
        self.cost = 0

    # method to print City objects
    def str(self):
        return "Name: " + self.name + " Cost: " + str(self.cost)


class Road(object):
    # constructor for Node objects
    def __init__(self, name, dist):
        self.name = name
        self.distance = dist

    # method to print City objects
    def str(self):
        return "Name: " + self.name + " Length: " + str(self.distance)


def construct_adjacency_list():
    file_roads = open("road-segments.txt", "r")

    global ROADS_ADJACENCY_LIST
    global CITIES
    road = file_roads.readline()
    while road != "":
        road = road.split(" ")

        start_city = City(road[0], road[0])
        end_city = City(road[1], road[1])

        road = Road(road[3][:-1], road[2])

        # Adjacency list format:
        # city1.name : List( (city2.name, road(name, cost)), )

        # Cities format:
        # city.name: City(Object)

        if start_city.name in ROADS_ADJACENCY_LIST:
            if start_city.name not in CITIES:
                CITIES[start_city.name + ""] = start_city
            ROADS_ADJACENCY_LIST[start_city.name + ""].append((end_city.name, road))
        else:
            CITIES[start_city.name + ""] = start_city
            ROADS_ADJACENCY_LIST[start_city.name + ""] = list()
            ROADS_ADJACENCY_LIST[start_city.name + ""].append((end_city.name, road))

        if end_city.name in ROADS_ADJACENCY_LIST:
            if end_city not in CITIES:
                CITIES[end_city.name + ""] = end_city
            ROADS_ADJACENCY_LIST[end_city.name + ""].append((start_city.name, road))
        else:
            CITIES[end_city.name + ""] = end_city
            ROADS_ADJACENCY_LIST[end_city.name + ""] = list()
            ROADS_ADJACENCY_LIST[end_city.name + ""].append((start_city.name, road))

        road = file_roads.readline()
    with open('roads.pickle', 'wb') as rp:
        pickle.dump(ROADS_ADJACENCY_LIST, rp)
    with open('cities.pickle', 'wb') as cp:
        pickle.dump(CITIES, cp)


def load_adjacency_list():
    global ROADS_ADJACENCY_LIST
    global CITIES
    try:
        ROADS_ADJACENCY_LIST_PICKLE = open('roads.pickle', 'rb')
        ROADS_ADJACENCY_LIST = pickle.load(ROADS_ADJACENCY_LIST_PICKLE)
        CITIES_PICKLE = open('cities.pickle', 'rb')
        CITIES = pickle.load(CITIES_PICKLE)
    except FileNotFoundError:
        construct_adjacency_list()


def find_node_to_explore(frontier):
    return min(frontier, key=attrgetter('cost'))


def expand_frontier(to_explore, frontier, explored, adjacencyMatrix, goal_state):
    global CITIES
    frontier.remove(to_explore)

    # city (city.name, road(name, cost))
    for city in adjacencyMatrix[to_explore.name]:  # List of connecting cities
        road = city[1]
        newCost = to_explore.cost + int(road.distance)  # New Cost to get to city
        end_city = CITIES[city[0]]
        if end_city in frontier:
            if newCost < end_city.cost:
                end_city.cost = newCost
                end_city.parent = to_explore
        elif end_city in explored:
            if newCost < end_city.cost:
                end_city.cost = newCost
                end_city.parent = to_explore
                explored.remove(end_city)
                frontier.add(end_city)
        else:
            end_city.cost = newCost
            end_city.parent = to_explore
            frontier.add(end_city)

    return frontier


# feel free to turn debugging (printing) on/off as you wish
def uniform_cost_search(adjacencyMatrix, startNode, goalNode, debug=False):
    global ROADS_ADJACENCY_LIST
    startNode.cost = 0
    startNode.parent = None
    frontier = set()
    frontier.add(startNode)
    explored = set()
    path = []
    found = False

    while (len(frontier) > 0):
        nextExplore = find_node_to_explore(frontier)
        explored.add(nextExplore)
        if nextExplore == goalNode:
            found = True
            break
        expand_frontier(nextExplore, frontier, explored, adjacencyMatrix, goalNode)

        # printing procedure to see your progress
        if (debug):
            print("frontier:")
            for node in frontier:
                print(node.str())
            print("explored:")
            for node in explored:
                print(node.str())

    # Once search is finished, show results
    if found:

        # Build route
        miles = 0
        city = goalNode
        while city.parent != None:
            path.append(city)
            city = city.parent
        path.append(city)
        path.reverse()

        # Connect cities with roads
        for i in range(0, len(path) - 1):
            start_city = path.__getitem__(i)
            end_city = path.__getitem__(i + 1)
            connecting_road = None

            # Determine connecting_road
            roads = ROADS_ADJACENCY_LIST[start_city.name]
            for road in roads:
                if road[0] == end_city.name:
                    connecting_road = road[1]

            directions = "From " + start_city.name + " take " + connecting_road.name + " for " + connecting_road.distance + " miles to " + end_city.name
            print(directions)
            miles += int(connecting_road.distance)
        print("Total route segments:", len(path))
        print("Total travel distance:", miles, "miles")
        # print()
        # print("frontier:")
        # for node in frontier:
        #     print(node.str())
        # print("explored:")
        # for node in explored:
        #     print(node.str())
        # print("We found the goal!")
        return path
    else:
        print("Goal not found :(")
        return None


def expand_frontier_bfs(to_explore, frontier, frontier_queue, explored, adjacencyMatrix, goal_state):
    global CITIES
    frontier.remove(to_explore)

    # city (city.name, road(name, cost))
    for city in adjacencyMatrix[to_explore.name]:  # List of connecting cities
        road = city[1]
        newCost = to_explore.cost + int(road.distance)  # New Cost to get to city
        end_city = CITIES[city[0]]
        if end_city in frontier:
            if newCost < end_city.cost:
                end_city.cost = newCost
                end_city.parent = to_explore
        elif end_city in explored:
            if newCost < end_city.cost:
                end_city.cost = newCost
                end_city.parent = to_explore
                explored.remove(end_city)
                frontier.add(end_city)
                frontier_queue.put(end_city)
        else:
            end_city.cost = newCost
            end_city.parent = to_explore
            frontier.add(end_city)
            frontier_queue.put(end_city)

    return frontier


# feel free to turn debugging (printing) on/off as you wish
def breadth_first_search(adjacencyMatrix, startNode, goalNode, debug=False):
    global ROADS_ADJACENCY_LIST
    startNode.cost = 0
    startNode.parent = None
    frontier_queue = Queue()
    frontier_queue.put(startNode)
    frontier = set()
    frontier.add(startNode)
    explored = set()
    path = []
    found = False

    while (len(frontier) > 0):
        nextExplore = frontier_queue.get()
        explored.add(nextExplore)
        if nextExplore == goalNode:
            found = True
            break
        expand_frontier_bfs(nextExplore, frontier, frontier_queue, explored, adjacencyMatrix, goalNode)

        # printing procedure to see your progress
        if (debug):
            print("frontier:")
            for node in frontier:
                print(node.str())
            print("explored:")
            for node in explored:
                print(node.str())

    # Once search is finished, show results
    if found:

        # Build route
        miles = 0
        city = goalNode
        while city.parent != None:
            path.append(city)
            city = city.parent
        path.append(city)
        path.reverse()

        # Connect cities with roads
        for i in range(0, len(path) - 1):
            start_city = path.__getitem__(i)
            end_city = path.__getitem__(i + 1)
            connecting_road = None

            # Determine connecting_road
            roads = ROADS_ADJACENCY_LIST[start_city.name]
            for road in roads:
                if road[0] == end_city.name:
                    connecting_road = road[1]

            directions = "From " + start_city.name + " take " + connecting_road.name + " for " + connecting_road.distance + " miles to " + end_city.name
            print(directions)
            miles += int(connecting_road.distance)
        print("Total route segments:", len(path))
        print("Total travel distance:", miles, "miles")
        # print()
        # print("frontier:")
        # for node in frontier:
        #     print(node.str())
        # print("explored:")
        # for node in explored:
        #     print(node.str())
        # print("We found the goal!")
        return path
    else:
        print("Goal not found :(")
        return None


def expand_frontier_dfs(to_explore, frontier, explored, adjacencyMatrix, goal_state):
    global CITIES

    # city (city.name, road(name, cost))
    for city in adjacencyMatrix[to_explore.name]:  # List of connecting cities
        road = city[1]
        newCost = to_explore.cost + int(road.distance)  # New Cost to get to city
        end_city = CITIES[city[0]]
        if end_city in frontier:
            if newCost < end_city.cost:
                end_city.cost = newCost
                end_city.parent = to_explore
        elif end_city in explored:
            if newCost < end_city.cost:
                end_city.cost = newCost
                end_city.parent = to_explore
                explored.remove(end_city)
                frontier.append(end_city)
        else:
            end_city.cost = newCost
            end_city.parent = to_explore
            frontier.append(end_city)

    return frontier


# feel free to turn debugging (printing) on/off as you wish
def depth_first_search(adjacencyMatrix, startNode, goalNode, debug=False):
    global ROADS_ADJACENCY_LIST
    startNode.cost = 0
    startNode.parent = None
    frontier = []
    frontier.append(startNode)
    explored = set()
    path = []
    found = False

    while (len(frontier) > 0):
        nextExplore = frontier.pop()
        explored.add(nextExplore)
        if nextExplore == goalNode:
            found = True
            break
        expand_frontier_dfs(nextExplore, frontier, explored, adjacencyMatrix, goalNode)

        # printing procedure to see your progress
        if (debug):
            print("frontier:")
            for node in frontier:
                print(node.str())
            print("explored:")
            for node in explored:
                print(node.str())

    # Once search is finished, show results
    if found:

        # Build route
        miles = 0
        city = goalNode
        while city.parent != None:
            path.append(city)
            city = city.parent
        path.append(city)
        path.reverse()

        # Connect cities with roads
        for i in range(0, len(path) - 1):
            start_city = path.__getitem__(i)
            end_city = path.__getitem__(i + 1)
            connecting_road = None

            # Determine connecting_road
            roads = ROADS_ADJACENCY_LIST[start_city.name]
            for road in roads:
                if road[0] == end_city.name:
                    connecting_road = road[1]

            directions = "From " + start_city.name + " take " + connecting_road.name + " for " + connecting_road.distance + " miles to " + end_city.name
            print(directions)
            miles += int(connecting_road.distance)
        print("Total route segments:", len(path))
        print("Total travel distance:", miles, "miles")
        # print()
        # print("frontier:")
        # for node in frontier:
        #     print(node.str())
        # print("explored:")
        # for node in explored:
        #     print(node.str())
        # print("We found the goal!")
        return path
    else:
        print("Goal not found :(")
        return None


def search_for_route(starting_city, destination_city, search_method):
    print("\nTraveling from", starting_city.name, "to", destination_city.name, "using", search_method)
    if (search_method == "dfs"):
        depth_first_search(ROADS_ADJACENCY_LIST, starting_city, destination_city)
    if (search_method == "bfs"):
        breadth_first_search(ROADS_ADJACENCY_LIST, starting_city, destination_city)
    if (search_method == "best"):
        uniform_cost_search(ROADS_ADJACENCY_LIST, starting_city, destination_city)


def test_search_methods():
    # The dfs tests are slightly different, because the nature of a dfs causes the path to be long and take a while to run
    abbott_NM = CITIES["Abbott,_New_Mexico"]
    roy_NM = CITIES["Roy,_New_Mexico"]
    new_albany_IN = CITIES["New_Albany,_Indiana"]
    dumas_TX = CITIES["Dumas,_Texas"]

    search_for_route(abbott_NM, roy_NM, "best")
    search_for_route(abbott_NM, roy_NM, "bfs")
    search_for_route(abbott_NM, dumas_TX, "dfs")

    search_for_route(new_albany_IN, roy_NM, "best")
    search_for_route(new_albany_IN, roy_NM, "bfs")
    # search_for_route(new_albany_IN, roy_NM, "dfs")


def main():
    load_adjacency_list()
    # test_search_methods()

    albany_NY = CITIES["Albany,_New_York"]
    roy_NM = CITIES["Roy,_New_Mexico"]
    new_albany_IN = CITIES["New_Albany,_Indiana"]
    dumas_TX = CITIES["Dumas,_Texas"]

    search_for_route(albany_NY, new_albany_IN, "best")

main()
