'''
Tool for verifying that all of the customers' capacities are fully covered
'''

import pandas as pd
import numpy as np
import pathlib, argparse
    
def capacity_check(coverage_data_path: pathlib.Path, 
                   customer_dataset_path: pathlib.Path, 
                   sep: str = ";",
                   verbose: bool = True) -> bool:
    '''
    Checks if all of the customers are coved if full
    Return True if all of the customers are covered, otherwise returns false
    '''
    passed = True
    color = "30"
    
    customer_dataset = pd.read_csv(customer_dataset_path, sep=sep)
    coverage_data = pd.read_csv(coverage_data_path, sep=sep)
    
    customer_demands = customer_dataset["value"]
    
    if verbose:
        print(f"\x1b[1m{coverage_data_path.name}\x1b[0m")
        print("-" * 40)
    
    for i in range(len(customer_demands)):
        # Select the demand for current customer
        demand = int(customer_demands.iloc[i])
        # Sum all values that belong to current customer (i + 1) and have coverage value higher that 0
        covered = sum(coverage_data.loc[(coverage_data["I"] == (i + 1)) & (coverage_data["value"] > 0), "value"])
    
        # print the result coloured depending if it's all covered or not
        # Customer i:    covered    /    demand
        if covered == demand:
            color = "32"
        else:
            color = "31"
            passed = False
        
        if verbose:
            print(f"\x1b[{color}mCustomer {i + 1}:\t{int(covered)}\t/{demand}\x1b[0m")
        
    result = "PASSED" if passed else "FAILED"
    
    if verbose:
        print("-" * 40)
        print(f"\x1b[1;{color}mResult:\t{result}\x1b[0m")

    return passed

def initialise_argparse():
    '''Initialise the argument parser'''
    parser = argparse.ArgumentParser(description="Parse .csv file with the coverage results and the original customer dataset .csv file to determine if all of the customers were successfully covered")
    
    parser.add_argument("--results", "-r", type=str, required=True, help="Enter the path to the customer coverage results .csv file")
    parser.add_argument("--dataset", "-d", type=str, required=True, help="Enter the path to the customer dataset .csv file")
    parser.add_argument("--separator", "-s", type=str, required=False, default=";", help="Choose separator for the .csv file")
    
    global args
    args = parser.parse_args()
    
# def __test():
#     capacity_check(
#         pathlib.Path("./src/tools/tmp/results/P_data.csv"),
#         pathlib.Path("./src/tools/tmp/test_dataset_1_customers.csv"),
#     ) 

def main() -> None:
    '''
    Function to run the scrip when called from a terminal/command line
    '''
    initialise_argparse()
    coverage_results = pathlib.Path(args.results)
    customer_dataset = pathlib.Path(args.dataset)
    
    capacity_check(coverage_results, customer_dataset, args.separator)

if __name__ == "__main__":
    # __test()
    main()