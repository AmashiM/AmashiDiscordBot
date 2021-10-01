

import requests
import json
import proxy_db
from requests.exceptions import ProxyError, ConnectionError, Timeout
from proxy_db.proxies import ProxiesList

# translator https://libretranslate.de/docs/

class Translate:

  @staticmethod
  def request(method: str, path: str, data: dict):
    url = f"https://libretranslate.de{'' if path is None else path}"
    proxy = next(ProxiesList())
    res = requests.request(
      method=("GET" if method is None else method),
      url=url,
      headers={ "Content-Type": "application/json" },
      data=json.dumps(data),
      proxies=proxy
    )
    return res


  @staticmethod
  def detect(text: str):
    res = Translate.request("POST", "/detect", {
      'q': text
    })
    return res

  @staticmethod
  def translate(lang1: str, lang2: str, text: str):
    pass
