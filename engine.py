"""P08 result engine.

Pure computation: no Streamlit import here so the module can be run headless
from the terminal (`python engine.py`) and reused by the UI.

Rule IDs printed in every trace line:

    R-10  grade point from the mark; letter grade from the final GPA
    R-11  theory below 25 or practical below 8 -> subject grade point 0
    R-12  absent -> mark shown as AB, grade point 0; compulsory absence -> F
    R-13  GPA formula, 5.00 cap, compulsory-failure cancellation
    R-29  the three office checking lists
"""

from __future__ import annotations

import json
import random
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

# --- constants ---------------------------------------------------------------

DATA_FILE = "P08_school_results_public.json"

# Mark -> grade point. Standard Bangladesh SSC scale; see README "Assumptions".
GRADE_TABLE = [(80, 5.0), (70, 4.0), (60, 3.5), (50, 3.0), (40, 2.0), (33, 1.0)]

# GPA -> letter. A+ is exactly 5.00.
LETTER_BANDS = [(5.00, "A+"), (4.00, "A"), (3.50, "A-"), (3.00, "B"), (2.00, "C"), (1.00, "D")]

THEORY_PASS = 25
PRACTICAL_PASS = 8
ABSENT = "AB"
GPA_CAP = 5.0
OPTIONAL_BONUS_FLOOR = 2.0
COMPULSORY_COUNT = 6

SUBJECT_NAMES = {
    "BAN": "Bangla",
    "ENG": "English",
    "MAT": "Mathematics",
    "PHY": "Physics",
    "CHE": "Chemistry",
    "BIO": "Biology",
    "HMT": "Higher Mathematics",
    "AGR": "Agriculture",
    "REL": "Religion",
}
PRACTICAL_SUBJECTS = {"PHY", "CHE", "BIO", "HMT", "AGR"}
COMPULSORY = ["BAN", "ENG", "MAT", "PHY", "CHE", "BIO"]
OPTIONALS = ["HMT", "AGR", "REL"]


# --- formatting --------------------------------------------------------------


