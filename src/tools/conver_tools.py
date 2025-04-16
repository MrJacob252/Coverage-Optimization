def param_matrix_to_pylist() -> None:
    
    # input_matrix: str = "/1 1, 2 1, 3 1, 4 1, 5 1, 6 1, 7 1, 8 1, 9 1, 10 1, 11 1, 12 1, 13 1, 14 1, 15 1, 16 1, 17 1, 18 1, 19 1, 20 1, 21 1, 22 1, 23 1, 24 1, 25 1, 26 1, 27 1, 28 1, 29 1, 30 1/"
    # input_matrix: str = "/1 547, 2 473, 3 277, 4 213, 5 194, 6 574, 7 802, 8 462, 9 744, 10 919, 11 219, 12 512, 13 400, 14 293, 15 248, 16 447, 17 481, 18 124, 19 850, 20 451, 21 614, 22 414, 23 222, 24 637, 25 861, 26 572, 27 703, 28 836, 29 995, 30 402/"
    input_matrix: str = "/1 21, 2 21, 3 32, 4 13, 5 90, 6 23, 7 84, 8 100, 9 71, 10 69, 11 41, 12 70, 13 24, 14 31, 15 63, 16 29, 17 34, 18 49, 19 66, 20 53, 21 83, 22 53, 23 27, 24 60, 25 70, 26 23, 27 18, 28 31, 29 49, 30 22, 31 91, 32 94, 33 85, 34 99, 35 28, 36 63, 37 109, 38 36, 39 82, 40 31, 41 57, 42 94, 43 104, 44 51, 45 31, 46 48, 47 27, 48 43, 49 27, 50 81, 51 90, 52 31, 53 34, 54 89, 55 84, 56 84, 57 56, 58 20, 59 30, 60 82, 61 85, 62 42, 63 13, 64 74, 65 76, 66 15, 67 91, 68 71, 69 10, 70 93, 71 23, 72 87, 73 29, 74 96, 75 23, 76 98, 77 87, 78 11, 79 79, 80 22, 81 50, 82 89, 83 41, 84 41, 85 90, 86 73, 87 93, 88 104, 89 46, 90 86, 91 66, 92 89, 93 65, 94 68, 95 15, 96 57, 97 93, 98 73, 99 66, 100 68/"

    input_matrix = input_matrix.strip("/")

    rows= input_matrix.split(", ")
    
    final_matrix: list[str] = []
    
    for r in rows:
        elements = r.split(" ")
        
        tmp_row = ["\t["]
        
        for e in elements:
            tmp_row.append(e)
            tmp_row.append(",")
        tmp_row[-1] = "],\n"
        
        final_matrix.append("".join(tmp_row))

    final_file = f"[\n{''.join(final_matrix)}]"
    print(final_file)

def load_file(file_path: str) -> list[str]:
    
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
        file.close()
        
    return lines

def save_file(file_path: str, data: str) -> None:
    
    with open(file_path, mode="w", encoding="utf-8") as file:
        file.writelines(data)
        file.close()
        

def python_format_matrix(data_matrix: list[list[str]]) -> str:
    """
    Converts the matrix of individual elements to format that can be copy and
    pasted into python
    """ 
    # list of formatted strings with opening bracket
    final_list: list[str] = ["[\n"]
    
    for row in data_matrix:
        tmp_row: list[str] = ["\t["]
        # for element in row:
        for element in row:
            tmp_element = element.strip()
            # only write non-empty elements
            tmp_row.extend(f"{tmp_element},")
            
        tmp_row[-1] = "],\n"
        final_list.append("".join(tmp_row))
    
    final_list.append("]")    
    
    return "".join(final_list)

def matrix_to_lists() -> None:
    matrix_file = "./tools/tmp/matrix_in.txt"

    matrix_from_file = load_file(matrix_file)

    # Delete the header with the indexes for columns
    matrix_from_file.pop(0)
    
    # clean lines a bit
    for i in range(len(matrix_from_file)):
        matrix_from_file[i] = matrix_from_file[i].strip()
    
    # matrix of individual elements
    matrix: list[list[str]] = []
    
    for element in matrix_from_file:
        tmp = element.split()
        # Remove the row index
        tmp.pop(0)
        
        matrix.append(tmp)
    
    final_lines = python_format_matrix(matrix)
    
    save_file("./tools/tmp/matrix_out.txt", final_lines)
        
       

def main() -> None:
    pass
    # param_matrix_to_pylist()
    matrix_to_lists()

if __name__ == "__main__":
    main()