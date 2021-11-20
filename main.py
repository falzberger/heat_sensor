import argparse
import functools
import logging
import threading
from logging.handlers import TimedRotatingFileHandler

from config import LOG_FILE, LOG_LEVEL
from temperature_sensor import TemperatureSensor

SENSORS = [
    TemperatureSensor('Netz', '/sys/bus/w1/devices/28-0120506b26b1/w1_slave',
                      check_interval=60, check_period=180, min_value=70),
    TemperatureSensor('Stoker', '/sys/bus/w1/devices/28-01205055d0f7/w1_slave',
                      check_interval=5, check_period=20, max_value=80),
    TemperatureSensor('Cutter', '/sys/bus/w1/devices/28-01204d485ba0/w1_slave',
                      check_interval=4, check_period=20, max_value=25),
]


def main(interval: int):
    logger = setup_logger()

    threads = []
    for sensor in SENSORS:
        thread = threading.Thread(name=sensor.name, target=functools.partial(sensor.monitor, summary_interval=interval))
        threads.append(thread)
        thread.start()
        logger.info(f'Started thread {sensor.name} temperature')

    for thread in threads:
        thread.join()
        logger.error(f'Thread for {thread.name} stopped execution')


def setup_logger() -> logging.Logger:
    logger = logging.getLogger('heat_sensor')
    logger.setLevel(LOG_LEVEL)
    handler = TimedRotatingFileHandler(LOG_FILE, when='midnight')
    handler.setLevel(LOG_LEVEL)
    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s', '%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start monitoring the temperature sensors.')
    parser.add_argument('--interval', type=int, default=86400,
                        help='The interval in seconds after which to send a summary to the telegram group.'
                             'Must be greater than or equal to 60 seconds, default is 86400 (1 day).')
    args = parser.parse_args()

    main(args.interval)
