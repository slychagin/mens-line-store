from django.db import models


class Slider(models.Model):
    objects = models.Manager()

    slider_image = models.ImageField(upload_to='sliderimg', blank=True, verbose_name='Фото слайдера')
    slider_title = models.CharField(max_length=100, blank=True, verbose_name='Заголовок')
    slider_text = models.CharField(max_length=200, blank=True, verbose_name='Текст')
    slider_css = models.CharField(max_length=200, null=True, default='-', verbose_name='CSS класс')

    def __str__(self):
        return self.slider_title

    class Meta:
        verbose_name = 'Слайд'
        verbose_name_plural = 'Слайды'
