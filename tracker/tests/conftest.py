import pytest
from tracker.factories import TransactionFactory

# fixture sets up a consistent state for testing, and removes this data once tests are complete
@pytest.fixture
def transactions():
    TransactionFactory.create_batch(25)