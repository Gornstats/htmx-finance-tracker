import pytest
from tracker.models import Transaction

# transactions is globally accessible from conftest file (factory created test data)
# decorator allows test access to django database
@pytest.mark.django_db
def test_queryset_get_income_method(transactions):
    qs = Transaction.objects.get_income()
    count = qs.count()
    assert count > 0
    assert all(
        [transaction.type == 'income' for transaction in qs]
    )
    print(f'type=income transaction test passed, {count} entries')
 
@pytest.mark.django_db
def test_queryset_get_expenses_method(transactions):
    qs = Transaction.objects.get_expenses()
    count = qs.count()
    assert count > 0
    assert all(
        [transaction.type == 'expense' for transaction in qs]
    )
    print(f'type=expense transaction test passed, {count} entries')

@pytest.mark.django_db
def test_queryset_get_total_income_method(transactions):
    total_income = Transaction.objects.get_total_income()
    assert total_income == sum(t.amount for t in transactions if t.type == 'income')
    print(f'total income test passed, total: ${total_income}')
   
@pytest.mark.django_db
def test_queryset_get_total_expenses_method(transactions):
    total_expenses = Transaction.objects.get_total_expenses()
    assert total_expenses == sum(t.amount for t in transactions if t.type == 'expense')
    print(f'total expenses test passed, total: ${total_expenses}')
