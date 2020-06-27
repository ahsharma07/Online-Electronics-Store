from django.db import models

# Create your models here.
class Product(models.Model):
    product_name=models.CharField(max_length=20)
    product_description=models.CharField(max_length=1000)
    category_list=[('Mobiles','Mobiles'),('Laptops','Laptops'),('Headphones','Headphones')]
    category=models.CharField(max_length=50,choices=category_list)
    price=models.IntegerField()
    published_date=models.DateField()
    image=models.ImageField(upload_to="store/images")
    def __str__(self):
        return self.product_name

class Orders(models.Model):
    items_json = models.CharField(max_length=5000)
    name = models.CharField(max_length=90)
    amount=models.IntegerField(default=0)
    email = models.CharField(max_length=50)
    address = models.CharField(max_length=110)
    city = models.CharField(max_length=30)
    state = models.CharField(max_length=20)
    zip_code = models.CharField(max_length=6)
    phone = models.CharField(max_length=15, default="")

class OrderUpdate(models.Model):
    order_id = models.IntegerField(default="")
    update_desc = models.CharField(max_length=500)
    timestamp = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.update_desc[0:7] + "..."

class Contact(models.Model):
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=70)
    phone = models.CharField(max_length=70)
    desc = models.CharField(max_length=500)
    def __str__(self):
        return self.name