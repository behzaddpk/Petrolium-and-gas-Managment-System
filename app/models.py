from django.db import models
from decimal import Decimal



# Station model
class Station(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    capacity = models.DecimalField(max_digits=10, decimal_places=2)  # Fuel capacity in liters
    contact_number = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)  # For soft delete

    def __str__(self):
        return self.name


class Supplier(models.Model):
    name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=20)
    address = models.CharField(max_length=255, blank=True, null=True)
    stations = models.ManyToManyField(Station, related_name='suppliers')  # Station-Supplier relationship

    def __str__(self):
        return self.name
    




class Product(models.Model):
    name = models.CharField(max_length=50)
    price_per_liter = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=10, default="liters")  # Unit of measurement
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name




# Purchase model
class Purchase(models.Model):
    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='purchases')
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='purchases')
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    purchase_date = models.DateTimeField(auto_now_add=True)
       

    def __str__(self):
        return f"Purchase at {self.station.name}"


class PurchaseItem(models.Model):
    purchase = models.ForeignKey(Purchase, related_name='items', on_delete=models.CASCADE)
    category = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='purchase_items')
    quantity_purchased = models.DecimalField(max_digits=10, decimal_places=2)  # Quantity purchased in liters
    price_per_liter = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.total_cost = self.quantity_purchased * self.price_per_liter
        super().save(*args, **kwargs)

        # Add purchased quantity to inventory
        inventory, created = FuelInventory.objects.get_or_create(
            station=self.purchase.station, category=self.category,
            defaults={'quantity': Decimal(self.quantity_purchased)}
        )
        if not created:
            inventory.quantity = Decimal(inventory.quantity) + Decimal(self.quantity_purchased)
            inventory.save()

    def __str__(self):
        return f"{self.category.name} - {self.quantity_purchased} liters"



class FuelInventory(models.Model):
    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='inventories')
    category = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventories')
    quantity = models.DecimalField(max_digits=10, decimal_places=2)  # Quantity in liters
    low_stock_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=500)
    last_updated = models.DateTimeField(auto_now=True)

    def is_low_stock(self):
        return self.quantity <= self.low_stock_threshold

    def __str__(self):
        return f"{self.station.name} - {self.category.name}"




class Sale(models.Model):
    station = models.ForeignKey(Station, on_delete=models.SET_NULL, null=True, blank=True, related_name='sales')
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='sales')
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    sale_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sale at {self.station.name} on {self.sale_date.strftime('%Y-%m-%d %H:%M:%S')}"

    

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, related_name='saleitems', on_delete=models.CASCADE)
    category = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity_sold = models.DecimalField(max_digits=10, decimal_places=2)  # Quantity sold in liters
    price_per_liter = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        # Automatically calculate total price for the sale item
        self.total_price = self.quantity_sold * self.price_per_liter
        super().save(*args, **kwargs)

        # Update the inventory
        inventory = FuelInventory.objects.get(station=self.sale.station, category=self.category)
        if self.quantity_sold > inventory.quantity:
            raise ValueError("Not enough fuel in inventory to process this sale.")
        inventory.quantity -= self.quantity_sold
        inventory.save()

    def __str__(self):
        return f"{self.category.name} Sale at {self.sale.station.name}"






class Report(models.Model):
    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='reports')
    category = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reports')
    
    # Detailed metrics
    opening_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Stock at the start of the day
    purchases_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Total purchases
    sales_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Total sales revenue
    closing_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Stock at the end of the day
    
    # Calculations
    profit = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Sales revenue - Purchase cost
    net_profit = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Profit - operational costs
    
    # Additional fields
    operational_costs = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Any extra costs
    fuel_sold = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Total quantity of fuel sold
    
    # Date of the report
    report_date = models.DateField(auto_now_add=True)

    def calculate_report(self):
        """
        Populate fields like `profit`, `net_profit`, and calculate stock metrics.
        """
        # Fetch inventory details
        inventory = FuelInventory.objects.get(station=self.station, category=self.category)
        self.opening_stock = self.closing_stock if self.closing_stock > 0 else inventory.quantity

        # Fetch sales data
        sales = SaleItem.objects.filter(
            sale__station=self.station,
            category=self.category,
            sale__sale_date__date=self.report_date
        )
        self.fuel_sold = sum(item.quantity_sold for item in sales)
        self.sales_total = sum(item.total_price for item in sales)

        # Fetch purchase data
        purchases = PurchaseItem.objects.filter(
            purchase__station=self.station,
            category=self.category,
            purchase__purchase_date__date=self.report_date
        )
        self.purchases_total = sum(item.total_cost for item in purchases)

        # Calculate profit and closing stock
        self.closing_stock = self.opening_stock + self.purchases_total - self.fuel_sold
        self.profit = self.sales_total - self.purchases_total
        self.net_profit = self.profit - self.operational_costs

    def save(self, *args, **kwargs):
        self.calculate_report()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Report for {self.station.name} - {self.report_date}"


