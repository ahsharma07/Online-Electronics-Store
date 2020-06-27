from django.shortcuts import render,HttpResponse
from django.contrib.auth.decorators import login_required
from math import ceil
import threading
from .models import Product,Orders,OrderUpdate,Contact
from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
from django.views.decorators.csrf import csrf_exempt
from Paytm import Checksum
MERCHANT_KEY = 'xxxxxxxxxxxxx'
# Create your views here.

def homeview(request):
    return render(request,"store/index.html")

def products(request):
    params={}
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])
        params = {'allProds': allProds}
    return render(request, 'store/products.html',params)

# def allProducts(request):
#     params = {}
#     allProds = []
#     catprods = Product.objects.values('category', 'id')
#     cats = {item['category'] for item in catprods}
#     for cat in cats:
#         prod = Product.objects.filter(category=cat)
#         n = len(prod)
#         nSlides = n // 4 + ceil((n / 4) - (n // 4))
#         allProds.append([prod, range(1, nSlides), nSlides])
#     params = {'allProds': allProds}
#     if request.is_ajax():
#         print("we are in ajax")
#         pass
#     return render(request, 'store/allprod.html', params)

def contact(request):
    if request.method=="POST":
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        desc = request.POST.get('desc', '')
        contact = Contact(name=name, email=email, phone=phone, desc=desc)
        contact.save()
    return render(request, 'store/contact.html')

def search(request):
    query = request.GET.get('search')
    print(query)
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query, item)]

        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        if len(prod) != 0:
            allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds': allProds, "msg": ""}
    if len(allProds) == 0 or len(query)<4:
        params = {'msg': "Please make sure to enter relevant search query"}
    print(params)
    return render(request, 'store/search.html', params)

def checkout(request):
    if request.method == "POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        amount = request.POST.get('amount', '')
        email = request.POST.get('email', '')
        address = request.POST.get('address1', '') + " " + request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')
        order = Orders(items_json=items_json, name=name, email=email, address=address, city=city,
                       state=state, zip_code=zip_code, phone=phone,amount=amount)
        order.save()

        id = order.id
        update = OrderUpdate(order_id=id, update_desc="The Order has been Placed")
        update.save()
        param_dict = {

                    'MID': 'xxxxxxxxxxxxxxxxxx',
                    'ORDER_ID': str(order.id),
                    'TXN_AMOUNT': str(amount),
                    'CUST_ID': str(email),
                    'MOBILE_NO':str(phone) ,
                    'EMAIL': str(email),
                    'INDUSTRY_TYPE_ID': 'Retail',
                    'WEBSITE': 'WEBSTAGING',
                    'CHANNEL_ID': 'WEB',
                    'CALLBACK_URL':'http://127.0.0.1:8000/handlerequest/',

            }
        param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, MERCHANT_KEY)
        return render(request, 'store/paytm.html', {'param_dict': param_dict})

    return render(request, 'store/checkout.html')


@csrf_exempt
def handlerequest(request):
    # paytm will send you post request here
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]

    verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
    if verify:
        if response_dict['RESPCODE'] == '01':
            print('order successful')
            order=Orders.objects.get(id=response_dict['ORDERID'])

            th1=threading.Thread(target=sendemail,args=[response_dict['ORDERID'],order.email])
            th1.start()
        else:
            print('order was not successful because' + response_dict['RESPMSG'])
            order=Orders.objects.filter(id=response_dict['ORDERID'])
            order.delete()
            update=OrderUpdate.objects.filter(id=response_dict['ORDERID'])
            update.delete()
    return render(request, 'store/paymentstatus.html', {'response': response_dict})

def tracker(request):
     if request.method=="POST":
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        try:
            order = Orders.objects.filter(id=orderId, email=email)
            if len(order)>0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                    response = json.dumps([updates,order[0].items_json], default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{}')
        except Exception as e:
            return HttpResponse('{}')
     return render(request, 'store/tracker.html')


# functions created
def sendemail(order_id,receiver_email):
    mail_content = f'This is test email for your order that order is successfully placed with Order ID {order_id} Thank You'
    # The mail addresses and password
    sender_address = 'xxxxxxxxxxxxxx'
    sender_pass = 'xxxxxxxxxxxxxxx'
    receiver_address = receiver_email
    # Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = 'A test mail sent by Electronics Store'  # The subject line
    # The body and the attachments for the mail
    message.attach(MIMEText(mail_content, 'plain'))
    # Create SMTP session for sending the mail
    session = SMTP('smtp.gmail.com', 587)  # use gmail with port
    session.starttls()  # enable security
    session.login(sender_address, sender_pass)  # login with mail_id and password
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()
    print('Mail Sent')

def searchMatch(query, item):
    if query in item.product_description.lower() or query in item.product_name.lower() or query in item.category.lower():
        return True
    else:
        return False
