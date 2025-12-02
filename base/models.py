from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

ITEM_TYPE_CHOICES = [
    ('Raw Material', 'Raw Material'),
    ('Finished Product', 'Finished Product'),
    ('Service', 'Service'),
]

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    address = models.CharField("Address", max_length=200, blank=True)
    use_yn = models.CharField("Active Status", max_length=1, choices=[('Y', 'Used'), ('N', 'Unused')], default='Y')


    def __str__(self):
        return f"{self.user.username} - {self.user}"


class CustomerInfo(models.Model):
    name = models.CharField()
    address = models.CharField()
    customerTpin = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_created")
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_updated", null=True, blank=True)
    def __str__(self):
        return self.name
    

class ItemInfo(models.Model):
    code = models.CharField(max_length=50, unique=True)
    itemClassCode = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    itemTypeCd = models.CharField(max_length=20, choices=ITEM_TYPE_CHOICES, null=True, blank=True)
    itemOrigin = models.CharField(max_length=100)
    pkgUnitCd = models.CharField(max_length=50)
    qtyUnitCd = models.CharField(max_length=50)
    vatCatCd = models.CharField(max_length=50, blank=True, null=True)
    iplCatCd = models.CharField(max_length=50, blank=True, null=True)
    tlCatCd = models.CharField(max_length=50, blank=True, null=True)
    exciseTxCatCd = models.CharField(max_length=50, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    qty = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.code})"
    

class StockItem(models.Model):
    item = models.ForeignKey(ItemInfo, on_delete=models.CASCADE, related_name='details')     
    qty = models.DecimalField(max_digits=13, decimal_places=2)  
    prc = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    sply_amt = models.DecimalField(max_digits=18, decimal_places=4, default=0) 
    taxbl_amt = models.DecimalField(max_digits=18, decimal_places=4, default=0)  
    vat_cat_cd = models.CharField(max_length=5)      
    tax_amt = models.DecimalField(max_digits=18, decimal_places=4, default=0)   
    tot_amt = models.DecimalField(max_digits=18, decimal_places=4, default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='stockitemdetail_created')

    def __str__(self):
        return f"{self.item} ({self.qty} units at {self.prc} each)"

class ItemStockMaster(models.Model):
    item = models.ForeignKey(ItemInfo, on_delete=models.CASCADE, related_name='stock_masters')
    available_qty = models.DecimalField(max_digits=13, decimal_places=2, default=0)
    last_updated = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='itemstockmaster_updated')

    def __str__(self):
        return f"StockMaster for {self.item.code} - Available: {self.available_qty}"
    

class Supplier(models.Model):
    tpin = models.IntegerField(unique=True)
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=300)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="suppliers_created"
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="suppliers_updated"
    )

    def __str__(self):
        return super().__str__() + f" - {self.name}"


class Sale(models.Model):
    org_invc_no = models.IntegerField()
    cis_invc_no = models.CharField(max_length=50)
    cust_tpin = models.CharField(max_length=20, blank=True, null=True)
    cust_nm = models.CharField(max_length=255)
    sales_ty_cd = models.CharField(max_length=5)
    rcpt_ty_cd = models.CharField(max_length=5)
    pmt_ty_cd = models.CharField(max_length=5)
    sales_stts_cd = models.CharField(max_length=5)
    cfm_dt = models.CharField(max_length=20)  
    sales_dt = models.CharField(max_length=10) 
    tot_item_cnt = models.IntegerField()
    tot_taxbl_amt = models.FloatField()
    tot_tax_amt = models.FloatField()
    tot_amt = models.FloatField()
    rcpt_no = models.IntegerField(blank=True, null=True)
    sdc_id = models.CharField(max_length=50, blank=True, null=True)
    qr_code_url = models.URLField(blank=True, null=True)
    generated_invoice = models.FileField(
        upload_to='invoices/%Y/%m/%d/', 
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.cust_nm} - {self.cis_invc_no}"


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, related_name="items", on_delete=models.CASCADE)
    item = models.ForeignKey('ItemInfo', on_delete=models.PROTECT)
    qty = models.FloatField()
    prc = models.FloatField()
    sply_amt = models.FloatField()
    vat_taxbl_amt = models.FloatField()
    vat_amt = models.FloatField()
    ipl_taxbl_amt = models.FloatField(default=0.0)
    ipl_amt = models.FloatField(default=0.0)
    tl_taxbl_amt = models.FloatField(default=0.0)
    tl_amt = models.FloatField(default=0.0)
    ecm_taxbl_amt = models.FloatField(default=0.0)
    ecm_amt = models.FloatField(default=0.0)
    tot_amt = models.FloatField()

    def __str__(self):
        return f"{self.item.name} ({self.sale.cis_invc_no})"


