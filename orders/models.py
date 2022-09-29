from django.contrib import admin
from django.db import models
from accounts.models import Account
from store.models import Product, Variation


class Payment(models.Model):
    objects = models.Manager()

    user = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name='Пользователь')
    payment_id = models.CharField(max_length=100, verbose_name='ID платежа')
    payment_method = models.CharField(max_length=100, verbose_name='Метод оплаты')
    amount_paid = models.CharField(max_length=100, verbose_name='Сумма оплаты')
    status = models.CharField(max_length=100, verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    def __str__(self):
        return self.payment_id

    class Meta:
        verbose_name = 'Оплату'
        verbose_name_plural = 'Оплаты'


class Order(models.Model):
    STATUS = (
        ('New', 'New'),
        ('Accepted', 'Accepted'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )
    objects = models.Manager()

    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, verbose_name='Пользователь')
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Платеж')
    order_number = models.CharField(max_length=20, verbose_name='Номер заказа')
    first_name = models.CharField(max_length=50, verbose_name='Имя')
    last_name = models.CharField(max_length=50, verbose_name='Фамилия')
    phone = models.CharField(max_length=15, verbose_name='Телефон')
    email = models.EmailField(max_length=50, verbose_name='Электронный адрес')
    address_line_1 = models.CharField(max_length=50, verbose_name='Адрес 1')
    address_line_2 = models.CharField(max_length=50, blank=True, verbose_name='Адрес 2')
    country = models.CharField(max_length=50, verbose_name='Страна')
    region = models.CharField(max_length=50, verbose_name='Регион')
    city = models.CharField(max_length=50, verbose_name='Город')
    order_note = models.CharField(max_length=100, blank=True, verbose_name='Примечание к заказу')
    order_total = models.FloatField(verbose_name='Сумма заказа')
    discount = models.FloatField(verbose_name='Скидка')
    status = models.CharField(max_length=10, choices=STATUS, default='New', verbose_name='Статус')
    ip = models.CharField(blank=True, max_length=20, verbose_name='IP адрес')
    is_ordered = models.BooleanField(default=False, verbose_name='Заказан')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    @admin.display(description='Фамилия Имя')
    def full_name(self):
        return f'{self.last_name} {self.first_name}'

    def full_address(self):
        return f'{self.address_line_1}; {self.address_line_2}'

    def __str__(self):
        return self.first_name

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


class OrderProduct(models.Model):
    objects = models.Manager()

    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='Заказ')
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Платеж')
    user = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name='Пользователь')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    variations = models.ManyToManyField(Variation, blank=True, verbose_name='Вариации')
    quantity = models.IntegerField(verbose_name='Количество')
    product_price = models.FloatField(verbose_name='Цена товара')
    is_ordered = models.BooleanField(default=False, verbose_name='Заказан')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    def __str__(self):
        return self.product.product_name

    class Meta:
        verbose_name = 'Товар в заказе'
        verbose_name_plural = 'Товары в заказе'
