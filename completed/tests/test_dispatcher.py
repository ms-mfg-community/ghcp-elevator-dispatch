import unittest

from simulation.building import Building
from simulation.dispatcher import Dispatcher
from simulation.elevator import Elevator
from simulation.passenger import Passenger


class DispatcherTests(unittest.TestCase):
    def test_assigns_closest_idle_elevator(self) -> None:
        building = Building(
            elevators=[
                Elevator(id="ev-01", current_floor=1),
                Elevator(id="ev-02", current_floor=4),
            ]
        )
        dispatcher = Dispatcher()
        passenger = Passenger(origin_floor=2, destination_floor=5)

        selected = dispatcher.assign_passenger(building, passenger)

        self.assertEqual(selected, "ev-01")
        self.assertIn(2, building.elevators[0].scheduled_stops)

    def test_queues_request_when_all_elevators_are_full(self) -> None:
        building = Building(
            elevators=[
                Elevator(
                    id="ev-01",
                    current_floor=1,
                    passengers=[
                        Passenger(origin_floor=1, destination_floor=2),
                        Passenger(origin_floor=1, destination_floor=3),
                    ],
                    capacity=2,
                )
            ]
        )
        dispatcher = Dispatcher()
        passenger = Passenger(origin_floor=4, destination_floor=1)

        selected = dispatcher.assign_passenger(building, passenger)

        self.assertIsNone(selected)
        self.assertEqual(len(building.pending_passengers), 1)
        self.assertIn("full", building.status_message)


if __name__ == "__main__":
    unittest.main()
