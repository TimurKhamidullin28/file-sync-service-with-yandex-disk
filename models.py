from datetime import datetime
import json
import os
from typing import Dict

from dotenv import load_dotenv
import requests

from api import api_request

load_dotenv()

TARGET_PATH = os.getenv("TARGET_PATH")
BASE_URL = os.getenv("BASE_URL")


class ConnectorWithCloudService:
    """
    Класс, описывающий модель коннектора, который отвечает за работу с Яндекс Диском (облачным сервисом)
    """
    def __init__(self, token: str, remote_dir: str):
        """
        Метод класса, инициализирующий его объект
        :param token: передается токен авторизации от API облачного сервиса
        :param remote_dir: передается имя директории на облачном сервисе
        """
        self.__token = token,
        self.__remote_dir = remote_dir
        self.__headers = {'Authorization': 'OAuth ' + f'{self.__token[0]}',
                          'Content-Type': 'application/json'}

    @classmethod
    def get_info_local(cls) -> Dict:
        """
        Метод класса, возвращающий информацию о файлах в отслеживаемой директории на локальном компьютере
        (имя файла и время его последнего изменения).
        """
        result = dict()
        for i_file in os.listdir(TARGET_PATH):
            modified_time = os.path.getmtime(os.path.join(TARGET_PATH, i_file))
            m_time = datetime.fromtimestamp(modified_time).strftime("%Y-%m-%d %H:%M:%S")
            result[i_file] = m_time

        return result

    def get_info_remote(self) -> Dict:
        """
        Метод класса, возвращающий информацию о файлах в директории на облачном хранилище
        (имя файла и время его последнего изменения).
        """
        result = dict()
        response = api_request(endpoint='resources',
                               params={'path': self.__remote_dir,
                                       'fields': '_embedded.items.name, _embedded.items.modified',
                                       'limit': '1000'},
                               headers=self.__headers)
        if response.status_code == requests.codes.ok:
            data = json.loads(response.text)
            for i_dict in data["_embedded"]["items"]:
                mod_time = datetime.fromisoformat(i_dict["modified"]).strftime("%Y-%m-%d %H:%M:%S")
                result[i_dict["name"]] = mod_time
            return result

    def load_file(self, file_name: str) -> None:
        """
        Метод класса, который загружает файл на облачное хранилище
        :param file_name: передается имя файла из отслеживаемой директории
        """
        response = api_request(endpoint='resources/upload',
                               params={'path': f'{self.__remote_dir}/{file_name}'},
                               headers=self.__headers)
        if response.status_code == requests.codes.ok:
            data = json.loads(response.text)
            link = data["href"]
            requests.put(url=link, data=open((os.path.join(TARGET_PATH, file_name)), 'rb').read())

    def update_file(self, file_name: str) -> None:
        """
        Метод класса, который обновляет файл в облачном хранилище
        :param file_name: передается имя файла из отслеживаемой директории
        """
        response = api_request(endpoint='resources/upload',
                               params={'path': f'{self.__remote_dir}/{file_name}',
                                       'overwrite': 'true'},
                               headers=self.__headers)
        if response.status_code == requests.codes.ok:
            data = json.loads(response.text)
            link = data["href"]
            requests.put(url=link, data=open((os.path.join(TARGET_PATH, file_name)), 'rb').read())

    def delete_file(self, file_name: str) -> None:
        """
        Метод класса, который безвозвратно удаляет файл из облачного хранилища
        :param file_name: передается имя файла из директории на облочном сервисе
        """
        requests.delete(url=f'{BASE_URL}resources',
                        params={'path': f'{self.__remote_dir}/{file_name}',
                                'permanently': 'true'},
                        headers=self.__headers)
