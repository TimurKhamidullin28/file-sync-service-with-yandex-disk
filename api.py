from typing import Dict
import requests
from dotenv import dotenv_values

config = dotenv_values(".env")


def api_request(endpoint: str, headers: Dict, params: Dict) -> requests.Response:
    """
    Универсальная функция, которая делает GET-запросы к API Яндекс Диска
    :param endpoint: окончание URL-адреса
    :param headers: заголовки запроса
    :param params: параметры запроса, части URL-адреса
    """
    return requests.get(
        f'{config["BASE_URL"]}{endpoint}',
        headers=headers,
        params=params,
        timeout=15
    )
