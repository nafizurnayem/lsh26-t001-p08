# P08 — School Result Processing & GPA Engine

**Team ID:** `LSH26-T001` · **Problem ID:** `P08` · **Repository:** `lsh26-t001-p08`

**Live:** `https://lsh26-t001-p08.streamlit.app/`

Reads a school marks file, computes each student's per-subject grade points,
GPA and letter grade under the P08 rules, and produces a per-student rule
trace plus three office checking lists.

## How to run it

    pip install -r requirements.txt
    streamlit run app.py

Then, in the sidebar under **Case File**, upload
`P08_school_results_public.json` from the organizers' submission kit — or any
file in the same shape. The 25 cases then appear in the **Data Source**
selector.

The fixture is **not committed to this repository**. With no file loaded the
app scores its own seeded 60-student cohort, so every screen still works.

Headless, no Streamlit needed:

    python engine.py        # scores the fixture, prints counts against the targets
    python test_engine.py   # 17 rule checks covering every documented trap

## Requirement proof

| Required item | Where it is | How to check it |
|---|---|---|
| 1. A cohort | Tab **1 · Cohort** | 60–80 students, two classes, six compulsory subjects plus one optional, practical subjects split into theory and practical. The header shows the hard-edge count against the required minimum of 8, and the roster names each student's edge case. "Generate a fresh cohort" builds 60 students with all four archetypes guaranteed (seed 7: 20 hard-edge students). |
| 2. Results | Tab **2 · Results** | A grade point for every subject, then raw GPA, final GPA and letter, two decimals, tinted by band, downloadable as CSV. |
| 3. Per-student trace | Tab **3 · Trace** | Seven rows per student: mark used, grade point, rule ID, plain-English reason. Where a strong average still failed, a banner names the culprit subject and shows raw GPA beside final GPA. |
| 4. Office checking lists | Tab **4 · Office List** | Three independent lists — optional rule, practical fail, absence — each with a CSV download. A student can appear on more than one. |
| Edge gallery (extra) | Tab **5 · Edge Gallery** | Finds the four hard archetypes automatically and shows two worked traces for each. |

Verification, in the sidebar: **Run all cases** re-scores every case in the
uploaded file, asserts the four invariants and compares against the counts
published in the brief.

| Population | Expected | Engine |
|---|---|---|
| Students scored | 1,765 | 1,765 |
| Optional grade point ≤ 2.0 | 589 | 589 |
| Compulsory failure → GPA 0.00 | 525 | 525 |
| Practical part below 8 somewhere | 316 | 316 |
| Practical fail with a passing theory mark | 260 | 260 |
| Failed despite an uncancelled average ≥ 3.50 | 75 | 75 |
| Absent in any subject | 50 | 50 |

Invariants held across every case: seven marks per student; letter F if and
only if a compulsory subject scored zero; final GPA within 0.00–5.00; raw GPA
never below final GPA.

## Problem-solving method

The rules were written first as a pure Python module, `engine.py`, with **no
Streamlit import**, so the whole rule set could be run headless over all 25
published cases and compared against the counts in the brief before any
interface existed.

Evaluation order is the core of P08. Absence (**R-12**) and the
theory/practical part gate (**R-11**) are both checked *before* the grade table
(**R-10**), because a theory 24 with a perfect practical 25 totals 49 and looks
like a pass. The trace line is built in the same branch that sets the grade
point, never reconstructed afterwards, so the reason shown to a teacher cannot
drift from the number used. **R-13** caps the GPA at 5.00 before rounding and
cancels it to 0.00 on any compulsory zero, while the uncancelled average stays
visible. **R-29** builds the three office lists as three independent passes.

The interface then maps one tab onto each required item, in order, so the work
can be checked without a walkthrough.

## Team contributions

| Member | GitHub | Major contribution |
|---|---|---|
| Md Nafizur Nayem | `nafizurnayem` | Specified and verified the P08 rule set, built `engine.py` and the five-tab Streamlit interface, ran the headless verification against the published counts, deployed the app. |

## Major decisions

- **The mark-to-grade-point table is not in the brief.** This engine uses the
  standard Bangladesh SSC scale (80+=5.0, 70–79=4.0, 60–69=3.5, 50–59=3.0,
  40–49=2.0, 33–39=1.0, below 33=0). Its boundaries mirror the letter bands the
  brief does give, and its pass mark of 33 equals theory 25 + practical 8. It
  is one list at the top of `engine.py` and can be swapped in seconds.
- **`Decimal` with `ROUND_HALF_UP`** everywhere a figure is shown. Python's
  `round()` is banker's rounding, and grade points arrive in half steps.
- **The optional subject contributes `max(0, gp - 2)`** and never fails a
  student; only a compulsory zero cancels the result.
- **The fixture is not redistributed here.** Judges load it, or any file in the
  same shape, through the sidebar.

## Known limitations

- The 25 published cases appear only after a judge uploads the JSON; without it
  the app runs on its generated cohort.
- No database or authentication — the app holds no state between page loads.
- An uploaded file is assumed to match the published schema; a malformed file
  raises a Streamlit error rather than a friendly message.
- No per-class statistics, historical comparison or PDF marksheet export.
- The interface was checked through Streamlit's `AppTest` harness and by hand
  in a browser; there is no automated visual regression test.

## Declarations

`EVENT.md` — event start record. `LICENSES.md` — third-party material and AI
disclosure. `evaluation-manifest.json` — the completed submission manifest.
Nothing is mocked; all figures come from the supplied dataset.
