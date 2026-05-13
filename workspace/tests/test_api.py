import unittest

from pydantic import ValidationError

from api.server import PassengerRequest


class ApiRequestValidationTests(unittest.TestCase):
    def test_passenger_request_accepts_basement_floor(self) -> None:
        payload = PassengerRequest(origin_floor=-1, destination_floor=5)

        self.assertEqual(payload.origin_floor, -1)
        self.assertEqual(payload.destination_floor, 5)

    def test_passenger_request_rejects_unsupported_floor(self) -> None:
        with self.assertRaises(ValidationError):
            PassengerRequest(origin_floor=0, destination_floor=5)


if __name__ == "__main__":
    unittest.main()
