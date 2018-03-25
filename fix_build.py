import os
from distutils.dir_util import copy_tree
from glob import glob


def copy_file():
    site_packages = os.path.join(os.environ.get('PYTHON'), 'Lib', 'site-packages')
    apscheduler_egg = glob(os.path.join(site_packages, 'APScheduler-*'))[0]
    apscheduler_foldername = os.path.basename(apscheduler_egg)
    copy_tree(apscheduler_egg,
              'dist/dlbot/{}'.format(apscheduler_foldername))
    copy_tree(r'dist/dlbot/PyQt5/Qt/plugins', r'dist/dlbot')
    os.remove('dist/dlbot/{}/requires.txt'.format(apscheduler_foldername))


if __name__ == "__main__":
    copy_file()
