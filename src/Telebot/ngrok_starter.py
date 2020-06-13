import subprocess
import platform
import requests
import json
import time
from urllib.parse import urlparse
from os.path import abspath, join, dirname
import sys
from . import ngrok_consts


def run_ngrok():
    """
    runs ngrok.
    ngrok is used as a web_hook for Telegram api.
    the localhost_url holds information about the location of the created server
    the function passes this public url of the created ngrock to the 
    Telegram-api to set the web-hook and logs the returned message 
    """
    lgm = common_utils.SingletonRotateLoggerManager()
    logger = lgm.create_logger("ngrok")

    ngrok_path = join(abspath(dirname(__file__)), 'ngrok.exe')

    platform_name = platform.platform()
    if 'Linux' in platform_name:
        if 'x86' in platform_name:
            ngrok_path = join(abspath(dirname(__file__)), 'ngrok')
        else:
            ngrok_path = join(abspath(dirname(__file__)), 'ngrok_arm')

    logger.info(ngrok_path)
    subprocess.Popen([ngrok_path, 'http', '8080'],
                     stdout=subprocess.PIPE)

    # sleep to allow the ngrok to fetch the url from the server
    time.sleep(3)

    # Url with tunnel details
    localhost_url = "http://localhost:4040/api/tunnels"

    # Get the tunnel information
    tunnel_url = requests.get(localhost_url).text

    json_tunnel_url = json.loads(tunnel_url)

    # Do the parsing of the get
    tunnel_url = json_tunnel_url['tunnels'][1]['public_url']
    my_ngrok = urlparse(tunnel_url).netloc
    logger.info(my_ngrok)

    telgram_url = \
        f"""
        https://api.telegram.org/{
            ngrok_consts.SECRET_KEY}/setWebHook?url=https://{my_ngrok}/"""

    # Get the response from Telegram if webhook was set successfully
    telegram_response = requests.get(telgram_url).text
    # TODO :  handle unsuccessfull webhook set
    logger.info(telegram_response)


if __name__ == "__main__":
    src_path = join(abspath(dirname(dirname(__file__))))
    sys.path.insert(1, src_path)
    import common_utils

    run_ngrok()
    input("keypress")

else:
    import common_utils
