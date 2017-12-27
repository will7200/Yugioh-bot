## Yugioh Bot

[![Join the chat at https://gitter.im/Yugioh-bot/Lobby](https://badges.gitter.im/Yugioh-bot/Lobby.svg)](https://gitter.im/Yugioh-bot/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![Discord](https://img.shields.io/discord/392538066633359360.svg?colorB=0082ff&style=flat)](https://discord.gg/PGWedhf)
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
 -- Note: Windows 10 Users make sure to disable Hyper-V in window services otherwise BSoD errors will occur.  
Python 3.5 or 3.6 (https://www.python.org/downloads/)  
Install tesseract (http://3.onj.me/tesseract/)  
If the above link is giving issues or is slow:
Tesseract at UB Mannheim (https://github.com/UB-Mannheim/tesseract/wiki)  
 -- Note: Testings occured on the 3.05.01 version  
Install cv2+contrib 3.2.0 (http://www.lfd.uci.edu/~gohlke/pythonlibs/#opencv)  
 -- opencv_python‑3.3.1+contrib works too

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
- No longer needed, App is opened through adb shell command  
    - Set Yugioh app to the most left of app and bottom on the first page(not the bottom app drawer though, checkout app_placement.png for example)

## Usage

To Start The Bot
``` bash
$ python main.py -s
```

Generate Config File --  Only Needed if you did not git clone master
``` bash
$ python main.py config --generate-config {optional --file-path path/to/file/config.ini}
```
The bot creates a file for runtime purposes that is specified in the config file name runtimepersistence under the bot section.  

The following values can be changed during runtime that will control the bot until the ui has been made. 
["run_now", "stop", "next_run_at"]

run_now: if the bot is currently stopped it will schedule a run immediately  
stop: if the bot is currently running it will halt execution  
next_run_at: will schedule a run at the specified time, if currently running it will remove the current job in place of the new one

GUI
````bash
$ pythonw main.py gui -s
````
This will start the bot with gui controls.  
So far the following signals have been implemented: 
* Stop
* Run Now  
![Image of Gui](https://image.ibb.co/ccQ79b/yugioh_duel_bots_gui.png)

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
