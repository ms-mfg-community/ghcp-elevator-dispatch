import unittest
from unittest.mock import patch

from simulation.simulation import SimulationEngine


class SpawnPassengerTests(unittest.TestCase):
    def test_spawns_passenger_when_random_below_threshold(self) -> None:
        engine = SimulationEngine(spawn_chance=0.5)
        with patch("simulation.simulation.random") as mock_random:
            mock_random.random.return_value = 0.1  # below 0.5
            mock_random.randint.return_value = 1
            mock_random.choice.return_value = 3

            engine._maybe_spawn_passenger()

        total_waiting = sum(
            len(passengers)
            for passengers in engine.building.waiting_passengers.values()
        )
        self.assertEqual(total_waiting, 1)

    def test_does_not_spawn_when_random_above_threshold(self) -> None:
        engine = SimulationEngine(spawn_chance=0.5)
        with patch("simulation.simulation.random") as mock_random:
            mock_random.random.return_value = 0.9  # above 0.5

            engine._maybe_spawn_passenger()

        total_waiting = sum(
            len(passengers)
            for passengers in engine.building.waiting_passengers.values()
        )
        self.assertEqual(total_waiting, 0)

    def test_guaranteed_spawn_with_chance_one(self) -> None:
        engine = SimulationEngine(spawn_chance=1.0)
        with patch("simulation.simulation.random") as mock_random:
            mock_random.random.return_value = 0.0
            mock_random.randint.return_value = 2
            mock_random.choice.return_value = 5

            engine._maybe_spawn_passenger()

        waiting = engine.building.waiting_passengers[2]
        self.assertEqual(len(waiting), 1)
        self.assertEqual(waiting[0].origin_floor, 2)
        self.assertEqual(waiting[0].destination_floor, 5)


if __name__ == "__main__":
    unittest.main()
