from rest_framework import serializers
from base.models import Sale, SaleItem, ItemInfo

class SaleItemSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name')

    class Meta:
        model = SaleItem
        fields = [
            'id', 'sale', 'item', 'item_name', 'qty', 'prc', 'sply_amt',
            'vat_taxbl_amt', 'vat_amt', 'ipl_taxbl_amt', 'ipl_amt',
            'tl_taxbl_amt', 'tl_amt', 'ecm_taxbl_amt', 'ecm_amt', 'tot_amt'
        ]


class SaleSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True, read_only=True)

    class Meta:
        model = Sale
        fields = [
            'id', 'tpin', 'bhf_id', 'org_invc_no', 'cis_invc_no', 'cust_tpin',
            'cust_nm', 'sales_ty_cd', 'rcpt_ty_cd', 'pmt_ty_cd', 'sales_stts_cd',
            'cfm_dt', 'sales_dt', 'tot_item_cnt', 'tot_taxbl_amt', 'tot_tax_amt',
            'tot_amt', 'result_cd', 'result_msg', 'result_dt', 'rcpt_no',
            'intrl_data', 'rcpt_sign', 'vsdc_rcpt_pbct_date', 'sdc_id', 'mrc_no',
            'qr_code_url', 'items'
        ]
