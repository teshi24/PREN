from typing import Dict
from collections import deque
from search import Node

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
def find_best_path(positions: Dict[int, End_Result]):
    # todo: fix
    pass

# code from aiso



def depth_first_graph_search(problem):
    node = Node(problem.initial)
    visited = set()
    if problem.goal_test(node.state):
      print(f'max_stored_item: {0}')
      print(f'visited nodes: {len(visited)}')
      return node
    frontier = deque()
    frontier.append(node)
    max_stored_item = 1
    while(frontier):
      print('-------- f --------')
      for item in frontier:
        # if problem.goal_test(item.state):
        print(item.state)
      print('------------------')
      node = frontier.pop()

      visited.add(node.state)
      if problem.goal_test(node.state):
        print(f'max_stored_item: {max_stored_item}')
        print(f'visited nodes: {len(visited)}')
        return node

      for neighbor in problem.get_actions_from(node.state):
        child = node.create_child_node(problem, neighbor)
        if child.state not in visited and child.state not in frontier:
          # if problem.goal_test(child.state):
          #   print(f'max_stored_item: {max_stored_item}')
          #   print(f'visited nodes: {len(visited)}')
          #   return child
          visited.add(child.state)
          frontier.append(child)
          if len(frontier) > max_stored_item:
            max_stored_item = len(frontier)

    print(f'max_stored_item: {max_stored_item}')
    print(f'visited nodes: {len(visited)}')
    return False

import heapq
def uniform_cost_search(problem):
    node = Node(problem.initial)
    visited = set()
    if problem.goal_test(node.state):
      return node
    frontier = []
    heapq.heappush(frontier, (node.path_cost, node))
    while(True):
      if not frontier:
        return False
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
        ## todo: write this pseudocode as valid python code
        ## elif child.state with higher path_cost is in frontier:
        ## replace this frontier node with child
        elif any(n[1].state == child.state and n[1].path_cost > child.path_cost for n in frontier):
          # Find the frontier node with the same state as child but with a higher path_cost
          for i, (cost, frontier_node) in enumerate(frontier):
              if frontier_node.state == child.state and frontier_node.path_cost > child.path_cost:
                  # Replace the frontier node with child
                  frontier[i] = (child.path_cost, child)
                  break


from search import UndirectedGraph
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

from search import GraphProblem
start = 'Sibiu'
goal = 'Bucharest'
problem = GraphProblem(start, goal, romania_graph)
goal_node = uniform_cost_search(problem)


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


evaluate(goal_node)
