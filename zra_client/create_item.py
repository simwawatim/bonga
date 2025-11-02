import json
from zra_client.client import ZRAClient
class CreateItem(ZRAClient):
    def __init__(self):
        super().__init__()

    def prepare_save_item_payload(self):
        payload = {
            "tpin": self.get_tpin(),
            "bhfId": self.get_branch_code(),
            "itemCd": "P200005",
            "itemClsCd": "43322555",
            "itemTyCd": "2",
            "itemNm": "Corn Flakes",
            "itemStdNm": "Corn Flakes",
            "orgnNatCd": "SA",
            "pkgUnitCd": "BOX",
            "qtyUnitCd": "U",
            "vatCatCd": "A",
            "btchNo": "null",
            "bcd": "null",
            "dftPrc": 15,
            "manufacturerTpin": "1000000000",
            "manufacturerItemCd": "ZM2EA1234",
            "rrp": 1000,
            "svcChargeYn": "Y",
            "rentalYn": "N",
            "addInfo": "null",
            "sftyQty": 5,
            "isrcAplcbYn": "N",
            "useYn": "Y",
            "regrNm": "ADMIN",
            "regrId": "ADMIN",
            "modrNm": "ADMIN",
            "modrId": "ADMIN"
            }


        
        print(json.dumps(payload, indent=4, sort_keys=True))
        return self.create_item_zra(payload)
