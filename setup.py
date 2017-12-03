from distutils.core import setup

import versioneer

DISTNAME = 'yugioh-bot'
AUTHOR = 'will7200'
EMAIL = 'yugiohbotgit@gmail.com'
LICENSE = 'MIT'
URL = 'https://github.com/will7200/Yugioh-bot'
CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Operating System :: Windows',
    'Intended Audience :: Yugiohers',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.5',
    'License :: OSI Approved :: MIT License',
    'Topic :: Bot']
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
    url=URL,
    description="Botting Yugioh-DuelLinks",
    long_description=open('README.md', 'rt').read(),
    keywords='yugioh bot yugioh-bot duellinks duel links yugioh-duellinks'
)
