import numpy as np
import pandas as pd
from numpy.typing import NDArray, ArrayLike
from typing import Literal, Any
import pathlib
from scipy.spatial.distance import cdist

def load_customers(path: str | pathlib.Path, 
                   file_type: Literal[".csv"] | Literal[".pkl"], 
                   sep: str = ";") -> tuple[NDArray[Any], NDArray[Any]]:
    '''
    Load the customer dataset and split it into location array and customer demand array
    '''
    match file_type:
        case ".csv":
            customer_data = pd.read_csv(path, sep=sep)
        case ".pkl":
            customer_data = pd.read_pickle(path)
            
    
    x_location = np.array(customer_data["x"].values)
    y_location = np.array(customer_data["y"].values)
    demand = np.array(customer_data["value"].values)
    
    # Check that all of the data columns have same length (just in case)
    if not (len(x_location) == len(y_location) == len(demand)):
        raise Exception("Something is wrong with the supplied dataset, the columns are not the same length")
    
    index_column = np.arange(1, len(x_location) + 1)
    
    # Create the location array
    customer_locations = np.column_stack((index_column, x_location, y_location))
    
    # Create the demand array
    customer_demand = np.column_stack((index_column, demand))
    
    return (customer_locations, customer_demand)

def load_service(path: str | pathlib.Path,
                 file_type: Literal[".csv"] | Literal[".pkl"],
                 sep: str = ";") -> tuple[NDArray[Any], NDArray[Any], NDArray[Any], int | float]:
    '''
    Load the service locations data and split them into:\n
    Location array, capacity array, weight array and max service coverage distance constant
    '''
    
    match file_type:
        case ".csv":
            service_data = pd.read_csv(path, sep=sep)
        case ".pkl":
            service_data = pd.read_pickle(path)
            
    x_location = np.array(service_data["x"].values)
    y_location = np.array(service_data["y"].values)
    capacity = np.array(service_data["value"].values)
    weight = np.array(service_data["weight"].values)
    max_range = float(service_data["range"].values[0])
    
    # Check that all of the data columns have same length (just in case)
    if not (len(x_location) == len(y_location) == len(capacity) == len(weight)):
        raise Exception("Something is wrong with the supplied dataset, the columns are not the same length")
    
    index_column = np.arange(1, len(x_location) + 1)
    
    # Location array
    service_locations = np.column_stack((index_column, x_location, y_location))
    
    # Capacity array
    service_capacity = np.column_stack((index_column, capacity))
    
    # Weight array
    service_weight = np.column_stack((index_column, weight))
    
    return (service_locations, service_capacity, service_weight, max_range)

def create_distance_matrix(service: NDArray[Any], 
                           customers: NDArray[Any],
                           decimals: int | None = None) -> NDArray[Any]:
    
    service_coords = service[:, 1:]
    customer_coords = customers[:, 1:]
    
    # Compute the distance matrix with the final shape of (customers, services)
    distance_matrix = cdist(customer_coords, service_coords)

    if decimals is not None:
        distance_matrix = np.round(distance_matrix, decimals=decimals)

    return distance_matrix

if __name__ == "__main__":
    pass