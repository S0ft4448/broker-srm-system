from django.urls import path 
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('new/', views.create_order, name='create_order'),
    path('archive/', views.archive, name='archive'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('order/<int:pk>',views.order_view, name ='order_view'),
    path('order_edit/<int:pk>',views.order_edit, name ='order_edit'),
    path('order_list',views.order_list, name ='order_list'),
    path('broker_menu',views.broker_menu, name='broker_menu')
    ]