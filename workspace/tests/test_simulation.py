import unittest
from unittest.mock import patch

from simulation.passenger import Passenger
from simulation.simulation import SimulationEngine


class SpawnPassengerTests(unittest.TestCase):
    def test_passenger_allows_basement_trips(self) -> None:
        passenger_from_basement = Passenger(origin_floor=-1, destination_floor=3)
        passenger_to_basement = Passenger(origin_floor=4, destination_floor=-1)

        self.assertEqual(passenger_from_basement.origin_floor, -1)
        self.assertEqual(passenger_to_basement.destination_floor, -1)

    def test_passenger_rejects_unsupported_floor(self) -> None:
        with self.assertRaises(ValueError):
            Passenger(origin_floor=0, destination_floor=3)

    def test_snapshot_includes_basement_with_label(self) -> None:
        engine = SimulationEngine(spawn_chance=0.0)

        floors = engine.building.snapshot()["floors"]

        self.assertEqual([floor["floor"] for floor in floors], [5, 4, 3, 2, 1, -1])
        self.assertEqual(floors[-1]["label"], "B1")

    def test_spawns_passenger_when_random_below_threshold(self) -> None:
        engine = SimulationEngine(spawn_chance=0.5)
        with patch("simulation.simulation.random") as mock_random:
            mock_random.random.return_value = 0.1  # below 0.5
            mock_random.choice.side_effect = [1, 3]

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
            mock_random.choice.side_effect = [2, 5]

            engine._maybe_spawn_passenger()

        waiting = engine.building.waiting_passengers[2]
        self.assertEqual(len(waiting), 1)
        self.assertEqual(waiting[0].origin_floor, 2)
        self.assertEqual(waiting[0].destination_floor, 5)

    def test_guaranteed_spawn_can_start_at_basement(self) -> None:
        engine = SimulationEngine(spawn_chance=1.0)
        with patch("simulation.simulation.random") as mock_random:
            mock_random.random.return_value = 0.0
            mock_random.choice.side_effect = [-1, 4]

            engine._maybe_spawn_passenger()

        waiting = engine.building.waiting_passengers[-1]
        self.assertEqual(len(waiting), 1)
        self.assertEqual(waiting[0].origin_floor, -1)
        self.assertEqual(waiting[0].destination_floor, 4)

    def test_elevator_moves_between_floor_one_and_basement(self) -> None:
        engine = SimulationEngine(spawn_chance=0.0)
        elevator = engine.building.elevators[0]
        elevator.current_floor = 1
        elevator.add_stop(-1)

        engine._advance_elevator(elevator)

        self.assertEqual(elevator.current_floor, -1)
        self.assertEqual(elevator.direction, "down")

    def test_counts_passengers_moved_when_they_exit(self) -> None:
        engine = SimulationEngine(spawn_chance=0.0)
        elevator = engine.building.elevators[0]
        elevator.current_floor = 5
        elevator.passengers = [Passenger(origin_floor=1, destination_floor=5)]
        elevator.add_stop(5)

        engine._advance_elevator(elevator)

        self.assertEqual(elevator.passengers_moved, 1)
        self.assertEqual(engine.building.snapshot()["elevators"][0]["passengers_moved"], 1)

    def test_average_wait_time_refreshes_every_sixty_seconds(self) -> None:
        engine = SimulationEngine(tick_interval=10.0, spawn_chance=0.0)
        elevator = engine.building.elevators[0]
        passenger = Passenger(origin_floor=3, destination_floor=5, requested_tick=1)
        engine.building.tick = 4
        engine.building.add_passenger(passenger)
        elevator.current_floor = 3
        elevator.add_stop(3)

        engine._advance_elevator(elevator)
        engine._maybe_refresh_average_wait_time()

        self.assertEqual(engine.building.average_passenger_wait_time_seconds, 0.0)

        engine.building.tick = 6
        engine._maybe_refresh_average_wait_time()

        snapshot = engine.building.snapshot()
        self.assertEqual(snapshot["average_passenger_wait_time_seconds"], 30.0)
        self.assertEqual(snapshot["wait_time_updated_tick"], 6)

    def test_simulation_finishes_at_max_ticks(self) -> None:
        engine = SimulationEngine(spawn_chance=0.0, max_ticks=5)
        engine.building.tick = 4

        engine.building.tick += 1
        engine.dispatcher.dispatch_pending(engine.building)
        for elevator in engine.building.elevators:
            engine._advance_elevator(elevator)
        engine._maybe_spawn_passenger()
        engine._maybe_refresh_average_wait_time()

        if engine.building.tick >= engine.max_ticks:
            engine.building.paused = True
            engine.building.finished = True
            engine.building.status_message = (
                f"Simulation complete \u2014 maximum of {engine.max_ticks:,} ticks reached."
            )

        snapshot = engine.building.snapshot()
        self.assertTrue(snapshot["paused"])
        self.assertTrue(snapshot["finished"])
        self.assertIn("complete", str(snapshot["status_message"]))
        self.assertEqual(snapshot["tick"], 5)


if __name__ == "__main__":
    unittest.main()
