"""
Part 3: bonus exercises (models.py and main.py)

Only start these once Exercises 1-6 are green.
"""

from datetime import date, timedelta

import pytest
from pydantic import ValidationError

import main
from models import Plant, PlantCreate, PlantUpdate


def days_ago(days):
    return (date.today() - timedelta(days=days)).isoformat()


class TestBonus1:
    """Bonus 1: PlantCreate custom validators"""

    def test_spaces_around_name_are_removed(self):
        assert PlantCreate(name="  Monstera  ").name == "Monstera"

    def test_blank_name_is_rejected_with_a_clear_message(self):
        with pytest.raises(ValidationError, match="name must not be blank"):
            PlantCreate(name="     ")

    def test_watered_today_is_fine(self):
        plant = PlantCreate(name="Monstera", last_watered=date.today())
        assert plant.last_watered == date.today()

    def test_watered_in_the_future_is_rejected(self):
        tomorrow = date.today() + timedelta(days=1)
        with pytest.raises(ValidationError, match="last_watered cannot be in the future"):
            PlantCreate(name="Monstera", last_watered=tomorrow)

    def test_validators_are_inherited_by_plant(self):
        with pytest.raises(ValidationError):
            Plant(id=1, name="   ")


class TestBonus2:
    """Bonus 2: PlantCreate rejects unknown fields"""

    def test_typo_in_field_name_is_rejected(self):
        with pytest.raises(ValidationError):
            PlantCreate(name="Monstera", indor=False)

    def test_client_cannot_send_its_own_id(self, client):
        response = client.post("/plants", json={"name": "Monstera", "id": 42})
        assert response.status_code == 422


class TestBonus3:
    """Bonus 3: PlantUpdate with only optional fields"""

    def test_every_field_is_optional(self):
        update = PlantUpdate()
        for field in ["name", "species", "indoor", "water_every_days", "last_watered", "tags"]:
            assert getattr(update, field) is None, f"{field} should default to None"

    def test_only_the_fields_that_were_sent_are_dumped(self):
        update = PlantUpdate(indoor=False)
        assert update.model_dump(exclude_unset=True) == {"indoor": False}

    def test_rules_still_apply_to_fields_that_are_sent(self):
        with pytest.raises(ValidationError):
            PlantUpdate(water_every_days=0)
        with pytest.raises(ValidationError):
            PlantUpdate(name="")

    def test_unknown_fields_are_rejected(self):
        with pytest.raises(ValidationError):
            PlantUpdate(colour="green")


class TestBonus4:
    """Bonus 4: PATCH /plants/{id} updates some fields"""

    def test_watering_a_plant_changes_only_last_watered(self, client_with_plants):
        response = client_with_plants.patch("/plants/1", json={"last_watered": days_ago(0)})
        assert response.status_code == 200
        plant = response.json()
        assert plant["last_watered"] == days_ago(0)
        assert plant["name"] == "Monstera", "fields that were not sent must not change"
        assert plant["water_every_days"] == 10, "fields that were not sent must not change"
        assert plant["tags"] == ["tropical"], "fields that were not sent must not change"

    def test_patch_is_stored(self, client_with_plants):
        client_with_plants.patch("/plants/2", json={"indoor": True})
        assert main.plants[2].indoor is True

    def test_unknown_id_gives_404(self, client_with_plants):
        response = client_with_plants.patch("/plants/99", json={"indoor": True})
        assert response.status_code == 404
        assert response.json() == {"detail": "Plant not found"}

    def test_invalid_value_gives_422(self, client_with_plants):
        response = client_with_plants.patch("/plants/1", json={"water_every_days": 0})
        assert response.status_code == 422


class TestBonus5:
    """Bonus 5: GET /plants with query filters"""

    def names(self, client, url):
        response = client.get(url)
        assert response.status_code == 200
        return [plant["name"] for plant in response.json()]

    def test_filter_by_indoor(self, client_with_plants):
        assert self.names(client_with_plants, "/plants?indoor=true") == ["Monstera"]
        assert self.names(client_with_plants, "/plants?indoor=false") == ["Aloe"]

    def test_filter_by_tag(self, client_with_plants):
        assert self.names(client_with_plants, "/plants?tag=succulent") == ["Aloe"]
        assert self.names(client_with_plants, "/plants?tag=cactus") == []

    def test_due_within_0_days_means_today_or_overdue(self, client_with_plants):
        # Aloe is 6 days overdue, Monstera needs water in 8 days
        assert self.names(client_with_plants, "/plants?due_within_days=0") == ["Aloe"]

    def test_due_within_more_days(self, client_with_plants):
        assert self.names(client_with_plants, "/plants?due_within_days=7") == ["Aloe"]
        assert self.names(client_with_plants, "/plants?due_within_days=8") == [
            "Monstera",
            "Aloe",
        ]

    def test_never_watered_plant_is_due_today(self, client):
        main.plants[1] = Plant(id=1, name="Basil")
        assert self.names(client, "/plants?due_within_days=0") == ["Basil"]

    def test_filters_can_be_combined(self, client_with_plants):
        assert self.names(client_with_plants, "/plants?indoor=true&due_within_days=0") == []

    def test_due_within_days_out_of_range_gives_422(self, client_with_plants):
        assert client_with_plants.get("/plants?due_within_days=-1").status_code == 422
        assert client_with_plants.get("/plants?due_within_days=61").status_code == 422
