from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Order, OrderPhoto, OrderDocument
from django.contrib.auth.admin import UserAdmin 
from django.contrib.auth.models import User

class CustomUserAdmin(UserAdmin):
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None,{
            'classes':('wide',),
            'fields': ('first_name', 'last_name', 'email')
        }),
    )

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


class OrderPhotoInline(admin.TabularInline):
    model = OrderPhoto
    extra = 1
    readonly_fields = ['preview']

    def preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="100" style="border-radius: 10px;" />')
        return "Немає фото"
    preview.short_description = "Прев'ю"

class OrderDocumentInline(admin.TabularInline):
    model = OrderDocument
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Что отображать в списке всех заказов
    list_display = ['id', 'user','full_name', 'phone', 'city', 'status', 'created_at']
    
    # Что можно нажать, чтобы перейти в заказ
    list_display_links = ['id', 'full_name']
    
    # Фильтры справа
    list_filter = ['status', 'created_at', 'region', 'comm_channel']
    
    # Поиск по полям
    search_fields = ['full_name', 'phone', 'city', 'address']
    
    # Группировка полей при редактировании
    fieldsets = (
        ("Основна інформація", {
            'fields': (('full_name', 'status'), ('phone', 'comm_channel'), 'socials', )
        }),

        ("Призначения", {
            'fields':('investor',)
        }

        ),
        ("Локація", {
            'fields': (('region', 'city'), 'address', ('latitude', 'longitude'))
        }),
        ("Службова інформація", {
            'fields': ('user', 'created_at'),
            'classes': ('collapse',) # Свернуть по умолчанию
        }),
    )
    
    readonly_fields = ['created_at']
    
    # Добавляем инлайны (фото и доки) вниз страницы
    inlines = [OrderPhotoInline, OrderDocumentInline]

    # Автоматическое назначение текущего пользователя при сохранении через админку
    def save_model(self, request, obj, form, change):
        if not obj.user_id:
            obj.user = request.user
        super().save_model(request, obj, form, change)