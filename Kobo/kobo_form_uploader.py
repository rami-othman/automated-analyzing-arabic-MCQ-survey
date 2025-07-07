from typing import Dict
import requests

class KoboFormUploader:
    """Handles uploading forms to Kobo Toolbox"""

    def __init__(self, api_url: str, token: str):
        self.api_url = api_url.rstrip('/') + '/'
        self.token = token
        self.headers = {
            "Authorization": f"Token {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def create_form(self, form_json: str, name: str) -> Dict:
        url = f"{self.api_url}api/v2/assets/"
        payload = {"asset_type": "survey", "name": name, "content": form_json}
        resp = requests.post(url, headers=self.headers, json=payload)
        resp.raise_for_status()
        try:
            return resp.json()
        except ValueError:
            return {"status": resp.status_code}

    def deploy_form(self, asset_uid: str) -> Dict:
        # 1️⃣ Retrieve version_id
        meta = requests.get(
            f"{self.api_url}api/v2/assets/{asset_uid}/",
            headers=self.headers,
            params={"format": "json"}
        )
        meta.raise_for_status()
        version_id = meta.json().get("version_id")

        # 2️⃣ Perform deployment via POST (correct method)
        url = f"{self.api_url}api/v2/assets/{asset_uid}/deployment/?format=json"
        payload = {"version_id": version_id, "active": True}
        resp = requests.post(url, headers=self.headers, json=payload)
        resp.raise_for_status()
        return resp.json()
