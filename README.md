# Warmup: Multi-Agent Pathfinding Search Algorithms

Implementation of classical AI search algorithms for **multi-agent pathfinding** using the **Python search client** from the DTU course **02285 AI and Multi-Agent Systems**.

This repository focuses on understanding and implementing core search techniques for grid-based planning problems, including uninformed search, informed search, heuristic design, and benchmarking.

## Overview

The project explores how different search strategies behave in multi-agent pathfinding environments where agents must navigate toward goal states while avoiding collisions and obstacles.

The implementation is based on the provided course search client, with development carried out in:

- `searchclient/searchclient_python`

The repository also contains the original Java and Python client structure distributed for the course.

## Implemented Algorithms

- **Breadth-First Search (BFS)**
- **Depth-First Search (DFS)**
- **A\* Search**
- **Greedy Best-First Search**

## Project Goals

- Implement graph search for multi-agent pathfinding
- Compare uninformed and informed search strategies
- Design and test heuristic functions
- Benchmark algorithm performance on multiple levels
- Analyze how branching factor, state-space size, and heuristic quality affect performance

## Repository Structure

```text
.
├── README.md
├── hospital_domain.pdf
└── searchclient/
    ├── Levels/
    ├── searchclient_java/
    ├── searchclient_python/
    ├── debugging.pdf
    └── server.jar
