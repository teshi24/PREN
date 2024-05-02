from typing import Dict, Type
from collections import deque
import heapq
from src.frame_analyzer.position_analyzer import PositionIdentifier
from src.path_finder.search import Node, UndirectedGraph, GraphProblem, Graph

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


def find_best_path(positions: Dict[int, Type[PositionIdentifier | None]]):
    print(positions)

    ## todo: add also the second layer
    ## todo: add backwards mecanism
    position_graph = Graph(dict(
        redA=dict(redB=25, redC=50, redD=75, blueC=0, blueD=25, blueA=50, blueB=75, yellowD=0, yellowA=25, yellowB=50, yellowC=75),
        redB=dict(redC=25, redD=50, redA=75, blueD=0, blueA=25, blueB=50, blueC=75, yellowA=0, yellowB=25, yellowC=50, yellowD=75),
        redC=dict(redD=25, redA=50, redB=75, blueA=0, blueB=25, blueC=50, blueD=75, yellowB=0, yellowC=25, yellowD=50, yellowA=75),
        redD=dict(redA=25, redB=50, redC=75, blueB=0, blueC=25, blueD=50, blueA=75, yellowC=0, yellowD=25, yellowA=50, yellowB=75),

        blueA=dict(blueB=25, blueC=50, blueD=75, redC=0, redD=25, redA=50, redB=75, yellowD=0, yellowA=25, yellowB=50, yellowC=75),
        blueB=dict(blueC=25, blueD=50, blueA=75, redD=0, redA=25, redB=50, redC=75, yellowA=0, yellowB=25, yellowC=50, yellowD=75),
        blueC=dict(blueD=25, blueA=50, blueB=75, redA=0, redB=25, redC=50, redD=75, yellowB=0, yellowC=25, yellowD=50, yellowA=75),
        blueD=dict(blueA=25, blueB=50, blueC=75, redB=0, redC=25, redD=50, redA=75, yellowC=0, yellowD=25, yellowA=50, yellowB=75),

        yellowA=dict(yellowB=25, yellowC=50, yellowD=75, redD=0, redA=25, redB=50, redC=75, blueB=0, blueC=25, blueD=50, blueA=75),
        yellowB=dict(yellowC=25, yellowD=50, yellowA=75, redA=0, redB=25, redC=50, redD=75, blueC=0, blueD=25, blueA=50, blueB=75),
        yellowC=dict(yellowD=25, yellowA=50, yellowB=75, redB=0, redC=25, redD=50, redA=75, blueD=0, blueA=25, blueB=50, blueC=75),
        yellowD=dict(yellowA=25, yellowB=50, yellowC=75, redC=0, redD=25, redA=50, redB=75, blueA=0, blueB=25, blueC=50, blueD=75)
    ))

    ## found redA - redD - blueA - yellowC
    ## redA - redD = 75 - blueA - 50 - yellowC = 75
    ## redA - yellowC = 75
    ## ['redC', 'redD', 'redA', 'blueD', 'blueA', 'blueB', 'blueC', 'yellowA', 'yellowB', 'yellowC', 'yellowD']

    # # Simplified graph dictionary initialization
    # position_graph2 = UndirectedGraph(dict(
    #     redA=dict(redB=25, redC=50, redD=75, blueC=0, blueD=25, blueA=50, blueB=75, yellowD=0, yellowA=25, yellowB=50, yellowC=75),
    #     redB=dict(redC=25, redD=50, blueD=0, blueA=25, blueB=50, blueC=75, yellowA=0, yellowB=25, yellowC=50, yellowD=75),
    #     redC=dict(redD=25, blueA=0, blueB=25, blueC=50, blueD=75, yellowB=0, yellowC=25, yellowD=50, yellowA=75),
    #     redD=dict(blueB=0, blueC=25, blueD=50, blueA=75, yellowC=0, yellowD=25, yellowA=50, yellowB=75),
    #     blueA=dict(blueB=25, blueC=50, blueD=75, yellowD=0, yellowA=25, yellowB=50, yellowC=75),
    #     blueB=dict(blueC=25, blueD=50, yellowA=0, yellowB=25, yellowC=50, yellowD=75),
    #     blueC=dict(blueD=25, yellowB=0, yellowC=25, yellowD=50, yellowA=75),
    #     blueD=dict(yellowC=0, yellowD=25, yellowA=50, yellowB=75),
    #     yellowA=dict(yellowB=25, yellowC=50, yellowD=75),
    #     yellowB=dict(yellowC=25, yellowD=50),
    #     yellowC=dict(yellowD=25),
    # ))

    start = ['redA']
    possible_goals = ['yellowC']
    problem = GraphProblem(start, possible_goals, position_graph)
    goal_node = uniform_cost_search(problem)
    evaluate(goal_node)
    # todo: fix
    pass


def uniform_cost_search(problem):
    node = Node(problem.initial)
    visited = set()
    if problem.goal_test(node.state):
        return node
    frontier = []
    heapq.heappush(frontier, (node.path_cost, node))
    while frontier:
        print('------------')
        for item in frontier:
            print(item[0])
            print(item[1].state)
        print('------------')
        node = heapq.heappop(frontier)[1]
        if problem.goal_test(node.state):
            return node
        visited.add(node.state)
        for action in problem.get_actions_from(node.state):
            child = node.create_child_node(problem, action)
            if child.state not in visited and child.state not in frontier:
                heapq.heappush(frontier, (child.path_cost, child))
                visited.add(child.state)
            elif any(n[1].state == child.state and n[1].path_cost > child.path_cost for n in frontier):
                # Find the frontier node with the same state as child but with a higher path_cost
                for i, (cost, frontier_node) in enumerate(frontier):
                    if frontier_node.state == child.state and frontier_node.path_cost > child.path_cost:
                        # Replace the frontier node with child
                        frontier[i] = (child.path_cost, child)
                        break
    return False


