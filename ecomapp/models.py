from django.db import models

class User(models.Model):  # Custom User Model (since you are not using Django auth)
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)  # Simple password storage (use hashing in production)

class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image = models.ImageField(upload_to='products/')

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Cart belongs to a user
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Product added to cart
    quantity = models.PositiveIntegerField(default=1)  # Default quantity is 1

    def total_price(self):
        return self.quantity * self.product.price  # Calculate total price

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()