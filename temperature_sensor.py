import logging
import re
from datetime import datetime, timedelta

import pandas as pd

from util import send_telegram


class TemperatureSensor:

    def __init__(self,
                 name: str,
                 path: str,
                 check_interval: int,
                 check_period: int,
                 min_value=None,
                 max_value=None) -> None:

        assert check_period > check_interval
        self.name = name
        self.path = path
        self.check_interval = check_interval
        self.check_period = check_period
        self.min_value = min_value
        self.max_value = max_value

        self.last_check = datetime.now()  # the datetime of the latest temperature check
        self.data = pd.Series(dtype=pd.Float64Dtype)

        self._logger = logging.getLogger('heat_sensor')

    def _get_warning_message(self, average, last) -> str:
        msg = f'{self.name}: Durchschnittliche Temperatur in den letzten {self.check_period} Sekunden: {average}°C.\n' \
                  f'Letzter gemessener Wert: {last}°C.\n' \
                  f'Soll: '

        if self.min_value is not None:
            msg += f'> {self.min_value}°C'
            if self.max_value is not None:
                msg += ', '
            else:
                msg += '.'
        if self.max_value is not None:
            msg += f'< {self.max_value}°C.'

        return msg

    def _read_sensor(self):
        temperature = None
        try:
            f = open(self.path, "r")
            line = f.readline()
            if re.match(r"([0-9a-f]{2} ){9}: crc=[0-9a-f]{2} YES", line):
                line = f.readline()
                m = re.match(r"([0-9a-f]{2} ){9}t=([+-]?[0-9]+)", line)
                if m:
                    temperature = float(m.group(2)) / 1000.0
            f.close()
        except Exception as e:
            self._logger.error(f'Error reading {self.path}: {e}')
        self._logger.info(f'Measured {self.name} temperature: {temperature}')
        return temperature

    def add_sensor_reading(self, dt: datetime):
        # if the first temperature reading fails, we try it a second time, otherwise we skip
        temperature = self._read_sensor()
        if temperature is None:
            temperature = self._read_sensor()
        if temperature is None:
            self._logger.warning(f'Could not read {self.name} temperature two times in a row')
            return

        self.data[dt] = temperature

    def check_temperature(self, period_end: datetime):
        self.last_check = period_end
        period_start = period_end - timedelta(seconds=self.check_period)

        interval: pd.Series = self.data.truncate(before=period_start, after=period_end, copy=True)
        latest = interval[-1] if len(interval) > 0 else None
        if latest is None:
            error_msg = f'Konnte seit {period_start} Sekunden keine Temperatur von {self.name} messen!'
            self._logger.info(f'Sending: {error_msg}')
            send_telegram(error_msg)
            return

        if self.min_value is not None:
            mask = interval < self.min_value
            if (mask.sum() / mask.count()) > 0.66:
                self._logger.warning(f'{self.name} to low: {latest} < {self.min_value}')
                send_telegram(self._get_warning_message(interval.mean(), latest))

        if self.max_value is not None:
            mask = interval > self.max_value
            if (mask.sum() / mask.count()) > 0.66:
                self._logger.warning(f'{self.name} to high: {latest} > {self.max_value}')
                send_telegram(self._get_warning_message(interval.mean(), latest))

    def monitor(self):
        """Monitors the temperature sensor and sends a telegram message if thresholds are violated."""
        while True:
            now = datetime.now()
            self.add_sensor_reading(now)

            # we only want to check the temperature if the specified seconds since the last check have passed
            expected_last_check_time = now - timedelta(seconds=self.check_interval)
            if expected_last_check_time > self.last_check:
                self.check_temperature(now)

    def remove_data_before(self, index: datetime):
        self.data.truncate(before=index, copy=False)
