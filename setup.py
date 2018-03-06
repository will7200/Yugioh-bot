from setuptools import setup
import pypandoc
from pypandoc.pandoc_download import download_pandoc

# see the documentation how to customize the installation path
# but be aware that you then need to include it in the `PATH`
try:
    pypandoc.get_pandoc_path()
except OSError:
    download_pandoc()
try:
    from pypandoc import convert

    read_md = lambda f: convert(f, 'rst')
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to RST")
    read_md = lambda f: open(f, 'r').read()
import versioneer
import unittest


def bot_test():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    return test_suite


DISTNAME = 'yugioh-bot'
AUTHOR = 'will7200'
EMAIL = 'yugiohbotgit@gmail.com'
LICENSE = 'MIT'
URL = 'https://github.com/will7200/Yugioh-bot'
CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Operating System :: Microsoft :: Windows',
    'Intended Audience :: End Users/Desktop',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'License :: OSI Approved :: MIT License']
setup(
    name=DISTNAME,
    maintainer=AUTHOR,
    version=versioneer.get_version(),
    packages=[
        'bot',
        'bot.providers',
        'bot.providers.nox',
        'bot.utils'
    ],
    cmdclass=versioneer.get_cmdclass(),
    classifiers=CLASSIFIERS,
    platforms='win32',
    maintainer_email=EMAIL,
    python_requires='>=3.5',
    url=URL,
    description="Botting Yugioh-DuelLinks",
    long_description=read_md('README.md'),
    keywords='yugioh bot yugioh-bot duellinks duel links yugioh-duellinks',
    test_suite='setup.bot_test'
)
