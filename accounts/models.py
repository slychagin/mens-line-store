from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class MyAccountManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, email, password=None):
        if not email:
            raise ValueError('Пользователь должен иметь электронный адрес')
        if not username:
            raise ValueError('Пользователь должен иметь имя пользователя')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, username, email, password):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password
        )

        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Account(AbstractBaseUser):
    first_name = models.CharField(max_length=50, verbose_name='Имя')
    last_name = models.CharField(max_length=50, verbose_name='Фамилия')
    username = models.CharField(max_length=50, unique=True, verbose_name='Имя пользователя')
    email = models.EmailField(max_length=100, unique=True, verbose_name='Электронная почта')
    phone_number = models.CharField(max_length=50, verbose_name='Телефон')

    # required
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')
    last_login = models.DateTimeField(auto_now_add=True, verbose_name='Последний вход')
    is_admin = models.BooleanField(default=False, verbose_name='Администратор')
    is_staff = models.BooleanField(default=False, verbose_name='Персонал')
    is_active = models.BooleanField(default=False, verbose_name='Активный')
    is_superuser = models.BooleanField(default=False, verbose_name='Супер пользователь')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = MyAccountManager()

    def __str__(self):
        return self.email

    def full_name(self):
        return f'{self.last_name} {self.first_name}'

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, add_label):
        return True

    class Meta:
        verbose_name = 'Учетную запись'
        verbose_name_plural = 'Учетные записи'


class UserProfile(models.Model):
    objects = models.Manager()

    user = models.OneToOneField(Account, on_delete=models.CASCADE, verbose_name='Пользователь')
    address_line_1 = models.CharField(blank=True, max_length=100, verbose_name='Адрес 1')
    address_line_2 = models.CharField(blank=True, max_length=100, verbose_name='Адрес 2')
    profile_picture = models.ImageField(blank=True, upload_to='userprofile', verbose_name='Фото профиля')
    city = models.CharField(blank=True, max_length=20, verbose_name='Город')
    region = models.CharField(blank=True, max_length=20, verbose_name='Регион')
    country = models.CharField(blank=True, max_length=20, verbose_name='Страна')

    def __str__(self):
        return self.user.first_name

    def full_address(self):
        return f'{self.address_line_1}; {self.address_line_2}'

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'
