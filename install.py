import os
import subprocess

# THESE ARE THE PARAMETERS USED TO CHECK AND INSTALL
# Change these to suit your needs
TESSERACT_SETUP = r'D:\Downloads\tesseract-ocr-setup-3.05.01.exe'
DEBUG = True
# THESE ARE UNLIKELY TO CHANGE UNLESS YOU INSTALLED NOX SOMEWHERE ELSE
NOX_BIN = os.path.join(os.environ.get(
    'USERPROFILE'), 'AppData', 'Roaming', 'Nox', 'bin')
NOX_BIN_OTHER = os.path.join(r'C:\Program Files (x86)\Nox\bin')


def run_command(command):
    if DEBUG:
        print("Running {}".format(command))
    subprocess.call(command, shell=True)


nox_file_commands = [
    'cp {} bin/adb.exe',
    'cp {} bin/'
]


def copy_nox_bin_files():
    adb_file_name = 'nox_adb.exe'
    dll_file_name = 'AdbWinApi.dll'
    path = NOX_BIN
    try:
        adb = os.stat(os.path.join(path, adb_file_name))
        dll = os.stat(os.path.join(path, dll_file_name))
    except FileNotFoundError:
        try:
            path = NOX_BIN_OTHER
            adb = os.stat(os.path.join(path, adb_file_name))
            dll = os.stat(os.path.join(path, dll_file_name))
        except FileNotFoundError:
            print("""Cannot find the required nox files in either
                    {} or {}, help is requireed""".format(NOX_BIN_OTHER, NOX_BIN))
    run_command('cp "{}" bin/adb.exe'.format(os.path.join(path, adb_file_name)))
    run_command('cp "{}" bin/'.format(os.path.join(path, dll_file_name)))


def check_if_tesseract_installed():
    try:
        run_command(r'bin\tess\tesseract.exe')
        return True, "Looks like tesseract is installed already skipping"
    except Exception as e:
        raise e


# Commands to Run
commands = [
    ['Installing Tesseract\n Make Sure to point it to the following directory {}'.format(
        os.path.join(os.getcwd(), 'bin', 'tess')), [
        'cp {} .'.format(TESSERACT_SETUP),
        TESSERACT_SETUP
    ], check_if_tesseract_installed],
    #['Installing Requirements', 'pip install -r requirements.txt'],
    ['Creating Temp Folder', 'mkdir tmp'],
    ['Copying nox files required', 
        copy_nox_bin_files
    ]
]
warning = "Make sure you run this from the root directory of Yugiob-Bot"


print(warning)
print("Installing Required components to get this bot up and running")
for command in commands:
    print(command[0])
    if len(command) == 3:
        skip, message = command[2]()
        if skip:
            print(message)
            continue
    if callable(command[1]):
        command[1]()
    elif type(command[1]) is list:
        for subcommand in command[1]:
            run_command(subcommand)
    else:
        run_command(command[1])
