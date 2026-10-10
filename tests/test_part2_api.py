"""
Part 2: the REST API (main.py)

These tests send real HTTP requests to your API through FastAPI's TestClient,
just like Postman or curl would, and check the status code and JSON body.

Fixtures (see conftest.py):
    client               an API with an empty database
    client_with_plants   an API that already has two plants:
      id 1: "Monstera"  indoor,  water every 10 days, watered 2 days ago,  tags ["tropical"]
      id 2: "Aloe"      outdoor, water every 14 days, watered 20 days ago, tags ["succulent"]
"""

from datetime import date, timedelta

import main
from models import Plant


def days_ago(days):
    return (date.today() - timedelta(days=days)).isoformat()


class TestExample2:
    """Example 2: GET /plants lists all plants"""

    def test_empty_list_at_start(self, client):
        response = client.get("/plants")
        assert response.status_code == 200
        assert response.json() == []

    def test_lists_every_plant(self, client):
        # Arrange: put two plants straight into the "database"
        main.plants[1] = Plant(id=1, name="Monstera")
        main.plants[2] = Plant(id=2, name="Aloe")
        # Act: send the request
        response = client.get("/plants")
        # Assert: check status code and JSON body
        assert response.status_code == 200
        names = [plant["name"] for plant in response.json()]
        assert names == ["Monstera", "Aloe"]

    def test_plants_are_sent_as_json_objects(self, client):
        main.plants[1] = Plant(id=1, name="Monstera", species="Monstera deliciosa")
        first = client.get("/plants").json()[0]
        assert first["id"] == 1
        assert first["name"] == "Monstera"
        assert first["species"] == "Monstera deliciosa"


class TestExercise03:
    """Exercise 3: GET /plants/{id} reads one plant"""

    def test_get_existing_plant(self, client_with_plants):
        response = client_with_plants.get("/plants/2")
        assert response.status_code == 200
        assert response.json() == {
            "id": 2,
            "name": "Aloe",
            "species": None,
            "indoor": False,
            "water_every_days": 14,
            "last_watered": days_ago(20),
            "tags": ["succulent"],
        }

    def test_unknown_id_gives_404(self, client_with_plants):
        response = client_with_plants.get("/plants/99")
        assert response.status_code == 404
        assert response.json() == {"detail": "Plant not found"}

    def test_id_that_is_not_a_number_gives_422(self, client):
        # You get this one for free: FastAPI checks `plant_id: int` for you.
        response = client.get("/plants/abc")
        assert response.status_code == 422


class TestExercise04:
    """Exercise 4: POST /plants adds a plant"""

    def test_create_returns_201_and_the_new_plant(self, client):
        response = client.post("/plants", json={"name": "Monstera"})
        assert response.status_code == 201, "a successful create answers 201 Created"
        assert response.json() == {
            "id": 1,
            "name": "Monstera",
            "species": None,
            "indoor": True,
            "water_every_days": 7,
            "last_watered": None,
            "tags": [],
        }

    def test_server_picks_increasing_ids(self, client):
        first = client.post("/plants", json={"name": "Monstera"}).json()
        second = client.post("/plants", json={"name": "Aloe"}).json()
        assert first["id"] == 1
        assert second["id"] == 2

    def test_new_id_follows_existing_plants(self, client_with_plants):
        response = client_with_plants.post("/plants", json={"name": "Basil"})
        assert response.json()["id"] == 3

    def test_created_plant_is_stored(self, client):
        client.post("/plants", json={"name": "Basil", "last_watered": "2026-01-15"})
        assert len(main.plants) == 1
        assert main.plants[1].name == "Basil"
        assert main.plants[1].last_watered == date(2026, 1, 15)

    def test_invalid_body_gives_422_and_nothing_is_stored(self, client):
        response = client.post("/plants", json={"name": "", "water_every_days": 0})
        assert response.status_code == 422
        # FastAPI explains every problem: one error for name, one for water_every_days
        assert len(response.json()["detail"]) == 2
        assert main.plants == {}


class TestExercise05:
    """Exercise 5: PUT /plants/{id} replaces a plant"""

    def test_replace_existing_plant(self, client_with_plants):
        response = client_with_plants.put("/plants/1", json={"name": "Big Monstera"})
        assert response.status_code == 200
        assert response.json()["id"] == 1
        assert response.json()["name"] == "Big Monstera"

    def test_put_replaces_the_whole_plant(self, client_with_plants):
        # Fields that are not sent go back to their defaults
        client_with_plants.put("/plants/1", json={"name": "Big Monstera"})
        stored = main.plants[1]
        assert stored.tags == []
        assert stored.water_every_days == 7
        assert stored.last_watered is None

    def test_unknown_id_gives_404(self, client_with_plants):
        response = client_with_plants.put("/plants/99", json={"name": "Nope"})
        assert response.status_code == 404
        assert response.json() == {"detail": "Plant not found"}
        assert 99 not in main.plants, "PUT must not create new plants"

    def test_put_needs_a_complete_body(self, client_with_plants):
        response = client_with_plants.put("/plants/1", json={"indoor": False})
        assert response.status_code == 422


class TestExercise06:
    """Exercise 6: DELETE /plants/{id} removes a plant"""

    def test_delete_returns_204_with_empty_body(self, client_with_plants):
        response = client_with_plants.delete("/plants/1")
        assert response.status_code == 204
        assert response.content == b""

    def test_deleted_plant_is_gone(self, client_with_plants):
        client_with_plants.delete("/plants/1")
        assert list(main.plants) == [2]

    def test_unknown_id_gives_404(self, client_with_plants):
        response = client_with_plants.delete("/plants/99")
        assert response.status_code == 404
        assert response.json() == {"detail": "Plant not found"}
