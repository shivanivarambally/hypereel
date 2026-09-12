"""Regression: a daily quota error can misleadingly include a short RetryInfo."""
import pytest
from hypereel.evaluation.gemini_retry_policy import retry_delay

@pytest.mark.parametrize(('error', 'expected'), [
    ('HTTP 429: GenerateRequestsPerDayPerProjectPerModel-FreeTier "retryDelay":"23s"', None),
    ('HTTP 503: temporarily unavailable', 20),
    ('HTTP 429: per-minute quota "retryDelay":"23s"', 25),
    ('HTTP 401: invalid credentials', None),
    ('HTTP 429: per-minute quota "retryDelay":"120s"', None),
])
def test_retry_classification(error, expected):
    assert retry_delay(error) == expected
