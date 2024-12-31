import sys
import subprocess
import importlib
import getpass
import os
import logging

# Configure logging
logging.basicConfig(
    filename="app.log",  # Log file name
    level=logging.DEBUG,  # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
    datefmt="%d-%m-%Y %H:%M:%S",  # Date format
)

logging.debug(
    "*******************************************************************************************************")  # Initial log entry
logging.debug("Started HEMA_Debugger.")

# List to hold external libraries that need to be installed
to_install = []

# List of your imports
imports = [
    "sys", "logging", "subprocess", "tkinter", "requests", 
    "os", "shutil", "json", "re", "webbrowser", "Pillow", "barcode", "io"
]

# List of known built-in modules (standard Python libraries)
builtin_modules = {
    "importlib", "getpass", "sys", "logging", "subprocess", "tkinter", "datetime", "os", "shutil", "json", 
    "re", "webbrowser", "collections", "itertools", "math", "time", "functools", 
    "random", "operator", "string", "statistics", "uuid", "io", "pickle", "socket", 
    "hashlib", "http", "urllib", "socketserver", "select", "platform", "email", 
    "http.client", "http.cookiejar", "http.cookies", "http.cookiejar", "http.server", 
    "http.cookiejar", "hashlib", "pdb", "sqlite3", "xml", "xml.etree", "csv", 
    "asyncio", "asyncore", "curses", "http.cookiejar", "traceback", "zlib", 
    "contextlib", "wsgiref", "http.cookiejar", "xml.sax", "http.cookies", "xmlrpc"
}

def run_program():
    logging.debug("Performing function 'run_program'.")
    # Get the current directory where the script is located
    current_directory = os.getcwd()

    # Construct the script path relative to the current directory
    script_path = os.path.join(current_directory, "HEMA_Gebak.pyw")
    print(script_path)
    try:
        subprocess.Popen(script_path, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        print("Launcher script started.")
        logging.debug("Launcher script started.")
    except Exception as e:
        print(f"Failed to start the launcher script: {e}")
        logging.error(f"Failed to start the launcher script: {e}")


# Check which ones are built-in or need installation
for lib in imports:
    try:
        # Try importing the module
        importlib.import_module(lib)
        if lib in builtin_modules:
            print(f"{lib} is built-in.")
            logging.debug(f"{lib} is built-in.")
        else:
            print(f"{lib} is an external library and needs to be installed.")
            logging.debug(f"{lib} is an external library and needs to be installed.")
            # Add the external library to the to_install list
            to_install.append(lib)
            
    except ImportError:
        # If ImportError occurs, the library is not installed
        print(f"{lib} is missing and needs to be installed.")
        logging.debug(f"{lib} is missing and needs to be installed.")
        # Add the missing library to the to_install list
        to_install.append(lib)

# Display the list of libraries to install
print("\nLibraries that need to be installed:", to_install)

# Prompt user for installation
logging.debug("Prompting user to install libraries.")
answer = input("Nu installeren? Y/N: ")
logging.debug(f"Answer = {answer}")
if answer.lower() == "y":
    failed_installations = []
    
    for lib in to_install:
        try:
            # Install the library directly using pip
            logging.debug(f"Trying to install: {lib}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
        except Exception as e:
            print(f"Failed to install {lib}: {e}")
            logging.error(f"Failed to install {lib}: {e}")
            failed_installations.append(lib)  # Add failed library to list
    
    if failed_installations:
        logging.debug("Writing failed installations to requirements.txt.")
        # Create or overwrite the 'requirements.txt' file with the failed libraries
        with open("requirements.txt", "w") as f:
            for lib in failed_installations:
                f.write(lib + "\n")
        print(f"\nThe following libraries failed to install and have been added to 'requirements.txt': {failed_installations}")
        logging.debug(f"\nThe following libraries failed to install and have been added to 'requirements.txt': {failed_installations}")
    else:
        print("Installation complete without failures.")
        logging.debug("Installation complete without failures.")

logging.debug("Prompting used to laucn program.")
answer = input("Want to launch the program? Y/N: ")
logging.debug(f"Answer = {answer}")
if answer.lower() == "y":
    run_program()