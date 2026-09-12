"""Local evaluation budget; historical spend is never reset by funding."""
from decimal import Decimal
import json

def check_reservation(root, spent, reserve):
    policy = json.loads((root / 'evals/iterations/gemini-funded-budget.json').read_text())
    baseline = Decimal(str(policy['baseline_cumulative_ledger_usd']))
    cap = Decimal(str(policy['new_evaluation_cap_usd']))
    current, request = Decimal(str(spent)), Decimal(str(reserve))
    if not all(x.is_finite() for x in (baseline, cap, current, request)):
        raise ValueError('Non-finite budget')
    if cap < 0 or request < 0 or current < baseline:
        raise ValueError('Invalid budget or reset ledger')
    if current + request > baseline + cap:
        raise RuntimeError('Funded evaluation cap reached; demo reserve protected')
    return float(baseline + cap - current - request)
