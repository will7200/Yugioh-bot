import os
import re
import subprocess
import pkg_resources
from shutil import copyfile
import requests
from colorama import Fore, Back, Style
from colorama import init
from lxml import html
from tqdm import tqdm

init(autoreset=True)
# THESE ARE THE PARAMETERS USED TO CHECK AND INSTALL
# Change these to suit your needs
# You can point tesserat setup to your already download tesseract setup
# otherwise this setup file will download it for you
TESSERACT_SETUP_FILE = r''
DEBUG = True
# THESE ARE UNLIKELY TO CHANGE UNLESS YOU INSTALLED NOX SOMEWHERE ELSE
NOX_BIN = os.path.join(os.environ.get(
    'USERPROFILE'), 'AppData', 'Roaming', 'Nox', 'bin')
NOX_BIN_OTHER = os.path.join(r'C:\Program Files (x86)\Nox\bin')
SKIP_PIP_TEST = False


def run_command(command, check_output=False):
    if DEBUG:
        print(Fore.WHITE + Back.YELLOW +
              "Running `{}`".format(command) + Style.NORMAL + Back.CYAN)
    if check_output:
        return subprocess.check_output(command, shell=True)
    return subprocess.call(command, shell=True)


def copy_nox_bin_files():
    adb_file_name = 'nox_adb.exe'
    dll_file_name = 'AdbWinApi.dll'
    path = NOX_BIN
    try:
        os.stat(os.path.join(path, adb_file_name))
        os.stat(os.path.join(path, dll_file_name))
    except FileNotFoundError:
        try:
            path = NOX_BIN_OTHER
            os.stat(os.path.join(path, adb_file_name))
            os.stat(os.path.join(path, dll_file_name))
        except FileNotFoundError:
            print(Fore.RED + """Cannot find the required nox files in either
                    {} or {}, help is requireed""".format(NOX_BIN_OTHER, NOX_BIN))
            return
    copyfile(os.path.join(path, adb_file_name), os.path.join('bin', 'adb.exe'))
    copyfile(os.path.join(path, dll_file_name), os.path.join('bin', dll_file_name))
    print(Back.GREEN + "Copied [{}] into bin folder".format(', '.join([adb_file_name, dll_file_name])) + Back.CYAN)


def check_if_tesseract_installed():
    try:
        os.stat(r'bin\tess\tesseract.exe')
        t = run_command(r'bin\tess\tesseract.exe -v', check_output=True)
        if not 'tesseract' in str(t):
            return False, "Tesseract file did not return expected output from command version"
        return True, "Looks like tesseract is installed already"
    except FileNotFoundError:
        return False, "No tesseract file found"
    except Exception as e:
        raise e


tess_search = r'tesseract-ocr-setup-[0-9].[0-9]{2}.[0-9]{2}(.*).exe'
tess_tested_against = 'tesseract-ocr-setup-3.05.01.exe'
domain_tess = 'https://digi.bib.uni-mannheim.de/tesseract/'


def download_tesseract_source(tess_download):
    try:
        os.stat(tess_download.text_content())
        print(Back.GREEN + "Found file {} locally, using instead".format(
            tess_download.text_content()))
        print(Back.GREEN + "Skipping Download" + Style.RESET_ALL)
        return tess_download.text_content()
    except FileNotFoundError:
        pass
    url = domain_tess + tess_download.get('href')
    print(Back.GREEN + Style.BRIGHT + "Downloading {}".format(url))
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    with tqdm(total=total_size, unit='B', unit_scale=True) as pbar:
        with open(tess_download.text_content(), "wb") as f:
            for data in response.iter_content(chunk_size=1024 * 4):
                f.write(data)
                pbar.update(len(data))
    return tess_download.text_content()


