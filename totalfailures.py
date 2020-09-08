
#stream to file
#make run > ../build/output.txt

file_name = "build/output.txt"
list_of_strings = ["FAILED TEST"]
fail_count_sum = 0


def search_multiple_strings_in_file(file_name, list_of_strings):
    """Get line from the file along with line numbers, which contains any string from the list"""
    line_number = 0
    list_of_results = []
    # Open the file in read only mode
    with open(file_name, 'r') as read_obj:
        # Read all lines in the file one by one
        for line in read_obj:
            line_number += 1
            # For each line, check if line contains any string from the list of strings
            for string_to_search in list_of_strings:
                if string_to_search in line:
                    # If any string is found in line, then append that line along with line number in list
                    fail_no, fail_str = line.split("F")
                    list_of_results.append((string_to_search, line_number, fail_no))
    # Return list of tuples containing matched string, line numbers and lines where string is found
    read_obj.close()
    return list_of_results



try:
    f = open(file_name)
    for i in range(0, len(search_multiple_strings_in_file(file_name, list_of_strings))):
        fail_count = int(search_multiple_strings_in_file(file_name, list_of_strings)[i][2])
        fail_count_sum = fail_count_sum + fail_count
    print("TOTAL FAILED TEST COUNT: ", fail_count_sum)
except FileNotFoundError:
    print("file does not exist")

input("Press Enter to continue")
