import unittest

from entities.plants.plant import Plant


class PlantVarietyTests(unittest.TestCase):
    def test_plants_have_distinct_variations_by_position(self):
        plant_a = Plant(x=4, y=10)
        plant_b = Plant(x=5, y=10)

        self.assertNotEqual(plant_a.variation, plant_b.variation)


if __name__ == "__main__":
    unittest.main()
