from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Order, OrderPhoto, OrderDocument
from django.contrib.auth.models import User, Group

@login_required
def index(request):
    user = request.user

    if user.groups.filter(name='Investors').exists():
        orders = Order.objects.filter(investor=user).order_by('-created_at')
        return redirect('order_list')
    elif user.groups.filter(name="Broker").exists():
        orders = Order.objects.filter(investor=user).order_by('-created_at')
        return redirect('broker_menu')

    if request.method == 'POST':

        full_name = request.POST.get('client_name')
        phone = request.POST.get('phone')
        comm_channel = request.POST.get('communication')
        

        socials_list = request.POST.getlist('socials')
        socials_str = ", ".join(filter(None, socials_list)) # Склеиваем в строку через запятую

        region = request.POST.get('region')
        city = request.POST.get('city')
        address = request.POST.get('address')
        
 
        lat = request.POST.get('latitude')
        lng = request.POST.get('longitude')

        if full_name and phone:
            # 2. Создаем сам заказ
            order = Order.objects.create(
                full_name=full_name,
                phone=phone,
                comm_channel=comm_channel,
                socials=socials_str,
                region=region,
                city=city,
                address=address,
                latitude=float(lat) if lat else None,
                longitude=float(lng) if lng else None,
                user=request.user, 
                status="new"
            )


            photos = request.FILES.getlist('photos')
            for f in photos:
                OrderPhoto.objects.create(order=order, image=f)

            documents = request.FILES.getlist('documents')
            for d in documents:
                OrderDocument.objects.create(order=order, file=d)

            return redirect('index')

    all_orders = Order.objects.all().order_by("-created_at")

    context = {
        'new_orders': all_orders.filter(status="new"),
        'processing_orders': all_orders.filter(status="process"),
        'new_count': all_orders.filter(status="new").count(),
        'proc_count': all_orders.filter(status="process").count(),
    }
    
    return render(request, 'index.html', context)

def order_view(request,pk):
    order = get_object_or_404(Order, pk=pk)
    user = request.user

    if user.groups.filter(name='Investors').exists():
        return render(request, 'order_view_investor.html', {'order':order})
    return render(request, 'order_view.html', {'order':order})

def order_edit(request,pk):
    order = get_object_or_404(Order, pk=pk)
 
    if request.method == "POST": 
        order.full_name = request.POST.get("client_name")
        order.status = request.POST.get("status")
        order.phone = request.POST.get("phone")
        order.region = request.POST.get("region")
        order.city = request.POST.get("city")
        order.comm_channel = request.POST.get("communication")
        order.address = request.POST.get("address")
        
        order.lat = request.POST.get("latitude")
        order.lng = request.POST.get("longitude")
        if request.FILES.get('photo'):
            order.photos = request.FILES.get("photos")
        if request.FILES.get('document'):
            order.document = request.FILES.get("document")

        order.save()

        investor_ids = request.POST.getlist('investors')
        order.investor.set(investor_ids)

        return redirect('order_view', pk=order.pk)

    all_investors = User.objects.filter(groups__name = 'Investors')

    return render(request, 'order_edit.html',{'order':order,'all_investors': all_investors})


def login_view(request):
    if request.method == 'POST':
        user_inp = request.POST.get('username')
        pass_inp = request.POST.get('password')
        
        user = authenticate(request, username=user_inp, password=pass_inp)
        
        if user is not None:
            auth_login(request, user)
            return redirect('index')
        else:
            messages.error(request, "Невірний логін або пароль!")
            
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def create_order(request):
    if request.method == 'POST':
        # 1. Получаем основные данные
        full_name = request.POST.get('client_name')
        phone = request.POST.get('phone')
        comm_channel = request.POST.get('communication')
        
        # Соцсети прилетают списком из динамических полей (name="socials")
        socials_list = request.POST.getlist('socials')
        socials_str = ", ".join(filter(None, socials_list)) # Склеиваем в строку через запятую

        region = request.POST.get('region')
        city = request.POST.get('city')
        address = request.POST.get('address')
        
        # Координаты (могут быть пустыми, если не ткнули на карту)
        lat = request.POST.get('latitude')
        lng = request.POST.get('longitude')

        if full_name and phone:
            # 2. Создаем сам заказ
            order = Order.objects.create(
                full_name=full_name,
                phone=phone,
                comm_channel=comm_channel,
                socials=socials_str,
                region=region,
                city=city,
                address=address,
                latitude=float(lat) if lat else None,
                longitude=float(lng) if lng else None,
                user=request.user, 
                status="new"
            )

            # 3. Сохраняем фото (их может быть несколько)
            photos = request.FILES.getlist('photos')
            for f in photos:
                OrderPhoto.objects.create(order=order, image=f)

            # 4. Сохраняем документы (их может быть несколько)
            documents = request.FILES.getlist('documents')
            for d in documents:
                OrderDocument.objects.create(order=order, file=d)

            return redirect('index')

    return render(request, 'create_order.html')

def archive(request):
    # Получаем выполненные и отклоненные заявки
    successful_orders = Order.objects.filter(status='success')
    failed_orders = Order.objects.filter(status='cancel')

    return render(request, 'archive.html', {
        'successful_orders': successful_orders,
        'failed_orders': failed_orders
    })

def profile_view(request):
    # Поки що просто відображаємо сторінку з даними поточного користувача
    return render(request, 'profile.html', {
        'user': request.user
    })

def edit_profile(request):
    if request.method == 'POST':
        # Получаем данные из формы
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        
        # Для телефона и соцсетей в идеале нужна модель Profile, 
        # но пока сохраним почту и имена, чтобы заработал базовый функционал
        user.save()
        
        messages.success(request, 'Профіль оновлено!')
        return redirect('profile')
        
    return render(request, 'edit_profile.html')

def profile_view(request):
    return render(request, 'profile.html')

def edit_profile(request):
    if request.method == 'POST':
        # Отримуємо координати з форми
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        
        if latitude and longitude:
            print(f"Координати отримано: Lat {latitude}, Lng {longitude}")
            # Тут ти можеш зберегти їх у базу даних до користувача
        
        return redirect('profile')
    
    return render(request, 'edit_profile.html')

def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'order_detali.html', {'order': order})

@login_required
def order_list(request):
    user = request.user

    if user.groups.filter(name="Investors").exists():
        orders = Order.objects.filter(investor=user).order_by('-created_at')
    elif user.is_staff:
        return redirect('index')
    else:
        return redirect('login')
    
    return render(request,'order_list.html',{'order':orders})


@login_required
def broker_menu(request):
    user = request.user

    if user.groups.filter(name="Broker").exists():
        orders = Order.objects.filter(user=user).order_by('-created_at')
    elif user.is_staff:
        return redirect('index')
    else:
        return redirect('login')
    
    return render(request,'broker_menu.html',{'order':orders})