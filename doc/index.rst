.. Global Router documentation master file, created by
   sphinx-quickstart on Thu Feb  2 17:19:05 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Global Router's documentation!
=========================================


This Global Router project is a VLSI (Very Large Scale Integration) global router that
has been implemented using Python. The goal of the project is to solve the global routing
problem, which is known to be NP-hard.

Global Routing in VLSI is an NP-hard problem. This means that finding an optimal solution
for the problem may require exponential time, and it is not possible to guarantee finding
the optimal solution within a reasonable time frame as the problem size grows.
That is why a heuristic algorithm is developed to create a near-optimal solution.

A web application is also developed to provide a user-friendly interface for the users to
upload their design and run the global router. The web application is developed using
Flask, a Python web framework. The web application is hosted on AWS (Amazon Web Services)
and can be accessed at https://gr.tanyiming.com/

.. toctree::
   :maxdepth: 2
   :caption: Contents

   architecture
   algorithm
   userguide
   cli
   models


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
