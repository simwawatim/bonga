from base.models import Supplier

class SupplierHelper:
    def supplierExists(self, supplierId):
        return Supplier.objects.filter(id=supplierId).exists()
    
    def getSupplierData(self, supplierId):
        try:
            supplier = Supplier.objects.get(id=supplierId)
            tpin = supplier.tpin
            name = supplier.name
            return tpin, name
        except Supplier.DoesNotExist:
    
            return None, None