def download_tesseract():
    r = requests.get(domain_tess)
    dom = html.fromstring(r.text)
    links = dom.cssselect('a')
    tess_links = list(filter(lambda x: re.search(
        tess_search, x.text_content()), links))
    original_link = list(filter(lambda x: x.text_content()
                                          == tess_tested_against, links))
    if len(original_link) == 1:
        tess_download = original_link[0]
        print(Back.GREEN + 'Found Expected Tesseract on site ({}), downloading'.format(
            tess_tested_against))
        return download_tesseract_source(tess_download)
    elif len(tess_links) > 0:
        print(Back.GREEN + "Found Tesseract links but none of them were tested against this bot")
        print(Back.GREEN + "Choose one of the following to install")
        for index, link in enumerate(tess_links):
            print(Back.GREEN + "{}. {}".format(index + 1, link.text_content()))
        while True:
            val = input(Back.GREEN + "Choose: ")
            if int(val) in range(1, len(tess_links) + 1):
                tess_download = tess_links[int(val) - 1]
                break
            print(Style.BRIGHT + Style.YELLOW + "Invalid value {}".format(val))
        return download_tesseract_source(tess_download)
    else:
        print(Style.BRIGHT + Style.RED +
              "Found no Tesseract links to download get help or download manually")
        return None


def install_tesseract():
    is_installed, message = check_if_tesseract_installed()
    if is_installed:
        print(Back.GREEN + message + Back.CYAN)
        return
    try:
        os.stat(TESSERACT_SETUP_FILE)
        command_runner(TESSERACT_SETUP_FILE)
    except FileNotFoundError:
        setup_file = download_tesseract()
    try:
        print(Style.BRIGHT + Back.CYAN + 'Make sure to point the installer to the following directory: {}'.format(
            os.path.join(os.getcwd(), 'bin', 'tess')))
        command_runner(setup_file)
    except FileNotFoundError:
        print("Oooo something happened when I downloaded the file, rerun this script")


def set_pip_test(value):
    global SKIP_PIP_TEST
    SKIP_PIP_TEST = value


def check_required_packages():
    if SKIP_PIP_TEST:
        return
    installed_packages = pkg_resources.working_set
    packages = {}
    for package in installed_packages:
        packages[package.project_name] = package.version
    with open('requirements.txt') as f:
        required = list(map(lambda x: x.split('=')[0].replace('>', ''), f.read().splitlines()))
    required = filter(lambda x: not '#' in x, required)
    all_installed = True
    for x in required:
        if x in ['scikit_image', 'scikit_learn', 'opencv_contrib_python']:
            continue
        if x not in packages:
            print(Back.YELLOW + "Not in pip {}".format(x))
            all_installed = False
    try:
        import sklearn
        import skimage
        import cv2
    except ImportError as e:
        print(Back.RED + "Import error for package")
        print(Back.Red + e)
    if not all_installed:
        print(
            Back.RED + Style.BRIGHT + "Not all packages required were found\ntry running `pip -r requirements.txt` again" + Back.CYAN)
    else:
        print(Back.GREEN + "All required packages found" + Back.CYAN)


# Commands to Run
commands = [
    ['Creating Temp Folder \t', 'mkdir tmp'],
    ['Installing Tesseract \t', install_tesseract],
    # ['Installing Requirements', 'pip install -r requirements.txt'], this command hangs have to do manually
    ['Copying nox files required \t', copy_nox_bin_files],
    ['Checking required packages\t', check_required_packages]
]
warning = "Make sure you run this from the root directory of Yugioh-Bot"


def command_runner(comm):
    if callable(comm):
        comm()
    elif type(comm) is list:
        for subcommand in comm:
            command_runner(subcommand)
    else:
        run_command(comm)


def main_install():
    print(Back.CYAN + Style.BRIGHT + warning)
    print(Back.CYAN + "Installing Required components to get this bot up and running")
    for index, command in enumerate(commands):
        print(Back.CYAN + "Component {}: {}{}".format(index, Fore.RED, command[0]) + Fore.WHITE)
        command_runner(command[1])


if __name__ == "__main__":
    main_install()
