from django.db import models
from django.contrib.auth.models import User

class Order(models.Model):
    # Статусы (для красоты в админке и фильтрации)
    STATUS_CHOICES = [
        ('new', 'Нова'),
        ('process', 'В роботі'),
        ('success', 'Виконана'),
        ('cancel', 'Скасована'),
    ]

    COMM_CHOICES = [
        ('phone', 'Дзвінок'),
        ('tg', 'Telegram'),
        ('viber', 'Viber'),
        ('whatsapp', 'WhatsApp'),
    ]

    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Сума")
    context = models.TextField(blank=True, null=True, verbose_name="Контекст")

    # Основная информация
    full_name = models.CharField(max_length=255, verbose_name="ПІБ Клієнта")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    comm_channel = models.CharField(max_length=20, choices=COMM_CHOICES, default='phone', verbose_name="Канал зв'язку")
  
    socials = models.TextField(blank=True, null=True, verbose_name="Соцмережі")

    region = models.CharField(max_length=100, blank=True, null=True, verbose_name="Область")
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="Місто")
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Адреса")
    
    latitude = models.FloatField(blank=True, null=True, verbose_name="Широта")
    longitude = models.FloatField(blank=True, null=True, verbose_name="Довгота")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Менеджер")
    investor = models.ManyToManyField(User, blank=True,
                                 related_name="assigned_orders",
                                 verbose_name="Призначеный инвестор",
                                 limit_choices_to={'groups__name':'Investors'}
                                 )
    def __str__(self):
        return f"Замовлення #{self.id} - {self.full_name}"

    class Meta:
        verbose_name = "Замовлення"
        verbose_name_plural = "Замовлення"

# Модель для множественных фото
class OrderPhoto(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='all_photos')
    image = models.ImageField(upload_to='images/')

# Модель для множественных документов
class OrderDocument(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='all_documents')
    file = models.FileField(upload_to='docs/')