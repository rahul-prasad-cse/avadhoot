from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.template import loader
from django.contrib.auth import authenticate, login
from django.views.generic import View
from .forms import UserForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib import auth
from django.contrib.auth.models import User
import datetime
import MySQLdb

def index(request):
    context = {'loggedin':0}
    if request.user.is_authenticated():
        if request.user.is_superuser:
            context = {
                'loggedin': 2,
                'name': request.user.first_name,
            }
        else:
            context={
                'loggedin':1,
                'name':request.user.first_name,
            }
    return render(request, 'login/index.html', context)

def products(request):
    sortby = request.POST.get('optradio')
    query = "select * from product order by "
    if sortby is None:
        print('none')
        query = "select * from product;"
    else:
        print(sortby)
        query+= sortby + ";"

    template = loader.get_template('login/products.html')
    db = MySQLdb.connect("localhost", "rahulp", "password1234", "avadhootent")
    cursor = db.cursor()
    cursor.execute(query)
    entries = []
    class product_object:
        def __init__(self,id,name,quantity,description,price):
            self.id = id
            self.name = name
            self.quantity = quantity
            self.description = description
            self.price = price

    for row in cursor:
        entries.append(product_object(row[0],row[1],row[2],row[3],row[4]))
    db.close()
    context = {'loggedin':0}
    if request.user.is_authenticated():
        context = {
            'loggedin': 1,
            'name': request.user.first_name,
        }
        if request.user.is_superuser:
            context['loggedin']=2
    context['products']=entries
    return HttpResponse(template.render(context,request))

@login_required(login_url = 'login:signin')
def addtocart(request, productid):
    quantity = int(request.POST.get('quantity'))
    db = MySQLdb.connect('localhost','rahulp','password1234','avadhootent')
    cursor = db.cursor()
    cursor.execute("select quantity from product where id = "+str(productid)+";")

    quantity_left = cursor.fetchone()
    quantity_left = quantity_left[0]
    if quantity_left < quantity:
        pass#show error message of stock less than required
        db.close()
        return redirect('login:products')
    else:
        cursor.execute("update product set quantity = " + str(quantity_left - quantity) + " where id = "+ str(productid) + ";")
        cursor.execute("select price from product where id = "+str(productid)+";")
        price = cursor.fetchone()
        price = price[0]
        preventries = cursor.execute("select * from cart where cust_id = "+str(request.user.id)+" and item_id="+str(productid)+";")

        if preventries == 0:
            cursor.execute( "insert into cart values(" +str(request.user.id)+","+str(productid)+","+str(quantity)+ ");" )
        else:
            cursor.execute("select quantity from cart where cust_id = "+str(request.user.id) + " and item_id = "+str(productid)+";")
            prevquantity = cursor.fetchone()
            prevquantity = prevquantity[0]
            cursor.execute("update cart set quantity = "+ str(prevquantity+quantity)+" where cust_id = "+str(request.user.id) + " and item_id = "+str(productid)+";")
        db.commit()
        db.close()
        return redirect('login:products')

def adminpages(request):
    context={}
    if request.user.is_superuser:
        context = {
            'loggedin': 2,
            'name': request.user.first_name,
        }
    else:
        context = {
            'loggedin': 1,
            'name': request.user.first_name,
        }
    return render(request,'login/adminpages.html',context)

def signin(request):
    context = {'loggedin':0}
    if request.user.is_authenticated():
        context = {
            'loggedin': 1,
            'name': request.user.first_name,
        }
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(username=username,password=password)
        if user is not None:
            auth.login(request, user)
            if request.user.is_superuser:
                return redirect('login:adminpages')
            context = {'loggedin':1,
                       'name':request.user.first_name,}
            return render(request,'login/index.html',context)
        else:
            messages.error(request,'Invalid username or password.')

    return render(request, 'login/signin.html',context)

