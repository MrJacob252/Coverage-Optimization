import argparse, pathlib, datetime, sys, os
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import pandas as pd

from src.tools import convert_tools, dataset_generator, load_data, dataset_visualisation
from src.models import clscp_balanced_sources as clscp_bs

# TODO:
# - [ ] If no path to dataset is given -> create new with some default setting
# - [ ] Ask to save the results
# - [ ] Save the results and the pictures (and new dataset to new folder)
# - [ ] Ask for a name of the run
# - [ ] Select model to use
# - [ ] Export the output of GAMSpy to some file
# - [ ] (Create some log file)




def init_arparse() -> None:
    '''Initialises argument parser and sets the parsed arguments as a global variable'''
    parser = argparse.ArgumentParser(description="TODO:")
    
    # TODO: add arguments
    parser.add_argument("--dataset", "-d", type=str, required=False, default="", nargs=2, help="Enter path to a service dataset and customer dataset")
    parser.add_argument("--save", "-s", type=str, required=False, default="", help="Folder where to save the results of the run")
    
    global args
    args = parser.parse_args() 
    
def generate_new_dataset() -> tuple[pathlib.Path, pathlib.Path]:
    '''
    Generate new dataset and display it to the user\n
    returns (service dataset path, customer dataset path)
    '''
    
    timestamp = datetime.datetime.now().strftime("%y%m%d_%H%M")
    file_name = f"{timestamp}"
    folder_path = pathlib.Path(f"./tmp/datasets/{timestamp}")
    
    # Create folder if it does not exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    visualSettings = dataset_generator.VisualConfig()
    
    services, customers = dataset_generator.generate_dataset(n=150,
                                                                         max_range=30,
                                                                         spacing=20,
                                                                         disc_radius=5,
                                                                         x_range=(0, 100),
                                                                         y_range=(0, 100),
                                                                         normal_center=(300, 3500),
                                                                         standard_deviation=(80, 100),
                                                                         dataset_name=file_name,
                                                                         file_extension=".csv",
                                                                         save_location=folder_path,
                                                                         visual_config=visualSettings,
                                                                         weight=None,
                                                                         round_customers=0)

    # NOTE: The dataset display will display the images by itself    
    # # Display the generated datasets
    # img_range = mpimg.imread(pathlib.Path(folder_path, f"{file_name}_range.png"))
    # img_no_range = mpimg.imread(pathlib.Path(folder_path, f"{file_name}_no_range.png"))
    
    # fig, axs = plt.subplots(1, 2, figsize=(10, 5))
    # axs[0].imshow(img_range)
    # axs[0].axis("off")
    # axs[0].set_title(f"{file_name} Range")
    # axs[1].imshow(img_no_range)
    # axs[1].axis("off")
    # axs[1].set_title(f"{file_name} No Range")
    # plt.tight_layout()
    # plt.show()    
    
    return(services, customers)
    
def run_clsp_bs(service_path: pathlib.Path, customer_path: pathlib.Path, save_path: pathlib.Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    
    service_location, service_capacity, service_weight, max_range = load_data.load_service(service_path, ".csv")
    customer_locations, customer_demand = load_data.load_customers(customer_path, ".csv")
    distance_matrix = load_data.create_distance_matrix(service_location, customer_locations, decimals=0)
    
    # P_data = how much is customer covered by what service
    # X_data = selected service centers -> sum(X_data) = number of selected centers
    P_data, X_data, output = clscp_bs.clscp_bs(customer_locations,
                                    customer_demand,
                                    service_location,
                                    service_capacity,
                                    service_weight,
                                    max_range,
                                    distance_matrix,
                                    0.8,
                                    save_path)
    
    with output.open("r", encoding="utf-8") as output_file:
        print(output_file.read())
    
    return (P_data, X_data)

def create_save_path() -> pathlib.Path:
    
    timestamp = datetime.datetime.now().strftime("%y%m%d_%H%M")
    
    if args.save == "":
        folder_path = pathlib.Path(f"./tmp/results/{timestamp}")
    else:
        folder_path = pathlib.Path(args.save)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        
    return folder_path
  
def save_results(customer_coverage: pd.DataFrame, seleted_centers: pd.DataFrame, save_path: pathlib.Path):
    
    timestamp = save_path.name
    
    customer_coverage.to_csv(pathlib.Path(save_path, f"{timestamp}_coverage.csv"), sep=";")
    seleted_centers.to_csv(pathlib.Path(save_path, f"{timestamp}_selected.csv"), sep=";")
    

        


def show_heatmap(customer_coverage_data: pd.DataFrame, save_path: pathlib.Path) -> None:
    
    figure, _= dataset_visualisation.heatmap(customer_coverage_data)
    # TODO: maybe include timestamp in the name
    figure.savefig(pathlib.Path(save_path, f"Heatmap.png"), dpi=1000)
    plt.show()
    plt.close(figure)
    
def show_result_scatter(service_dataset_path: pathlib.Path, 
                        customer_dataset_path: pathlib.Path,
                        save_path: pathlib.Path):
    
    hex_colors = [
        '#e61919',  # Bright Red
        '#1a80f2',  # Strong Blue
        '#26bf33',  # Vivid Green
        '#ff9900',  # Orange
        '#a633cc',  # Purple
        '#f2cc1a',  # Golden Yellow
        '#00cccc',  # Cyan / Teal
        '#ff66cc',  # Pink
        '#996600',  # Dark Brown/Olive
    ]
    
    service_dataframe = pd.read_csv(service_dataset_path, sep=";")
    service_locations, _, _, _, = load_data.load_service(service_dataset_path, file_type=".csv")
    customer_dataframe = pd.read_csv(customer_dataset_path, sep=";")
    customer_coverage = pd.read_csv(pathlib.Path(save_path, f"{save_path.name}_coverage.csv"), sep=";")
    selected_centers = pd.read_csv(pathlib.Path(save_path, f"{save_path.name}_selected.csv"), sep=";")
        
    distance_matrix = load_data.create_distance_matrix(service_locations, service_locations, decimals=0)
    
    colored_service_data = dataset_visualisation.color_the_centers(selected_centers, service_dataframe, distance_matrix)
    
    figure, _ = dataset_visualisation.plot_the_results(colored_service_data,
                                                       customer_dataframe,
                                                       customer_coverage,
                                                       hex_colors,
                                                       x_range=(0, 100),
                                                       y_range=(0, 100),
                                                       toggle_ranges=True)
    
    figure.savefig(pathlib.Path(save_path, f"Scatter.png"), dpi=1000)
    plt.show()
    plt.close(figure)
    
    


def main():
    init_arparse()
    
    if args.dataset is "":
        service_dataset_path, customer_dataset_path = generate_new_dataset()
    else:
        service_dataset_path = pathlib.Path(args.dataset[0])
        customer_dataset_path = pathlib.Path(args.dataset[1])
        
    save_path = create_save_path()
    customer_coverage, selected_centers = run_clsp_bs(service_dataset_path, customer_dataset_path, save_path)
    
    save_results(customer_coverage, selected_centers, save_path)
    
    show_heatmap(customer_coverage, save_path)
    
    show_result_scatter(service_dataset_path, customer_dataset_path, save_path)


    # TODO: some bullshittery is happening, prints here will throw exception
    print("print")
    
    
    
     
    

if __name__ == "__main__":
    main()