# TransportFlow

A Python-based Transportation Problem solver that uses Vogel’s Approximation Method (VAM), Least Cost Method, and MODI optimization to minimize transportation costs.

## Project Overview

TransportFlow is a university project that allocates available employees from four companies to ten destinations, such as banks, hospitals, universities, and factories.

The program calculates transportation allocations while satisfying supply and demand constraints and comparing the total costs of different methods.

## Methods Used

- **Balance Check:** Checks whether total supply equals total demand.
- **Vogel’s Approximation Method (VAM):** Finds an initial feasible solution using row and column penalties.
- **Least Cost Method:** Finds an initial feasible solution by selecting the lowest available transportation cost.
- **MODI Method:** Iteratively improves the initial solution to minimize the total transportation cost.

## Scenarios

1. **Demand Greater Than Supply:** Adds a Dummy Source.
2. **Supply Greater Than Demand:** Adds a Dummy Demand destination.
3. **Balanced Supply and Demand:** No dummy row or column is needed.

## Features

- Solves three transportation scenarios.
- Displays allocation quantities for each route.
- Compares the costs produced by VAM, Least Cost, and MODI.
- Generates graphs using Matplotlib.
- Handles unbalanced transportation problems using dummy rows or columns.

## Requirements

- Python 3
- NumPy
- Matplotlib

Install the required libraries:

```bash
python -m pip install numpy matplotlib
```

## How to Run

1. Download or clone the repository.
2. Open a terminal in the project folder.
3. Install the required libraries.
4. Run the Python script:

```bash
python main.py
```

Replace `main.py` with the actual name of your Python file.

## Project Team

Add the names of the project team members here.

## Academic Project

Developed as a university project to demonstrate transportation optimization techniques and compare different allocation methods.
