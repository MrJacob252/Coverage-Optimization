'''
Capacitated Location Set Covering Problem - System Optimal
From: R. L. Church, Alan Murray; Location Covering Models History, Applications and Advancements 
ISBN: 978-3-319-99846-6
'''
from gamspy import Container, Set, Parameter, Variable, Equation, Sum, Model, Sense
import pandas as pd
import numpy as np
from numpy.typing import NDArray
from typing import Any
import pathlib

import src.tools.load_data as load
import src.tools.dataset_visualisation as vis

def clscp_so(customer_locations: NDArray[Any],
             customer_demand: NDArray[Any],
             service_locations: NDArray[Any],
             service_capacity: NDArray[Any],
             distance_matrix: NDArray[Any],
             max_range: int | float,
             save_path: pathlib.Path | str = "") -> tuple[pd.DataFrame, pd.DataFrame, pathlib.Path]:
    '''
    Solves given problem using CLSCP - System Optimal variant
    Returns: 
    '''
    m = Container()
    
    # Define dimension of I and J
    dim_i = len(customer_locations)
    dim_j = len(service_locations)
    i_space = np.linspace(1, dim_i, dim_i, dtype=int)
    j_space = np.linspace(1, dim_j, dim_j, dtype=int)
    
    # Sets
    I = Set(
        m,
        name = "I",
        description="Indexes of customer demand points/areas/locations",
        records=i_space
    )
    
    J = Set(
        m,
        name="J",
        description="Indexes of potential facility sites",
        records=j_space,
    )
    
    # Scalars

    # Desired maximal service standard
    S: int | float = max_range
    
    # Parameters
    C = Parameter(
        m,
        name="C",
        domain=J,
        description="Capacity of potential facility j"
    )
    for i in service_capacity:
        C[str(int(i[0]))] = float(i[1])
        
    d_ij = Parameter(
        m,
        name="d_ij",
        domain=[I, J],
        description="Distance matrix (shortest distance between i and j)"
    )
    for i, row in enumerate(i_space):
        for j, col in enumerate(j_space):
            d_ij[str(row), str(col)] = 1 if distance_matrix[i][j] <= S else 0
    
    a_i = Parameter(
        m,
        name="a_i",
        domain=I,
        description="Amount of demand at i"
    )
    for i in customer_demand:
        a_i[str(int(i[0]))] = float(i[1])
    
    # Variables
    z_ij = Variable(
        m,
        name="z_ij",
        domain=[I, J],
        type="positive",
        description="Fraction of demand i that is assigned to facility j"
    )
    
    X = Variable(
        m,
        name="X_j",
        domain=J,
        type="binary",
        description="Decision variable: 1 if facility is located at j, otherwise 0"
    )
    
    XS = Variable(
        m,
        name="XS",
        type="free",
        description="objective function (number of selected centers)"
    )
    
    # Equations
    
    # Objective function
    OBJFUN = Equation(
        m,
        name="Objective_function",
        description="Objective function (Number of selected centers)"
    )
    
    OBJFUN[...] = XS == Sum(J, X[J])
    
    # Constraints
    EQ1 = Equation(
        m,
        domain=[I],
        name="EQ1",
        description="Constraint 1"
    )
    EQ2 = Equation(
        m,
        domain=[J],
        name="EQ2",
        description="Constraint 2"
    )
    
    
    EQ1[I] = Sum(J, z_ij[I, J] * d_ij[I, J]) == 1
    EQ2[J] = Sum(I, a_i[I] * z_ij[I, J]) <= C[J]*X[J]
    
    model = Model(
        m,
        name="CLSCP_System_Optimal",
        problem="MIP",
        equations=m.getEquations(),
        sense=Sense.MIN,
        objective=XS
    )
    
    output_file_path = pathlib.Path(save_path, f"gamspy.out")
    with output_file_path.open("w+", encoding="utf-8") as output_file:
        model.solve(output=output_file)
        output_file.flush()
        output_file.seek(0)
        
    print("Hammer time")
    
    capacities = pd.DataFrame(z_ij.toList(), columns=["I", "J", "value"])
    selected = pd.DataFrame(X.toList(), columns=["J", "selected"])
    
    capacities = recalculate_capacities(capacities, customer_demand)
    
    return (capacities, selected, output_file_path)
    
def recalculate_capacities(calculated_capacities: pd.DataFrame, customer_demand: NDArray[Any]) -> pd.DataFrame:
    '''Recalculate the resulting capacity fraction into integer demand values'''
    
    final_capacities = calculated_capacities.copy()
    
    for customer_index, demand in customer_demand:
        
        # Filter the data to list only facilities that covet this customer
        filtered_demand = calculated_capacities[calculated_capacities["I"] == str(int(customer_index))][calculated_capacities["value"] != 0.0]
        num_services = len(filtered_demand)
        
        # Only one service is covering the customer
        if num_services == 1:
            dataframe_index = filtered_demand.index[0]
            final_capacities.loc[dataframe_index, "value"] = demand
            
        else:
            sum_demand = 0
            for dataframe_index in filtered_demand.index:
                if not dataframe_index == filtered_demand.index[-1]:
                    covered = np.round(final_capacities.loc[dataframe_index, "value"] * demand)
                    sum_demand += covered
                    final_capacities.loc[dataframe_index, "value"] = covered
                # Different behaviour for the last element to preserve the total value
                else:
                    final_capacities.loc[dataframe_index, "value"] = demand - sum_demand
    
    return final_capacities
    

def __test():
    
    c_loc, c_dem = load.load_customers("./src/tools/tmp/test_dataset_1_customers.csv", ".csv")
    s_loc, s_cap, _, max_range = load.load_service("./src/tools/tmp/test_dataset_1_service.csv", ".csv")
    
    distance_matrix = load.create_distance_matrix(s_loc, c_loc, decimals=0)
    
    save_path = pathlib.Path("./src/models/tmp/clscp_so_test")
    clscp_so(c_loc, c_dem, s_loc, s_cap, distance_matrix, max_range, save_path)
    
    

if __name__ == "__main__":
    __test()