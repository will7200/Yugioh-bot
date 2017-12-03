import signal
import logging
import logging.config

import click
import time
import os

import sys
from apscheduler.schedulers.background import BackgroundScheduler

import yaml
from bot import logger
from bot.providers import get_provider


def setup_logging(
        default_path='logging.yaml',
        default_level=logging.INFO,
        env_key='LOG_CFG'
):
    """Setup logging configuration

    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


setup_logging()

from bot.utils.common import make_config_file, default_config
from bot.duel_links_runtime import DuelLinkRunTime


@click.group()
def cli():
    pass


@click.command()
@click.option("--generate-config", default=False, help="Generate Config file", is_flag=True)
@click.option("--file-path", default="configtest.ini", help="File Location")
def config(generate_config, file_path):
    if generate_config:
        make_config_file(file_path)


@click.command()
@click.option("-s", "--start", is_flag=True, default=False)
@click.option("-c", "--config-file", default="config.ini")
def bot(start, config_file):
    if start:

        def handler(signum, frame):
            if signum == signal.SIGINT:
                dlRuntime.shutdown()
                logger.info("Exiting")
                sys.exit(0)

        signal.signal(signal.SIGINT, handler)
        uconfig = default_config()
        uconfig.read(config_file)
        scheduler = BackgroundScheduler()
        dlRuntime = DuelLinkRunTime(uconfig, scheduler)
        scheduler.start()
        try:
            dlRuntime.set_provider(get_provider(uconfig.get('bot', 'provider'))(scheduler, uconfig, dlRuntime))
        except Exception as e:
            logger.fatal("Could not get a provider, take a look at your config file")
            logger.fatal(e)
            sys.exit(0)
        dlRuntime.main()

        while True:
            try:
                time.sleep(5)
                if dlRuntime._shutdown:
                    return
            except InterruptedError:
                pass


@click.command()
@click.option("-s", "--start", is_flag=True, default=False)
@click.option("-c", "--config-file", default="config.ini")
def gui(start, config_file):
    if start:
        import sys
        from PyQt5.QtWidgets import QSystemTrayIcon
        from PyQt5.QtWidgets import QMessageBox
        from PyQt5.QtWidgets import QApplication
        from bot.dl_gui import DuelLinksGui
        app = QApplication(sys.argv)

        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.critical(None, "Systray",
                                 "Systray not dected on system.")
            sys.exit(1)

        QApplication.setQuitOnLastWindowClosed(False)

        uconfig = default_config()
        uconfig.read(config_file)
        scheduler = BackgroundScheduler()
        dlRuntime = DuelLinkRunTime(uconfig, scheduler)
        scheduler.start()
        try:
            dlRuntime.set_provider(get_provider(uconfig.get('bot', 'provider'))(scheduler, uconfig, dlRuntime))
        except Exception as e:
            logger.fatal("Could not get a provider, take a look at your config file")
            logger.fatal(e)
            sys.exit(0)
        dlRuntime.main()
        window = DuelLinksGui(dlRuntime)
        window.show()
        sys.exit(app.exec_())




cli.add_command(bot)
cli.add_command(config)
cli.add_command(gui)

if __name__ == "__main__":
    cli()
