from decimal import Decimal
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.utils import timezone

# custom user model

class User(AbstractUser):
    class Role(models.TextChoices):
        ACOUNTING_EMPLOYEE = 'ACOUNTING' , 'Acounting employee'
        ADMIN = 'ADMIN', 'Administrator'

        role = models.CharField(
            max_length=20,
            choices = Role.choices,
            default = Role.ACOUNTING_EMPLOYEE,
            verbose_name="نقش کاربری",
        )

    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"

    # deleted users
    class delete(self,*args ,**kwargs):
        self.is_active = False 
        self.save()

        
    def __str__(self):
        return f'{self.get_full_name() or self.username} ({self.get_role_display()})'
    
    
# transactions category
class Category(models.Model):

    class CategoryType(models.TextChoices):
        INCOME= 'INCOME', 'درآمد'
        EXPENSES= 'EXPENSES' , 'هزینه'
        Name=models.CharField(
            max_length=100,
            verbose_name='نام دسته بندی'
        )

    type=models.CharField(
            max_length=12,
            choices = CategoryType.choices,
            verbose_name='نوع دسته بندی'   
    )

    description= models.CharField(
            max_length= 255,
            blank= True,
            null= True,
            verbose_name='توضیحات کوتاه'
    )

    is_active = models.BooleanField(
            default= True,
            verbose_name='فعال'
    )
    class Meta:
        verbose_name = 'دسته بندی'
        verbose_name_plural= 'دسته بندی ها'
        ordering = ['-id']

    def __str__(self):

        if self.description :
            return f"نام = {self.name}  نوع = {self.get_type_display()}  توضیحات = {self.get_description_dispay()}"
        
        return f"نام = {self.name}  نوع = {self.get_type_display()}"

#transactions
class Transaction(models.Model):
    """
    مدل تراکنش‌های مالی سیستم.
    شامل ولیدیتور برای جلوگیری از مبالغ منفی و صفر، و حفاظت از حذف داده‌های متصل.
    """
    class TransactionType(models.CharField): 
        INCOME = 'INCOME', 'درآمد'
        EXPENSE = 'EXPENSE', 'هزینه'
        RECEIPT = 'RECEIPT', 'دریافت (ورود نقدینگی)'
        PAYMENT = 'PAYMENT', 'پرداخت (خروج نقدینگی)'      
    type=models.CharField(
        max_length=10 ,
        choices=TransactionType.choices ,
        verbose_name='نوع تراکنش', 
    )  

    title = models.CharField(
        max_length= 150 ,
        verbose_name='عنوان '
    )

    amount = models.BigIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='مبلغ (ریال )'
    )

    Category= models.ForeignKey(
        Category,
        on_delete=models.PROTECT ,
        related_name= 'Transactions',
        verbose_name='دسته بندی تراکنش'
    )

    crated_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='Transactions',
        verbose_name='سازنده این تراکنش'
    )

    date = models.DateField(
        default=timezone.now,
        verbose_name='تاریخ تراکنش'
    )
    # blank = True ?????
    description = models.CharField(
        blank=True,
        verbose_name='توضیحات تکمیلی'
    )

    created_time =  models.DateField(
        auto_now_add=True,
        verbose_name='زمان ثبت تراکنش'
    )

    is_deleted = models.BooleanField(
        default=False ,
        verbose_name= "حذف شده؟"
    )
    delete_date=models.DateTimeField(
        null=True ,
        blank=True,
        verbose_name="تاریخ حذف"
    )
    deleted_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='delete_item_logs',
        verbose_name='حذف کننده کاربران'
    )

    class Meta:
        verbose_name = "تراکنش"
        verbose_name_plural = "تراکنش‌ها"
        ordering = ['-date', '-created_time']

    def __str__(self):
        return f"{self.title} | {self.amount} | {self.get_type_display()}"