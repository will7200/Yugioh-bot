import os
from distutils.dir_util import copy_tree
from glob import glob

copy_folders = [
    'APScheduler-*',
    'setuptools*',
    'six-*',
    'pytz*',
    'tzlocal*',

]


def copy_file():
    site_packages = os.path.join(os.environ.get('PYTHON'), 'Lib', 'site-packages')
    for folder in copy_folders:
        setupfolders = glob(os.path.join(site_packages, folder))
        for f in setupfolders:
            foldername = os.path.basename(f)
            copy_tree(f,
                      'dist/dlbot/{}'.format(foldername))
    copy_tree(r'dist/dlbot/PyQt5/Qt/plugins', r'dist/dlbot')
    # os.remove('dist/dlbot/{}/requires.txt'.format(apscheduler_foldername))


if __name__ == "__main__":
    copy_file()
