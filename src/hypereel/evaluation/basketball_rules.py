"""Deterministic legality checks over detected basketball event sequences.

The vision model decides *what it sees*. Which combinations of events are
possible is settled by the rules of the game, so it is decided here in code
rather than left to inference. See ``docs/BASKETBALL_RULES.md`` for the rules
themselves and their provenance.

Motivating failure (W1): human review established a made free throw, after which
a player collected the ball. The model reported a missed field goal followed by a
defensive rebound, in all eight runs. Collecting the ball after a made free throw
is an inbound, not a rebound — the ball is dead. The model's follow-up event was
illegal given its own shot event, and the likely cause was reading the catch as a
rebound and back-inferring a miss to make the sequence cohere.

Violations are reported, never silently repaired: when a pair is illegal, either
the shot label or the follow-up label is wrong and code cannot tell which.
"""
from __future__ import annotations

from dataclasses import dataclass

# Both taxonomies are covered deliberately. The fourteen-label set is current;
# `made_basket` and `three_pointer` come from the earlier four-label recipes
# (basketball_team_evaluation and friends), which are still in use. Keying rules
# to one taxonomy was exactly the bug that made the verification prompt a no-op
# for thirteen of fourteen labels, so it is not repeated here.
LEGACY_MADE = frozenset({'made_basket', 'three_pointer'})

# Shots after which the ball is dead, so no rebound can follow (R1).
BALL_DEAD_AFTER = frozenset({
    'two_point_made', 'three_point_made', 'made_field_goal', 'free_throw_made',
}) | LEGACY_MADE
# Shots after which the ball is live, so a rebound may follow (R1).
BALL_LIVE_AFTER = frozenset({
    'two_point_miss', 'three_point_miss', 'missed_field_goal', 'free_throw_miss',
})
REBOUNDS = frozenset({'offensive_rebound', 'defensive_rebound'})
MADE_FIELD_GOALS = frozenset({
    'two_point_made', 'three_point_made', 'made_field_goal',
}) | LEGACY_MADE
SHOT_LABELS = BALL_DEAD_AFTER | BALL_LIVE_AFTER

# A free throw that is not the final attempt of its set leaves the ball dead, so
# a miss is not reboundable either. The taxonomy carries no attempt-ordinal, so
# a rebound after `free_throw_miss` is allowed but flagged (R1, closing note).
NEEDS_ATTEMPT_ORDINAL = 'free_throw_miss'


@dataclass(frozen=True)
class Violation:
    """One illegal or suspect combination, with the rule that caught it."""
    rule: str
    severity: str  # 'illegal' | 'review'
    detail: str
    event_indices: tuple[int, ...]


def _label(event) -> str | None:
    if isinstance(event, dict):
        return event.get('moment_type') or event.get('label')
    return getattr(event, 'moment_type', None) or getattr(event, 'label', None)


def _time(event) -> float:
    if isinstance(event, dict):
        value = event.get('event_time', event.get('time_seconds'))
    else:
        value = getattr(event, 'event_time', None) or getattr(event, 'time_seconds', None)
    return float(value) if value is not None else 0.0


def _team(event) -> str | None:
    if isinstance(event, dict):
        return event.get('team')
    return getattr(event, 'team', None)


def validate_sequence(events) -> list[Violation]:
    """Check one window's events against the rules. Returns violations found.

    ``events`` may be Classification objects or plain dicts. Ordering is by
    ``event_time``; events without a time sort first and are still checked.
    """
    indexed = sorted(enumerate(events), key=lambda pair: _time(pair[1]))
    violations: list[Violation] = []

    def preceding_shot(position: int):
        """Nearest shot event before ``position`` in time order."""
        for earlier_index, event in reversed(indexed[:position]):
            if _label(event) in SHOT_LABELS:
                return earlier_index, event
        return None, None

    for position, (index, event) in enumerate(indexed):
        label = _label(event)

        if label in REBOUNDS:
            shot_index, shot = preceding_shot(position)
            if shot is None:
                violations.append(Violation(
                    'R1', 'illegal',
                    f'{label} with no preceding shot event in this window; '
                    'a rebound requires a missed shot that leaves the ball live',
                    (index,)))
                continue
            shot_label = _label(shot)
            if shot_label in BALL_DEAD_AFTER:
                what = ('made free throw' if shot_label == 'free_throw_made' else 'made field goal')
                violations.append(Violation(
                    'R1', 'illegal',
                    f'{label} follows {shot_label}; after a {what} the ball is dead and the '
                    'opponent inbounds, so collecting the ball is an inbound, not a rebound',
                    (shot_index, index)))
            elif shot_label == NEEDS_ATTEMPT_ORDINAL:
                violations.append(Violation(
                    'R1', 'review',
                    f'{label} follows {shot_label}; legal only if that was the final free-throw '
                    'attempt of the set, which the taxonomy does not record',
                    (shot_index, index)))
            else:
                shooter, rebounder = _team(shot), _team(event)
                if shooter and rebounder:
                    same = shooter.strip().lower() == rebounder.strip().lower()
                    if same and label == 'defensive_rebound':
                        violations.append(Violation(
                            'R2', 'illegal',
                            f'defensive_rebound credited to {rebounder}, the same team as the '
                            f'shooter; same-team recovery is an offensive rebound',
                            (shot_index, index)))
                    elif not same and label == 'offensive_rebound':
                        violations.append(Violation(
                            'R2', 'illegal',
                            f'offensive_rebound credited to {rebounder} against shooter '
                            f'{shooter}; opposing-team recovery is a defensive rebound',
                            (shot_index, index)))

        elif label == 'assist':
            if not any(_label(other) in MADE_FIELD_GOALS for _i, other in indexed):
                violations.append(Violation(
                    'R4', 'illegal',
                    'assist with no made field goal in this window; free throws are never '
                    'assisted and an assist requires a made basket',
                    (index,)))

        elif label == 'block':
            if not any(_label(other) in SHOT_LABELS for _i, other in indexed):
                violations.append(Violation(
                    'R5', 'review',
                    'block with no shot event in this window; a block requires a shot attempt '
                    'whose flight is visibly altered',
                    (index,)))

    labels = [_label(event) for _i, event in indexed]
    if 'steal' in labels and 'turnover' in labels:
        violations.append(Violation(
            'R6', 'review',
            'steal and turnover both present; these describe one possession change from two '
            'sides and should not be counted as separate events',
            tuple(i for i, event in indexed if _label(event) in {'steal', 'turnover'})))

    return violations


def rules_prompt_text() -> str:
    """Rule constraints for inclusion in a detector or verifier prompt.

    Deliberately a constant, not a retrieval. The rule set is one page and
    closed, so fetching it per window would add a failure mode (a retriever
    that misses the free-throw rule on a free-throw window) for no benefit.
    """
    return (
        '\nBasketball rules that constrain valid answers:\n'
        '- A rebound requires a shot that visibly MISSED and left the ball live. '
        'If you did not see the ball fail to go through the net, do not report a rebound.\n'
        '- After a MADE field goal or a MADE free throw the ball is dead. A player collecting '
        'the ball is inbounding it, NOT rebounding. Never report a rebound after a made shot.\n'
        '- A missed free throw is only reboundable if it was the final attempt of its set.\n'
        '- Offensive rebound means the rebounder is on the SAME team as the shooter; defensive '
        'rebound means the OPPOSING team. Decide by team, not by which end of the floor.\n'
        '- If neither team clearly controls the ball, report no rebound rather than guessing.\n'
        '- An assist requires a made field goal. Free throws are never assisted.\n'
        '- A steal and a turnover are one possession change seen from two sides; report one.\n'
    )
