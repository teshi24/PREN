from typing import Dict, Type
import heapq
from src.frame_analyzer.position_analyzer import PositionIdentifier

# end_positions_percentages: Dict[int, End_Result] = {
#     1: starting_point.copy(),
#     2: starting_point.copy(),
#     3: starting_point.copy(),
#     4: starting_point.copy(),
#     5: starting_point.copy(),
#     6: starting_point.copy(),
#     7: starting_point.copy(),
#     8: starting_point.copy(),
# }
#

defaultConfig: Dict[int, Type[PositionIdentifier | None]] = {
    1: None,
    2: None,
    3: None,
    4: None,
    5: None,
    6: None,
    7: None,
    8: None
}


def print_graph(graph):
    print(graph)
    for node in graph.get_nodes():
        print(node)
        print(graph.get_edges(node))
    pass


position_graph = {
    'redC': [('blueA', 0), ('yellowD', 0),
             ('redD', 25), ('redA', 50), ('redB', 75)],
    'redD': [('blueB', 0), ('yellowA', 0),
             ('redA', 25), ('redB', 50), ('redC', 75)],
    'redA': [('blueC', 0), ('yellowB', 0),
             ('redB', 25), ('redC', 50), ('redD', 75)],
    'redB': [('blueD', 0), ('yellowC', 0),
             ('redA', 25), ('redB', 50), ('redC', 75)],
    'blueA': [('redC', 0), ('yellowD', 0),
              ('blueB', 25), ('blueC', 50), ('blueD', 75)],
    'blueB': [('redD', 0), ('yellowA', 0),
              ('blueC', 25), ('blueD', 50), ('blueA', 75)],
    'blueC': [('redA', 0), ('yellowB', 0),
              ('blueD', 25), ('blueA', 50), ('blueB', 75)],
    'blueD': [('redB', 0), ('yellowC', 0),
              ('blueA', 25), ('blueB', 50), ('blueC', 75)],
    'yellowD': [('redC', 0), ('blueA', 0),
                ('yellowA', 25), ('yellowB', 50), ('yellowC', 75)],
    'yellowA': [('redD', 0), ('blueB', 0),
                ('yellowB', 25), ('yellowC', 50), ('yellowD', 75)],
    'yellowB': [('redA', 0), ('blueC', 0),
                ('yellowC', 25), ('yellowD', 50), ('yellowA', 75)],
    'yellowC': [('redB', 0), ('blueD', 0),
                ('yellowD', 25), ('yellowA', 50), ('yellowB', 75)],
}


def find_best_path(positions):
    start_node = 'redA'
    goal_node = 'yellowB'
    ## should be direct and 0 - it is, just total costs are fucked up
    start_node = 'redA'
    goal_node = 'yellowC'
    # ## should be over yellowB 0 and yellowC = 25 - it is
    start_node = 'blueA'
    goal_node = 'blueD'
    # ## should be direct and 75 - it was
    start_node = 'yellowB'
    goal_node = 'redD'
    # ## should be over redA 0 and redD = 75
    start_node = 'yellowD'
    goal_node = 'redB'
    # should be 75

    total_cost, path_with_costs = bidirectional_uniform_cost_search_with_costs(position_graph, start_node, goal_node)
    if path_with_costs:
        print("Total Cost from", start_node, "to", goal_node, ":", total_cost)
        print("Path with Step Costs:")
        for node, step_cost in path_with_costs:
            print("Node:", node, "- Step Cost:", step_cost)
    else:
        print("No path found from", start_node, "to", goal_node)


def bidirectional_uniform_cost_search_with_costs(graph, start, goal):
    # Priority queues for forward and backward searches
    forward_frontier = [(0, start)]  # (cost, node) for forward search
    forward_cost_so_far = {start: 0}

    # Dictionaries to store the parent node of each node in the final path from both directions
    forward_came_from = {}
    forward_current_node = start

    while forward_frontier and forward_current_node is not goal:
        # Forward search
        forward_current_cost, forward_current_node = heapq.heappop(forward_frontier)

        for next_node, cost in graph[forward_current_node]:
            new_cost = forward_current_cost + cost
            if next_node not in forward_cost_so_far or new_cost < forward_cost_so_far[next_node]:
                forward_cost_so_far[next_node] = new_cost
                heapq.heappush(forward_frontier, (new_cost, next_node))
                forward_came_from[next_node] = (forward_current_node, cost)

    # Reconstruct the path from start to goal
    forward_path = []
    print(f'forward_cost_so_far {forward_cost_so_far}')
    print(f'forward_cost_so_far.values() {forward_cost_so_far.values()}')
    print(f'forward_came_from {forward_came_from}')
    total_cost = sum(forward_cost_so_far.values())
    # Construct forward path
    current_node = goal
    while current_node in forward_came_from:
        parent_node, step_cost = forward_came_from[current_node]
        forward_path.insert(0, (current_node, step_cost))
        current_node = parent_node
        ## todo: add up costs here
    forward_path.insert(0, (start, 0))  # Add start node with cost 0

    print(forward_path)
    return total_cost, forward_path