@login_required(login_url = 'login:signin')
def orders(request):
    class orderdisplay:
        def __init__(self,order_id, order_date, total_cost, payment_status, delivery_status):
            self.order_id = order_id
            self.order_date = order_date
            self.total_cost = total_cost
            self.payment_status = payment_status
            self.delivery_status = delivery_status

    id = request.user.id
    db = MySQLdb.connect('localhost','rahulp','password1234','avadhootent')
    cursor = db.cursor()
    cursor.execute("select * from orders where cust_id = "+str(id)+";")
    entries = cursor.fetchall()
    orderentries = []
    for item in entries:
        nowdate = item[2].strftime("%Y-%m-%d")
        cursor.execute("select status from payment where payment_id = "+str(item[5])+";")
        status = cursor.fetchone()
        status = int(status[0])
        orderentries.append(orderdisplay(item[0],nowdate,item[3],status,item[4]))

    context = {
        'order_entries': orderentries,
        'loggedin': 1,
        'name': request.user.first_name,
    }

    if request.user.is_superuser:
        context['loggedin']=2;
    return render(request,'login/orders.html',context)

def contactus(request):
    context = {'loggedin':0}
    if request.user.is_authenticated():
        context = {
            'loggedin': 1,
            'name': request.user.first_name,
        }
        if request.user.is_superuser:
            context['loggedin']=2
    return render(request, 'login/contactus.html',context)

@login_required(login_url = 'login:signin')
def cart(request):
    print('cart')
    db = MySQLdb.connect('localhost','rahulp','password1234','avadhootent')
    cursor = db.cursor()
    cursor.execute("select cart.item_id,cart.quantity,product.price from cart inner join product on cart.item_id = product.id where cart.cust_id = '" + str(request.user.id) + "';")
    class cartobject:
        def __init__(self,item_id,name,description,quantity,cost_item,cust_id):
            self.item_id = item_id
            self.name = name
            self.description = description
            self.quantity = quantity
            self.cost_item = cost_item
            self.cust_id = cust_id

    cart_items = []
    entries=[]
    for item in cursor:
        entries.append(item)

    final_price = 0
    for item in entries:
        cursor.execute("select name,description from product where id = "+str(item[0]) + ";")
        namedesc = cursor.fetchone()
        cart_items.append(cartobject(item[0],namedesc[0],namedesc[1],item[1],item[2],request.user.id))
        final_price += float(item[1])*float(item[2])

    context = {
        'order_total':final_price,
        'cart_items':cart_items,
        'loggedin': 1,
        'name': request.user.first_name,
    }
    if request.user.is_superuser:
        context['loggedin'] = 2
    return render(request, 'login/cart.html',context)

def removecartitem(request,itemid,custid):
    print('removecartitem')
    db = MySQLdb.connect('localhost','rahulp','password1234','avadhootent')
    cursor = db.cursor()
    cursor.execute("select quantity from cart where cust_id = "+str(custid) + " and item_id = "+ str(itemid) + ";")
    quantity = cursor.fetchone()
    quantity = int(quantity[0])
    cursor.execute("delete from cart where cust_id = "+str(custid) + " and item_id = "+ str(itemid) + ";")
    cursor.execute("update product set quantity = quantity + "+ str(quantity) + ";")
    db.commit()
    db.close()
    return redirect('login:cart')

def sendmail(request):
    context = {'loggedin':0}
    if request.user.is_authenticated():
        context = {
            'loggedin': 1,
            'name': request.user.first_name,
        }
        if request.user.is_superuser:
            context['loggedin']=2
    try:
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

    except (KeyError):
        context['error_meassage']='Error Occurred.'
        return render(request,'login/contactus.html',context)
    else:
        return render(request, 'login/contactus.html', context)

def signup(request):
    context = {'loggedin':0}
    if request.user.is_authenticated():
        context = {
            'loggedin': 1,
            'name': request.user.first_name,
        }
        if request.user.is_superuser:
            context['loggedin']=2
    template = loader.get_template('login/signup.html')
    return HttpResponse(template.render({}, request,context))

