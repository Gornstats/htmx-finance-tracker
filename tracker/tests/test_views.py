from datetime import datetime, timedelta
import pytest
from django.urls import reverse
from tracker.models import Category

@pytest.mark.django_db
def test_total_values_appear_on_transaction_page(user_transactions, client):
    user = user_transactions[0].user
    #login test user to allow access to their data
    client.force_login(user)
    
    income_total = sum(t.amount for t in user_transactions if t.type == 'income')
    expense_total = sum(t.amount for t in user_transactions if t.type == 'expense')
    net = income_total - expense_total
    
    response = client.get(reverse('transactions-list'))
    
    assert response.context['total_income'] == income_total
    assert response.context['total_expenses'] == expense_total
    assert response.context['net_income'] == net

    print(f"income total: {income_total}, expense total: {expense_total}, net: {net}")

@pytest.mark.django_db
def test_transaction_type_filter(user_transactions, client):
    user = user_transactions[0].user
    client.force_login(user)
    
    # check income, by including it as a parameter in the get request (applied to filter)
    GET_params = {'transaction_type': 'income'}
    response = client.get(reverse('transactions-list'), GET_params)
    
    qs = response.context['filter'].qs
    
    for transaction in qs:
        assert transaction.type == 'income'
    
    # check expenses
    GET_params = {'transaction_type': 'expense'}
    response = client.get(reverse('transactions-list'), GET_params)
    
    qs = response.context['filter'].qs
    
    for transaction in qs:
        assert transaction.type == 'expense'
    
    print("transaction type filter passed")

@pytest.mark.django_db
def test_start_end_date_filter(user_transactions, client):
    user = user_transactions[0].user
    client.force_login(user)
    
    start_date_cutoff = datetime.now().date() - timedelta(days=183)
    GET_params = {'start_date': start_date_cutoff}
    response = client.get(reverse('transactions-list'), GET_params)
    
    qs = response.context['filter'].qs
    
    for transaction in qs:
        assert transaction.date >= start_date_cutoff

    end_date_cutoff = datetime.now().date() - timedelta(days=60)
    GET_params = {'end_date': end_date_cutoff}
    response = client.get(reverse('transactions-list'), GET_params)

    qs = response.context['filter'].qs

    for transaction in qs:
        assert transaction.date <= end_date_cutoff
    
    print("start/end date filter passed")
    
@pytest.mark.django_db
def test_category_filter(user_transactions, client):
    user = user_transactions[0].user
    client.force_login(user)

    # get primary keys for first 2 categories
    category_pks = Category.objects.all()[:2].values_list('pk', flat=True)
    GET_params = {'category': category_pks}

    response = client.get(reverse('transactions-list'), GET_params)

    qs = response.context['filter'].qs

    for transaction in qs:
        assert transaction.category.pk in category_pks
        
    print("category filter passed")

    
    
    