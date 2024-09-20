from gamspy import Container, Set, Parameter, Variable, Equation, Model, Sum, Sense, Options


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
    pass