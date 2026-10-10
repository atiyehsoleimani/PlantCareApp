"""
Part 1: Pydantic models (models.py)

These tests create models directly, without any web server. That's how you
can check your validation rules quickly.

    pytest.raises(ValidationError)  ->  "this data MUST be rejected"
"""

from datetime import date

import pytest
from pydantic import ValidationError

from models import Plant, PlantCreate


class TestExample1:
    """Example 1: a Pydantic model (PlantCreate and Plant)"""

    def test_only_name_is_needed(self):
        plant = PlantCreate(name="Monstera")
        assert plant.name == "Monstera"
        assert plant.species is None

    def test_optional_field_can_be_given(self):
        plant = PlantCreate(name="Monstera", species="Monstera deliciosa")
        assert plant.species == "Monstera deliciosa"

    def test_name_is_required(self):
        with pytest.raises(ValidationError):
            PlantCreate(species="a plant without a name")

    def test_name_must_be_1_to_50_characters(self):
        with pytest.raises(ValidationError):
            PlantCreate(name="")
        with pytest.raises(ValidationError):
            PlantCreate(name="x" * 51)

    def test_plant_is_a_plant_create_with_an_id(self):
        plant = Plant(id=1, name="Monstera")
        assert plant.id == 1
        assert plant.name == "Monstera"
        with pytest.raises(ValidationError):
            Plant(name="Monstera")  # no id


class TestExercise01:
    """Exercise 1: PlantCreate indoor and water_every_days"""

    def test_defaults(self):
        plant = PlantCreate(name="Monstera")
        assert plant.indoor is True, "indoor should default to True"
        assert plant.water_every_days == 7, "water_every_days should default to 7"

    def test_values_can_be_given(self):
        plant = PlantCreate(name="Aloe", indoor=False, water_every_days=14)
        assert plant.indoor is False
        assert plant.water_every_days == 14

    def test_values_are_converted_to_the_right_type(self):
        # JSON from a client is often "stringly typed": Pydantic converts it.
        plant = PlantCreate(name="Aloe", indoor="false", water_every_days="14")
        assert plant.indoor is False
        assert plant.water_every_days == 14

    def test_nonsense_values_are_rejected(self):
        with pytest.raises(ValidationError):
            PlantCreate(name="Aloe", indoor="sometimes")
        with pytest.raises(ValidationError):
            PlantCreate(name="Aloe", water_every_days="often")

    def test_water_every_1_and_60_days_are_allowed(self):
        assert PlantCreate(name="Aloe", water_every_days=1).water_every_days == 1
        assert PlantCreate(name="Aloe", water_every_days=60).water_every_days == 60

    @pytest.mark.parametrize("days", [0, 61, -3])
    def test_water_every_days_outside_1_to_60_is_rejected(self, days):
        with pytest.raises(ValidationError):
            PlantCreate(name="Aloe", water_every_days=days)


class TestExercise02:
    """Exercise 2: PlantCreate last_watered and tags"""

    def test_defaults(self):
        plant = PlantCreate(name="Monstera")
        assert plant.last_watered is None, "last_watered should default to None"
        assert plant.tags == [], "tags should default to []"

    def test_date_string_becomes_a_date_object(self):
        plant = PlantCreate(name="Monstera", last_watered="2026-01-15")
        assert plant.last_watered == date(2026, 1, 15)

    def test_invalid_date_is_rejected(self):
        with pytest.raises(ValidationError):
            PlantCreate(name="Monstera", last_watered="2026-13-45")

    def test_tags_are_a_list_of_strings(self):
        plant = PlantCreate(name="Aloe", tags=["succulent", "pet-safe"])
        assert plant.tags == ["succulent", "pet-safe"]

    def test_tags_must_be_a_list(self):
        with pytest.raises(ValidationError):
            PlantCreate(name="Aloe", tags="succulent")

    def test_model_dump_turns_the_date_back_into_json(self):
        plant = PlantCreate(name="Monstera", last_watered=date(2026, 1, 15))
        assert plant.model_dump(mode="json")["last_watered"] == "2026-01-15"
