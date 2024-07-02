import pytest
from tracker.factories import TransactionFactory, UserFactory

# fixtures set up a consistent state for testing, and removes this data once tests are complete
# for creating dummy users, or transactions, for tests
@pytest.fixture
def transactions():
    return TransactionFactory.create_batch(25)

@pytest.fixture
def user_transactions():
    user = UserFactory()
    # all generated transactions are linked to same user
    return TransactionFactory.create_batch(25, user=user)

@pytest.fixture
def user():
    return UserFactory()

#injects above user fixture into this fixture
@pytest.fixture
def transaction_dict_params(user):
    transaction = TransactionFactory.create(user=user)
    return {
        'type': transaction.type,
        'category': transaction.category_id,
        'date': transaction.date,
        'amount': transaction.amount,
    }