class ItemStockMaster(models.Model):
    item = models.ForeignKey(ItemInfo, on_delete=models.CASCADE, related_name='stock_masters')
    available_qty = models.DecimalField(max_digits=13, decimal_places=2, default=0)
    last_updated = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.item.code} - {self.available_qty}"

class Purchase(models.Model):
    cisInvcNo = models.CharField(max_length=50)
    orgInvcNo = models.IntegerField()
    
    spplrTpin = models.CharField(max_length=20)
    spplrBhfId = models.CharField(max_length=10)
    spplrNm = models.CharField(max_length=255)
    spplrInvcNo = models.CharField(max_length=50)

    regTyCd = models.CharField(max_length=5)
    pchsTyCd = models.CharField(max_length=5)
    rcptTyCd = models.CharField(max_length=5)
    pmtTyCd = models.CharField(max_length=5)
    pchsSttsCd = models.CharField(max_length=5)

    cfmDt = models.CharField(max_length=20)
    pchsDt = models.CharField(max_length=20)
    cnclReqDt = models.CharField(max_length=20, blank=True)
    cnclDt = models.CharField(max_length=20, blank=True)

    totItemCnt = models.IntegerField()
    totTaxblAmt = models.DecimalField(max_digits=18, decimal_places=4)
    totTaxAmt = models.DecimalField(max_digits=18, decimal_places=4)
    totAmt = models.DecimalField(max_digits=18, decimal_places=2)

    remark = models.TextField(blank=True)
    regrNm = models.CharField(max_length=255)
    regrId = models.CharField(max_length=255)
    modrNm = models.CharField(max_length=255)
    modrId = models.CharField(max_length=255)

    def __str__(self):
        return f"Purchase {self.cisInvcNo}"


class PurchaseItem(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name="items")
    itemSeq = models.IntegerField()
    itemCd = models.CharField(max_length=50)
    itemClsCd = models.CharField(max_length=50)
    itemNm = models.CharField(max_length=255)

    bcd = models.CharField(max_length=100, null=True, blank=True)
    pkgUnitCd = models.CharField(max_length=10)
    pkg = models.DecimalField(max_digits=18, decimal_places=2)
    qtyUnitCd = models.CharField(max_length=10)
    qty = models.DecimalField(max_digits=18, decimal_places=2)

    prc = models.DecimalField(max_digits=18, decimal_places=2)
    splyAmt = models.DecimalField(max_digits=18, decimal_places=2)
    dcRt = models.DecimalField(max_digits=5, decimal_places=2)
    dcAmt = models.DecimalField(max_digits=18, decimal_places=2)

    taxTyCd = models.CharField(max_length=5)

    taxblAmt = models.DecimalField(max_digits=18, decimal_places=2)
    vatCatCd = models.CharField(max_length=5)

    taxAmt = models.DecimalField(max_digits=18, decimal_places=2)
    totAmt = models.DecimalField(max_digits=18, decimal_places=2)
    iplCatCd = models.CharField(max_length=50, null=True, blank=True)
    tlCatCd = models.CharField(max_length=50, null=True, blank=True)
    exciseCatCd = models.CharField(max_length=50, null=True, blank=True)

    iplTaxblAmt = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    tlTaxblAmt = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    exciseTaxblAmt = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)

    iplAmt = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    tlAmt = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    exciseTxAmt = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.itemNm}"


class Quotation(models.Model):
    quotation_no = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey(
        CustomerInfo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quotations"
    )
    customer_name = models.CharField(max_length=255)
    customer_tpin = models.CharField(max_length=50, blank=True, null=True)

    quotation_date = models.DateTimeField(default=timezone.now)
    expiry_date = models.DateTimeField(null=True, blank=True)
    total_items = models.IntegerField(default=0)
    total_taxable = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    total_tax = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    status = models.CharField(
        max_length=20,
        choices=[
            ("DRAFT", "Draft"),
            ("SENT", "Sent"),
            ("APPROVED", "Approved"),
            ("REJECTED", "Rejected"),
            ("CONVERTED", "Converted to Sale"),
        ],
        default="DRAFT"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="quotation_created"
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="quotation_updated"
    )

    def __str__(self):
        return f"Quotation {self.quotation_no} - {self.customer_name}"


class QuotationItem(models.Model):
    quotation = models.ForeignKey(
        Quotation,
        on_delete=models.CASCADE,
        related_name="items"
    )
    item = models.ForeignKey(ItemInfo, on_delete=models.PROTECT)

    qty = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=18, decimal_places=2)
    supply_amount = models.DecimalField(max_digits=18, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=18, decimal_places=2)
    total_amount = models.DecimalField(max_digits=18, decimal_places=2)

    vat_category = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f"{self.item.name} - Qty: {self.qty}"
