from datetime import datetime, timedelta
import pytest
from django.urls import reverse
from tracker.models import Category, Transaction
from pytest_django.asserts import assertTemplateUsed

# mark allows access to django database for testing
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

@pytest.mark.django_db
def test_add_transaction_request(user, transaction_dict_params, client):
    client.force_login(user)
    user_transaction_count = Transaction.objects.filter(user=user).count()
    # send request with dummy transaction data
    headers = {'HTTP_HX-Request': 'true'}
    response = client.post(
        reverse('create-transaction'),
        transaction_dict_params,
        **headers
    )
    # confirm the transaction count has increased by one after transaction POST request
    assert Transaction.objects.filter(user=user).count() == user_transaction_count + 1
    # confirm transaction was successful and correct template shown
    assertTemplateUsed(response, 'tracker/partials/transaction-success.html')

    print("add transaction test passed")

@pytest.mark.django_db
def test_cannot_add_transaction_with_negative_amount(user, transaction_dict_params, client):
    client.force_login(user)
    user_transaction_count = Transaction.objects.filter(user=user).count()
    # override transaction value with negative number
    transaction_dict_params['amount'] = -20
    headers = {'HTTP_HX-Request': 'true'}
    response = client.post(
        reverse('create-transaction'),
        transaction_dict_params,
        **headers
    )
    # confirm transaction failed as it was negative (count should be unchanged)
    assert Transaction.objects.filter(user=user).count() == user_transaction_count
    assertTemplateUsed(response, 'tracker/partials/create-transaction.html')
    # confirm failed form response is correctly applying HTMX retarget
    assert 'HX-Retarget' in response.headers
    
    print("cannot add negative transaction test passed")

@pytest.mark.django_db
def test_update_transaction_request(user, transaction_dict_params, client):
    client.force_login(user)
    # confirm test user only has one transaction (as per test factory setup)
    assert Transaction.objects.filter(user=user).count() == 1

    transaction = Transaction.objects.first()

    # update the transaction via a POST request - mutate the dict params
    now = datetime.now().date()
    transaction_dict_params['amount'] = 99
    transaction_dict_params['date'] = now
    client.post(
        reverse('update-transaction', kwargs={'pk': transaction.pk}),
        transaction_dict_params
    )

    # check the request has UPDATED, not created a new transaction
    assert Transaction.objects.filter(user=user).count() == 1
    transaction = Transaction.objects.first()
    assert transaction.amount == 99
    assert transaction.date == now
    print("update transaction test passed")

@pytest.mark.django_db
def test_delete_transaction_request(user, transaction_dict_params, client):
    client.force_login(user)
    assert Transaction.objects.filter(user=user).count() == 1
    transaction = Transaction.objects.first()
    
    client.delete(
        reverse('delete-transaction', kwargs={'pk':transaction.pk})
    )
    
    assert Transaction.objects.filter(user=user).count() == 0
    print("delete transaction test passed")
