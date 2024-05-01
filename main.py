import time
from requests.exceptions import Timeout, TooManyRedirects, ConnectionError
from dotenv import dotenv_values
from loguru import logger

from models import ConnectorWithCloudService


def sync_files(connector: ConnectorWithCloudService, logger_file: logger):
    remote_files = connector.get_info_remote()
    local_files = connector.get_info_local()

    if remote_files:
        for i_file in remote_files.keys():
            if i_file not in local_files.keys():
                try:
                    connector.delete_file(i_file)
                    logger_file.info('Файл {} успешно удален'.format(i_file))

                except (Timeout, TooManyRedirects, ConnectionError):
                    logger_file.error('Файл {} не удален. Ошибка соединения.'.format(i_file))

    for i_file in local_files.keys():
        if not remote_files or i_file not in remote_files.keys():
            try:
                connector.load_file(i_file)
                logger_file.info('Файл {} успешно записан'.format(i_file))
            except (Timeout, TooManyRedirects, ConnectionError):
                logger_file.error('Файл {} не записан. Ошибка соединения.'.format(i_file))
            except OSError:
                logger_file.error("Ошибка чтения файла {}".format(i_file))
        if remote_files:
            if i_file in remote_files.keys() and local_files[i_file] > remote_files[i_file]:
                try:
                    connector.update_file(i_file)
                    logger_file.info('Файл {} успешно перезаписан'.format(i_file))
                except (Timeout, TooManyRedirects, ConnectionError):
                    logger_file.error('Файл {} не перезаписан. Ошибка соединения.'.format(i_file))
                except OSError:
                    logger_file.error("Ошибка чтения файла {}".format(i_file))


if __name__ == '__main__':
    config = dotenv_values(".env")

    logger.add(config["LOGFILE_PATH"], format="{time:%Y-%m-%d %H:%M:%S} {level} {message}",
               rotation="12:00", level="DEBUG")
    logger.info("Программа синхронизации файлов начинает работу с директорией {}".format(config["TARGET_PATH"]))

    connector_yandex = ConnectorWithCloudService(token=config["YANDEX_DISK_TOKEN"],
                                                 remote_dir=config["REMOTE_PATH"])
    while True:
        sync_files(connector=connector_yandex, logger_file=logger)
        time.sleep(float(config["INTERVAL"]))
