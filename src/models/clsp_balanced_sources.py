'''
This file implements algorithm proposed by M. Seda and P. Seda in their article: 
Coverage Optimization with Balanced Capacitated Fragmentation
https://doi.org/10.3390/math13050808
'''

from gamspy import Container, Set, Parameter, Variable, Variable, Equation, Sum, Model, Sense
import pandas as pd
import numpy as np
import plotly.express as px
import io, sys

def clsp_bs():

    # dimension of I
    dim_i = 100
    i_space = np.linspace(1, dim_i, dim_i, dtype=int)
    # dimension of j
    dim_j = 30
    j_space = np.linspace(1, dim_j, num=dim_j, dtype=int)


    m = Container()

    # SETS

    I = Set(
        m,
        name = "I",
        description="indexes of customer locations",
        records=i_space
    )

    J = Set(
        m,
        name="J",
        description="indexes of service centres",
        records=j_space
    )

    # PARAMETERS

    W = Parameter(
        m,
        name="W",
        domain=J,
        description="weights of the centres",
        records=sd.weights_of_centres
    )

    C = Parameter(
        m,
        name="C",
        domain=J,
        description="capacity of the centres",
        records=sd.capacity_of_centres
    )

    B = Parameter(
        m,
        name="B",
        domain=I,
        description="number of customers",
        records=sd.number_of_customers
    )

    # SCALAR

    D_MAX = 35
    # D_MAX = 15
    # D_MAX = 100
    r = 0.8
    
    M = len(I)
    N = len(J)

    # TABLE

    A = Parameter(
        m,
        name="A",
        domain=[I, J],
        description="distance matrix",
    )

    for i, row in enumerate(i_space):
        for j, col in enumerate(j_space):
            # # Load the distance data to the distance matrix
            # A[str(row), str(col)] = sd.distance_matrix[i][j]
            
            # Directly convert the distance matrix data to binary reachability matrix
            A[str(row), str(col)] = 1 if sd.distance_matrix[i][j] <= D_MAX else 0

    print(A.records)
    # print(A["1", "0"])

    print(sd.distance_matrix[0][0] <= D_MAX)
    print(sd.distance_matrix[1][0] <= D_MAX)

    # VARIABLES
    
    X = Variable(
        m,
        name="X",
        domain=J,
        type="binary",
        description="decision variable (whether or to select centre j to cover)"
    )
    
    P = Variable(
        m,
        name="P",
        domain=[I, J],
        type="integer",
        description="number of persons from location i covered from centre j",
    )
    
    XS = Variable(
        m,
        name="XS",
        type="free",
        description="objective function (number of selected centres)"
    )
    
    # EQUATIONS
    
    EQ1 = Equation(
        m,
        name="EQ1",
        domain=[I],
        description="conditions for covering each customer from at least one centre",
    )
    
    EQ3 = Equation(
        m,
        name="EQ3",
        domain=[J],
        description="capacity of selected centre j must cover the sum of all customers assigned to it",
    )
    
    EQ4 = Equation(
        m,
        name="EQ4",
        domain=[I],
        description="people from location i are covered from selected centres"
    )
    
    EQ5 = Equation(
        m,
        name="EQ5",
        domain=[J],
        description="customers cannot be covered from a non-selected centre"
    )
    
    EQ6 = Equation(
        m,
        name="EQ6",
        domain=[I,J],
        description="threshold of fragments"
    )
    
    OBJFUN = Equation(
        m,
        name="OBJFUN",
        description="objective function (number of selected centres)"
    )
    
    EQ1[I] = Sum(J, A[I, J] * X[J]) >= 1
    EQ3[J] = C[J] * X[J] >= Sum(I, A[I, J] * P[I, J])
    EQ4[I] = B[I] == Sum(J, A[I, J] * P[I, J])
    EQ5[J] = Sum(I, P[I, J]) <= Sum(I, B[I]) * X[J]
    EQ6[I, J] = P[I, J] >= r * B[I] * X[J] * A[I, J]/N
    OBJFUN[...] = XS == Sum(J, W[J] * X[J])
    
    model = Model(
        m,
        name="facility_locations",
        problem="MIP",
        equations=m.getEquations(),
        sense=Sense.MIN,
        objective=XS
    )
    
    output = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    
    solve_info = model.solve(output=output)
    
    # Objective value
    print("==============================")
    print(f"XS: {XS.toValue()}")
    
    P_data = pd.DataFrame(P.toList(), columns=["I", "J", "value"])
    X_data = pd.DataFrame(X.toList(), columns=["J", "selected"])
    # Y_data_pivoted = Y_data.pivot(index="I", columns="J", values="value")
    
    # print(Y_data)
    
    fig = px.density_heatmap(P_data, x="J", y="I",z="value", text_auto=True,)
    fig.show()
    
    P_data.to_pickle(".test/data/P_data.pkl")
    X_data.to_pickle(".test/data/X_data.pkl")
