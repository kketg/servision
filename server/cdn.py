import requests
import json

class CDN:

    def __init__(self, address, port):
        self.url = f"http://{address}:{port}"
        
    # Creates persistent connection to CDN
    def connect(self, algorithms):
        status = requests.get(f"{self.url}/status")
        if status.status_code == 200:
            result = status.json()
            if result["result"] != 0:
                raise Exception("Connection to CDN failed")
            self.update(algorithms)
        else:
            raise Exception("Connection to CDN failed")
    
    # Updates algorithm directories if the list has changed
    def update(self, algorithms):
        status = requests.post(f"{self.url}/update",json=algorithms)
        if status.status_code == 200:
            result = status.json()
            if result["result"] != 0:
                raise Exception("Failed to update CDN")
        else:
            raise Exception("Failed to update CDN")
        
    # Purges files for a specific algorithm from the CDN
    def purge(self, algo):
        status = requests.post(f"{self.url}/purge/{algo}")
        if status.status_code == 200:
            result = status.json()
            if result["result"] != 0:
                raise Exception(f"Failed to purge {algo} from CDN")
        else:
            raise Exception(f"Failed to purge {algo} from CDN")


    # Sends file meant for processing to be archived
    def send_proc_file(self, token, filestream):
        requests.post(f"{self.url}/recv/proc/{token}",files={'file': filestream})

    # Sends file meant to be downloaded by user
    def send_out_file(self, token, filestream):
        requests.post(f"{self.url}/recv/out/{token}",files={'file': filestream})

    # Download file for processing
    def get_proc_file(self, token):
        requests.post(f"{self.url}/srv/proc/{token}")
        
    # Download file to send to user
    def get_out_file(self, token):
        requests.post(f"{self.url}/srv/out/{token}")