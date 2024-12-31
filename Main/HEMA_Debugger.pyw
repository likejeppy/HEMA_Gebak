import subprocess
import getpass

# Path to the Python script
script_path = r"C:/Users/{}/Documents/GitHub/HEMA_Gebak/Main/requirements.py".format(getpass.getuser())

# Command to run the script in the command prompt (cmd)
cmd = f"start cmd /C python \"{script_path}\"" # change /C to /K to not auto close terminal

# Open in command prompt
try:
    subprocess.Popen(cmd, shell=True)
    print("The Python file was opened in CMD.")
except Exception as e:
    print(f"Failed to open the Python file in CMD: {e}")
