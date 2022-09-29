from django.db import models
from django.db.models import Avg, Count
from django.urls import reverse
from accounts.models import Account
from category.models import Category


class Product(models.Model):
    objects = models.Manager()
    product_name = models.CharField(max_length=200, unique=True, verbose_name='Наименование товара')
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True, verbose_name='Описание')
    price = models.IntegerField(verbose_name='Цена')
    product_image = models.ImageField(upload_to='photos/products', verbose_name='Фото товара')
    stock = models.IntegerField(verbose_name='Количество на складе')
    is_available = models.BooleanField(default=True, verbose_name='Доступен')
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    modified_date = models.DateTimeField(auto_now=True, verbose_name='Дата изменений')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')

    def get_url(self):
        """
        Get to go to product detail page.
        :return: reverse url for particular product
        """
        return reverse('product_detail', args=[self.category.slug, self.slug])

    def __str__(self):
        return self.product_name

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def average_review(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg

    def count_review(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(count=Count('id'))
        count = 0
        if reviews['count'] is not None:
            count = int(reviews['count'])
        return count


class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager, self).filter(variation_category='color', is_active=True)

    def sizes(self):
        return super(VariationManager, self).filter(variation_category='size', is_active=True)


variation_category_choice = (
    ('color', 'цвет'),
    ('size', 'размер'),
)


class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    variation_category = models.CharField(max_length=100, choices=variation_category_choice, verbose_name='Категория '
                                                                                                          'вариации')
    variation_value = models.CharField(max_length=100, verbose_name='Значение вариации')
    is_active = models.BooleanField(default=True, verbose_name='Активно')
    created_date = models.DateTimeField(auto_now=True, verbose_name='Дата создания')

    objects = VariationManager()

    def __str__(self):
        return self.variation_value

    class Meta:
        verbose_name = 'Вариацию'
        verbose_name_plural = 'Вариации'


class ReviewRating(models.Model):
    objects = models.Manager()

    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    user = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name='Пользователь')
    subject = models.CharField(max_length=100, blank=True, verbose_name='Тема')
    review = models.TextField(max_length=500, blank=True, verbose_name='Отзыв')
    rating = models.FloatField(verbose_name='Рейтинг')
    ip = models.CharField(max_length=20, blank=True, verbose_name='IP адрес')
    status = models.BooleanField(default=True, verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    def __str__(self):
        return self.subject

    class Meta:
        verbose_name = 'Отзыв и оценку'
        verbose_name_plural = 'Отзывы и оценки'


class ProductGallery(models.Model):
    objects = models.Manager()

    product = models.ForeignKey(Product, default=None, on_delete=models.CASCADE, verbose_name='Товар')
    image = models.ImageField(upload_to='store/products', max_length=255, verbose_name='Фото')

    def __str__(self):
        return self.product.product_name

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'Галерея товаров'
