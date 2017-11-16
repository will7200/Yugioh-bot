## Yugioh Bot

[![Software License][ico-license]](LICENSE)
[![Build Status][ico-travis]][link-travis]
[![Coverage Status][ico-scrutinizer]][link-scrutinizer]
[![Quality Score][ico-code-quality]][link-code-quality]


Bot to help with those npc in Yugioh Duel Links.

## Features
- Auto-duel npc
- Collect worlds rewards


## Prerequisites

Have Nox installed (https://www.bignox.com)  
Python 3.5.3 (https://www.python.org/downloads/)  
Install tesseract (http://3.onj.me/tesseract/)  
Install cv2+contrib 3.2.0 (http://www.lfd.uci.edu/~gohlke/pythonlibs/#opencv)  

## Install

Via git

``` bash
$ git clone https://github.com/will7200/Yugioh-bot
$ cd Yugioh-bot
$ pip install -r requirements.txt (or use conda if using)
$ pip install (wheel_file) (cv2+contrib)
```

- Copy downloaded tesseract folder into bin\tess\
- Copy C:\Users\USER_NAME\AppData\Roaming\Nox\bin\nox_adb.exe as adb.exe into bin directory
- Copy C:\Users\USER_NAME\AppData\Roaming\Nox\bin\AdbWinApi.dll into bin directory
- Set Nox as 480x800 phone
- Download Yugioh app
- Setup Yugioh app, link, etc... (first time only)
- Set Yugioh app to the most left of app and bottom on the first page(not the bottom app drawer though, checkout app_placement.png for example)

## Usage

``` bash
$ python main.py
```

The bot creates a file name run_at.json in the current directory that it stores some data. Changing values such as run now to true will
force the bot to run again. Changing the value stop to true will stop the bot, and will stop the current pass through.

## Wakatime

Check out what files I'm working on through [WakaTime](https://wakatime.com/@will2700/projects/fofjloaywu)  


## Change log

Please see [CHANGELOG](CHANGELOG.md) for more information on what has changed recently.


## Contributing

Please see [CONTRIBUTING](CONTRIBUTING.md) and [CONDUCT](CONDUCT.md) for details.

## Security

If you discover any security related issues, please open a issue with "Security -" as the prefix.

## Credits

- [William Flores][link-author]

- [All Contributors][link-contributors]

- tellomichmich (https://github.com/tellomichmich/PokeNoxBot) for the idea and some basic guides for nox usage with python
## License

The MIT License (MIT). Please see [License File](LICENSE) for more information.

[ico-version]: https://img.shields.io/packagist/v/:vendor/:package_name.svg?style=flat-square
[ico-license]: https://img.shields.io/badge/license-MIT-brightgreen.svg?style=flat-square
[ico-travis]: https://img.shields.io/travis/:vendor/:package_name/master.svg?style=flat-square
[ico-scrutinizer]: https://img.shields.io/scrutinizer/coverage/g/:vendor/:package_name.svg?style=flat-square
[ico-code-quality]: https://img.shields.io/scrutinizer/g/:vendor/:package_name.svg?style=flat-square
[ico-downloads]: https://img.shields.io/packagist/dt/:vendor/:package_name.svg?style=flat-square

[link-travis]: https://travis-ci.org/:vendor/:package_name
[link-scrutinizer]: https://scrutinizer-ci.com/g/:vendor/:package_name/code-structure
[link-code-quality]: https://scrutinizer-ci.com/g/:vendor/:package_name
[link-author]: https://github.com/will7200
[link-contributors]: ../../contributors