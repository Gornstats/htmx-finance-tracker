import pytest
from tracker.factories import TransactionFactory, UserFactory

# fixtures set up a consistent state for testing, and removes this data once tests are complete
@pytest.fixture
def transactions():
    return TransactionFactory.create_batch(25)

@pytest.fixture
def user_transactions():
    user = UserFactory()
    # all generated transactions are linked to same user
    return TransactionFactory.create_batch(25, user=user)
