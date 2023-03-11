.. Global Router documentation master file, created by
   sphinx-quickstart on Thu Feb  2 17:19:05 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Global Router's documentation!
=========================================

This Global Router project is a VLSI (Very Large Scale Integration) global router that has been implemented using Python. The goal of the project is to solve the global routing problem, which is known to be NP-hard. 

Global Routing in VLSI is an NP-hard problem. This means that finding an optimal solution for the problem may require exponential time, and it is not possible to guarantee finding the optimal solution within a reasonable time frame as the problem size grows.

The global routing problem involves finding a feasible routing solution that connects all the pins of a multi-pin net using the minimum possible wire length and minimum overflow, where overflow occurs when two or more nets occupy the same routing channel simultaneously.

Due to the problem's complexity, global routing in VLSI is typically solved using heuristic or approximation algorithms, which may not always produce the optimal solution but provide a good enough solution in a reasonable time frame.

To improve the solution, this project has incorporated the use of randomization and multiprocessing.

Overall, the Global Router project is a powerful tool for VLSI designers, providing a fast and efficient way to solve the global routing problem and optimize layout designs. With its advanced features and capabilities, it is a valuable asset for any team working in the field of VLSI design.

.. toctree::
   :maxdepth: 2
   :caption: Contents

   cli
   models


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
