"""Test GCP Models."""

from datetime import datetime

from sapimclient.model.gcp import Participant


def test_participant() -> None:
    """Test Participant."""
    pa = Participant(
        payee_id='spam',
        last_name='eggs',
        effective_start_date=datetime(2025, 1, 1, 0, 0),
        effective_end_date=datetime(2025, 1, 1, 0, 0),
        user_id='spam',
    )
    assert pa.payee_id == 'spam'
    assert pa.last_name == 'eggs'
    assert pa.effective_start_date == datetime(2025, 1, 1, 0, 0)
    assert pa.effective_end_date == datetime(2025, 1, 1, 0, 0)
    assert pa.user_id == 'spam'
