import json
from zra_client.client import ZRAClient
class CreateUser(ZRAClient):
    def __init__(self):
        super().__init__()

    def prepare_save_user_payload(self, username, address, is_active, last_id):
        payload = {
            "tpin": self.get_tpin(),
            "bhfId": self.get_branch_code(),
            "userId": last_id,
            "userNm": username,
            "adrs": address,
            "useYn":  is_active,
            "regrNm": "Admin",
            "regrId": "Admin",
            "modrNm": "Admin",
            "modrId": "Admin"
            }
        
        print(json.dumps(payload, indent=4, sort_keys=True))
        return self.create_user(payload)
