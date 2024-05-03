from typing import Dict, Type
import heapq
from src.frame_analyzer.position_analyzer import PositionIdentifier

## todo: replace with any config, in case we were not able to find a solution
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

position_graph = {
    'blue1': [('yellow2', 0), ('red3', 0),
              ('blue2', 25), ('blue3', 50), ('blue4', 75)],
    'blue2': [('yellow3', 0), ('red4', 0),
              ('blue3', 25), ('blue4', 50), ('blue1', 75)],
    'blue3': [('yellow4', 0), ('red1', 0),
              ('blue4', 25), ('blue1', 50), ('blue2', 75)],
    'blue4': [('yellow1', 0), ('red2', 0),
              ('blue1', 25), ('blue2', 50), ('blue3', 75)],
    'yellow2': [('red3', 0), ('blue1', 0),
                ('yellow3', 25), ('yellow4', 50), ('yellow1', 75)],
    'yellow3': [('red4', 0), ('blue2', 0),
                ('yellow4', 25), ('yellow1', 50), ('yellow2', 75)],
    'yellow4': [('red1', 0), ('blue3', 0),
                ('yellow1', 25), ('yellow2', 50), ('yellow3', 75)],
    'yellow1': [('red2', 0), ('blue4', 0),
                ('yellow2', 25), ('yellow3', 50), ('yellow4', 75)],
    'red3': [('blue1', 0), ('yellow2', 0),
             ('red4', 25), ('red1', 50), ('red2', 75)],
    'red4': [('blue2', 0), ('yellow3', 0),
             ('red1', 25), ('red2', 50), ('red3', 75)],
    'red1': [('blue3', 0), ('yellow4', 0),
             ('red2', 25), ('red3', 50), ('red4', 75)],
    'red2': [('blue4', 0), ('yellow1', 0),
             ('red3', 25), ('red4', 50), ('red1', 75)],
}


def get_goal_positions_by_level(positions, level):
    result = {}
    if level == 0:
        for i in range(1, 5):
            if positions[i]:
                result[i] = positions[i]
    elif level == 1:
        for i in range(5, 9):
            if positions[i]:
                result[i - 4] = positions[i]

    return [value + str(key) for key, value in result.items()]

def find_best_path(positions):
    start_node = 'blue1'
    print(positions)
    level1 = get_goal_positions_by_level(positions, 0)
    print(level1)

    for pos in level1:
        goal_node = pos
        print(f'start {start_node} to goal {goal_node}')
        total_cost, path_with_costs = bidirectional_uniform_cost_search_with_costs(position_graph, start_node, goal_node)
        if path_with_costs:
            print("Total Cost from", start_node, "to", goal_node, ":", total_cost)
            # print("Path with Step Costs:")
            # for node, step_cost in path_with_costs:
            #     print("Node:", node, "- Step Cost:", step_cost)
        else:
            print("No path found from", start_node, "to", goal_node)

    level2 = get_goal_positions_by_level(positions, 1)
    print(level2)
    ## todo: also handle level2

    # start_node = 'red1'
    # goal_node = 'yellow4'
    # ## should be direct and 0 - it is, just total costs are fucked up
    # start_node = 'red1'
    # goal_node = 'yellow1'
    # # ## should be over yellow4 0 and yellow1 = 25 - it is
    # start_node = 'blue1'
    # goal_node = 'blue4'
    # # ## should be direct and 75 - it was
    # start_node = 'yellow4'
    # goal_node = 'red4'
    # # ## should be over red1 0 and red4 = 75
    # start_node = 'yellow2'
    # goal_node = 'red2'
    # should be 75
    #
    # total_cost, path_with_costs = bidirectional_uniform_cost_search_with_costs(position_graph, start_node, goal_node)
    # if path_with_costs:
    #     print("Total Cost from", start_node, "to", goal_node, ":", total_cost)
    #     print("Path with Step Costs:")
    #     for node, step_cost in path_with_costs:
    #         print("Node:", node, "- Step Cost:", step_cost)
    # else:
    #     print("No path found from", start_node, "to", goal_node)


def bidirectional_uniform_cost_search_with_costs(graph, start, goal):
    forward_frontier = [(0, start)]  # (cost, node)
    forward_cost_so_far = {start: 0}

    # Dictionaries to store the parent node of each node in the final path
    forward_came_from = {}
    forward_current_node = start

    while forward_frontier and forward_current_node is not goal:
        forward_current_cost, forward_current_node = heapq.heappop(forward_frontier)

        for next_node, cost in graph[forward_current_node]:
            new_cost = forward_current_cost + cost
            if next_node not in forward_cost_so_far or new_cost < forward_cost_so_far[next_node]:
                forward_cost_so_far[next_node] = new_cost
                heapq.heappush(forward_frontier, (new_cost, next_node))
                forward_came_from[next_node] = (forward_current_node, cost)

    # Reconstruct the path from start to goal
    forward_path = []
    # Construct forward path
    current_node = goal
    total_cost = 0
    while current_node in forward_came_from:
        parent_node, step_cost = forward_came_from[current_node]
        forward_path.insert(0, (current_node, step_cost))
        total_cost += step_cost
        current_node = parent_node
    forward_path.insert(0, (start, 0))  # Add start node with cost 0

    return total_cost, forward_path
