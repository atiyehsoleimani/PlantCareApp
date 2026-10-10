"""
Shared test setup, plus the lab grader.

You don't need to change anything in this file.

Every example and exercise has its own test class in the test files, e.g.
`class TestExercise03`. An exercise is complete when ALL of its tests pass.
After the tests run, a checklist with your progress is printed.
"""

from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

import main
from models import Plant


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
def days_ago(days):
    return date.today() - timedelta(days=days)


@pytest.fixture
def client():
    """A test client talking to your API, with an empty database."""
    main.plants.clear()
    yield TestClient(main.app)
    main.plants.clear()


@pytest.fixture
def client_with_plants(client):
    """Same as `client`, but the database already holds two plants."""
    main.plants[1] = Plant(
        id=1,
        name="Monstera",
        species="Monstera deliciosa",
        water_every_days=10,
        last_watered=days_ago(2),  # next watering in 8 days
        tags=["tropical"],
    )
    main.plants[2] = Plant(
        id=2,
        name="Aloe",
        indoor=False,
        water_every_days=14,
        last_watered=days_ago(20),  # should have been watered 6 days ago!
        tags=["succulent"],
    )
    return client


# ---------------------------------------------------------------------------
# The grader: collects the result of every test per exercise and prints a
# progress report at the end. These `pytest_...` functions are "hooks":
# pytest calls them automatically at certain moments.
# ---------------------------------------------------------------------------
SECTIONS = {
    "TestExample": "Examples (already working: read these first!)",
    "TestExercise": "Exercises",
    "TestBonus": "Bonus",
}

exercises = {}  # "TestExercise03" -> {"title": ..., "tests": {test id: passed?}}
tests_ran = False


def pytest_collection_finish(session):
    """Called once pytest knows which tests will run."""
    for item in session.items:
        if item.cls is None:
            continue
        exercise = exercises.setdefault(
            item.cls.__name__, {"title": item.cls.__doc__.strip(), "tests": {}}
        )
        exercise["tests"][item.nodeid] = False


def pytest_runtest_logreport(report):
    """Called after each test phase (setup, call, teardown)."""
    global tests_ran
    tests_ran = True
    for exercise in exercises.values():
        if report.nodeid in exercise["tests"]:
            if report.when == "call" and report.passed:
                exercise["tests"][report.nodeid] = True
            if report.failed:
                exercise["tests"][report.nodeid] = False


def is_complete(name):
    return all(exercises[name]["tests"].values())


@pytest.hookimpl(wrapper=True, tryfirst=True)
def pytest_terminal_summary(terminalreporter):
    """Called at the very end: prints the progress report."""
    yield  # first let pytest print its own summary, then add ours below it
    write = terminalreporter.write_line
    terminalreporter.write_sep("=", "LAB 7 PROGRESS")

    if not tests_ran:
        write("No exercises could be run. There is probably an error in your")
        write("code that stops the tests from loading: read the error above.")
        return

    for prefix, heading in SECTIONS.items():
        names = sorted(name for name in exercises if name.startswith(prefix))
        if not names:
            continue
        write(f" {heading}")
        for name in names:
            tests = exercises[name]["tests"]
            mark = "✅" if is_complete(name) else "❌"
            passed = sum(tests.values())
            write(f"   {mark} {exercises[name]['title']:<52} {passed}/{len(tests)} tests")
        write("")

    core = [name for name in exercises if name.startswith("TestExercise")]
    bonus = [name for name in exercises if name.startswith("TestBonus")]
    if core:
        completed = sum(is_complete(name) for name in core)
        percent = round(100 * completed / len(core))
        bar = "#" * (percent // 5) + "-" * (20 - percent // 5)
        write(f" Exercises [{bar}] {completed}/{len(core)} = {percent}%")
        if completed == len(core):
            write(" 🎉 All exercises done, well done! Try the bonus next.")
    if bonus:
        write(f" Bonus: {sum(is_complete(name) for name in bonus)}/{len(bonus)}")
