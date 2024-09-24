from gamspy import Container, Set, Parameter, Variable, Equation, Model, Sum, Sense, Options
import pandas as pd
import sys

if __name__ == "__main__":
    
    # Container to encapsulate all the essential data (data, sets, parameters etc...)
    m = Container()
    
    # Sets - directly correspond to the indices in algebraic representation of a model
    ## If no name is specified the gamspy will generate automatic name (string of numbers and letters)
    ## To access symbol in a container: container["symbol_name"]
    i = Set(container=m, name="i", description="plants")
    j = Set(container=m, name="j", description="markets")
    
    # Parameters
    # To index parameter -> include domain attribute
    a = Parameter(
        container=m,
        name="a",
        domain=i,
        description="supply of commodity at plant i (in cases)"
    )
    b = Parameter(
        container=m,
        name="b",
        domain=j,
        description="demand for commodity at market j (in cases)"
    )
    c = Parameter(
        container=m,
        name="c",
        domain=[i, j],
        description="cost per unit of shipment between plant i and market j"
    )
    
    # Variables 
    # Declares shipment variable for each (i, j) pair
    x = Variable(
        container=m,
        name="x",
        domain=[i, j],
        type="Positive",
        description="amount of commodity to ship from plant i to market j"
    )
    
    # Equations
    # Declaration takes two steps
    # 1. Declare the gamspy symbol
    supply = Equation(
        container=m,
        name="supply",
        domain=i,
        description="observe supply limit at plant i"
    )
    demand = Equation(
        container=m,
        name="demand",
        domain=j,
        description="satisfy demand at domain j"
    )
    # 2. Definition of the equation
    supply[i] = Sum(j, x[i,j]) <= a[i]
    demand[j] = Sum(i, x[i,j]) >= b[j]
    # Print the latex representation
    print(demand.latexRepr())
    
    # Objective
    ## Does not need separate Equation declaration
    ## Can be declared directly in the Model() statement or like this:
    obj = Sum((i,j), c[i,j] * x[i,j])
    
    # Model
    ## Consolidates: constraints, objective function, sense (minimise, maximise, feasibility) and problem type
    ## Two alternative ways to get equations:
    ### List them
    ### Retrieve all equation in container by calling m.getEquations()
    transport = Model(
        container=m,
        name="transport",
        # equations=[supply, demand] # Listing Equations
        equations=m.getEquations(),
        problem="LP",
        sense=Sense.MIN, # Minimise
        objective=obj
    )
    
    # Data
    i.setRecords(["seattle", "san-diego"])
    j.setRecords(["new-york", "chicago", "topeka"])
    a.setRecords([("seattle", 350), ("san-diego", 600)])
    b.setRecords([("new-york", 325), ("chicago", 300), ("topeka", 275)])
    # print(i.records)
    # print(b.records)
    
    ## Distances
    distances = pd.DataFrame(
        [
            ["seattle", "new-york", 2.5],
            ["seattle", "chicago", 1.7],
            ["seattle", "topeka", 1.8],
            ["san-diego", "new-york", 2.5],
            ["san-diego", "chicago", 1.8],
            ["san-diego", "topeka", 1.4],
        ],
        columns=["from", "to", "distance"]
    ).set_index(["from", "to"])
    
    d = Parameter(
        container=m,
        name="d",
        domain=[i, j],
        description="distance between plant i and market j",
        records=distances.reset_index(),
    )
    print(d.records)
    
    ## Calculating cost per unit of shipment between plant i and market j
    ### 1. Python assignment
    freight_cost = 90
    # cost = freight_cost * distances / 1000
    # c.setRecords(cost.reset_index())
    # print(c.records)
    
    ### 2. GAMSpy assignment
    c[i, j] = freight_cost * d[i, j] / 1000
    # print(c.records)
    
    # Solve
    ## To view the output of the solver use sys library
    
    # Verifying generated model
    ## To view generated equations and variables use
    ### getEquationListing and getVariableListing
    ### but we first need to solve the model with column_listing_limit and variable_listing_limit
    
    transport.solve(
        output=sys.stdout,
        options=Options(
            equation_listing_limit=10,
            variable_listing_limit=10,
        )
    )
    
    # Inspect generated equations and variables
    print(transport.getEquationListing())
    print(transport.getVariableListing())
    
    # Same can be called on the individual equation and variable symbols
    print(supply.getEquationListing())
    print(x.getVariableListing())
    
    
    # Retrieving results
    ## Variable results
    print(x.records)
    ## Objective values
    print(transport.objective_value)
    