import logging
import logging.config
import os
import signal
import sip
import sys
import time
import traceback

import click
import yaml
from apscheduler.schedulers.background import BackgroundScheduler

from install import set_pip_test, main_install


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


def setup_runtime(uconfig):
    from bot.duel_links_runtime import DuelLinkRunTime
    from bot import logger
    from bot.providers import get_provider
    os.makedirs(uconfig.get('locations', 'log'), exist_ok=True)
    setup_logging()
    scheduler = BackgroundScheduler()
    dlRuntime = DuelLinkRunTime(uconfig, scheduler)
    dlRuntime.stop = False  # Need to Ensure that it runs
    scheduler.start()
    try:
        dlRuntime.set_provider(get_provider(uconfig.get('bot', 'provider'))(scheduler, uconfig, dlRuntime))
    except Exception as e:
        logger.critical("Could not get a provider, take a look at your config file")
        logger.critical(e)
        logger.debug(traceback.format_exc())
        sys.exit(1)
    try:
        dlRuntime.get_provider().sleep_factor = uconfig.getint('bot', 'sleep_factor')
    except Exception as e:
        logger.critical("Could not set sleep factor, take a look at your config file")
        logger.critical(e)
        sys.exit(1)
    return dlRuntime


@click.group()
def cli():
    pass


@click.command()
@click.option("--generate-config", default=False, help="Generate Config file", is_flag=True)
@click.option("--file-path", default="configtest.ini", help="File Location")
def config(generate_config, file_path):
    from bot.utils.common import make_config_file
    if generate_config:
        make_config_file(file_path)


@click.command()
@click.option("-s", "--start", is_flag=True, default=False)
@click.option("-c", "--config-file", default="config.ini")
def bot(start, config_file):
    if start:
        from bot import logger
        def handler(signum, frame):
            if signum == signal.SIGINT:
                dlRuntime.shutdown()
                logger.info("Exiting Yugioh-DuelLinks Bots")
                sys.exit(0)

        from bot.utils.common import make_config_file, default_config
        signal.signal(signal.SIGINT, handler)
        uconfig = default_config()
        uconfig.read(config_file)
        dlRuntime = setup_runtime(uconfig)
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
        from bot.utils.common import make_config_file, default_config
        from bot.duel_links_runtime import DuelLinkRunTime
        from bot.dl_gui import DuelLinksGui
        from bot import logger
        sip.setdestroyonexit(False)
        app = QApplication(sys.argv)

        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.critical(None, "Systray",
                                 "Systray not dected on system.")
            sys.exit(1)

        QApplication.setQuitOnLastWindowClosed(False)

        uconfig = default_config()
        uconfig.read(config_file)
        dlRuntime = setup_runtime(uconfig)
        dlRuntime.main()
        window = DuelLinksGui(dlRuntime, uconfig.get('locations', 'assets'))
        window.show()

        def handler(signum, frame):
            if signum == signal.SIGINT:
                window.__quit__()
                logger.info("Exiting Yugioh-DuelLinks Bots")

        signal.signal(signal.SIGINT, handler)

        def inmain():
            return app.exec_()

        sys.exit(inmain())


@click.command()
def version():
    import bot
    print("Using {}".format(bot.__version__))


@click.command()
def setup():
    set_pip_test(True)
    main_install()


cli.add_command(bot)
cli.add_command(config)
cli.add_command(gui)
cli.add_command(version)
cli.add_command(setup)

if __name__ == "__main__":
    cli()
