# Heat Sensor

A small Python program that monitors measurements of multiple temperature sensors. If the measurements exceed defined
thresholds, the program sends a message to a Telegram group.

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