from django.db import models

# Station model
class Station(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    capacity = models.DecimalField(max_digits=10, decimal_places=2)  # Fuel capacity in liters
    contact_number = models.CharField(max_length=20)

    def __str__(self):
        return self.name


# FuelType model
class FuelType(models.Model):
    name = models.CharField(max_length=50)
    price_per_liter = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


# Inventory model
class FuelInventory(models.Model):
    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='inventories')
    fuel_type = models.ForeignKey(FuelType, on_delete=models.CASCADE, related_name='inventories')
    quantity = models.DecimalField(max_digits=10, decimal_places=2)  # Quantity in liters
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.station.name} - {self.fuel_type.name}"





# Supplier model
class Supplier(models.Model):
    name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=20)
    address = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name


# Sales model
class Sale(models.Model):
    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='sales')
    fuel_type = models.ForeignKey(FuelType, on_delete=models.CASCADE, related_name='sales')
    quantity_sold = models.DecimalField(max_digits=10, decimal_places=2)  # Quantity sold in liters
    price_per_liter = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_date = models.DateTimeField(auto_now_add=True)
    station = models.ForeignKey(Station, on_delete=models.SET_NULL, null=True, blank=True, related_name='stations')

    def __str__(self):
        return f"Sale at {self.station.name} - {self.fuel_type.name}"


# Purchase model
class Purchase(models.Model):
    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='purchases')
    fuel_type = models.ForeignKey(FuelType, on_delete=models.CASCADE, related_name='purchases')
    quantity_purchased = models.DecimalField(max_digits=10, decimal_places=2)  # Quantity purchased in liters
    price_per_liter = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateTimeField(auto_now_add=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='purchases')

    def __str__(self):
        return f"Purchase at {self.station.name} - {self.fuel_type.name}"


# Report model
class Report(models.Model):
    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='reports')
    fuel_type = models.ForeignKey(FuelType, on_delete=models.CASCADE, related_name='reports')
    sales_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    purchases_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    report_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Report for {self.station.name} - {self.report_date}"
