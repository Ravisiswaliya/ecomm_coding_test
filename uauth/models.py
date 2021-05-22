from django.db import models
from uauth.utils import create_token
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import BaseUserManager


class TimeStampModel(models.Model):
    class Meta:
        abstract = True

    cdate = models.DateTimeField(auto_now_add=True)
    udate = models.DateTimeField(auto_now=True)


class MyAccountManager(BaseUserManager):

    def create_user(self, email, password=None, role_type=None):
        if not email:
            raise ValueError("Must have an email address")

        user = self.model(email=self.normalize_email(email), role_type=role_type)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password, role_type='ADMIN')
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class Account(AbstractBaseUser, PermissionsMixin, TimeStampModel):
    FA = "FA"
    SELLER = "SELLER"
    ROLE_TYPE_CHOICE = [
        (FA, 'FA'),
        (SELLER, 'SELLER'),
    ]

    name = models.CharField(max_length=255, null=True, blank=True)
    contact = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(max_length=255, unique=True)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    role_type = models.CharField(max_length=20, choices=ROLE_TYPE_CHOICE)

    objects = MyAccountManager()

    USERNAME_FIELD = 'email' 

    def get_token(self):
        return create_token(self)
    
    def __str__(self):
        return self.email

    


class Product(TimeStampModel):
    seller = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='product_seller')
    product_name = models.CharField(max_length=150)
    product_description = models.TextField(blank=True, null=True)
    total_quantity = models.IntegerField(default=1)
    sold_cout = models.IntegerField(default=0)
    product_price = models.IntegerField(default=0)


    @property
    def remaining_items(self):
        return self.total_quantity - self.sold_cout

    def __str__(self):
        return self.product_name


