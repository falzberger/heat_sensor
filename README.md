# Heat Sensor

A small Python program that monitors measurements of multiple temperature sensors. If the measurements exceed defined
thresholds, the program sends a message to a Telegram group.

In the [`data`](data) directory, CSV files for each sensor are generated, containing timestamps and values of the
measurements. Note, however, that erroneous measurements are not recorded.

## Development

Install the required dependencies with `pip`.

```bash
pip3 install -r requirements.txt
```

Create a `config.py` file where you define the following values:

```python
# Logging
LOG_FILE = 'log/log.out'
LOG_LEVEL = 'INFO'

# Telegram
BOT_TOKEN = ''  # You need to create a Telegram bot for the program.
CHAT_ID = ''  # Identifies the group chat the program will send to. 
```

Run `main.py`. There is an optional command-line argument for specifying an interval in seconds, after which the bot
should send measurement statistics to the telegram group. The default value is 86400 seconds (1 day), to send statistics
every hour, use:

```bash
python3 main.py --interval 3600
```