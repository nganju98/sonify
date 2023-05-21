import time
import soco
import logging
import logging.handlers

log_file_name = 'logs/MyLog'
# use very short interval for this example, typical 'when' would be 'midnight' and no explicit interval
handler = logging.handlers.TimedRotatingFileHandler(log_file_name, when="D", backupCount=5)
handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
logger = logging.getLogger() # or pass string to give it a name
logger.addHandler(handler)
logger.setLevel(logging.INFO)

while True:
    try:
        devices = {device.player_name: device for device in soco.discover()}
        print(devices)
        primary = devices['Kitchen']
        logger.info(devices)

        logger.info(primary.all_groups)
        print(primary.volume)
        biggestGroup = max(len(group.members) for group in primary.all_groups)
        logger.info(f'Biggest Group = {biggestGroup}')
        secondary = devices['Dining Room']
        if (secondary.volume != primary.volume):
            secondary.volume = primary.volume
            logger.info("Changing secondary volume to match primary")
        if biggestGroup < 2:
            logger.info(f'joining groups')
            secondary.join(primary)
            time.sleep(1)
            primary.play()
    except Exception as err:
        logger.exception(f'{type(err).__name__} trying to reconnect...')
    time.sleep(30)