# code from aiso

# def uniform_cost_search(problem):
#     node = Node(problem.initial)
#     visited = set()
#     current_path_costs = set()
#     if problem.goal_test(node.state):
#         return node
#     frontier = []
#     print(f'node {node}')
#     print(f'node.state {node.state}')
#     print(f'node.path_cost {node.path_cost}')
#     heapq.heappush(frontier, (node.path_cost, [node]))
#     current_path_costs.add(node.path_cost)
#     while True:
#         print('entered while')
#         if not frontier:
#             return False
#         print('------------')
#         for item in frontier:
#             print(item[0])
#             print(item[1])
#         print('------------')
#         # todo: this needs to be able to handle a list
#         nodes = heapq.heappop(frontier)[1]
#         if problem.goal_test(nodes):
#             return nodes
#         for node in nodes:
#             visited.add(node.state)
#
#         node = nodes[0] ## todo: check if sufficient; should actually be, bc. the states with the same costs are pointing to the same directions
#         print(node.state)
#         print(problem.get_actions_from(node.state))
#         for action in problem.get_actions_from(node.state):
#             print(action)
#             child = node.create_child_node(problem, action)
#             if child.state not in visited and child.state not in frontier:
#                 if child.path_cost in current_path_costs:
#                     print('duplicate detected')
#                     print(f'current_path_costs {current_path_costs}')
#                     print(f'child.path_cost {child.path_cost}')
#                     ## update the list
#                     for i, (cost, frontier_nodes) in enumerate(frontier):
#                         if cost == child.path_cost:
#                             frontier_nodes.append(child)
#                             frontier[i] = (child.path_cost, frontier_nodes)
#                             break
#                     visited.add(child.state)
#                     continue  # todo: handle duplicates better - bc, we need to be able to stick 2 items at the same time
#                 heapq.heappush(frontier, (child.path_cost, [child]))
#                 current_path_costs.add(child.path_cost)
#                 visited.add(child.state)
#
#             # todo: needs to be able to handle a list of states
#             elif any(n[1].state == child.state and n[1].path_cost > child.path_cost for n in frontier):
#                 for i, (cost, frontier_node) in enumerate(frontier):
#                     if frontier_node.state == child.state and frontier_node.path_cost > child.path_cost:
#                         frontier[i] = (child.path_cost, child)
#                         break


# def uniform_cost_search(problem):
#     node = Node(problem.initial)
#     visited = set()
#     if problem.goal_test(node.state):
#         return node
#
#     frontier = []
#     heapq.heappush(frontier, (node.path_cost, node))
#     # Use a dictionary to track the best path cost to a node found so far.
#     frontier_states = {node.state: node.path_cost}
#
#     while frontier:
#         print('------------')
#         for item in frontier:
#             print(item[0], item[1].state)
#         print('------------')
#
#         # Get the node with the lowest cost
#         node = heapq.heappop(frontier)[1]
#         visited.add(node.state)
#
#         # Check for goal after popping it off the frontier
#         if problem.goal_test(node.state):
#             return node
#
#         print(node.state)
#         print(problem.get_actions_from(node.state))
#
#         for action in problem.get_actions_from(node.state):
#             print(action)
#             child = node.create_child_node(problem, action)
#
#             # Check if a cheaper path to the state has been found
#             if child.state not in visited or (
#                     child.state in frontier_states and frontier_states[child.state] > child.path_cost):
#                 # Update the state's cost in frontier_states
#                 frontier_states[child.state] = child.path_cost
#                 heapq.heappush(frontier, (child.path_cost, child))
#                 print(f'Pushing to frontier: {child.state} with path cost {child.path_cost}')
#
#                 # Remove the old node if it's still in the frontier
#                 if child.state in visited:
#                     visited.remove(child.state)
#
#     return False

def test():
    romania_graph = UndirectedGraph(dict(
        Arad=dict(Zerind=75, Sibiu=140, Timisoara=118),
        Bucharest=dict(Urziceni=85, Pitesti=101, Giurgiu=90, Fagaras=211),
        Craiova=dict(Drobeta=120, Rimnicu=146, Pitesti=138),
        Drobeta=dict(Mehadia=75),
        Eforie=dict(Hirsova=86),
        Fagaras=dict(Sibiu=99),
        Hirsova=dict(Urziceni=98),
        Iasi=dict(Vaslui=92, Neamt=87),
        Lugoj=dict(Timisoara=111, Mehadia=70),
        Oradea=dict(Zerind=71, Sibiu=151),
        Pitesti=dict(Rimnicu=97),
        Rimnicu=dict(Sibiu=80),
        Urziceni=dict(Vaslui=142)))

    start = 'Sibiu'
    goal = 'Bucharest'
    problem = GraphProblem(start, goal, romania_graph)
    goal_node = uniform_cost_search(problem)
    evaluate(goal_node)


def evaluate(node):
    if node:
        print("The search algorithm reached " + node.state + " with a cost of " + str(node.path_cost) + ".")
        print("The actions that led to the solutions are the following: ")
        print(node.get_solution())
        print(f"The algorithm visited {len(node.get_solution())} cities")
        print(f'depth = {node.depth}')
        print(f'path cost = {node.path_cost}')
    else:
        print('no solution found')
