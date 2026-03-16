from abc import ABC, abstractmethod
from collections import deque
import sys

from searchclient.action import Action
from searchclient.state import State
from searchclient.color import Color


class Heuristic(ABC):
    def __init__(self, initial_state: State) -> None:
        # Here's a chance to pre-process the static parts of the level.
        self.shortest_paths = self._compute_shortest_paths(initial_state)
        self.shortest_path_steps = None
        self.shortest_path_steps = self._compute_shortest_path_steps(initial_state)
        #
        #print("#Preprocessing complete!", file=sys.stderr, flush=True)
        #print(f"#Shortest paths computed: {self.shortest_path_steps }", file=sys.stderr, flush=True)
        # for start_pos, paths in self.shortest_path_steps.items():
        #     print(f"From {start_pos}:", file=sys.stderr, flush=True)
        #     print(f"{paths}", file=sys.stderr, flush=True)
        #     break

    def _compute_shortest_path_steps(self, initial_state: State) -> dict[tuple[int, int], dict[tuple[int, int], list[Action]]]:
        """
        Compute shortest path steps from every free cell to every other free cell using BFS.
        Returns a dictionary: {(start_row, start_col): {(end_row, end_col): [actions]}}
        """
        shortest_path_steps = {}
        rows = len(initial_state.walls)
        cols = len(initial_state.walls[0])

        # For each cell, run BFS to find shortest path to all other cells
        for start_row in range(rows):
            for start_col in range(cols):
                if initial_state.walls[start_row][start_col]:
                    continue

                steps = {}
                queue = deque([(start_row, start_col, [])])
                visited = set()
                visited.add((start_row, start_col))

                while queue:
                    row, col, path = queue.popleft()
                    steps[(row, col)] = path
                    # Explore neighbors (up, down, left, right)
                    for dr, dc, action in [(-1, 0, Action.MoveN), (1, 0, Action.MoveS), (0, -1, Action.MoveW), (0, 1, Action.MoveE)]:
                        new_row, new_col = row + dr, col + dc
                        if (0 <= new_row < rows and 0 <= new_col < cols and 
                            not initial_state.walls[new_row][new_col] and 
                            (new_row, new_col) not in visited):
                            visited.add((new_row, new_col))
                            queue.append((new_row, new_col, path + [action]))

                shortest_path_steps[(start_row, start_col)] = steps

        return shortest_path_steps
    
    def _compute_shortest_paths(self, initial_state: State) -> dict[tuple[int, int], dict[tuple[int, int], int]]:
        """
        Compute shortest paths from every free cell to every other free cell using BFS.
        Returns a dictionary: {(start_row, start_col): {(end_row, end_col): distance}}
        """
        shortest_paths = {}
        rows = len(initial_state.walls)
        cols = len(initial_state.walls[0])

        # For each cell, run BFS to find shortest path to all other cells
        for start_row in range(rows):
            for start_col in range(cols):
                if initial_state.walls[start_row][start_col]:
                    continue

                distances = {}
                queue = deque([(start_row, start_col, 0)])
                visited = set()
                visited.add((start_row, start_col))

                while queue:
                    row, col, dist = queue.popleft()
                    distances[(row, col)] = dist
                    # Explore neighbors (up, down, left, right)
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        new_row, new_col = row + dr, col + dc
                        if (0 <= new_row < rows and 0 <= new_col < cols and 
                            not initial_state.walls[new_row][new_col] and 
                            (new_row, new_col) not in visited):
                            visited.add((new_row, new_col))
                            queue.append((new_row, new_col, dist + 1))

                shortest_paths[(start_row, start_col)] = distances

        return shortest_paths

    def _get_distance(self, from_pos: tuple[int, int], to_pos: tuple[int, int]) -> int:
        """Get shortest distance between two positions, or a large value if unreachable."""
        if from_pos in self.shortest_paths:
            return self.shortest_paths[from_pos].get(to_pos, 10**9)
        return 10**9

    def _get_next_goal(self, state: State) -> list | None:
        next_goal = getattr(state, "next_goal", None)
        if next_goal is None:
            next_goal = getattr(state, "next_sup_goal", None)
        if next_goal is None or len(next_goal) != 3:
            return None
        return next_goal

    def h(self, state: State) -> int:
        hval= (self.h_agents_to_goals_sub_goal(state) 
            + self.h_boxes_to_goals_sub_goal(state) 
            + self.h_agents_to_boxes_sub_goal(state)
        )
        
        if self._get_next_goal(state) is None:
            hval += self.h_boxes_to_goals(state)*0.1 
            hval += self.h_agents_to_goals(state)*0.1
        return hval

    def h_goal_count(self, state: State) -> int:
        # Goal count heuristic: number of boxes not in goal cells
        count = 0
        for row in range(len(state.goals)):
            for col in range(len(state.goals[row])):
                goal = state.goals[row][col]
                # Count unsatisfied box goals
                if "A" <= goal <= "Z":
                    if state.boxes[row][col] != goal:
                        count += 1
                
                # Count unsatisfied agent goals
                if "0" <= goal <= "9":
                    agent_num = int(goal)
                    if not (state.agent_rows[agent_num] == row and state.agent_cols[agent_num] == col):
                        count += 1
        # print(f"remaining goals {count}", file=sys.stdout, flush=True)
        return count

    
    def h_agents_to_goals_sub_goal(self, state: State) -> int:
        next_goal = self._get_next_goal(state)
        if next_goal is None:
            return 0

        goal_symbol = str(next_goal[0])
        goal_row = int(next_goal[1])
        goal_col = int(next_goal[2])

        if not ("0" <= goal_symbol <= "9"):
            return 0

        agent_num = int(goal_symbol)
        if agent_num >= len(state.agent_rows):
            return 0

        agent_row = state.agent_rows[agent_num]
        agent_col = state.agent_cols[agent_num]
        dist = self._get_distance((agent_row, agent_col), (goal_row, goal_col))
        return 0 if dist == 10**9 else dist

    def h_boxes_to_goals_sub_goal(self, state: State) -> int:
        next_goal = self._get_next_goal(state)
        if next_goal is None:
            return 0

        goal_symbol = str(next_goal[0]).upper()
        goal_row = int(next_goal[1])
        goal_col = int(next_goal[2])

        if not ("A" <= goal_symbol <= "Z"):
            return 0

        closest_box_dist = 10**9
        for box_row in range(len(state.boxes)):
            for box_col in range(len(state.boxes[box_row])):
                if state.boxes[box_row][box_col] == goal_symbol:
                    dist = self._get_distance((box_row, box_col), (goal_row, goal_col))
                    if dist < closest_box_dist:
                        closest_box_dist = dist

        return 0 if closest_box_dist == 10**9 else closest_box_dist

    def h_agents_to_boxes_sub_goal(self, state: State) -> int:
        next_goal = self._get_next_goal(state)
        if next_goal is None:
            return 0
        goal_symbol = str(next_goal[0]).upper()
        if not ("A" <= goal_symbol <= "Z"):
            return 0
        target_box_color = State.box_colors[ord(goal_symbol) - ord("A")]
        closest_dist = 10**9
        for agent_num in range(len(state.agent_rows)):
            if State.agent_colors[agent_num] != target_box_color:
                continue

            agent_row = state.agent_rows[agent_num]
            agent_col = state.agent_cols[agent_num]

            for box_row in range(len(state.boxes)):
                for box_col in range(len(state.boxes[box_row])):
                    if state.boxes[box_row][box_col] == goal_symbol:
                        dist = self._get_distance((agent_row, agent_col), (box_row, box_col))
                        if dist < closest_dist:
                            closest_dist = dist

        return 0 if closest_dist == 10**9 else closest_dist


    def h_coredore_penelty(self, state: State) -> int:
        #penelty for agent in a cell that is surrounded by walls on 2 opposite sides mening it is blocking the path for other agents 
        penalty = 0
        for agent_num in range(len(state.agent_rows)):
            agent_row = state.agent_rows[agent_num]
            agent_col = state.agent_cols[agent_num]

            # Check if the agent is in a cell that is surrounded by walls on 2 opposite sides
            if (State.walls[agent_row - 1][agent_col] and State.walls[agent_row + 1][agent_col]) or \
               (State.walls[agent_row][agent_col - 1] and State.walls[agent_row][agent_col + 1]):
                penalty += 1  # Arbitrary penalty value for being in a coredore position
       
        # if penalty > 1:
        #     penalty += 10  # Additional penalty for multiple agents in coredore positions

        # else:
        #     penalty = 1  # No penalty if no agents are in coredore positions
        return penalty
    
    def h_agents_to_goals(self, state: State) -> int:
        remaining_cost = 0
        # For each agent position, find the minimum cost to get to its goal
        for agent_num in range(len(state.agent_rows)):
            agent_row = state.agent_rows[agent_num]
            agent_col = state.agent_cols[agent_num]

            closest_goal_dist = 10**9
            for goal_row in range(len(state.goals)):
                for goal_col in range(len(state.goals[goal_row])):
                    goal = state.goals[goal_row][goal_col]
                    if goal == str(agent_num):
                        dist = self._get_distance((agent_row, agent_col), (goal_row, goal_col))
                        if dist < closest_goal_dist:
                            closest_goal_dist = dist

            if closest_goal_dist != 10**9:
                remaining_cost += closest_goal_dist
        return remaining_cost

    def h_boxes_to_goals(self, state: State) -> int:
        remaining_cost = 0
        # Find the distance from each box to its closest goal
        for box_row in range(len(state.boxes)):
            for box_col in range(len(state.boxes[box_row])):
                box = state.boxes[box_row][box_col]

                if "A" <= box <= "Z":
                    multiplier = 1

                    closest_goal_dist = 10**9
                    for goal_row in range(len(state.goals)):
                        for goal_col in range(len(state.goals[goal_row])):
                            goal = state.goals[goal_row][goal_col]
                            if goal == box:
                                dist = self._get_distance((box_row, box_col), (goal_row, goal_col))
                                if dist < closest_goal_dist:
                                    closest_goal_dist = dist

                    if closest_goal_dist != 10**9:
                        remaining_cost += multiplier * closest_goal_dist
        return remaining_cost

    def h_agents_to_boxes(self, state: State) -> int:
        remaining_cost = 0
        # Get the distance from each agent to its closest box of the same color
        for agent_num in range(len(state.agent_rows)):
            agent_row = state.agent_rows[agent_num]
            agent_col = state.agent_cols[agent_num]
            agent_color = State.agent_colors[agent_num]
            closest_box_dist = 10**9
            for box_row in range(len(state.boxes)):
                for box_col in range(len(state.boxes[box_row])):
                    box = state.boxes[box_row][box_col]
                    if "A" <= box <= "Z":
                        box_color = State.box_colors[ord(box) - ord("A")]
                        if box_color == agent_color:
                            dist = self._get_distance((agent_row, agent_col), (box_row, box_col))
                            if dist < closest_box_dist:
                                closest_box_dist = dist
            if closest_box_dist != 10**9:
                remaining_cost += closest_box_dist
        return remaining_cost


    
    @abstractmethod
    def f(self, state: State) -> int: ...

    @abstractmethod
    def __repr__(self) -> str: ...


class HeuristicAStar(Heuristic):
    def __init__(self, initial_state: State) -> None:
        super().__init__(initial_state)

    def f(self, state: State) -> int:
        return state.g + self.h(state)

    def __repr__(self) -> str:
        return "A* evaluation"


class HeuristicWeightedAStar(Heuristic):
    def __init__(self, initial_state: State, w: int) -> None:
        super().__init__(initial_state)
        self.w = w

    def f(self, state: State) -> int:
        return state.g + self.w * self.h(state)

    def __repr__(self) -> str:
        return f"WA*({self.w}) evaluation"


class HeuristicGreedy(Heuristic):
    def __init__(self, initial_state: State) -> None:
        super().__init__(initial_state)

    def f(self, state: State) -> int:
        return self.h(state)

    def __repr__(self) -> str:
        return "greedy evaluation"
