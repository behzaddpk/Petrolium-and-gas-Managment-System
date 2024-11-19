from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from app.models import *
from app.froms import *
from django.contrib.auth.decorators import login_required
from decimal import Decimal, InvalidOperation
from django.db import transaction
import json
from django.utils.timezone import now
from datetime import timedelta

# Create your views here.


def signin(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')


        user = authenticate(request, email=email, password=password)

        if not user:
            messages.error(request, 'Invalid username or password')
        else:
            login(request, user)
            return redirect('dashboard')


    return render(request, 'sign-in.html')


def sign_out(request):
    logout(request)
    return redirect('signin')



def dashboard(request):
    stations = Station.objects.all()
    products = Product.objects.all()
    inventories = FuelInventory.objects.all()


    context = {
        "stations": stations,
        'inventories': inventories,
        
    }
    return render(request, 'dashboard.html')


def station(request):
    stations = Station.objects.all()

    return render(request, 'station/station.html', {'stations': stations})



def add_station(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        address = request.POST.get('address')
        contact = request.POST.get('contact')
        capacity = request.POST.get('capacity')
        is_active = request.POST.get('is_active') == 'on'  # Checkbox needs to be checked to be 'on'

        # Validation for empty fields
        if not name or not address or not contact or not capacity:
            messages.error(request, "All fields are required.")
            return redirect('station')  # Redirect back to the station page

        # Create and save the new station
        station = Station(
            name=name, 
            location=address, 
            contact_number=contact, 
            capacity=capacity, 
            is_active=is_active
        )
        station.save()

        messages.success(request, "Station added successfully.")
        return redirect('station')  # Redirect to the station list page

        
def edit_station(request, station_id):
    station = Station.objects.get(id=station_id)  # Get the station by its ID

    if request.method == 'POST':
        name = request.POST.get('name')
        address = request.POST.get('address')
        contact = request.POST.get('contact')
        capacity = request.POST.get('capacity')
        is_active = request.POST.get('is_active') == 'on'  # Checkbox for active status

        # Validation for empty fields
        if not name or not address or not contact or not capacity:
            messages.error(request, "All fields are required.")
            return redirect('edit_station', station_id=station.id)  # Redirect back to edit page

        # Update the station
        station.name = name
        station.location = address
        station.contact_number = contact
        station.capacity = capacity
        station.is_active = is_active
        station.save()

        messages.success(request, "Station updated successfully.")
        return redirect('station')  # Redirect to the station list page





# Delete station view
def delete_station(request, station_id):
    station = Station.objects.get(id=station_id)
    station.delete()
    messages.success(request, "Station deleted successfully.")
    return redirect('station')  # Redirect back to the station list page


# Fuel type

# Display all FuelTypes
def product(request):
    products = Product.objects.all()
    return render(request, 'products/products.html', {'products': products})

# Add a new FuelType
def add_product(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        price_per_liter = request.POST.get('price_per_liter')
        description = request.POST.get('description', '')

        if not name or not price_per_liter:
            messages.error(request, "Name and Price per Liter are required.")
            return redirect('product')

        Product.objects.create(
            name=name,
            price_per_liter=price_per_liter,
            description=description
        )
        messages.success(request, "Product added successfully.")
        return redirect('products')

# Edit an existing FuelType
def edit_product(request, product_id):
    product = Product.objects.get(id=product_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        price_per_liter = request.POST.get('price_per_liter')
        description = request.POST.get('description', '')

        if not name or not price_per_liter:
            messages.error(request, "Name and Price per Liter are required.")
            return redirect('product')

        product.name = name
        product.price_per_liter = price_per_liter
        product.description = description
        product.save()

        messages.success(request, "Product updated successfully.")
        return redirect('products')

# Delete a FuelType
def delete_product(request, product_id):
    product = Product.objects.get(id=product_id)
    product.delete()
    messages.success(request, "Product deleted successfully.")
    return redirect('products')





# Supplier list view
def supplier_list(request):
    suppliers = Supplier.objects.all()
    return render(request, 'suppliers/suppliers.html', {'suppliers': suppliers})



# Add supplier view
def add_supplier(request):
    if request.method == 'POST':
        name = request.POST['name']
        contact_number = request.POST['contact_number']
        address = request.POST.get('address', '')
        
        Supplier.objects.create(name=name, contact_number=contact_number, address=address)
        messages.success(request, 'Supplier added successfully.')
        return redirect('suppliers')
    return render(request, 'suppliers/suppliers.html')

# Edit supplier view
def edit_supplier(request, id):
    supplier = Supplier.objects.get(id=id)
    
    if request.method == 'POST':
        supplier.name = request.POST['name']
        supplier.contact_number = request.POST['contact_number']
        supplier.address = request.POST.get('address', '')
        supplier.save()
        
        messages.success(request, 'Supplier updated successfully.')
        return redirect('suppliers')
    
    

# Delete supplier view
def delete_supplier(request, id):
    supplier = Supplier.objects.get(id=id)
    supplier.delete()
    messages.success(request, 'Supplier deleted successfully.')
    return redirect('suppliers')




# Sale list view
def sale_list(request):
    sales = Sale.objects.all().select_related('station')
    stations = Station.objects.all()
    categories = Product.objects.all()

    # Preload category prices for JavaScript
    category_prices = {str(category.id): str(category.price_per_liter) for category in categories}

    context = {
        'sales': sales,
        'stations': stations,
        'categories': categories,
        'category_prices_json': json.dumps(category_prices),
    }
    return render(request, 'sales/sales.html', context=context)


from django.http import JsonResponse


def get_category_price(request, category_id):
    try:
        category = Product.objects.get(id=category_id)
        return JsonResponse({'price_per_liter': category.price_per_liter}, status=200)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Category not found'}, status=404)
    





def add_sale(request):
    if request.method == 'POST':
        # Retrieve the station, supplier, and product details from the form
        station_id = request.POST['station']
        supplier_id = request.POST['supplier']

        # Retrieve the categories, quantities, and prices
        category_ids = request.POST.getlist('categories')
        quantities = request.POST.getlist('quantities')
        prices = request.POST.getlist('prices')

        try:
            with transaction.atomic():
                # Step 1: Calculate total cost and create SaleItems
                sale_items = []
                total_cost = Decimal(0)

                for category_id, quantity, price in zip(category_ids, quantities, prices):
                    quantity = Decimal(quantity)
                    price = Decimal(price)
                    item_total_cost = quantity * price

                    # Step 2: Create SaleItem for each product
                    sale_item = SaleItem(
                        category_id=category_id,
                        quantity_sold=quantity,
                        price_per_liter=price,
                        total_price=item_total_cost
                    )
                    sale_items.append(sale_item)
                    total_cost += item_total_cost

                    # Step 3: Update inventory for the sale
                    inventory = FuelInventory.objects.get(station_id=station_id, category_id=category_id)
                    if quantity > inventory.quantity:
                        raise ValueError("Not enough fuel in inventory to process this sale.")
                    inventory.quantity -= quantity
                    inventory.save()

                # Step 4: Create and save the Sale instance
                sale = Sale(
                    station_id=station_id,
                    supplier_id=supplier_id,
                    total_cost=total_cost  # Total cost from SaleItems
                )
                sale.save()  # Save the Sale to generate its primary key

                # Step 5: Assign Sale to SaleItems and save them
                for sale_item in sale_items:
                    sale_item.sale = sale  # Associate Sale with SaleItem
                
                # Save SaleItems after the Sale instance is saved and has its primary key
                SaleItem.objects.bulk_create(sale_items)  # Save all SaleItems at once

                # Show success message and redirect to sales page
                messages.success(request, "Sale added successfully.")
                return redirect('sale')

        except Exception as e:
            messages.error(request, f"Error adding sale: {e}")
            return redirect('sale')

    else:
        # If GET request, render the sale form
        stations = Station.objects.all()
        categories = Product.objects.all()
        suppliers = Supplier.objects.all()

        return render(request, 'sales/add_sale.html', {
            'stations': stations,
            'categories': categories,
            'suppliers': suppliers
        })

from django.db import transaction
from decimal import Decimal

def edit_sale(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)  # Fetch the sale instance

    if request.method == 'POST':
        # Debug incoming data
        print("POST data:", request.POST)

        station_id = request.POST.get('station')
        supplier_id = request.POST.get('supplier')
        category_ids = request.POST.getlist('categories')
        quantities = request.POST.getlist('quantities')
        prices = request.POST.getlist('prices')

        try:
            with transaction.atomic():
                # Get and update station and supplier
                station = get_object_or_404(Station, id=station_id)
                supplier = get_object_or_404(Supplier, id=supplier_id)
                sale.station = station
                sale.supplier = supplier

                # Reset inventory for the sale's existing items
                for sale_item in sale.saleitems.all():
                    inventory = FuelInventory.objects.get(
                        station=sale.station,
                        category=sale_item.category
                    )
                    inventory.quantity += sale_item.quantity_sold  # Restore inventory
                    inventory.save()

                # Clear old sale items (to be re-added)
                sale.saleitems.all().delete()

                total_cost = Decimal(0)
                new_details = []

                # Update Sale Items
                for category_id, quantity, price in zip(category_ids, quantities, prices):
                    category = get_object_or_404(Product, id=category_id)
                    quantity = Decimal(quantity)
                    price = Decimal(price)
                    total_price = quantity * price
                    total_cost += total_price

                    # Adjust inventory
                    inventory = FuelInventory.objects.get(
                        station=station,
                        category=category
                    )
                    if quantity > inventory.quantity:
                        raise ValueError(f"Not enough inventory for category {category.name}.")

                    inventory.quantity -= quantity
                    inventory.save()

                    # Create new SaleItem
                    new_details.append(SaleItem(
                        sale=sale,
                        category=category,
                        quantity_sold=quantity,
                        price_per_liter=price,
                        total_price=total_price
                    ))

                # Bulk create new SaleItems
                SaleItem.objects.bulk_create(new_details)

                # Update and save the Sale instance
                sale.total_cost = total_cost
                sale.save()

                messages.success(request, "Sale updated successfully.")
                return redirect('sale')  # Redirect to sales list

        except Exception as e:
            # Debugging
            print(f"Error updating sale: {e}")
            messages.error(request, f"Error updating sale: {e}")
            return redirect('edit_sale', sale_id=sale.id)

    else:
        # Render the edit sale form for a GET request
        stations = Station.objects.all()
        categories = Product.objects.all()
        suppliers = Supplier.objects.all()
        sale_items = sale.saleitems.all()  # Fetch sale items for this sale

        return render(request, 'sales/edit_sale.html', {
            'sale': sale,
            'sale_items': sale_items,
            'stations': stations,
            'categories': categories,
            'suppliers': suppliers,
        })
    

def sale_receipt(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)
    return render(request, 'receipts/sale_receipt.html', {'sale': sale})



# Delete Sale view
def delete_sale(request, sale_id):
    sale = Sale.objects.get(id=sale_id)
    sale.delete()
    messages.success(request, 'Sale deleted successfully.')
    return redirect('sale')






# purchase
def purchase(request):
    purchase_list = Purchase.objects.select_related('station', 'supplier').all()
    stations = Station.objects.all()
    categories = Product.objects.all()
    suppliers = Supplier.objects.all()
    purchase_item = PurchaseItem.objects.all()

    context = {
        'purchases': purchase_list,
        'items':purchase_item,
        'stations': stations,
        'categories': categories,
        'suppliers': suppliers,
    }
    return render(request, 'purchase/purchase.html', context=context)






def add_purchase(request):
    stations = Station.objects.all()
    categories = Product.objects.all()
    suppliers = Supplier.objects.all()

    if request.method == 'POST':
        station_id = request.POST['station']
        supplier_id = request.POST['supplier']

        # Retrieve the list of categories, quantities, and prices
        category_ids = request.POST.getlist('categories')
        quantities = request.POST.getlist('quantities')
        prices = request.POST.getlist('prices')

        
        # Ensure all database operations are atomic
        with transaction.atomic():
            # Create a new Purchase entry (without items yet)
            purchase = Purchase(
                station_id=station_id,
                supplier_id=supplier_id,
                total_cost=Decimal(0),  # Initial cost is zero
            )
            purchase.save()

            # List to store PurchaseItem objects
            purchase_items = []
            total_cost = Decimal(0)

            for category_id, quantity, price in zip(category_ids, quantities, prices):
                # Convert to Decimal for precision
                quantity = Decimal(quantity)
                price = Decimal(price)
                item_total_cost = quantity * price

                # Create a PurchaseItem for each product
                purchase_item = PurchaseItem(
                    purchase=purchase,
                    category_id=category_id,
                    quantity_purchased=quantity,
                    price_per_liter=price,
                    total_cost=item_total_cost
                )
                purchase_items.append(purchase_item)
                total_cost += item_total_cost

                # Update inventory
                inventory, created = FuelInventory.objects.get_or_create(
                    station_id=station_id,
                    category_id=category_id,
                    defaults={'quantity': Decimal(0)}
                )
                inventory.quantity += quantity
                inventory.save()

            # Save all the new purchase items to the database
            PurchaseItem.objects.bulk_create(purchase_items)

            # Update the total cost for the purchase
            purchase.total_cost = total_cost
            purchase.save()

            # Show success message and redirect
            messages.success(request, "Purchase item added successfully.")
            return redirect('purchase')
       

    return render(request, 'purchase/add_purchase.html', {
        'stations': stations,
        'categories': categories,
        'suppliers': suppliers,
    })


def edit_purchase(request, purchase_id):
    purchase = Purchase.objects.get(id=purchase_id)
    stations = Station.objects.all()
    categories = Product.objects.all()
    suppliers = Supplier.objects.all()

    if request.method == 'POST':
        station_id = request.POST['station']
        supplier_id = request.POST['supplier']

        category_ids = request.POST.getlist('categories')
        quantities = request.POST.getlist('quantities')
        prices = request.POST.getlist('prices')

        try:
            with transaction.atomic():
                # Update station and supplier
                purchase.station_id = station_id
                purchase.supplier_id = supplier_id
                purchase.save()

                # Delete old purchase details
                purchase.items.all().delete()

                new_details = []
                for category_id, quantity, price in zip(category_ids, quantities, prices):
                    category_instance = Product.objects.get(id=category_id)
                    quantity = Decimal(quantity)
                    price = Decimal(price)
                    total_cost = quantity * price

                    # Update inventory
                    inventory, created = FuelInventory.objects.get_or_create(
                        station_id=station_id,
                        category=category_instance,
                        defaults={'quantity': Decimal(0)}
                    )
                    inventory.quantity = quantity
                    inventory.save()

                    # Create new purchase item
                    new_details.append(PurchaseItem(
                        purchase=purchase,
                        category=category_instance,
                        quantity_purchased=quantity,
                        price_per_liter=price,
                        total_cost=total_cost
                    ))

                # Save all new details and update total cost
                PurchaseItem.objects.bulk_create(new_details)
                purchase.total_cost = sum(item.total_cost for item in new_details)
                purchase.save()

                messages.success(request, "Purchase updated successfully.")
                return redirect('purchase')

        except Exception as e:
            messages.error(request, f"Error updating purchase: {e}")
            return redirect('purchase')

    return render(request, 'purchase/edit_purchase.html', {
        'purchase': purchase,
        'stations': stations,
        'categories': categories,
        'suppliers': suppliers
    })



def purchase_receipt(request, purchase_id):
    # Fetch the purchase object with its related purchase items
    purchase = get_object_or_404(Purchase, id=purchase_id)
    purchase_items = purchase.items.all()  # Get related purchase items

    # Context to pass to the template
    context = {
        'purchase': purchase,
        'purchase_items': purchase_items,
    }
    
    return render(request, 'receipts/purchase_receipt.html', context)




def delete_purchase(request, purchase_id):
    # Fetch the purchase object or return 404 if it doesn't exist
    purchase = get_object_or_404(Purchase, id=purchase_id)

    # Use a transaction to ensure atomicity
    with transaction.atomic():
        # Loop through all PurchaseItems related to this Purchase
        purchase_items = purchase.items.all()  # Related name 'items' in PurchaseItem
        for item in purchase_items:
            try:
                # Find the corresponding inventory record
                inventory = FuelInventory.objects.get(station=purchase.station, category=item.category)

                # Subtract the item's quantity from the inventory
                inventory.quantity -= Decimal(item.quantity_purchased)

                # Ensure quantity doesn't drop below 0
                if inventory.quantity <= 0:
                    inventory.delete()
                else:
                    inventory.save()
            except FuelInventory.DoesNotExist:
                # If inventory doesn't exist, it's a logic issue
                messages.error(request, f"Inventory for {item.category.name} not found. Data inconsistency detected.")
                return redirect('purchase')

        # Delete all related PurchaseItems
        purchase_items.delete()

        # Delete the Purchase object
        purchase.delete()

    messages.success(request, 'Purchase and its items were deleted successfully, and inventory was updated.')
    return redirect('purchase')







def fuel_inventory_list(request):
    """Display all fuel inventories."""
    inventories = FuelInventory.objects.select_related('station', 'category').all()
    stations = Station.objects.all()
    categories = Product.objects.all()
    return render(request, 'inventory/inventory.html', {
        'inventories': inventories,
        'stations': stations,
        'categories': categories
    })


def add_fuel_inventory(request):
    """Add a new fuel inventory."""
    if request.method == 'POST':
        station_id = request.POST.get('station')
        category_id = request.POST.get('category')
        quantity = request.POST.get('quantity')
        price_per_liter = request.POST.get('price_per_liter')
        date = request.POST.get('date')

        total_cost = float(quantity) * float(price_per_liter)
        try:
            station = Station.objects.get(id=station_id)
            category = Product.objects.get(id=category_id)
            inventory = FuelInventory.objects.create(
                station=station,
                category=category,
                quantity=quantity,
                price_per_liter=price_per_liter,
                purchase_date=date,
                total_cost=total_cost
            )
            inventory.save()
            messages.success(request, "Fuel inventory added successfully.")
        except Exception as e:
            messages.error(request, f"Error adding fuel inventory: {e}")
        return redirect('inventory')


def edit_fuel_inventory(request, inventory_id):
    """Edit an existing fuel inventory."""
    inventory = FuelInventory.objects.get(id=inventory_id)
    if request.method == 'POST':
        station_id = request.POST.get('station')
        category_id = request.POST.get('category')
        quantity = request.POST.get('quantity')

        try:
            inventory.station = Station.objects.get(id=station_id)
            inventory.category = Product.objects.get(id=category_id)
            inventory.quantity = quantity
            inventory.save()
            messages.success(request, "Fuel inventory updated successfully.")
        except Exception as e:
            messages.error(request, f"Error updating fuel inventory: {e}")
        return redirect('inventory')


def delete_fuel_inventory(request, inventory_id):
    """Delete an existing fuel inventory."""
    inventory = FuelInventory.objects.get(id=inventory_id)
   
    inventory.delete()
    messages.success(request, "Fuel inventory deleted successfully.")
    return redirect('inventory')







def report_list(request):
    # Fetch reports and apply filters if needed
    station_id = request.GET.get('station')
    category_id = request.GET.get('category')

    reports = Report.objects.all().order_by('-report_date')
    if station_id:
        reports = reports.filter(station_id=station_id)
    if category_id:
        reports = reports.filter(category_id=category_id)

    stations = Station.objects.all()
    categories = Product.objects.all()

    context = {
        'reports': reports,
        'stations': stations,
        'categories': categories,
    }
    return render(request, 'report/report_list.html', context=context)

def generate_report(request):
    if request.method == "POST":
        station_id = request.POST.get('station')
        category_id = request.POST.get('category')

        # Validate inputs
        if not station_id or not category_id:
            messages.error(request, "Please select a station and category.")
            return redirect('report_list')

        # Generate report
        station = Station.objects.get(id=station_id)
        category = Product.objects.get(id=category_id)
        today = now().date()

        # Check if report already exists
        if Report.objects.filter(station=station, category=category, report_date=today).exists():
            messages.error(request, "Report for this station and category already exists.")
        else:
            Report.objects.create(station=station, category=category, report_date=today)
            messages.success(request, "Report generated successfully!")

        return redirect('report_list')


def generate_daily_reports():
    today = now().date()
    stations = Station.objects.all()
    products = Product.objects.all()

    for station in stations:
        for product in products:
            # Check if report already exists
            if not Report.objects.filter(station=station, category=product, report_date=today).exists():
                report = Report.objects.create(
                    station=station,
                    category=product,
                    report_date=today,
                )
                report.save()  # Trigger calculations