class UserFormView(View):
    form_class = UserForm
    template_name = 'login/signup.html'
    def get(self,request):
        form = self.form_class(None)
        context = {'loggedin':0}
        if request.user.is_authenticated():
            context = {
                'loggedin': 1,
                'name': request.user.first_name,
            }
            if request.user.is_superuser:
                context['loggedin'] = 2
        context['form']=form
        return render(request,self.template_name, context)

    def post(self,request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user.set_password(password)
            user.save()

            address = request.POST.get('address')
            city = request.POST.get('city')
            state = request.POST.get('state')
            pin = request.POST.get('pin')
            phone = request.POST.get('phone')
            db = MySQLdb.connect('localhost','rahulp','password1234','avadhootent')
            cursor = db.cursor()
            cursor.execute("select id from auth_user where username = '"+ username + "';")

            userid = cursor.fetchone()
            userid = int(userid[0])
            cursor.execute(
                "insert ignore into user_address values (" + str(pin) + ",'" + str(city) + "','" + str(state) + "')")
            cursor.execute("insert into users values(" + str(userid) + ",'" + str(address)+ "',"+str(pin)+",'"+str(phone)+"');")

            db.commit()
            db.close()

            user = authenticate(username = username, password = password)
            if user is not None:

                if user.is_active:
                    login(request, user)
                    return redirect('login:index')
        context = {'loggedin': 0,}
        if request.user.is_authenticated():
            context = {
                'loggedin': 1,
                'name': request.user.first_name,
            }
            if request.user.is_superuser:
                context['loggedin'] = 2
        context['form']=form
        return render(request, self.template_name, context)

def logout(request):
    context = {'loggedin': 0, }
    if request.user.is_authenticated():
        auth.logout(request)
        messages.success(request, 'Successfully logged out.')
    return render(request,'login/index.html',context)

def placeorder(request):
    db = MySQLdb.connect('localhost','rahulp','password1234','avadhootent')
    cursor = db.cursor()
    id = request.user.id
    now = datetime.datetime.now()
    today = now.strftime("%d/%m/%y")
    cursor.execute("select cart.quantity,product.price from cart inner join product on cart.item_id = product.id where cart.cust_id = "+str(id)+";")
    pricecalculate = cursor.fetchall()
    order_total = 0.0
    for item in pricecalculate:
        order_total += item[0]*item[1]
    cursor.execute("insert into payment (status,details) values (0,'');")
    cursor.execute("insert into orders (cust_id,order_date,total_cost,payment_id,delivery_status) values ("+str(id)+",CURDATE(),"+str(order_total)+",LAST_INSERT_ID(),0);")
    cursor.execute("select order_id from orders where cust_id = "+str(id)+";")
    order_id = cursor.fetchall()
    order_id = int(order_id[-1][0])
    cursor.execute("select cart.item_id,cart.quantity,product.price from cart inner join product on cart.item_id = product.id where cart.cust_id = "+str(id)+" ;")
    cart_items = cursor.fetchall()
    for item in cart_items:
        cursor.execute("insert into order_items values ("+str(order_id)+","+str(item[0])+","+str(item[1])+","+str(item[2])+");")
        cursor.execute("delete from cart where cust_id = "+str(id)+" and item_id = "+str(item[0])+";")
    db.commit()
    db.close()
    return redirect('login:orders')

def redirecttopay(request,orderid):
    context = {'loggedin': 0}
    if request.user.is_authenticated():
        context = {
            'loggedin': 1,
            'name': request.user.first_name,
        }
        if request.user.is_superuser:
            context['loggedin']=2
    return render(request, 'login/redirecttopay.html', context)

def cancelorder(request,orderid):
    db = MySQLdb.connect('localhost','rahulp','password1234','avadhootent')
    cursor = db.cursor()
    cursor.execute("select item_id,item_quantity from order_items where order_id = "+str(orderid)+";")
    torestore = cursor.fetchall()
    for item in torestore:
        cursor.execute("update product set quantity = quantity + " + str(item[1]) + " where id = "+ str(item[0])+ ";");
    cursor.execute("delete from order_items where order_id = "+str(orderid)+";")
    cursor.execute("delete from orders where order_id = "+str(orderid)+";")
    db.commit()
    db.close()
    return redirect('login:orders')

def admin_user_details(request):
    context = {
        'loggedin':2,
        'name': request.user.first_name,
    }
    class user_details:
        def __init__(self,id,username,first_name,last_name,address,city,state,phone):
            self.id = id
            self.username = username
            self.first_name = first_name
            self.last_name = last_name
            self.address = address
            self.city = city
            self.state = state
            self.phone = phone

    db = MySQLdb.connect('localhost','rahulp','password1234','avadhootent')
    cursor = db.cursor()
    cursor.execute("select users.userid,auth_user.username,auth_user.first_name,auth_user.last_name,users.address,users.pincode,users.phone from users inner join auth_user on users.userid = auth_user.id;")
    uservalues = cursor.fetchall()
    entries = []
    for item in uservalues:
        cursor.execute("select city,state from user_address where pin = "+str(item[5])+";")
        citystate = cursor.fetchone()
        entries.append(user_details(item[0],item[1],item[2],item[3],item[4],citystate[0],citystate[1],item[6]))
    db.close()
    context['details'] = entries
    return render(request,'login/admin_user_details.html',context)

def view_user_orders(request,orderid):
    class orderdisplay:
        def __init__(self,order_id, order_date, total_cost, payment_status, delivery_status):
            self.order_id = order_id
            self.order_date = order_date
            self.total_cost = total_cost
            self.payment_status = payment_status
            self.delivery_status = delivery_status

    id = orderid
    db = MySQLdb.connect('localhost','rahulp','password1234','avadhootent')
    cursor = db.cursor()
    cursor.execute("select * from orders where cust_id = "+str(id)+";")
    entries = cursor.fetchall()
    orderentries = []
    for item in entries:
        nowdate = item[2].strftime("%Y-%m-%d")
        cursor.execute("select status from payment where payment_id = "+str(item[5])+";")
        status = cursor.fetchone()
        status = int(status[0])
        orderentries.append(orderdisplay(item[0],nowdate,item[3],status,item[4]))

    context = {
        'order_entries': orderentries,
        'loggedin': 2,
        'name': request.user.first_name,
    }
    db.close()
    return render(request,'login/adminorders.html',context)

def admin_orders(request):
    class order_display:
        def __init__(self,orderid,customername,productnames,orderdate,cost,deliverystatus,paymentstatus,paymentdetails):
            self.orderid = orderid
            self.customername = customername
            self.productnames = productnames
            self.orderdate = orderdate
            self.cost = cost
            self.deliverystatus = deliverystatus
            self.paymentstatus = paymentstatus
            self.paymentdetails = paymentdetails

    db = MySQLdb.connect('localhost','rahulp','password1234','avadhootent')
    cursor = db.cursor()
    cursor.execute("select orders.order_id,auth_user.first_name,auth_user.last_name,orders.order_date,orders.total_cost,orders.delivery_status,orders.payment_id  from orders inner join auth_user on orders.cust_id = auth_user.id;")
    entries = cursor.fetchall()
    details = []
    for item in entries:
        cursor.execute("select status,details from payment where payment_id = "+str(item[-1])+";")
        paymentstat = cursor.fetchone()
        cursor.execute("select order_items.item_quantity, product.name from order_items inner join product on order_items.item_id = product.id  where order_items.order_id = "+str(item[0])+";")
        productsget = cursor.fetchall()
        listofproducts = ""
        for element in productsget:
            listofproducts+= str(element[1])+": "+str(element[0])+",\n"
        details.append(order_display(item[0],str(item[1])+" "+str(item[2]),listofproducts,item[3],item[4],item[5],paymentstat[0],paymentstat[1]))
    db.close()
    context={
        'loggedin':2,
        'name': request.user.first_name,
        'details': details,
    }
    return render(request,'login/admin_orders.html',context)

def admin_employee(request):
    class adminemployee:
        def __init__(self,id,name,address,city,state,pincode,sex,phone,salary,dateofjoin):
            self.id = id
            self.name = name
            self.address = address
            self.city = city
            self.state = state
            self.pincode = pincode
            self.sex = sex
            self.phone = phone
            self.salary = salary
            self.dateofjoin = dateofjoin

    db = MySQLdb.connect('localhost', 'rahulp', 'password1234', 'avadhootent')
    cursor = db.cursor()
    cursor.execute("select employee.id, employee.first_name, employee.last_name, employee.address,user_address.city,user_address.state,employee.pincode, employee.sex, employee.phone, employee.salary, employee.date_of_join from employee inner join user_address on employee.pincode = user_address.pin order by employee.first_name ;")
    entries = cursor.fetchall()
    people = []
    for item in entries:
        people.append(adminemployee(item[0],str(item[1])+" "+str(item[2]),item[3],item[4],item[5],item[6],item[7],item[8],item[9],item[10]))
    context = {
        'loggedin':2,
        'name': request.user.first_name,
        'details':people,
    }
    db.close()
    return render(request,'login/employees.html',context)

def addemployee(request):
    context = {
        'loggedin': 2,
        'name': request.user.first_name,
    }
    return render(request,'login/addemployee.html',context)

def insertemployee(request):
    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    address = request.POST.get('address')
    city = request.POST.get('city')
    state = request.POST.get('state')
    pincode = request.POST.get('pin')
    phone = request.POST.get('phone')
    sex = request.POST.get('sex')
    salary = request.POST.get('salary')
    dateofjoin = request.POST.get('dateofjoin')
    print(dateofjoin)
    print(type(dateofjoin))
    db = MySQLdb.connect('localhost', 'rahulp', 'password1234', 'avadhootent')
    cursor = db.cursor()
    cursor.execute(
        "insert ignore into user_address values (" + str(pincode) + ",'" + str(city) + "','" + str(state) + "');")
    cursor.execute(
        "insert into employee (first_name,last_name,address,pincode,sex,phone,salary,date_of_join) values ('" + str(first_name) + "','" + str(last_name) + "','" + str(address) + "'," + str(pincode) + ",'" + str(sex) + "','" + str(phone) + "'," + str(salary) + ",'" + str(dateofjoin) + "');")

    db.commit()
    db.close()
    return redirect('login:admin_employee')

def removeemployee(request,emplid):
    db = MySQLdb.connect('localhost', 'rahulp', 'password1234', 'avadhootent')
    cursor = db.cursor()
    cursor.execute("delete from employee where id = "+str(emplid)+";")
    db.commit()
    db.close()
    return redirect('login:admin_employee')

def admin_products(request):
    class product_display:
        def __init__(self,id,name,quantity,description,price):
            self.id = id
            self.name = name
            self.quantity = quantity
            self.description = description
            self.price = price

    db = MySQLdb.connect('localhost','rahulp','password1234','avadhootent')
    cursor = db.cursor()
    cursor.execute("select * from product order by name;")
    entries = cursor.fetchall()
    details = []
    for item in entries:
        details.append(product_display(item[0],item[1],item[2],item[3],item[4]))
    db.close()
    context = {
        'loggedin':2,
        'name': request.user.first_name,
        'details': details,
    }
    return render(request,'login/admin_products.html',context)

def viewstockproduct(request,prodid):
    class stockview:
        def __init__(self,supplierid,suppliername,quantity,dateofsupply,comments):
            self.supplierid = supplierid
            self.suppliername = suppliername
            self.quantity = quantity
            self.dateofsupply = dateofsupply
            self.comments = comments

    db = MySQLdb.connect('localhost','rahulp','password1234','avadhootent')
    cursor = db.cursor()
    cursor.execute("select stock.supplier_id,supplier.first_name,supplier.last_name,stock.quantity,stock.date_of_supply,stock.comments from stock inner join supplier on stock.supplier_id = supplier.id where stock.prod_id = "+str(prodid)+";")
    entries = cursor.fetchall()
    details = []
    for item in entries:
        details.append(stockview(item[0],str(item[1])+" "+str(item[2]),item[3],item[4],item[5]))
    db.close()
    context = {
        'loggedin':2,
        'name': request.user.first_name,
        'details': details,
    }
    return render(request,'login/view_stocks_product.html',context)

def admin_supplier(request):
    class supplierpeople:
        def __init__(self, id, name, address,city,state,pincode,phone):
            self.id = id
            self.name = name
            self.address = address
            self.city = city
            self.state = state
            self.pincode = pincode
            self.phone = phone

    db = MySQLdb.connect('localhost', 'rahulp', 'password1234', 'avadhootent')
    cursor = db.cursor()
    cursor.execute(
        "select supplier.id,supplier.first_name,supplier.last_name,supplier.address,user_address.city,user_address.state,supplier.pincode,supplier.phone from supplier inner join user_address on supplier.pincode = user_address.pin;")
    entries = cursor.fetchall()
    details = []
    for item in entries:
        details.append(supplierpeople(item[0], str(item[1]) + " " + str(item[2]), item[3], item[4], item[5],item[6],item[7]))
    db.close()
    context = {
        'loggedin': 2,
        'name': request.user.first_name,
        'details': details,
    }
    return render(request, 'login/viewsuppliers.html', context)

def viewstocksupplier(request,suppid):
    class stockview:
        def __init__(self,id,name,price,quantity,dateofsupply,comments):
            self.id = id
            self.name = name
            self.price = price
            self.quantity = quantity
            self.dateofsupply = dateofsupply
            self.comments = comments

    db = MySQLdb.connect('localhost','rahulp','password1234','avadhootent')
    cursor = db.cursor()
    cursor.execute("select stock.prod_id,product.name,product.price,stock.quantity,stock.date_of_supply,stock.comments from stock inner join product on stock.prod_id = product.id where stock.supplier_id = "+str(suppid)+";")
    entries = cursor.fetchall()
    details = []
    for item in entries:
        details.append(stockview(item[0],(item[1]), (item[2]),item[3],item[4],item[5]))
    db.close()
    context = {
        'loggedin':2,
        'name': request.user.first_name,
        'details': details,
    }
    return render(request,'login/view_stocks_supplier.html',context)

def addsupplier(request):
    context = {
        'loggedin': 2,
        'name': request.user.first_name,
    }
    return render(request, 'login/addsupplier.html', context)

def insertsupplier(request):
    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    address = request.POST.get('address')
    city = request.POST.get('city')
    state = request.POST.get('state')
    pincode = request.POST.get('pin')
    phone = request.POST.get('phone')

    db = MySQLdb.connect('localhost','rahulp','password1234','avadhootent')
    cursor = db.cursor()
    cursor.execute(
        "insert ignore into user_address values (" + str(pincode) + ",'" + str(city) + "','" + str(state) + "');")
    cursor.execute("insert into supplier (first_name,last_name,address,pincode,phone) values ('"+str(first_name)+"','"+str(last_name)+"','"+str(address)+"',"+str(pincode)+",'"+str(phone) + "');")

    db.commit()
    db.close()
    return redirect('login:admin_supplier')

def admin_stock(request):
    class stockvalues:
        def __init__(self, supplier_id, supplier_name, product_name,  quantity, dateofsupply, comment):
            self.supplier_id = supplier_id
            self.supplier_name = supplier_name
            self.product_name = product_name
            self.quantity = quantity
            self.dateofsupply = dateofsupply
            self.comment = comment

    db = MySQLdb.connect('localhost', 'rahulp', 'password1234', 'avadhootent')
    cursor = db.cursor()
    cursor.execute("select supplier.id,supplier.first_name,supplier.last_name,stock.prod_id, stock.quantity,stock.date_of_supply,stock.comments from stock inner join supplier on stock.supplier_id = supplier.id;")
    entries = cursor.fetchall()
    details = []
    for item in entries:
        cursor.execute("select product.name from product where id = "+str(item[3])+";")
        prodname = cursor.fetchone()
        prodname = prodname[0]
        details.append(stockvalues(item[0], str(item[1]) + " " + str(item[2]), prodname, item[4], item[5], item[6]))
    db.close()
    context = {
        'loggedin': 2,
        'name': request.user.first_name,
        'details': details,
    }
    return render(request, 'login/admin_stock.html', context)

def addstock(request):
    class supplierform:
        def __init__(self, id, name):
            self.id = id
            self.name = name

    class productform:
        def __init__(self, id, name):
            self.id = id
            self.name = name

    db = MySQLdb.connect('localhost', 'rahulp', 'password1234', 'avadhootent')
    cursor = db.cursor()
    cursor.execute("select id,first_name,last_name from supplier;")
    suppliers = cursor.fetchall()
    cursor.execute("select id,name from product;")
    products = cursor.fetchall()
    supplier = []
    product = []
    for item in suppliers:
        supplier.append(supplierform(item[0],str(item[1])+" "+str(item[2])))
    for item in products:
        product.append(productform(item[0],item[1]))
    context = {
        'product':product,
        'suppliers':supplier,
        'loggedin': 2,
        'name': request.user.first_name,
    }

    return render(request, 'login/addstock.html', context)

def insertstock(request):
    supplierid = request.POST.get('supplier')
    productoption = request.POST.get('optradio')
    quantity = request.POST.get('quantity')
    comments = request.POST.get('comment')

    db = MySQLdb.connect('localhost', 'rahulp', 'password1234', 'avadhootent')
    cursor = db.cursor()

    if productoption == "old":
        productchosen = request.POST.get('product')
        print(supplierid)
        print(productoption)
        print(quantity)
        print(comments)
        print(productchosen)
        cursor.execute("insert into stock values ("+ str(productchosen) +","+str(supplierid)+","+str(quantity)+",CURDATE(),'"+str(comments)+"');")
        cursor.execute("update product set quantity = quantity + "+str(quantity)+" where id = "+str(productchosen)+";")
    elif productoption == "new":
        print(supplierid)
        name = request.POST.get('name')
        price = request.POST.get('price')
        description = request.POST.get('description')
        cursor.execute("insert into product (name,quantity,description,price) values ('"+str(name)+"',"+str(quantity)+",'"+str(description)+"',"+str(price)+");")
        cursor.execute("select LAST_INSERT_ID();")
        id = cursor.fetchone()
        id = int(id[0])
        cursor.execute("insert into stock values (" + str(id)+","+str(supplierid)+","+str(quantity)+",CURDATE(),'"+str(comments) +"');")
    db.commit()
    db.close()
    return redirect('login:admin_stock')

def feedback(request):
    name = request.POST.get('name')
    email = request.POST.get('email')
    subject = request.POST.get('subject')
    message = request.POST.get('message')

    db = MySQLdb.connect('localhost','rahulp','password1234','avadhootent')
    cursor = db.cursor()
    cursor.execute("insert into feedback (name,email,subject,message) values ('"+str(name)+"','"+str(email)+"','"+str(subject)+"','"+str(message)+"');")
    db.commit()
    db.close()
    return redirect('login:index')

def viewfeedback(request):
    

    db = MySQLdb.connect('localhost', 'rahulp', 'password1234', 'avadhootent')
    cursor = db.cursor()
    cursor.execute(
        "insert into feedback (name,email,subject,message) values ('" + str(name) + "','" + str(email) + "','" + str(
            subject) + "','" + str(message) + "');")
    db.commit()
    db.close()
    return redirect('login:index')