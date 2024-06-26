from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import TransactionQuerySet

class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        # django admin will show plural name of model with an S suffix, the meta class overrides this

    def __str__(self):
        return self.name


# financial transaction (income or expense), has an amount (decimal), and a date
# has a category (Foreign Key)
# belongs to a user (Foreign Key)
class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = (
        ('income', 'Income'),
        ('expense', 'Expense'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=7, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    # when category deleted, set any transactions with that category to Unknown
    category = models.ForeignKey(Category, on_delete=models.SET('Unknown'))
    date = models.DateField()
    
    objects = TransactionQuerySet.as_manager()

    def __str__(self):
        return f"{self.type} of {self.amount} on {self.date} by {self.user}"
    
    # pre-sort list by descending date
    class Meta:
        ordering = ['-date']

    