import json
import pytest
from hypereel.evaluation.gemini_budget import check_reservation

@pytest.fixture
def budget(tmp_path):
    folder=tmp_path/'evals/iterations';folder.mkdir(parents=True)
    (folder/'gemini-funded-budget.json').write_text(json.dumps({'baseline_cumulative_ledger_usd':7.2,'new_evaluation_cap_usd':2}))
    return tmp_path

def test_last_request_at_cap(budget):
    assert check_reservation(budget,9,.2)==0

def test_reserve_stops_before_demo_money(budget):
    with pytest.raises(RuntimeError):check_reservation(budget,9,.21)

def test_prior_reservations_count_across_runs(budget):
    with pytest.raises(RuntimeError):check_reservation(budget,9.19,.02)

def test_no_ledger_reset(budget):
    with pytest.raises(ValueError):check_reservation(budget,0,.05)

@pytest.mark.parametrize('value',[float('nan'),float('inf'),-.1])
def test_invalid_reservation(budget,value):
    with pytest.raises(ValueError):check_reservation(budget,7.2,value)
