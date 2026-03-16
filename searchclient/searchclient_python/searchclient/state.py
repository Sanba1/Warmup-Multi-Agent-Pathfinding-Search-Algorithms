import random
import sys
from typing import ClassVar

from searchclient.action import Action, ActionType
from searchclient.color import Color


class State:
    _RNG = random.Random(1)

    agent_colors: ClassVar[list[Color | None]]
    walls: ClassVar[list[list[bool]]]
    box_colors: ClassVar[list[Color | None]]
    goals: ClassVar[list[list[str]]]
    sup_goals: dict[int, list[list[str]]]
    next_sup_goal: list[str] | None

    def __init__(self, agent_rows: list[int], agent_cols: list[int], boxes: list[list[str]]) -> None:
        """
        Constructs an initial state.
        Arguments are not copied, and therefore should not be modified after being passed in.

        The lists walls, boxes, and goals are indexed from top-left of the level, row-major order (row, col).
               Col 0  Col 1  Col 2  Col 3
        Row 0: (0,0)  (0,1)  (0,2)  (0,3)  ...
        Row 1: (1,0)  (1,1)  (1,2)  (1,3)  ...
        Row 2: (2,0)  (2,1)  (2,2)  (2,3)  ...
        ...

        For example, State.walls[2] is a list of booleans for the third row.
        State.walls[row][col] is True if there's a wall at (row, col).

        The agent rows and columns are indexed by the agent number.
        For example, State.agent_rows[0] is the row location of agent '0'.

        Note: The state should be considered immutable after it has been hashed, e.g. added to a dictionary or set.
        """
        self.agent_rows = agent_rows
        self.agent_cols = agent_cols
        self.boxes = boxes
        self.parent: State | None = None
        self.joint_action: list[Action] | None = None
        self.g = 0
        self._hash: int | None = None   

    def result(self, joint_action: list[Action]) -> "State":
        """
        Returns the state resulting from applying joint_action in this state.
        Precondition: Joint action must be applicable and non-conflicting in this state.
        """

        # Copy this state.
        copy_agent_rows = self.agent_rows[:]
        copy_agent_cols = self.agent_cols[:]
        copy_boxes = [row[:] for row in self.boxes]

        # Apply each action.
        for agent, action in enumerate(joint_action):
            agent_row = self.agent_rows[agent]
            agent_col = self.agent_cols[agent]

            if action.type is ActionType.NoOp:
                pass

            elif action.type is ActionType.Move:
                copy_agent_rows[agent] += action.agent_row_delta
                copy_agent_cols[agent] += action.agent_col_delta

            elif action.type is ActionType.Push:
                # Box is in front of agent (in the direction the agent moves)
                box_row = agent_row + action.agent_row_delta
                box_col = agent_col + action.agent_col_delta

                # Box destination is box cell + box delta
                new_box_row = box_row + action.box_row_delta
                new_box_col = box_col + action.box_col_delta

                # Move agent into the old box cell
                copy_agent_rows[agent] = box_row
                copy_agent_cols[agent] = box_col

                # Move box into new cell
                copy_boxes[new_box_row][new_box_col] = copy_boxes[box_row][box_col]
                copy_boxes[box_row][box_col] = ""

            elif action.type is ActionType.Pull:
                # Agent destination
                new_agent_row = agent_row + action.agent_row_delta
                new_agent_col = agent_col + action.agent_col_delta

                # Box is behind agent relative to the box delta:
                # It moves with (box_row_delta, box_col_delta) into agent's current cell.
                box_row = agent_row - action.box_row_delta
                box_col = agent_col - action.box_col_delta

                # Move agent first
                copy_agent_rows[agent] = new_agent_row
                copy_agent_cols[agent] = new_agent_col

                # Move box into agent's old position
                copy_boxes[agent_row][agent_col] = copy_boxes[box_row][box_col]
                copy_boxes[box_row][box_col] = ""

        copy_state = State(copy_agent_rows, copy_agent_cols, copy_boxes)
        copy_state.parent = self
        copy_state.joint_action = joint_action.copy()
        copy_state.g = self.g + 1

        return copy_state

    def is_goal_state(self) -> bool:
        for row in range(len(State.goals)):
            for col in range(len(State.goals[row])):
                goal = State.goals[row][col]

                if "A" <= goal <= "Z" and self.boxes[row][col] != goal:
                    return False
                if "0" <= goal <= "9" and not (
                    self.agent_rows[ord(goal) - ord("0")] == row and self.agent_cols[ord(goal) - ord("0")] == col
                ):
                    return False
        return True

    def get_sup_goals(self) -> dict[int,list[list[str]]]:
        # Returns a dictionary mapping agent number to list of goal positions (row, col) for that agent.
        sup_goals: dict[int, list[list[str]]] = {}

        for agent_number in range(len(State.agent_colors)):
            sup_goals[agent_number] = []

        for row in range(len(State.goals)):
            for col in range(len(State.goals[row])):
                goal = State.goals[row][col]
                if goal != "":
                    if "0" <= goal <= "9":
                        agent_number = ord(goal) - ord("0")

                        sup_goals[agent_number].append([goal,row, col])
                    if "A" <= goal <= "Z":
                        box_color = State.box_colors[ord(goal) - ord("A")]
                        for agent_number, agent_color in enumerate(State.agent_colors):
                            if agent_color == box_color:
                                
                                sup_goals[agent_number].append([goal,row, col])
        State.sup_goals = sup_goals
        print(f"#Sup goals: {State.sup_goals}")
        return sup_goals
    
    def get_next_sup_goal(self) -> list[str] | None:
        # Returns the next sup goal to be solved, or None if there are no more sup goals.
        curent_sup_goal = None
        for agent_number in range(len(State.agent_colors)):
            if agent_number in State.sup_goals and len(State.sup_goals[agent_number]) > 0:
                for goal in State.sup_goals[agent_number]:
                    if str(goal[0]) == str(agent_number) and curent_sup_goal is None:
                        curent_sup_goal = goal
                    else:
                        curent_sup_goal = goal
                        State.next_sup_goal = curent_sup_goal
                        print(f"#Next sup goal: {State.next_sup_goal}")    
                        return curent_sup_goal
                                 
        State.next_sup_goal = curent_sup_goal
        print(f"#Next sup goal: {State.next_sup_goal}")           
        return curent_sup_goal

    def is_sup_goal_state(self) -> bool:
        # Returns whether this state is a sup goal state, and the rest of the sup goals if so.
        State.sup_goals
        for agent_number, goals in State.sup_goals.items():
            for goal in goals:

                if "A" <= goal[0] <= "Z":
                    box_row = goal[1]
                    box_col = goal[2]
                    if self.boxes[box_row][box_col] == goal[0]:
                        goals.remove(goal)
                        #if len(goals) == 0:
                            #del State.sup_goals[agent_number]
                        return True
                    
                elif int(goal[0]) == int(agent_number):
                    agent_row = self.agent_rows[agent_number]
                    agent_col = self.agent_cols[agent_number]
                    if goal[1] == agent_row and goal[2] == agent_col:
                        goals.remove(goal)
                        #if len(goals) == 0:
                            #del State.sup_goals[agent_number]
                        return True
                
        return False

    def get_expanded_states(self) -> list["State"]:
        num_agents = len(self.agent_rows)

        # Determine list of applicable action for each individual agent.
        applicable_actions = [
            [action for action in Action if self.is_applicable(agent, action)] for agent in range(num_agents)
        ]

        # Iterate over joint actions, check conflict and generate child states.
        joint_action = [Action.NoOp for _ in range(num_agents)]
        actions_permutation = [0 for _ in range(num_agents)]
        expanded_states = []
        while True:
            for agent in range(num_agents):
                joint_action[agent] = applicable_actions[agent][actions_permutation[agent]]

            if not self.is_conflicting(joint_action):
                expanded_states.append(self.result(joint_action))

            # Advance permutation.
            done = False
            for agent in range(num_agents):
                if actions_permutation[agent] < len(applicable_actions[agent]) - 1:
                    actions_permutation[agent] += 1
                    break
                else:  # noqa: RET508
                    actions_permutation[agent] = 0
                    if agent == num_agents - 1:
                        done = True

            # Last permutation?
            if done:
                break

        State._RNG.shuffle(expanded_states)
        return expanded_states

    def is_applicable(self, agent: int, action: Action) -> bool:

        def _is_in_bounds(row: int, col: int) -> bool:
            return 0 <= row < len(State.walls) and 0 <= col < len(State.walls[0])
        
        agent_row = self.agent_rows[agent]
        agent_col = self.agent_cols[agent]
        _agent_color = State.agent_colors[agent]

        new_agent_row = agent_row + action.agent_row_delta
        new_agent_col = agent_col + action.agent_col_delta

        if action.type is ActionType.NoOp:
            return True
        
        elif len(State.sup_goals[agent]) == 0:
            return False
        
        if action.type is ActionType.Move:
            if not _is_in_bounds(new_agent_row, new_agent_col):
                return False
            return self.is_free(new_agent_row, new_agent_col)
        
        if action.type is ActionType.Push:
            if not _is_in_bounds(new_agent_row, new_agent_col):
                return False

            # There must be a box in front of the agent (where the agent moves)
            if self.boxes[new_agent_row][new_agent_col] == "":
                return False

            # Agent may only push boxes of its own color
            box_letter = self.boxes[new_agent_row][new_agent_col]
            box_color = State.box_colors[ord(box_letter) - ord("A")]
            if box_color != _agent_color:
                return False

            # The box destination cell must be free
            box_dest_row = new_agent_row + action.box_row_delta
            box_dest_col = new_agent_col + action.box_col_delta
            if not _is_in_bounds(box_dest_row, box_dest_col):
                return False

            return self.is_free(box_dest_row, box_dest_col)


        if action.type is ActionType.Pull:
            # Agent destination must be free
            if not _is_in_bounds(new_agent_row, new_agent_col):
                return False
            if not self.is_free(new_agent_row, new_agent_col):
                return False

            # The box is behind agent relative to box delta
            box_row = agent_row - action.box_row_delta
            box_col = agent_col - action.box_col_delta
            if not _is_in_bounds(box_row, box_col):
                return False

            if self.boxes[box_row][box_col] == "":
                return False    

            # Agent may only push boxes of its own color
            box_letter = self.boxes[box_row][box_col]
            box_color = State.box_colors[ord(box_letter) - ord("A")]
            if box_color != _agent_color:
                return False


            # Agent may only pull boxes of its own color
            box_letter = self.boxes[box_row][box_col]
            box_color = State.box_colors[ord(box_letter) - ord("A")]
            if box_color != _agent_color:
                return False

            return True


        assert False, f"Not implemented for action type {action.type}."

    def is_conflicting(self, joint_action: list[Action]) -> bool:
        num_agents = len(self.agent_rows)

        destination_rows = [-1 for _ in range(num_agents)]  # row of new cell to become occupied by action
        destination_cols = [-1 for _ in range(num_agents)]  # column of new cell to become occupied by action
        box_rows = [-1 for _ in range(num_agents)]  # current row of box moved by action
        box_cols = [-1 for _ in range(num_agents)]  # current column of box moved by action

        # Collect cells to be occupied and boxes to be moved.
        for agent in range(num_agents):
            action = joint_action[agent]
            agent_row = self.agent_rows[agent]
            agent_col = self.agent_cols[agent]

            if action.type is ActionType.NoOp:
                pass

            elif action.type is ActionType.Move:
                destination_rows[agent] = agent_row + action.agent_row_delta
                destination_cols[agent] = agent_col + action.agent_col_delta
                box_rows[agent] = agent_row  # Distinct dummy value.
                box_cols[agent] = agent_col  # Distinct dummy value.

            elif action.type is ActionType.Push:
                destination_rows[agent] = agent_row + action.agent_row_delta
                destination_cols[agent] = agent_col + action.agent_col_delta
                box_rows[agent] =  agent_row + action.agent_row_delta + action.box_row_delta
                box_cols[agent] = agent_col + action.agent_col_delta + action.box_col_delta
                #print(f"Agent {agent} pushes box from ({agent_row + action.agent_row_delta}, {agent_col + action.agent_col_delta}) to ({box_rows[agent]}, {box_cols[agent]})", file=sys.stderr, flush=True)
            
            elif action.type is ActionType.Pull:
                destination_rows[agent] = agent_row + action.agent_row_delta
                destination_cols[agent] = agent_col + action.agent_col_delta
                box_rows[agent] = agent_row - action.box_row_delta
                box_cols[agent] = agent_col - action.box_col_delta
        
        for a1 in range(num_agents):
            if joint_action[a1] is Action.NoOp:
                continue

            for a2 in range(a1 + 1, num_agents):
                if joint_action[a2] is Action.NoOp:
                    continue

                # Moving into same cell?
                if destination_rows[a1] == destination_rows[a2] and destination_cols[a1] == destination_cols[a2]:
                    return True
                
                # Moving into box being moved by other agent?
                if destination_rows[a1] == box_rows[a2] and destination_cols[a1] == box_cols[a2]:
                    return True
                
                if destination_rows[a2] == box_rows[a1] and destination_cols[a2] == box_cols[a1]:
                    return True
                
                # Moving box into box being moved by other agent
                if box_rows[a2] == box_rows[a1] and box_cols[a2] == box_cols[a1]:
                    return True
                
                if box_rows[a2] == box_rows[a1] and box_cols[a2] == box_cols[a1]:
                    return True

                
        return False

    def is_free(self, row: int, col: int) -> bool:
        return not State.walls[row][col] and not self.boxes[row][col] and self.agent_at(row, col) is None

    def agent_at(self, row: int, col: int) -> str | None:
        for agent in range(len(self.agent_rows)):
            if self.agent_rows[agent] == row and self.agent_cols[agent] == col:
                return chr(agent + ord("0"))
        return None

    def extract_plan(self) -> list[list[Action]]:
        plan = []
        state: State | None = self
        while state is not None and state.joint_action is not None:
            plan.append(state.joint_action)
            state = state.parent
        plan.reverse()
        return plan

    def __hash__(self) -> int:
        if self._hash is None:
            prime = 31
            h = 1
            h = h * prime + hash(tuple(self.agent_rows))
            h = h * prime + hash(tuple(self.agent_cols))
            h = h * prime + hash(tuple(State.agent_colors))
            h = h * prime + hash(tuple(tuple(row) for row in self.boxes))
            h = h * prime + hash(tuple(State.box_colors))
            h = h * prime + hash(tuple(tuple(row) for row in State.goals))
            h = h * prime + hash(tuple(tuple(row) for row in State.walls))
            self._hash = h
        return self._hash

    def __eq__(self, other: object) -> bool:
        if self is other:
            return True
        if not isinstance(other, State):
            return False
        if self.agent_rows != other.agent_rows:
            return False
        if self.agent_cols != other.agent_cols:
            return False
        if State.agent_colors != other.agent_colors:
            return False
        if State.walls != other.walls:
            return False
        if self.boxes != other.boxes:
            return False
        if State.box_colors != other.box_colors:
            return False
        return State.goals == other.goals

    def __repr__(self) -> str:
        lines = []
        for row in range(len(self.boxes)):
            line = []
            for col in range(len(self.boxes[row])):
                if self.boxes[row][col]:
                    line.append(self.boxes[row][col])
                elif State.walls[row][col] is not None:
                    line.append("+")
                elif (agent := self.agent_at(row, col)) is not None:
                    line.append(agent)
                else:
                    line.append(" ")
            lines.append("".join(line))
        return "\n".join(lines)
