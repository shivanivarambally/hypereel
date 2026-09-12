"""Respect hard daily quota; retry only transient Gemini capacity/rate errors."""
import re

def retry_delay(error):
    text = str(error)
    # Daily quotas cannot be repaired by a short RetryInfo delay.
    if 'RequestsPerDay' in text or 'requests_per_day' in text.lower():
        return None
    if not any(code in text for code in ('HTTP 429', 'HTTP 503')):
        return None
    match = re.search(r'"retryDelay"\s*:\s*"([0-9.]+)s"', text)
    delay = max(20.0, float(match.group(1)) + 2) if match else 20.0
    # Longer cooldowns require a later explicit continuation, not repeated waits.
    return delay if delay <= 60 else None
