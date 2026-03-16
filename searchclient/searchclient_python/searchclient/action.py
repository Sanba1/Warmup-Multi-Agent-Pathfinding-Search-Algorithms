from enum import Enum, unique
from typing import Literal


@unique
class ActionType(Enum):
    NoOp = 0
    Move = 1
    Push = 2
    Pull = 3


@unique
class Action(Enum):
    #   List of possible actions. Each action has the following parameters,
    #    taken in order from left to right:
    #    1. The name of the action as a string. This is the string sent to the server
    #    when the action is executed. Note that for Pull and Push actions the syntax is
    #    "Push(X,Y)" and "Pull(X,Y)" with no spaces.
    #    2. Action type: NoOp, Move, Push or Pull (only NoOp and Move initially supported)
    #    3. agentRowDelta: the vertical displacement of the agent (-1,0,+1)
    #    4. agentColDelta: the horisontal displacement of the agent (-1,0,+1)
    #    5. boxRowDelta: the vertical displacement of the box (-1,0,+1)
    #    6. boxColDelta: the horisontal discplacement of the box (-1,0,+1)
    #    Note: Origo (0,0) is in the upper left corner. So +1 in the vertical direction is down (S)
    #    and +1 in the horisontal direction is right (E).
    NoOp = ("NoOp", ActionType.NoOp, 0, 0, 0, 0)

    MoveN = ("Move(N)", ActionType.Move, -1, 0, 0, 0)
    MoveS = ("Move(S)", ActionType.Move, 1, 0, 0, 0)
    MoveE = ("Move(E)", ActionType.Move, 0, 1, 0, 0)
    MoveW = ("Move(W)", ActionType.Move, 0, -1, 0, 0)
    
    PushNN = ("Push(N,N)", ActionType.Push, -1, 0, -1, 0)  # Agent N, Box N
    PushNE = ("Push(N,E)", ActionType.Push, -1, 0, 0, 1)   # Agent N, Box E
    PushNW = ("Push(N,W)", ActionType.Push, -1, 0, 0, -1)  # Agent N, Box W
    
    PushSS = ("Push(S,S)", ActionType.Push, 1, 0, 1, 0)    # Agent S, Box S
    PushSE = ("Push(S,E)", ActionType.Push, 1, 0, 0, 1)    # Agent S, Box E
    PushSW = ("Push(S,W)", ActionType.Push, 1, 0, 0, -1)   # Agent S, Box W
    
    PushEE = ("Push(E,E)", ActionType.Push, 0, 1, 0, 1)    # Agent E, Box E
    PushEN = ("Push(E,N)", ActionType.Push, 0, 1, -1, 0)   # Agent E, Box N
    PushES = ("Push(E,S)", ActionType.Push, 0, 1, 1, 0)    # Agent E, Box S
    
    PushWW = ("Push(W,W)", ActionType.Push, 0, -1, 0, -1)  # Agent W, Box W
    PushWN = ("Push(W,N)", ActionType.Push, 0, -1, -1, 0)  # Agent W, Box N
    PushWS = ("Push(W,S)", ActionType.Push, 0, -1, 1, 0)   # Agent W, Box S
   


    # Pull actions - format: Pull(agent_dir, box_dir)
    PullNN = ("Pull(N,N)", ActionType.Pull, -1, 0, -1, 0)
    PullNE = ("Pull(N,E)", ActionType.Pull, -1, 0, 0, 1)
    PullNW = ("Pull(N,W)", ActionType.Pull, -1, 0, 0, -1)
    
    PullSS = ("Pull(S,S)", ActionType.Pull, 1, 0, 1, 0)
    PullSE = ("Pull(S,E)", ActionType.Pull, 1, 0, 0, 1)
    PullSW = ("Pull(S,W)", ActionType.Pull, 1, 0, 0, -1)
    
    PullEE = ("Pull(E,E)", ActionType.Pull, 0, 1, 0, 1)
    PullEN = ("Pull(E,N)", ActionType.Pull, 0, 1, -1, 0)
    PullES = ("Pull(E,S)", ActionType.Pull, 0, 1, 1, 0)
    
    PullWW = ("Pull(W,W)", ActionType.Pull, 0, -1, 0, -1)
    PullWN = ("Pull(W,N)", ActionType.Pull, 0, -1, -1, 0)
    PullWS = ("Pull(W,S)", ActionType.Pull, 0, -1, 1, 0)

      


    def __init__(
        self,
        name: str,
        type: ActionType,
        ard: Literal[-1, 0, 1],
        acd: Literal[-1, 0, 1],
        brd: Literal[-1, 0, 1],
        bcd: Literal[-1, 0, 1],
    ) -> None:
        self.name_ = name
        self.type = type
        self.agent_row_delta = ard  # vertical displacement (-1,0,+1)
        self.agent_col_delta = acd  # horizontal displacement (-1,0,+1)
        self.box_row_delta = brd  # horisontal displacement box (-1,0,+1)
        self.box_col_delta = bcd  # vertical displacement box (-1,0,+1)
