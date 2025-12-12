import json
from zra_client.client import ZRAClient

class CreateUser(ZRAClient):
    def __init__(self):
        super().__init__()

    def prepare_save_customer_payload(self, data, request):

        cust_no = data.get("custNo", "097xxxxxxx")
        cust_tpin = data.get("customerTpin", "2000000000")
        cust_name = data.get("custNm", "ZRA")
        address = data.get("address", "null")
        fax_no = data.get("faxNo", "null")
        use_yn = data.get("useYn", "Y")
        remark = data.get("remark", "null")

        payload = {
            "tpin": self.get_tpin(),
            "bhfId": self.get_branch_code(),
            "custNo": cust_no,
            "custTpin": cust_tpin,
            "custNm": cust_name,
            "address": address,
            "faxNo": fax_no,
            "useYn": use_yn,
            "remark": remark,
            "regrNm": request.user.username,
            "regrId": request.user.id,
            "modrNm": request.user.username,
            "modrId": request.user.id
        }

        print(json.dumps(payload, indent=4, sort_keys=True))
        return self.create_customer(payload)
