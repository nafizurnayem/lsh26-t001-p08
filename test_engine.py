"""Hand-checked cases and the four invariants, runnable with `python test_engine.py`.

No pytest dependency: the deploy target only installs streamlit and pandas.
"""

import engine


def student(optional="REL", **marks):
    base = {
        "BAN": 80, "ENG": 80, "MAT": 80,
        "PHY": {"theory": 60, "practical": 20},
        "CHE": {"theory": 60, "practical": 20},
        "BIO": {"theory": 60, "practical": 20},
        optional: 80 if optional == "REL" else {"theory": 60, "practical": 20},
    }
    base.update(marks)
    return {"id": "T", "name": "Test", "class": "Class 9", "optional": optional, "marks": base}


def result(**kwargs):
    return engine.student_result(student(**kwargs), engine.COMPULSORY)


CHECKS = []


def check(name):
    def wrap(fn):
        CHECKS.append((name, fn))
        return fn

    return wrap


# --- rule table --------------------------------------------------------------


@check("grade table boundaries")
def _():
    assert engine.grade_point(100) == 5.0
    assert engine.grade_point(80) == 5.0
    assert engine.grade_point(79) == 4.0
    assert engine.grade_point(33) == 1.0
    assert engine.grade_point(32) == 0.0
    assert engine.grade_point(0) == 0.0


@check("A+ is exactly 5.00, 4.99 is an A")
def _():
    assert engine.band(5.0) == "A+"
    assert engine.band(4.99) == "A"
    assert engine.band(4.00) == "A"
    assert engine.band(3.99) == "A-"
    assert engine.band(3.00) == "B"
    assert engine.band(2.00) == "C"
    assert engine.band(1.00) == "D"
    assert engine.band(0.99) == "F"


@check("rounding is half-up, always two decimals")
def _():
    assert engine.fmt(4.125) == "4.13"       # round() would give 4.12
    assert engine.fmt(4.375) == "4.38"
    assert engine.fmt(5.0) == "5.00"
    assert engine.fmt(0.0) == "0.00"


# --- trap 1: part fail is checked before the table ---------------------------


@check("theory 24 with practical 25 totals 49 but scores zero (R-11)")
def _():
    row = engine.subject_row("PHY", {"theory": 24, "practical": 25}, True, True)
    assert row["total"] == 49
    assert row["gp"] == 0.0
    assert row["rule"] == "R-11"


@check("practical 7 behind a passing theory scores zero (R-11)")
def _():
    row = engine.subject_row("CHE", {"theory": 60, "practical": 7}, True, True)
    assert row["gp"] == 0.0 and row["rule"] == "R-11"


@check("theory 25 and practical 8 exactly is a pass, table applies (R-10)")
def _():
    row = engine.subject_row("PHY", {"theory": 25, "practical": 8}, True, True)
    assert row["rule"] == "R-10" and row["gp"] == 1.0   # total 33


# --- trap 9: AB never reaches a numeric comparison ---------------------------


@check("absent in a practical subject does not crash and scores zero (R-12)")
def _():
    row = engine.subject_row("BIO", "AB", True, True)
    assert row["gp"] == 0.0 and row["rule"] == "R-12" and row["mark_used"] == "AB"


# --- student-level rules -----------------------------------------------------


@check("clean A+: six 5.0s and a strong optional caps at 5.00")
def _():
    r = result(optional="REL", REL=95)
    assert r["final_gpa_str"] == "5.00" and r["letter"] == "A+"
    assert r["raw_gpa"] == 5.0


@check("optional bonus never goes negative (trap 7)")
def _():
    low = result(optional="REL", REL=35)     # optional gp 1.0, adds nothing
    none_ = result(optional="REL", REL=45)   # optional gp 2.0, adds nothing
    assert low["raw_gpa"] == none_["raw_gpa"]
    assert low["optional_weak"] and none_["optional_weak"]


@check("optional failure never fails the student (trap 2)")
def _():
    r = result(optional="REL", REL="AB")
    assert not r["compulsory_failed"]
    assert r["letter"] != "F"
    assert r["absent"] and r["optional_weak"]


@check("one compulsory zero cancels a strong average (R-13)")
def _():
    r = result(MAT=20)
    assert r["raw_gpa"] >= 3.50
    assert r["final_gpa_str"] == "0.00" and r["letter"] == "F"
    assert r["culprit_subjects"] == ["MAT"]
    assert r["high_average_failure"]


@check("compulsory absence fails the result (R-12)")
def _():
    r = result(BIO="AB")
    assert r["letter"] == "F" and r["culprit_subjects"] == ["BIO"]


@check("divide by six, not seven (trap 8)")
def _():
    # Compulsory grade points: 4.0 4.0 4.0 3.5 3.5 3.5 = 22.5. Optional 5.0 -> bonus 3.0.
    r = result(
        optional="REL",
        BAN=70, ENG=70, MAT=70,
        PHY={"theory": 45, "practical": 20},
        CHE={"theory": 45, "practical": 20},
        BIO={"theory": 45, "practical": 20},
        REL=85,
    )
    assert r["subject_gps"]["BAN"] == 4.0 and r["subject_gps"]["PHY"] == 3.5
    assert r["optional_gp"] == 5.0
    assert r["raw_gpa"] == (22.5 + 3.0) / 6            # not / 7
    assert r["final_gpa_str"] == "4.25" and r["letter"] == "A"


@check("cap applies before rounding (trap 4)")
def _():
    r = result(optional="REL", REL=100)                # 6 x 5.0 + bonus 3.0 = 33 / 6 = 5.5
    assert r["raw_gpa"] == 5.0 and r["final_gpa_str"] == "5.00"


# --- generator and dataset ---------------------------------------------------


@check("generated cohort has 60 students, two classes, all four archetypes")
def _():
    case = engine.generate_cohort(seed=7, size=60)
    results = engine.run_case(case)
    engine.invariants(results, case["students"])
    assert len(case["students"]) == 60
    assert len({s["class"] for s in case["students"]}) == 2
    assert sum(r["high_average_failure"] for r in results) >= 1
    assert sum(r["practical_fail_passing_theory"] for r in results) >= 1
    assert sum(r["optional_weak"] for r in results) >= 1
    assert sum(r["absent"] for r in results) >= 1


@check("all 25 supplied cases match the published counts")
def _():
    data = engine.load_file()
    results = engine.run_all(data)
    students = [s for c in data["cases"] for s in c["students"]]
    engine.invariants(results, students)
    assert engine.counts(results) == engine.TARGETS


@check("checking lists overlap rather than exclude (R-29)")
def _():
    data = engine.load_file()
    results = engine.run_all(data)
    lists = engine.checking_lists(results)
    ids = [set(id(r) for r in lists[k]) for k in ("optional", "practical_fail", "absent")]
    assert any(a & b for i, a in enumerate(ids) for b in ids[i + 1:]), "lists must be independent passes"


def main():
    failures = 0
    for name, fn in CHECKS:
        try:
            fn()
            print("PASS  {}".format(name))
        except AssertionError as exc:
            failures += 1
            print("FAIL  {}  -- {}".format(name, exc))
    print("\n{}/{} checks passed".format(len(CHECKS) - failures, len(CHECKS)))
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
