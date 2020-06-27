from django.urls import path
from . import views
urlpatterns=[
    path("",views.homeview,name='home'),
    path("products/",views.products , name='products'),
    # path("allpro/",views.allProducts , name='allproducts'),
    path("search/",views.search,name='search'),
    path("contact/",views.contact,name='contact'),
    path("checkout/",views.checkout,name='checkout'),
    path("tracker/",views.tracker,name='tracker'),
    path("handlerequest/",views.handlerequest,name='handlerequest'),
]