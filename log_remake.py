import re
import sys
import os

root_folder_path = str(sys.argv[1])
log_file = open("log_remake.log", 'w')
log_file.write("START" + os.linesep)

def get_files_list(root_folder_path):
    extensions_to_check = "\.(C|c|c\+\+|cc|cpp|cxx|h|hh|hpp)$" # More extensions can be added if needed
    result_list = []
    for root, dirs, files in os.walk(root_folder_path):
        for files in files:
            if (re.search(extensions_to_check, files)):
                result_list.append(os.path.join(root, files))
    return result_list

def implement_logging(input_file_path):
    file = open(input_file_path, 'r')
    result_file_path = input_file_path + ".bak"
    bak = open(result_file_path, 'w')
    logger_name = logger_name_creator()
    flag = True

    # Simple pattern which searches for any occurance of std::cout or std::cerr (case sensitive):
    simple_r = re.compile("(std::)?(cout|cerr)\s*<<")
    # For "cout" this has to be replaced with string in next line:
    cout_start = "(std::)?cout\s*<<"
    trace_start = "LOG4CXX_TRACE(" + logger_name + ","
    # For "cerr" this has to be replaced with string in next line:
    cerr_start = "(std::)?cerr\s*<<"
    error_start = "LOG4CXX_ERROR(" + logger_name + ","
    # Line end to use without macro
    normal_end = "(\s*<<\s*std::endl)?;(\r|\n)"
    log_end = ");" + os.linesep
    # Line end to use with macro
    macro_normal_end = "(\s*<<\s*std::endl;)?\);(\r|\n)"
    macro_log_end = "););" + os.linesep

    for line in file.readlines():
        buffer = line
        for match in re.finditer(simple_r, line):
            if flag:
                log_file.write("IMPLEMENTATION NEEDED: " + input_file_path + "  |  " + logger_name + os.linesep)
                flag = False
            # Swapping begenning of the log
            if re.search(cout_start, buffer):
                buffer = re.sub(cout_start, trace_start, buffer)
            elif re.search(cerr_start, buffer):
                buffer = re.sub(cerr_start, error_start, buffer)
            else:
                log_file.write("ATENTION NEEDED: Could not swap begenning of the log" + os.linesep)
            # Swapping ending of the log
            if re.search(macro_normal_end, buffer):
                buffer = re.sub(macro_normal_end, macro_log_end, buffer)
            elif re.search(normal_end, buffer):
                buffer = re.sub(normal_end, log_end, buffer)
            else:
                log_file.write("ATENTION NEEDED: Could not swap end of the log" + os.linesep)

        bak.write(buffer)

    file.close()
    bak.close()
    os.replace(result_file_path, input_file_path)

# Function to create logger name
def logger_name_creator(file_path):
    current_folder_path = file_path
    if re.search("modules", current_folder_path):
        logger_name = "modLoggerPtr"
    elif re.search("resources", current_folder_path):
        logger_name = "resLoggerPtr"
    else:
        logger_name = "otherLoggerPtr"
    return logger_name

# main body
for file in (get_files_list(root_folder_path)):
    implement_logging(file)
log_file.write("END" + os.linesep)
log_file.close()