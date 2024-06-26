from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django_htmx.http import retarget
from tracker.models import Transaction
from tracker.filters import TransactionFilter
from tracker.forms import TransactionForm

# Create your views here.
def index(request):
    return render(request, 'tracker/index.html')

@login_required
def transactions_list(request):
    transaction_filter = TransactionFilter(
        request.GET,
        # select_related avoids n+1 problem, creates JOIN to include related model data
        queryset=Transaction.objects.filter(user=request.user).select_related('category')
    )
    total_income = transaction_filter.qs.get_total_income()
    total_expenses = transaction_filter.qs.get_total_expenses()
    context = {'filter': transaction_filter,
                'total_income': total_income,
                'total_expenses': total_expenses,
                'net_income': total_income - total_expenses
            }
    
    if request.htmx:
        return render(request, 'tracker/partials/transactions-container.html', context)
    else:
        return render(request, 'tracker/transactions-list.html', context)

@login_required
def create_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            # do not immediately add (commit) form data to database
            transaction = form.save(commit=False)
            # add user to transaction first
            transaction.user = request.user
            transaction.save()
            context = {'message': "Transaction added successfully"}
            return render(request, 'tracker/partials/transaction-success.html', context)
        else:
            context = {'form': form}
            response = render(request, 'tracker/partials/create-transaction.html', context)
            # change target of htmx response when errors on form (to avoid duplicate headers)
            return retarget(response, '#transaction-block')
    
    context = {'form': TransactionForm()}

    if request.htmx:
        return render(request, 'tracker/partials/create-transaction.html', context)
    else:
        raise PermissionDenied()

