from rest_framework import serializers
from .models import Category , Transaction
#Category serializers

class Categoryserializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source = 'get_type_display', read_only = True)

    class meta:
        model = Category
        fields = ['id','name' , 'type', 'type_display','discription', 'is_active']
        read_only_fields = ['id']

    def validate_name(self,value):
        if not value.strip():
            return serializers.ValidationError('نام دسته نمی تواند خالی باشد')
        return value.strip()

#transactions serializers
class Transactionsserializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_type = serializers.CharField(source='category.type', read_only=True)
    type_display = serializers.CharField(sourse = 'get_type_display',read_only = True)
    # نمایش نام کاربری ثبت‌کننده (به جای فرستادن کل آبجکت کاربر یا فقط ID)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class meta:
        model = Transaction
        Fields = ['id','name','type','title','amount','created_by','date','created_time','description','created_by_username','created time','is_deleted']
        read_only_fields = ['id', 'type_display', 'category_name', 'category_type','created_by_username', 'created_time', 'is_deleted']

    def validate_amount(self,value):
        if value <= 0 :
            return serializers.ValidationError('میلغ تراکنش باید حتما عددی مثبت و بزرگ تر از صفر باشد')
        return value
    
    def validate_category(self,value):
        # check if the category of this transaction isn't deleted
        if not value.is_active :
            return serializers.ValidationError(f'دسته بندی ای به نام {value} وجود ندارد')
        return value

    
    def validate(self, data):
        """
        اعتبارسنجی سطح کل آبجکت (Cross-Field Validation):
        بررسی تطابق منطقی بین «نوع تراکنش» و «نوع دسته‌بندی» انتخابی
        """
        transaction_type = data.get('type', getattr(self.instance, 'type', None))
        category = data.get('category', getattr(self.instance, 'category', None))

        if transaction_type and category:
            # ۱. اگر تراکنش از نوع «درآمد» یا «دریافت» است، دسته‌بندی حتماً باید از نوع «درآمد» (INCOME) باشد
            if transaction_type in [Transaction.TransactionType.INCOME, Transaction.TransactionType.RECEIPT]:
                if category.type != Category.CategoryType.INCOME:
                    raise serializers.ValidationError({
                        "category": f"خطای عدم تطابق: برای تراکنش‌های نوع «{Transaction.TransactionType(transaction_type).label}»، باید دسته‌بندی با ماهیت «درآمد» انتخاب کنید (دسته‌بندی انتخابی شما از نوع «هزینه» است)."
                    })

            # ۲. اگر تراکنش از نوع «هزینه» یا «پرداخت» است، دسته‌بندی حتماً باید از نوع «هزینه» (EXPENSE) باشد
            elif transaction_type in [Transaction.TransactionType.EXPENSE, Transaction.TransactionType.PAYMENT]:
                if category.type != Category.CategoryType.EXPENSES:
                    raise serializers.ValidationError({
                        "category": f"خطای عدم تطابق: برای تراکنش‌های نوع «{Transaction.TransactionType(transaction_type).label}»، باید دسته‌بندی با ماهیت «هزینه» انتخاب کنید (دسته‌بندی انتخابی شما از نوع «درآمد» است)."
                    })

        return data