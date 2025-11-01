import json
from zra_client.client import ZRAClient
class CreateUser(ZRAClient):
    def __init__(self):
        super().__init__()

    def prepare_save_customer_payload(self):
        payload = {
            "tpin": self.get_tpin(),
            "bhfId": self.get_branch_code(),
            "custNo": "097xxxxxxx",
            "custTpin": "2000000000",
            "custNm": "ZRA",
            "adrs":" null",
            "faxNo":" null",
            "useYn": "Y",
            "remark":" null",
            "regrNm": "Admin",
            "regrId": "Admin",
            "modrNm": "Admin",
            "modrId": "Admin"
            }

        
        print(json.dumps(payload, indent=4, sort_keys=True))
        return self.create_customer(payload)
