# Lab 7: a Houseplant API with FastAPI and Pydantic

In this lab you build a small but complete REST API that keeps track of
your houseplants and tells you which ones need water:

- **Part 1 (`models.py`)**: describe your data with **Pydantic** models, so
  bad data is rejected before it ever reaches your code.
- **Part 2 (`main.py`)**: use those models to build the **REST endpoints**
  (`GET`, `POST`, `PUT`, `DELETE`) with the correct status codes.
- **Bonus**: more Pydantic (custom validators, partial updates), `PATCH`,
  and filtering with query parameters.

Each part starts with a working **example** that already passes its tests.
Read it first, then do the exercises below it, following the same pattern.
The instructions for every exercise are in the comments of `models.py` and
`main.py`. Start at the top of `models.py`.

## Setup

Using the `uv` package manager (https://docs.astral.sh/uv/getting-started/installation/),
run this in this folder:

```
uv init
uv add -r requirements.txt
```

## Check your progress

```
uv run pytest
```

The tests grade your work automatically. At the end you'll see a checklist
like this:

```
================================ LAB 7 PROGRESS ================================
 Examples (already working: read these first!)
   ✅ Example 1: a Pydantic model (PlantCreate and Plant)  5/5 tests
   ✅ Example 2: GET /plants lists all plants              3/3 tests

 Exercises
   ✅ Exercise 1: PlantCreate indoor and water_every_days  8/8 tests
   ✅ Exercise 2: PlantCreate last_watered and tags        6/6 tests
   ❌ Exercise 3: GET /plants/{id} reads one plant         1/3 tests
 ...
 Exercises [######--------------] 2/6 = 33%
 Bonus: 0/5
```

An exercise is complete when all of its tests pass. The percentage counts the
six exercises only; the bonus is extra. Above the checklist, pytest shows
what went wrong in each failing test.

To run the tests of just one exercise, use `-k`:

```
uv run pytest -k Exercise03
uv run pytest -k Bonus
```

The tests live in `tests/`. Reading them is a good way to understand exactly
what is expected. Don't change them.

## Try your API by hand

```
uv run fastapi dev main.py
```

Open http://127.0.0.1:8000/docs, click an endpoint, then **Try it out**.

Or use **Bruno**: open the `bruno/` folder as a collection (**Open Collection**).
It has a request for every endpoint, including the error cases. Each one
checks its status code, and its **Docs** tab says which exercise it belongs to.
Right-click a folder and choose **Run** to send all its requests in order.

Or use curl:

```bash
# Add a plant (the server picks the id)
curl -X POST http://127.0.0.1:8000/plants \
  -H "Content-Type: application/json" \
  -d '{"name": "Monstera", "water_every_days": 10, "last_watered": "2026-09-20", "tags": ["tropical"]}'

# Send bad data and read the 422 error that Pydantic produces
curl -X POST http://127.0.0.1:8000/plants \
  -H "Content-Type: application/json" \
  -d '{"name": "", "water_every_days": 0}'

# List and read
curl http://127.0.0.1:8000/plants
curl http://127.0.0.1:8000/plants/1

# Remove
curl -i -X DELETE http://127.0.0.1:8000/plants/1

# Bonus: "I just watered it", changing only one field
curl -X PATCH http://127.0.0.1:8000/plants/1 \
  -H "Content-Type: application/json" \
  -d '{"last_watered": "2026-09-27"}'

# Bonus: which plants need water today?
curl "http://127.0.0.1:8000/plants?due_within_days=0"
```

## The exercises

| #         | File        | You learn                                                        |
|-----------|-------------|------------------------------------------------------------------|
| Example 1 | `models.py` | A model: required and optional fields, `Field(...)` rules, inheritance |
| 1         | `models.py` | More fields, defaults, number ranges, how Pydantic converts values |
| 2         | `models.py` | Dates and lists, and turning them back into JSON                 |
| Example 2 | `main.py`   | An endpoint: `GET` a collection                                  |
| 3         | `main.py`   | `GET` one resource, `404 Not Found`                              |
| 4         | `main.py`   | `POST`, `201 Created`, the server chooses the id, free `422`     |
| 5         | `main.py`   | `PUT` replaces the whole resource                                |
| 6         | `main.py`   | `DELETE`, `204 No Content`, writing an endpoint from scratch     |
| Bonus 1   | `models.py` | Writing your own checks with `@field_validator`                  |
| Bonus 2   | `models.py` | Rejecting unknown fields (catching typos)                        |
| Bonus 3   | `models.py` | A model where everything is optional (for `PATCH`)               |
| Bonus 4   | `main.py`   | `PATCH` changes only what was sent                               |
| Bonus 5   | `main.py`   | Query parameters: which plants need water soon?                  |

## What's different from the last lesson's `users.py`?

Compare your finished API with `users.py` from the FastAPI lesson:

- There the **client** sent the `id`. Here the **server** chooses it, so two
  clients can never create two plants with the same id.
- There, `PUT /users/3` changed "the third user in the list", not "the user
  with id 3". Here plants are stored by id, so the id in the URL always means
  the same plant, even after others are deleted.
- There, `POST` returned the whole list. Here it returns the created plant
  with `201 Created`, which is what REST clients expect.
- Unknown ids now answer `404` everywhere instead of crashing with a `500`.
