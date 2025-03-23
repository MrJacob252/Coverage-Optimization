from gamspy import Container, Set, Alias, Parameter, Variable, Equation, Model, Sum, Sense
import numpy as np
import sys
import io
import pandas as pd

"""
Millco has three wood mills and is planning three new logging sites. 
Each mill has a maximum capacity and each logging site can harvest a certain
number of truckloads of lumber per day. The cost of a haul is $2/mile of 
distance. If distances from logging sites to mills are given below, 
how should the hauls be routed to minimize hauling costs while meeting all 
demands?

| Logging Site | Mill A | Mill B | Mill C | Max loads per day |
| ------------ | ------ | ------ | ------ | ----------------- |
| 1            | 8      | 15     | 50     | 20                |
| 2            | 10     | 17     | 20     | 30                |
| 3            | 30     | 26     | 15     | 45                |
| Mill demand  | 30     | 35     | 30     |                   |
"""

if __name__ == "__main__":
    m = Container()
    
    """Model the sets and parameters"""
    sites = Set(container=m, name="sites", records=["1", "2", "3"])
    mills = Set(container=m, name="mills", records=["Mill A", "Mill B", "Mill C"])
    dist = Parameter(
        container=m,
        name = "dist",
        domain=[sites, mills],
        records=np.array([
            [8 , 15, 50],
            [10, 17, 20],
            [30, 26, 15],
        ])
    )
    supply = Parameter(
        container=m,
        name="supply",
        domain=sites,
        records=np.array([20, 30, 45])
    )
    demand = Parameter(
        container=m,
        name="demand",
        domain=mills,
        records=np.array([30, 35, 30])
    )
    cost_per_haul = 4
    
    """Model variables"""
    ship = Variable(
        container=m,
        name="ship",
        type="positive",
        domain=[sites, mills]
    )
    
    defcost = cost_per_haul * Sum([sites, mills], ship[sites, mills] * dist[sites, mills])
    
    defsupply = Equation(
        container=m,
        name="defsupply",
        domain=sites
    )
    defsupply[sites] = Sum(mills, ship[sites, mills]) == supply[sites]
    
    defdemand = Equation(
        container=m,
        name="defdemand",
        domain=mills
    )
    defdemand[mills] = Sum(sites, ship[sites, mills]) == demand[mills]
    
    millco = Model(
        container=m,
        name="millco",
        equations=m.getEquations(),
        problem="LP",
        sense=Sense.MIN,
        objective=defcost
    )
    
    # Used to print complete output of the solver to the console
    output = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    
    # Returns DataFrame with some info about the problem/solver
    solve_info = millco.solve(output=output)
    
    print("\n==============================\n")
    
    if isinstance(solve_info, pd.DataFrame):
        print(solve_info.T)
    
    print("\n==============================\n")
    
    print(ship.records.pivot(index="sites", columns="mills", values="level"))
    
    print(f"\nTotal cost will be {millco.objective_value}")
    