"""
https://gamspy.readthedocs.io/en/latest/user/notebooks/clsp.html

In this guide, we will explore the Capacitated Lot-Sizing Problem (CLSP), which is a classic 
optimization problem in operations research. The CLSP involves determining the optimal production 
quantities of multiple items over a planning horizon, subject to capacity constraints and demand 
requirements. The objective is to minimize the total production, fixed and inventory holding costs 
while satisfying the demand for each item. The fundamental economic question here is:

>> How much to produce of each product and when?
"""
from gamspy import Container, Set, Alias, Parameter, Variable, Variable, Equation, Sum, Model, Sense
import pandas as pd
import numpy as np
from itertools import product
import plotly.express as px
import io, sys


if __name__ == "__main__":
    
    """ ===== DATA ===== """
    
    products = ["Product_A", "Product_B", "Product_C",]
    resources = ["Resource_A", "Resource_B"]
    time_periods = [1, 2, 3, 4]
    
    # Products k that can be handled by resource j
    kj = pd.DataFrame(product(products, resources))
    
    demand_data = pd.DataFrame({
        "Product_A": {1: 100, 2: 150, 3: 120, 4: 180},
        "Product_B": {1: 80, 2: 100, 3: 90, 4: 120},
        "Product_C": {1: 50, 2: 60, 3: 70, 4: 80},
    }).unstack()
    
    setup_cost_data = pd.DataFrame(
        [("Product_A", 100), ("Product_B", 200), ("Product_C", 300)]
    )
    holding_cost_data = pd.DataFrame(
        [("Product_A", 0.2), ("Product_B", 0.1), ("Product_C", 0.6)]
    )
    
    capacity_data = pd.DataFrame(
        [
            ("Resource_A", 1, 340),
            ("Resource_B", 1, 340),
            ("Resource_A", 2, 330),
            ("Resource_B", 2, 330),
            ("Resource_A", 3, 300),
            ("Resource_B", 3, 300),
            ("Resource_A", 4, 380),
            ("Resource_B", 4, 380),
        ]
    )
    
    # Container definition
    m = Container()
    
    # SETS
    k = Set(m, name="k", description="products", records=products)
    j = Set(m, name="j", description="resources", records=resources)
    t = Set(m, name="t", description="time periods", records=time_periods)
    KJ = Set(
        m,
        name="KJ",
        domain=[k, j],
        description="products k that can be handled by resource j",
        records=kj,
    )
    
    # ALIAS
    tau = Alias(m, name="tau", alias_with=t)
    
    # PARAMETERS
    d = Parameter(
        m,
        name="d",
        domain=[k, t],
        description="demand of product k in period t",
        records=demand_data
    )
    
    s = Parameter(
        m,
        name="s",
        domain=k,
        description="fixed setup cost for product k",
        records=setup_cost_data,
    )
    
    h = Parameter(
        m,
        name="h",
        domain=k,
        description="holding cost for product k",
        records=holding_cost_data
    )
    
    c = Parameter(
        m,
        name="c",
        domain=[j, t],
        description="production capacity of resource j in period t",
        records=capacity_data
    )
    
    # VARIABLES
    X = Variable(
        m,
        name="X",
        domain=[k, t],
        type="positive",
        description="lot size of product in period t"
    )
    
    Y = Variable(
        m,
        name="Y",
        domain=[k, t],
        type="binary",
        description="indicate if product k is manufactured in period t",
    )
    
    Z = Variable(
        m,
        name="Z",
        domain=[k, t],
        type="positive",
        description="stock of product k in period t"
    )
    
    """ ===== FORMULATION ===== """
    
    objective = Sum((k, t), s[k] * Y[k, t] + h[k] * Z[k, t])
    
    stock = Equation(
        m,
        name="stock",
        domain=[k, t],
        description="Stock balance equation"
    )
    stock[...] = Z[k, t] == Z[k, t.lag(1)] + X[k, t] - d[k, t]
    
    production = Equation(
        m,
        name="production",
        domain=[k, t],
        description="Ensure production"
    )
    production[...] = X[k, t] <= Y[k, t] * Sum(tau, d[k, tau])
    
    capacity = Equation(
        m,
        name="capacity",
        domain=[j, t],
        description="Capacity restriction"
    )
    capacity[...] = Sum(KJ[k ,j], X[k, t]) <= c[j, t]
    
    Z.fx[k, t].where[t.last] = 0
    
    clsp = Model(
        m,
        name="CLSP",
        problem="MIP",
        equations=m.getEquations(),
        sense=Sense.MIN,
        objective=objective, # type: ignore
    )
    
    output = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    
    solve_info = clsp.solve(output=output)
    
    print("\n==============================\n")
    
    if isinstance(solve_info, pd.DataFrame):
        print(solve_info.T)
    
    print("\n==============================\n")
    
    print(f"Objective function value: {clsp.objective_value}")
    
    print("\n==============================\n")
    
    print("Product Quantities:")
    print(X.records.pivot(index="t", columns="k", values="level"))
    
    fig = px.bar(
        X.records, 
        x="t", 
        y="level", 
        color="k", 
        title="Production Quantities"
    )
    fig.show()
    
    # fig.write_image("production_quantities.pdf")
    
    print("\n==============================\n")
    
    print("Stock levels:")
    print(Z.records.pivot(index="t", columns="k", values="level"))
    
    fig = px.bar(
        Z.records, 
        x="t", 
        y="level", 
        color="k",
        title="Stock"
    )
    fig.show()
    
    # fig.write_image("stock_levels.pdf")