import json
from helper.supplier import SupplierHelper
from base.utils.response_handler import api_response

from zra_client.client import ZRAClient
from datetime import datetime

SUPPLIER_HELPER_INSTANCE  = SupplierHelper()
class PurchaseInvoiceCreation(ZRAClient):

    def create_manual_purchase_invoice(self, purchase_data):
            name = purchase_data.get("name")
            supplier_name = purchase_data.get("spplrNm") or purchase_data.get("supplier_name")
            supplierId = purchase_data.get("supplierId")

            if not supplierId or not str(supplierId).isdigit():
                return api_response(
                    status="fail",
                    message="Supplier ID must be a valid number.",
                    status_code=400  
                )

            if not SUPPLIER_HELPER_INSTANCE.supplierExists(supplierId):
                return api_response(
                    status="fail",
                    message=f"Supplier with ID {supplierId} does not exist.",
                    status_code=404
                )
            
            tpin, name = SUPPLIER_HELPER_INSTANCE.getSupplierData(supplierId)
            if not tpin or not name:
                return api_response(
                    status="fail",
                    message=f"Supplier with ID {supplierId} does not exist.",
                    status_code=404
                )

            modified_by = purchase_data.get("modified_by")
            cfmDt = datetime.now().strftime("%Y%m%d%H%M%S")
            pchsDt = datetime.now().strftime("%Y%m%d")
            purchase_invoice_no = purchase_data.get("spplrInvcNo") or purchase_data.get("custom_purchase__invoice")
            remarks = purchase_data.get("remark") or purchase_data.get("custom_purchase_remarks")

            VAT_RATE = 0.16
            IPL_RATE = 0.05
            TL_RATE = 0.03
            EXCISE_RATE = 0.02

            items = purchase_data.get("purchase_invoice_items")

            formatted_items = []
            item_seq = 1

            vat_mapping = {
                "A": "Standard Rated 16%",
                "B": "Minimum Taxable Value (MTV)",
                "Exports": "Exports",
                "C2": "Zero-rating Local Purchases Order",
                "C3": "Zero-rated by nature 0%",
                "D": "Exempt",
                "E": "Disbursement",
                "C1": "Reverse VAT",
                "N/A": "N/A"
            }
            ipl_mapping = {
                "IPL1": "Insurance Premium Levy",
                "IPL2": "Re-Insurance"
            }
            tl_mapping = {"TL": "Tourism Levy"}
            excise_mapping = {"ECM": "Excise on Coal", "EXE": "Excise Electricity"}

            for item in items:
                itemCode = item.get("itemCode")
                qty = item.get("qty")
                price = item.get("price")
                item_total = round(qty * price, 2)
                itemName = item.get("itemName")
                itemClassCode = item.get("itemClassCode")
                packageUnitCode = item.get("packageUnitCode")
                unitOfMeasure = item.get("unitOfMeasure") 

                VatCd = item.get("VatCd")
                IplCd = item.get("IplCd")
                tlCd = item.get("custom_tl")
                get_excise_name = item.get("custom_excise")

                vatCd = next((code for code, desc in vat_mapping.items() if desc == VatCd), None)
                iplCd = next((code for code, desc in ipl_mapping.items() if desc == IplCd), None)
                tlCd = next((code for code, desc in tl_mapping.items() if desc == tlCd), None)
                exciseCd = next((code for code, desc in excise_mapping.items() if desc == get_excise_name), None)

                if vatCd == "A":
                    taxbl_amt = round(item_total / (1 + VAT_RATE), 2)
                    vat_tax_amt = round(item_total - taxbl_amt, 2)
                else:
                    taxbl_amt = item_total
                    vat_tax_amt = 0

                ipl_tax_amt = round(taxbl_amt * IPL_RATE, 2) if iplCd else 0
                tl_tax_amt = round(taxbl_amt * TL_RATE, 2) if tlCd else 0
                excise_tax_amt = round(taxbl_amt * EXCISE_RATE, 2) if exciseCd else 0

                total_tax_amt = vat_tax_amt + ipl_tax_amt + tl_tax_amt + excise_tax_amt
                total_amount = round(taxbl_amt + total_tax_amt, 2)

                formatted_items.append({
                    "itemSeq": item_seq,
                    "itemCd": itemCode,
                    "itemClsCd": itemClassCode,
                    "itemNm": itemName,
                    "bcd": "",
                    "pkgUnitCd": packageUnitCode,
                    "pkg": 0,
                    "qtyUnitCd": unitOfMeasure,
                    "qty": qty,
                    "prc": price,
                    "splyAmt": item_total,
                    "dcRt": 0,
                    "dcAmt": 0,
                    "taxTyCd": vatCd,
                    "iplCatCd": iplCd,
                    "tlCatCd": tlCd,
                    "exciseCatCd": exciseCd,
                    "taxblAmt": taxbl_amt,
                    "vatCatCd": vatCd,
                    "iplTaxblAmt": round(taxbl_amt, 2) if iplCd else "",
                    "tlTaxblAmt": round(taxbl_amt, 2) if tlCd else "",
                    "exciseTaxblAmt": round(taxbl_amt, 2) if exciseCd else "",
                    "taxAmt": total_tax_amt,
                    "iplAmt": ipl_tax_amt if iplCd else "",
                    "tlAmt": tl_tax_amt if tlCd else "",
                    "exciseTxAmt": excise_tax_amt if exciseCd else "",
                    "totAmt": total_amount
                })

                item_seq += 1

            payload = {
                "tpin": self.get_tpin(),
                "bhfId": self.get_branch_code(),
                "cisInvcNo": name,
                "spplrTpin": tpin,
                "spplrNm": name,
                "spplrInvcNo": purchase_invoice_no,
                "regTyCd": "M",
                "pchsTyCd": "N",
                "rcptTyCd": "P",
                "pmtTyCd": "01",
                "pchsSttsCd": "02",
                "cfmDt": cfmDt,
                "pchsDt": pchsDt,
                "cnclReqDt": "",
                "cnclDt": "",
                "totItemCnt": len(formatted_items),
                "totTaxblAmt": round(sum(i["taxblAmt"] for i in formatted_items), 2),
                "totTaxAmt": round(sum(i["taxAmt"] for i in formatted_items), 2),
                "totAmt": round(sum(i["totAmt"] for i in formatted_items), 2),
                "remark": remarks,
                "regrNm": "Admin",
                "regrId": "Admin",
                "modrNm": "Admin",
                "modrId": "Admin",
                "itemList": formatted_items
            }

            print(json.dumps(payload, indent=2))

            response = self.create_purchase_zra_client(payload)
            response = response.json()
            if response.get("resultCd") == "000":
                update_stock_items = []
                update_stock_master_items = []

                for item in self.to_use_data.get("itemList", []):
                    update_stock_items.append({
                        "itemSeq": item.get("itemSeq"),
                        "itemCd": item.get("itemCd"),
                        "itemClsCd": item.get("itemClsCd"),
                        "itemNm": item.get("itemNm"),
                        "pkgUnitCd": item.get("pkgUnitCd"),
                        "qtyUnitCd": item.get("qtyUnitCd"),
                        "qty": item.get("qty"),
                        "prc": item.get("prc"),
                        "splyAmt": item.get("splyAmt"),
                        "taxblAmt": item.get("taxblAmt"),
                        "vatCatCd": item.get("vatCatCd"),
                        "taxAmt": item.get("taxAmt"),
                        "totAmt": item.get("totAmt"),
                        "pkg": item.get("pkg", 1),
                        "totDcAmt": item.get("dcAmt", 0),
                    })

                    update_stock_master_items.append({
                        "itemCd": item.get("itemCd"),
                        "rsdQty": 12
                    })

                ocrnDt = datetime.now().strftime("%Y%m%d")
                update_stock_payload = {
                    "tpin": self.get_tpin(),
                    "bhfId": self.get_branch_code(),
                    "sarNo": 1,
                    "orgSarNo": 0,
                    "regTyCd": "M",
                    "sarTyCd": "02",
                    "ocrnDt": ocrnDt,
                    "totItemCnt": self.to_use_data['totItemCnt'],
                    "totTaxblAmt": self.to_use_data['totTaxblAmt'],
                    "totTaxAmt": self.to_use_data['totTaxAmt'],
                    "totAmt": self.to_use_data['totAmt'],
                    "regrId": self.to_use_data["regrId"],
                    "regrNm": self.to_use_data["regrId"],
                    "modrNm": self.to_use_data["regrId"],
                    "modrId": self.to_use_data["regrId"],
                    "itemList": update_stock_items
                }

                update_stock_master_payload = {
                    "tpin": self.get_tpin(),
                    "bhfId": self.get_branch_code(),
                    "regrId": self.to_use_data["regrId"],
                    "regrNm": self.to_use_data["regrId"],
                    "modrNm": self.to_use_data["regrId"],
                    "modrId": self.to_use_data["regrId"],
                    "stockItemList": update_stock_master_items
                }
            else:
                api_response(
                    status="fail",
                    message=response,
                    status_code=300
                )