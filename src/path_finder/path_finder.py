import logging
import heapq

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
start_nodes_by_position = {
    0: 'blue1',
    25: 'blue2',
    50: 'blue3',
    75: 'blue4',
}
action_mapping = {
    0: 4,  # stay
    25: 1,  # forward 90 degrees
    50: 2,  # forward 180 degrees
    75: 3  # backwards 90 degrees
}
color_mapping = {
    'blue': 1,
    'yellow': 2,
    'red': 3
}


def initialize_start_node(current_position):
    return start_nodes_by_position[current_position]


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


def get_as_commands(costs, start_position):
    logging.debug('------ path_finder.get_as_commands start ------')
    position = start_position
    commands = []
    for action, colors in sorted(costs.items()):
        logging.debug(f'{action}: {colors}')
        colors_len = len(colors)
        if colors_len:
            action_to_take = (action - position) % 100
            logging.debug(f'action to take: {action_to_take}')
            commands.append(action_mapping[action_to_take])
            position = (position + action) % 100
            for i in range(colors_len):
                color = colors[i][:-1]
                logging.debug(f'color to push: {color}')
                commands.append(color_mapping[color])
                if i < colors_len - 1:
                    logging.debug(f'stay')
                    commands.append(action_mapping[0])
    logging.debug(f'commands: {commands}')
    logging.debug(f'position: {position}')
    logging.debug('------- path_finder.get_as_commands end -------')
    return commands, position


def get_commands_by_level(positions, level, start_position):
    goal_positions = get_goal_positions_by_level(positions, level)
    logging.debug(goal_positions)
    start_node = initialize_start_node(start_position)
    logging.debug(f'start node {start_node}')

    costs = {
        0: [],
        25: [],
        50: [],
        75: []
    }

    for pos in goal_positions:
        goal_node = pos
        logging.debug(f'start {start_node} to goal {goal_node}')
        total_cost, path_with_costs = bidirectional_uniform_cost_search_with_costs(position_graph, start_node,
                                                                                   goal_node)
        if path_with_costs:
            logging.debug("Total Cost from", start_node, "to", goal_node, ":", total_cost)
            logging.debug("Path with Step Costs:")
            for node, step_cost in path_with_costs:
                logging.debug("Node:", node, "- Step Cost:", step_cost)
            logging.debug('--------------')
            costs[total_cost].append(goal_node)
        else:
            logging.debug("No path found from", start_node, "to", goal_node)

    logging.debug(costs)

    return get_as_commands(costs, start_position)


def find_best_path(positions):
    start_position = 0
    logging.info(f'find_best_path, provided positions: {positions}')

    commands_level1, new_start_position = get_commands_by_level(positions, 0, start_position)
    commands_level2, end_position = get_commands_by_level(positions, 1, new_start_position)

    commands = commands_level1 + commands_level2
    logging.info(f'commands: {commands}')
    logging.info(f'end position: {end_position}')

    return commands


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
