from django.db import models
from accounts.models import Account
from store.models import Product, Variation


class Cart(models.Model):
    objects = models.Manager()
    cart_id = models.CharField(max_length=250, blank=True, verbose_name='ID корзины')
    date_added = models.DateField(auto_now_add=True, verbose_name='Дата добавления')

    def __str__(self):
        return self.cart_id

    class Meta:
        verbose_name = 'Корзину'
        verbose_name_plural = 'Корзины'


class CartItem(models.Model):
    objects = models.Manager()
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, verbose_name='Пользователь')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    variations = models.ManyToManyField(Variation, blank=True, verbose_name='Вариации')
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True, verbose_name='Корзина')
    quantity = models.IntegerField(verbose_name='Количество')
    is_active = models.BooleanField(default=True, verbose_name='Активно')

    def sub_total(self):
        return self.product.price * self.quantity

    def __unicode__(self):
        return self.product

    class Meta:
        verbose_name = 'Товар в корзине'
        verbose_name_plural = 'Товары в корзине'
