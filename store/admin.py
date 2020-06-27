from django.contrib import admin
from .models import Product,Orders,OrderUpdate,Contact
# Register your models here.
admin.site.site_header="Store Admin"
admin.site.site_title="Welcome Admin"
admin.site.register(Product)
admin.site.register(Orders)
admin.site.register(OrderUpdate),
admin.site.register(Contact),