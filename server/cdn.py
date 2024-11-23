import requests
import json

class CDN:

    def __init__(self, address, port):
        self.url = f"http://{address}:{port}"
        status = requests.get(f"{self.url}/status")
        if status.status_code == 200:
            result = json.loads(status.json())
            if result["result"] != 0:
                raise Exception("Connection to CDN failed")
        else:
            raise Exception("Connection to CDN failed")

    def send_proc_file(self, token, filestream):
        requests.post(f"{self.url}/recv/proc/{token}",files={'file': filestream})

    def send_out_file(self, token, filestream):
        requests.post(f"{self.url}/recv/out/{token}",files={'file': filestream})

    def get_proc_file(self, token):
        requests.post(f"{self.url}/srv/proc/{token}")
    def get_out_file(self, token):
        requests.post(f"{self.url}/srv/out/{token}")