def fmt(x):
    """Two decimals, half-up. Python's round() is banker's rounding."""
    return str(Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def round2(x):
    return float(Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


# --- rules -------------------------------------------------------------------


def grade_point(total):
    """R-10: grade point from a total mark out of 100."""
    for cut, gp in GRADE_TABLE:
        if total >= cut:
            return gp
    return 0.0


def band(gpa):
    """R-10: letter grade from the final GPA, compared at two decimals."""
    value = round2(gpa)
    for cut, letter in LETTER_BANDS:
        if value >= cut:
            return letter
    return "F"


def subject_row(code, mark, is_practical, is_compulsory):
    """One whole trace line: the mark used, the grade point, and the deciding rule.

    Evaluation order is the whole game: absence and the part-fail gate are both
    checked before the grade table.
    """
    row = {
        "code": code,
        "subject": SUBJECT_NAMES.get(code, code),
        "compulsory": is_compulsory,
        "practical_subject": is_practical,
        "theory": None,
        "practical": None,
        "absent": False,
        "part_failed": False,
    }

    if mark == ABSENT:
        tail = (
            " A compulsory absence fails the whole result."
            if is_compulsory
            else " An optional subject never fails a student."
        )
        row.update(
            mark_used=ABSENT,
            total=None,
            gp=0.0,
            rule="R-12",
            absent=True,
            why="Absent in this subject, so the grade point is 0." + tail,
        )
        return row

    if is_practical:
        theory = mark["theory"]
        practical = mark["practical"]
        total = theory + practical
        row.update(
            theory=theory,
            practical=practical,
            total=total,
            mark_used="{}+{}={}".format(theory, practical, total),
        )
        if theory < THEORY_PASS or practical < PRACTICAL_PASS:
            parts = []
            if theory < THEORY_PASS:
                parts.append("theory {} is below {}".format(theory, THEORY_PASS))
            if practical < PRACTICAL_PASS:
                parts.append("practical {} is below {}".format(practical, PRACTICAL_PASS))
            row.update(
                gp=0.0,
                rule="R-11",
                part_failed=True,
                why="Part fail: {}, so the total of {} never reaches the table.".format(
                    " and ".join(parts), total
                ),
            )
            return row
    else:
        total = mark
        row.update(total=total, mark_used=str(total))

    gp = grade_point(total)
    if gp == 0.0:
        why = "Total {} is below the pass mark of 33, so the grade point is 0.".format(total)
    else:
        cut = next(c for c, g in GRADE_TABLE if total >= c)
        why = "Total {} falls in the {}+ band, so the grade point is {}.".format(total, cut, gp)
    row.update(gp=gp, rule="R-10", why=why)
    return row


def student_result(student, compulsory, case_id=""):
    """Full result for one student: rows, raw GPA, final GPA, letter, flags."""
    optional_code = student["optional"]
    order = list(compulsory) + [optional_code]

    rows = [
        subject_row(
            code,
            student["marks"][code],
            code in PRACTICAL_SUBJECTS,
            code in compulsory,
        )
        for code in order
    ]
    by_code = {r["code"]: r for r in rows}

    compulsory_gps = [by_code[c]["gp"] for c in compulsory]
    optional_gp = by_code[optional_code]["gp"]

    # R-13: the optional contributes only what it earns above 2.0, never negative.
    bonus = max(0.0, optional_gp - OPTIONAL_BONUS_FLOOR)
    raw_gpa = min(GPA_CAP, (sum(compulsory_gps) + bonus) / COMPULSORY_COUNT)

    compulsory_failed = any(gp == 0.0 for gp in compulsory_gps)
    final_gpa = 0.0 if compulsory_failed else raw_gpa
    letter = "F" if compulsory_failed else band(final_gpa)

    culprits = [r["code"] for r in rows if r["compulsory"] and r["gp"] == 0.0]

    practical_rows = [r for r in rows if r["practical"] is not None and r["practical"] < PRACTICAL_PASS]

    return {
        "case_id": case_id,
        "id": student["id"],
        "name": student["name"],
        "class": student["class"],
        "optional": optional_code,
        "rows": rows,
        "subject_gps": {r["code"]: r["gp"] for r in rows},
        "raw_gpa": raw_gpa,
        "final_gpa": final_gpa,
        "raw_gpa_str": fmt(raw_gpa),
        "final_gpa_str": fmt(final_gpa),
        "letter": letter,
        "compulsory_failed": compulsory_failed,
        "culprit_subjects": culprits,
        "optional_gp": optional_gp,
        "optional_weak": optional_gp <= OPTIONAL_BONUS_FLOOR,
        "practical_fail": bool(practical_rows),
        "practical_fail_passing_theory": any(r["theory"] >= THEORY_PASS for r in practical_rows),
        "absent": any(r["absent"] for r in rows),
        "high_average_failure": compulsory_failed and raw_gpa >= 3.50,
    }


def checking_lists(results):
    """R-29: three independent passes. A student may appear on more than one."""
    return {
        "optional": [r for r in results if r["optional_weak"]],
        "practical_fail": [r for r in results if r["practical_fail"]],
        "absent": [r for r in results if r["absent"]],
    }


# --- data --------------------------------------------------------------------


def load_file(path=DATA_FILE):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def case_ids(data):
    return [c["case_id"] for c in data["cases"]]


def load_case(data, case_id):
    for case in data["cases"]:
        if case["case_id"] == case_id:
            return case
    raise KeyError("no such case: {}".format(case_id))


def run_case(case):
    return [student_result(s, case["compulsory"], case["case_id"]) for s in case["students"]]


def run_all(data):
    out = []
    for case in data["cases"]:
        out.extend(run_case(case))
    return out


# --- seeded cohort generator -------------------------------------------------

FIRST = [
    "Arif", "Kamal", "Lamia", "Nusrat", "Rakib", "Sadia", "Tanvir", "Mitu",
    "Jubayer", "Rumana", "Shakib", "Farhana", "Imran", "Nadia", "Rafi",
    "Tasnim", "Sabbir", "Mehjabin", "Hasan", "Sumaiya",
]
LAST = [
    "Hossain", "Islam", "Begum", "Rahman", "Ahmed",
    "Khan", "Chowdhury", "Akter", "Sarker", "Mia",
]


def _mark(rng, code, low, high):
    """A mark inside a total band, split into theory and practical when needed."""
    total = rng.randint(low, high)
    if code not in PRACTICAL_SUBJECTS:
        return total
    practical = max(0, min(25, round(total * 0.25) + rng.randint(-2, 2)))
    theory = max(0, min(75, total - practical))
    return {"theory": theory, "practical": practical}


def generate_cohort(seed=7, size=60, case_id="GEN"):
    """60+ students, two classes, all four archetypes guaranteed present.

    Satisfies required item 1 without depending on the supplied file.
    """
    rng = random.Random(seed)
    students = []

    for i in range(size):
        optional = OPTIONALS[i % len(OPTIONALS)]
        marks = {code: _mark(rng, code, 40, 95) for code in COMPULSORY + [optional]}
        student = {
            "id": "G{:03d}".format(i + 1),
            "name": "{} {}".format(rng.choice(FIRST), rng.choice(LAST)),
            "class": "Class 9" if i % 2 == 0 else "Class 10",
            "optional": optional,
            "marks": marks,
            "archetype": "",
        }

        if i < 3:
            # Strong average, one compulsory subject fails outright.
            for code in COMPULSORY:
                marks[code] = _mark(rng, code, 78, 95)
            marks["MAT"] = rng.randint(10, 30)
            student["archetype"] = "high-average failure"
        elif i < 6:
            # Practical part fails behind a comfortably passing theory mark.
            marks["PHY"] = {"theory": rng.randint(45, 60), "practical": rng.randint(0, 7)}
            student["archetype"] = "practical fail, passing theory"
        elif i < 9:
            # Optional at or below the point where it starts helping.
            marks[optional] = _mark(rng, optional, 33, 45)
            student["archetype"] = "optional too low to help"
        elif i < 12:
            # Absent, alternating between a compulsory and an optional subject.
            marks["BIO" if i % 2 else optional] = ABSENT
            student["archetype"] = "absent"

        students.append(student)

    return {
        "case_id": case_id,
        "subjects": [
            {"code": c, "name": SUBJECT_NAMES[c], "practical": c in PRACTICAL_SUBJECTS}
            for c in SUBJECT_NAMES
        ],
        "compulsory": list(COMPULSORY),
        "students": students,
    }


# --- verification ------------------------------------------------------------


def invariants(results, students):
    """The four asserts from the plan, run across whatever is loaded."""
    assert all(len(s["marks"]) == 7 for s in students), "every student sits 7 subjects"
    assert all((r["letter"] == "F") == r["compulsory_failed"] for r in results), "F <=> compulsory failure"
    assert all(0.0 <= r["final_gpa"] <= 5.0 for r in results), "final GPA within 0..5"
    assert all(r["raw_gpa"] >= r["final_gpa"] for r in results), "raw GPA never below final"


def counts(results):
    return {
        "students": len(results),
        "optional_gp_le_2": sum(r["optional_weak"] for r in results),
        "compulsory_failure": sum(r["compulsory_failed"] for r in results),
        "practical_below_8": sum(r["practical_fail"] for r in results),
        "practical_fail_passing_theory": sum(r["practical_fail_passing_theory"] for r in results),
        "high_average_failure": sum(r["high_average_failure"] for r in results),
        "absent": sum(r["absent"] for r in results),
    }


TARGETS = {
    "students": 1765,
    "optional_gp_le_2": 589,
    "compulsory_failure": 525,
    "practical_below_8": 316,
    "practical_fail_passing_theory": 260,
    "high_average_failure": 75,
    "absent": 50,
}


def main():
    data = load_file()
    results = run_all(data)
    students = [s for c in data["cases"] for s in c["students"]]

    invariants(results, students)
    got = counts(results)

    print("cases: {}".format(len(data["cases"])))
    width = max(len(k) for k in got)
    ok = True
    for key, value in got.items():
        target = TARGETS[key]
        ok = ok and value == target
        print("  {} {:<{}}  got {:>5}   expected {:>5}".format(
            "OK  " if value == target else "FAIL", key, width, value, target))
    print("invariants: all green")
    print("counts: {}".format("all match" if ok else "MISMATCH"))


if __name__ == "__main__":
    main()
