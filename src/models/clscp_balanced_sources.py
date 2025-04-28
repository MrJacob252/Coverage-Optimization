'''
This file implements algorithm proposed by M. Seda and P. Seda in their article: 
Coverage Optimization with Balanced Capacitated Fragmentation
https://doi.org/10.3390/math13050808
'''

from gamspy import Container, Set, Parameter, Variable, Equation, Sum, Model, Sense
import pandas as pd
import numpy as np
import plotly.express as px
import io, sys
from numpy.typing import NDArray
from typing import Any
import pathlib

import src.tools.load_data as load
import src.tools.dataset_visualisation as vis

def clscp_bs(customer_locations: NDArray[Any],
            customer_demand: NDArray[Any],
            service_locations: NDArray[Any],
            service_capacity: NDArray[Any],
            service_weight: NDArray[Any],
            max_range: int | float,
            distance_matrix: NDArray[Any],
            r_parameter: float,
            save_path: pathlib.Path | str = "")  -> tuple[pd.DataFrame, pd.DataFrame, pathlib.Path]:
    '''
    Solve given problem using CLSP with balanced sources
    Returns (P_data, X_data)
    '''
    
    # Define dimension of I and J
    dim_i = len(customer_locations)
    dim_j = len(service_locations)
    i_space = np.linspace(1, dim_i, dim_i, dtype=int)
    j_space = np.linspace(1, dim_j, dim_j, dtype=int)
    

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
        # records=service_weight
    )
    for i in service_weight:
        W[str(i[0])] = float(i[1])

    C = Parameter(
        m,
        name="C",
        domain=J,
        description="capacity of the centres",
        # records=service_capacity
    )
    for i in service_capacity:
        C[str(int(i[0]))] = float(i[1])

    B = Parameter(
        m,
        name="B",
        domain=I,
        description="number of customers",
        # records=customer_demand
    )
    for i in customer_demand:
        B[str(int(i[0]))] = float(i[1])

    # SCALAR

    # D_MAX = 35
    # # D_MAX = 15
    # # D_MAX = 100
    # r = 0.8
    
    D_MAX = max_range
    r = r_parameter
    M = dim_i
    N = dim_j
    
    # M = len(I)
    # N = len(J)

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
            A[str(row), str(col)] = 1 if distance_matrix[i][j] <= D_MAX else 0

    # print(A.records)
    # print(A["1", "0"])

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
    
    # TODO: Do something with the output section
    
    # output = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    # solve_info = model.solve(output=output)
    output_file_path = pathlib.Path(save_path, f"gamspy.out")
    with output_file_path.open("w+", encoding="utf-8") as output_file:
        model.solve(output=output_file)
        output_file.flush()
        output_file.seek(0)
    
    # Objective value
    print("==============================")
    print(f"XS: {XS.toValue()}")
    
    P_data = pd.DataFrame(P.toList(), columns=["I", "J", "value"])
    X_data = pd.DataFrame(X.toList(), columns=["J", "selected"])
    # Y_data_pivoted = Y_data.pivot(index="I", columns="J", values="value")
    
    # print(Y_data)
    
    # fig = px.density_heatmap(P_data, x="J", y="I",z="value", text_auto=True,)
    # fig.show()
        
    # P_data.to_pickle(".test/data/P_data.pkl") 
    # X_data.to_pickle(".test/data/X_data.pkl")
    # P_data.to_csv("./src/tools/tmp/results/P_data.csv", sep=";")
    # X_data.to_csv("./src/tools/tmp/results/X_data.csv", sep=";")
    
    return (P_data, X_data, output_file_path)

if __name__ == "__main__":
    
    c_loc, c_dem = load.load_customers("./src/tools/tmp/test_dataset_1_customers.csv", ".csv")
    s_loc, s_cap, s_wei, max_range = load.load_service("./src/tools/tmp/test_dataset_1_service.csv", ".csv")
    
    distance_matrix = load.create_distance_matrix(s_loc, c_loc, decimals=0)
    
    clscp_bs(c_loc, c_dem, s_loc, s_cap, s_wei, max_range, distance_matrix, 0.8)