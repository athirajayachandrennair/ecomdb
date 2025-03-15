from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Cart, Order, OrderItem, User
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


# Home page


from django.shortcuts import render
from .models import Product

def home(request):
    query = request.GET.get('query', '')
    if query:
        products = Product.objects.filter(name__icontains=query)
    else:
        products = Product.objects.all()
    
    return render(request, 'home.html', {'products': products, 'query': query})


def register(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        
        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': "Username already exists!"})

        user = User.objects.create(username=username, password=password)
        request.session['user_id'] = user.id  # Log in user after registration
        return redirect('home')  # Redirect to homepage

    return render(request, 'register.html')


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        try:
            user = User.objects.get(username=username, password=password)
            request.session['user_id'] = user.id  # Store user ID in session
            return redirect('home')

        except User.DoesNotExist:
            return render(request, 'login.html', {'error': "Invalid username or password"})

    return render(request, 'login.html')

def logout_user(request):
    request.session.flush()  # Clear session data
    return redirect('login')


def add_to_cart(request, product_id):
    if 'user_id' not in request.session:
        return redirect('login')

    user = get_object_or_404(User, id=request.session['user_id'])
    product = get_object_or_404(Product, id=product_id)

    cart_item, created = Cart.objects.get_or_create(user=user, product=product)

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('view_cart')

def view_cart(request):
    if 'user_id' not in request.session:
        return redirect('login')

    user = get_object_or_404(User, id=request.session['user_id'])
    cart_items = Cart.objects.filter(user=user)
    total_price = sum(item.total_price() for item in cart_items)

    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})


def place_order(request):
    if 'user_id' not in request.session:
        return redirect('login')

    user = get_object_or_404(User, id=request.session['user_id'])
    cart_items = Cart.objects.filter(user=user)

    if not cart_items.exists():
        return redirect('view_cart')

    total_price = sum(item.product.price * item.quantity for item in cart_items)
    
    # Create an Order
    order = Order.objects.create(user=user, total_price=total_price)

    # Move Cart Items to OrderItems
    for item in cart_items:
        OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)
    
    # Clear Cart
    cart_items.delete()

    return redirect('order_success')


def order_success(request):
    return render(request, 'order_success.html')

def purchase_history(request):
    if 'user_id' not in request.session:
        return redirect('login')  # Redirect if not logged in

    user = get_object_or_404(User, id=request.session['user_id'])
    orders = Order.objects.filter(user=user).order_by('-created_at')  # Fetch orders for the user

    return render(request, 'purchase_history.html', {'orders': orders})


def download_invoice(request, order_id):
    if 'user_id' not in request.session:
        return redirect('login')

    user = get_object_or_404(User, id=request.session['user_id'])
    order = get_object_or_404(Order, id=order_id, user=user)
    order_items = OrderItem.objects.filter(order=order)

    # Create response object
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'

    # Generate PDF using ReportLab
    pdf = canvas.Canvas(response, pagesize=A4)
    pdf.setTitle(f"Invoice #{order.id}")

    # Add title
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(200, 800, f"Invoice for Order #{order.id}")

    # Add user details
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, 770, f"Customer: {user.username}")
    pdf.drawString(50, 750, f"Date: {order.created_at.strftime('%Y-%m-%d')}")

    # Table Header
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, 720, "Product")
    pdf.drawString(300, 720, "Quantity")
    pdf.drawString(400, 720, "Price")

    # Table Data
    y = 700
    pdf.setFont("Helvetica", 12)
    for item in order_items:
        pdf.drawString(50, y, item.product.name)
        pdf.drawString(300, y, str(item.quantity))
        pdf.drawString(400, y, f"${item.product.price}")
        y -= 20

    # Total Price
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y - 20, f"Total Price: ${order.total_price}")

    # Save the PDF
    pdf.showPage()
    pdf.save()

    return response