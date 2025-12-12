from base.utils.response_handler import api_response
from zra_client.client import ZRAClient
from rest_framework import status
from base.models import ItemInfo 
from django.db.models import Max
import json


class CreateItem(ZRAClient):
    ITEM_TYPE_MAP = {
        "Raw Material": "1",
        "Finished Product": "2",
        "Service": "3"
    }

    def __init__(self):
        super().__init__()

    def generate_item_code(self, itemOrigin="ZM", itemType="1", pkgUnit="NT", qtyUnit="BA"):
        prefix = f"{itemOrigin}{itemType}{pkgUnit}{qtyUnit}"
        last_item = ItemInfo.objects.filter(code__startswith=prefix).order_by('id').last()

        if last_item and last_item.code:
            try:
                last_number = int(last_item.code[-7:])
            except ValueError:
                last_number = 0
            new_number = str(last_number + 1).zfill(7)
        else:
            new_number = "0000001"

        return f"{prefix}{new_number}"

    def prepare_save_item_payload(self, data, request):
        print("Input data:", data)

        itemName = data.get("name")
        itemTypeCd = data.get("itemTypeCd") 
        price = data.get("price")
        qty = data.get("qty")
        itemOriginCd = data.get("itemOrigin", "ZM")
        pkgUnitCd = data.get("pkgUnitCd", "NT")
        qtyUnitCd = data.get("qtyUnitCd", "BA")
        if itemTypeCd not in self.ITEM_TYPE_MAP:
            return api_response(
                status="fail",
                message=f"Invalid itemTypeCd '{itemTypeCd}'. Allowed values are: {list(self.ITEM_TYPE_MAP.keys())}",
                data={},
                http_status=status.HTTP_400_BAD_REQUEST
            )

        zra_item_type_cd = self.ITEM_TYPE_MAP[itemTypeCd] 

        itemCd = self.generate_item_code(
            itemOrigin=itemOriginCd,
            itemType=zra_item_type_cd,
            pkgUnit=pkgUnitCd,
            qtyUnit=qtyUnitCd
        )

        payload = {
            "tpin": self.get_tpin(),
            "bhfId": self.get_branch_code(),
            "itemCd": itemCd,
            "itemClsCd": data.get("itemClassCode", "21102100"),
            "itemTyCd": zra_item_type_cd,
            "itemNm": itemName,
            "orgnNatCd": itemOriginCd,
            "pkgUnitCd": pkgUnitCd,
            "qtyUnitCd": qtyUnitCd,
            "vatCatCd": data.get("vatCatCd", "A"),
            "btchNo": "null",
            "bcd": "null",
            "dftPrc": price,
            "manufacturerTpin": "1000000000",
            "manufacturerItemCd": "ZM2EA1234",
            "rrp": 1000,
            "svcChargeYn": "Y",
            "rentalYn": "N",
            "addInfo": "null",
            "sftyQty": qty,
            "isrcAplcbYn": "N",
            "useYn": "Y",
            "regrNm": request.user.username,
            "regrId": request.user.id,
            "modrNm": request.user.username,
            "modrId": request.user.id
        }

        print("ZRA Payload:\n", json.dumps(payload, indent=4, sort_keys=True))
        external_response = self.create_item_zra(payload)
        return external_response, itemCd
        
