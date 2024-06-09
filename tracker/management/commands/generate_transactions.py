# populate database with some demo data using Django Management commands
import random
from faker import Faker
from django.core.management.base import BaseCommand
from tracker.models import User, Transaction, Category


class Command(BaseCommand):
    help = "Generates sample transactions for testing"
    
    def handle(self, *args, **options):
        fake = Faker()
        
        # create sample categories
        categories = [
            "Bills",
            "Food",
            "Clothes",
            "Medical",
            "Housing",
            "Salary",
            "Social",
            "Travel",
            "Holiday",
        ]
        
        for category in categories:
            Category.objects.get_or_create(name=category)
            
        # get first test user
        user = User.objects.filter(username='super').first()
        if not user:
            user = User.objects.create_superuser(username='super', password='test')
        
        # create transactions
        categories = Category.objects.all()
        types = [x[0] for x in Transaction.TRANSACTION_TYPE_CHOICES]
        for i in range(20):
            Transaction.objects.create(
                category = random.choice(categories),
                user = user,
                amount = random.uniform(5,1500),
                date = fake.date_between(start_date='-1y', end_date='today'),
                type = random.choice(types)
            )
