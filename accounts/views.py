from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group

from .models import *
from .forms import OrderForm, CreateUserForm
from .filters import OrderFilter
from .decorators import unauthenticated_user, allowed_users, admin_only

# Create your views here.

@unauthenticated_user
def registerPage(request):
    # form = UserCreationForm()
    form = CreateUserForm()
    if request.method == 'POST':
        # form = UserCreationForm(request.POST)
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            group = Group.objects.get(name='customer')
            user.groups.add(group)
            messages.success(request, 'Account was created for ' + username)
            return redirect('login')
        else :
            # print('------------this form is not saved------------')
            # print(form)
            pass
    else:
        # print('-----------GET method--------------')
        pass
    context = {'form' : form}
    return render(request, 'accounts/register.html', context)

@unauthenticated_user
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # print('-------------',username,'-------------')
        # print('-------------',password,'-------------')
        user = authenticate(request, username=username, password=password)
        if user is not None :
            login(request, user)
            return redirect('home')
        else :
            messages.info(request, 'Username or Password is incorrect')
    context = {}
    return render(request, 'accounts/login.html', context)

def logoutUser(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
@admin_only
def home(request):
    orders = Order.objects.all()
    customers = Customers.objects.all()
    total_customers = customers.count()
    total_orders = orders.count()
    delivered = orders.filter(status="Delivered").count()
    pending = orders.filter(status="Pending").count()
    context = {
        'orders' : orders, 
        'customers' : customers, 
        'total_customers' : total_customers,
        'total_orders' : total_orders,
        'pending' : pending,
        'delivered' : delivered,
        }
    return render(request, 'accounts/dashboard.html', context)

def userPage(request):
    context = {}
    return render(request, 'accounts/user.html', context)

def contact(request):
    return render(request, 'accounts/about.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def products(request):
    products = Product.objects.all()
    return render(request, 'accounts/products.html', {'products':products})

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def customers(request, pk_test):
    customer = Customers.objects.get(id=pk_test)
    orders = customer.order_set.all()
    total_orders = orders.count()

    myFilter = OrderFilter(request.GET, queryset=orders)
    orders = myFilter.qs

    context = {
        'customer' : customer,
        'orders' : orders,
        'total_orders' : total_orders,
        'myFilter' : myFilter,
        }
    return render(request, 'accounts/customers.html',  context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def createOrder(request, pk):
    OrderFormSet = inlineformset_factory(Customers, Order, fields=('product', 'status'), extra=3)
    customer = Customers.objects.get(id=pk)
    formset = OrderFormSet(queryset=Order.objects.none(), instance=customer)
    # form  = OrderForm(initial={'customer':customer})

    if request.method == 'POST':
        # print('POST data : {}'.format(request.POST))
        # form = OrderForm(request.POST)
        formset = OrderFormSet(request.POST, instance=customer)
        if formset.is_valid():
            formset.save()
            return redirect('/')

    context = {'formset' : formset}
    return render(request, 'accounts/order_form.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def updateOrder(request, pk):
    order = Order.objects.get(id=pk)
    form = OrderForm(instance=order)

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('/')

    context = {'form' : form}
    return render(request, 'accounts/order_form.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def deleteOrder(request, pk):
    order = Order.objects.get(id=pk)
    if request.method == 'POST' :
        order.delete()
        return redirect('/')
    context = {'item' : order}
    return render(request, 'accounts/delete_order.html', context)
    