# Basketball rules governing event labels

Source of truth for which event combinations are legal. Used three ways: as
prompt text handed to the vision model, as deterministic validation in
`src/hypereel/evaluation/basketball_rules.py`, and as the reference a human
reviewer checks against.

## Provenance

Rules were stated by the project owner during W1 adjudication on 15 September
2026, then checked against official NBA sources on the same date. Each rule
below carries its citation and a verification status.

| Status | Meaning |
|---|---|
| **Verified** | Quoted from an official NBA source |
| **Inferred** | Follows from a quoted rule but is not stated verbatim |
| **Convention** | Standard statistical practice, not found in the sources checked |

Sources consulted:

- [NBA.com Stat Glossary](https://www.nba.com/stats/help/glossary) — statistical
  definitions of rebound, offensive/defensive rebound, assist, block.
- [NBA Rule No. 9: Free Throws and Penalties](https://official.nba.com/rule-no-9-free-throws-and-penalties/)
  — what happens after a successful free throw.
- [NBA Rule No. 6: Putting Ball in Play – Live/Dead Ball](https://official.nba.com/rule-no-6-putting-ball-in-play-live-dead-ball/)
  — dead-ball conditions, held ball, jump ball.
- [NBA Rule No. 4: Definitions](https://official.nba.com/rule-no-4-definitions/)
  — held ball.

### League caveat — read this before enforcing R3

**The development footage is not NBA basketball.** The teams (East Bay Elite,
Spartans, Campus, Unlimited) appear to be amateur or club sides, which would
play under NFHS or FIBA rules. The rules verified here are NBA rules because
that is the standard requested.

For R1, R2, R4 and R5 this makes no practical difference; the statistical
definitions of rebound, assist and block are consistent across codes. **R3 is
the exception.** The NBA resolves a held ball with an actual jump ball, whereas
NFHS and FIBA use alternating possession. R3 is therefore marked NBA-specific
and should not be used to reject output on non-NBA footage without confirming
the governing code. Since the taxonomy emits no possession-arrow event, this has
no effect on current validation.

## Why this exists

W1 produced the failure that motivated it. Human review established a **made
free throw**; number 24 of the Black team then collected the ball. The model
reported a missed field goal followed by a **defensive rebound**, in all eight
runs.

Under the rules, collecting the ball after a made free throw is **not a
rebound** — the ball is dead and the opposing team inbounds. The model's second
event was not merely mislabelled, it was illegal given the shot that preceded
it. The working theory is that the model saw the catch, read it as a rebound,
and back-inferred a miss to make the sequence coherent. Encoding the rule
removes the need for that inference: a catch after a made shot has a legal
explanation that is not a rebound.

## R1 — A rebound requires a missed shot that leaves the ball live

**Verified.** NBA.com Stat Glossary: *"A rebound occurs when a player recovers
the ball after a **missed** shot."* A made shot therefore cannot produce a
rebound, by definition.

**Verified** for the made-free-throw case. NBA Rule 9: *"After a successful free
throw which is not followed by another free throw, the ball shall be put into
play by a throw-in, as after any successful field goal."* The ball goes to the
**opponent** for a throw-in, so a player collecting it is inbounding, not
rebounding.

**Verified** for the non-final free throw. NBA Rule 6 lists the ball becoming
dead on a *"free throw which will not remain in play (free throw which will be
followed by another free throw...)"*. Dead ball, so no rebound.

**Inferred** for the missed final free throw remaining live. Rule 6 makes the
ball dead only when the free throw *"will not remain in play"*, and Rule 9 refers
to *"a free throw that is unsuccessful and the ball continues in play"*, with the
game clock started *"when the missed free throw is legally touched by any
player."* Both clauses presuppose a live ball. Not stated verbatim as a positive
rule.

A rebound is credited only when a shot attempt fails to score **and** the ball
remains live. Both conditions are necessary.

| Preceding event | Ball state | Rebound possible? |
|---|---|---|
| Made field goal (2pt or 3pt) | dead | **No** — opponent inbounds |
| Missed field goal | live | Yes |
| **Made free throw** | **dead** | **No** — opponent inbounds |
| Missed free throw, **not** the final attempt | dead | **No** — shooter shoots again |
| Missed free throw, final attempt | live | Yes |

A player collecting the ball after a made basket or a made free throw is
performing an **inbound**, not a rebound. It is not a scorable event in this
taxonomy.

## R2 — Rebound type follows team, not position on court

**Verified.** NBA.com Stat Glossary: offensive rebounds are *"collected while
they were on offense"*; defensive rebounds *"while they were on defense"*. The
shooting team is the offence, so:

- **Offensive rebound** — the rebounding player is on the **same** team as the
  shooter.
- **Defensive rebound** — the rebounding player is on the **opposing** team to
  the shooter.

Determined by team, never by which end of the floor the player is standing on.

**Convention.** The NBA sources checked do not define what counts as gaining
control. The NCAA statisticians' manual requires regaining control — grabbing or
dribbling, tipping into the basket, or slapping/passing to a teammate in one
controlled action — and merely touching the ball is not enough.

## R3 — Contested and uncontrolled recoveries (NBA-specific)

**Verified, NBA only.** Rule 4 defines a held ball as *"when two opponents have
one or both hands firmly on the ball"*. Rule 6: *"The ball shall be put into play
by a jump ball at the circle which is closest to the spot where: A held ball
occurs"*, and *"the jump ball shall be between the two involved players"*. No
alternating-possession arrow appears in the NBA rules.

**This is where NBA diverges from the likely governing code for this footage.**
NFHS and FIBA resolve a held ball by alternating possession instead of a jump
ball. See the league caveat above before enforcing R3.

Either way the consequence for this taxonomy is the same: a contested recovery
with no clear control is **not a rebound**.

**Convention.** If the ball goes out of bounds off a missed shot with no player
control, the statistical convention is a **team rebound**, which this taxonomy
does not model. Prefer emitting no rebound event over guessing a team.

## R4 — Assist

**Verified.** NBA.com Stat Glossary: an assist is a *"pass that leads directly to
a made basket"*. No made basket means no assist.

**Convention.** That free throws are never assisted is standard statistical
practice and is not stated in the glossary text checked. It follows from a free
throw being an undefended dead-ball attempt that no pass creates.

## R5 — Block

**Verified.** NBA.com Stat Glossary: *"A block occurs when an offensive player
attempts a shot, and the defense player tips the ball, blocking their chance to
score."* A shot attempt is required, and the defender must touch **the ball**.

**Inferred.** Contact with the shooter rather than the ball is a foul, not a
block — this follows from "tips the ball". A blocked shot that still scores is
not a block, since the glossary requires the block to prevent the chance to
score.

## R6 — Steal and turnover are one event from two sides

**Convention.** Not a rules question; this is an artefact of the taxonomy
offering both perspectives of one possession change as separate labels.

A steal by the defence always produces a turnover by the offence. Emitting both
for one possession change describes the same event twice. The scorer treats them
as aliases; prefer `steal` when a defender visibly causes it, `turnover` when
possession is lost without defensive contact.

A possession change caused by a made basket or a rebound is **neither** a steal
nor a turnover.

## Legality matrix

Rows are the shot event; columns are whether the listed follow-up is legal in
the same sequence.

| Shot event | offensive_rebound | defensive_rebound | assist |
|---|:--:|:--:|:--:|
| `two_point_made` | no | no | yes |
| `three_point_made` | no | no | yes |
| `two_point_miss` | yes | yes | no |
| `three_point_miss` | yes | yes | no |
| `free_throw_made` | **no** | **no** | no |
| `free_throw_miss` (final) | yes | yes | no |
| `free_throw_miss` (not final) | no | no | no |
| `made_field_goal` | no | no | yes |
| `missed_field_goal` | yes | yes | no |

The taxonomy does not currently carry whether a free throw is the final attempt
of its set. Validation therefore treats `free_throw_miss` permissively and flags
it for review rather than rejecting it. Adding an `is_final_attempt` field would
let R1 be enforced exactly.

## What validation does with a violation

`validate_sequence` returns violations; it does not silently delete events. An
illegal pair is surfaced for human review, because either the shot label or the
follow-up label is wrong and the code cannot tell which. In W1's case the shot
label was wrong; the model had the rebound observation roughly right in the
sense that a player did collect the ball, but the correct reading was an
inbound after a made free throw.
