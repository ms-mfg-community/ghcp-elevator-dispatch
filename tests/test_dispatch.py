import os
import unittest
from unittest.mock import patch

from elevator_dispatch.ai import AzureOpenAISettings
from elevator_dispatch.dispatch import build_dispatch_plan, forecast_demand


class DispatchPlanTests(unittest.TestCase):
    def test_dispatch_prefers_car_aligned_with_direction_and_capacity(self) -> None:
        payload = {
            "request": {"origin_floor": 3, "destination_floor": 12, "passengers": 2},
            "elevators": [
                {
                    "id": "A",
                    "current_floor": 2,
                    "direction": "up",
                    "capacity": 10,
                    "load": 3,
                    "queued_stops": [6],
                },
                {
                    "id": "B",
                    "current_floor": 3,
                    "direction": "down",
                    "capacity": 10,
                    "load": 1,
                    "queued_stops": [],
                },
            ],
            "request_time": "2026-04-20T08:55:00",
        }

        result = build_dispatch_plan(payload, AzureOpenAISettings(model="gpt-4.1"))

        self.assertEqual(result["assigned_elevator"], "A")
        self.assertEqual(result["model_used"], "gpt-4.1")

    def test_forecast_marks_lobby_during_morning_peak(self) -> None:
        forecast = forecast_demand("2026-04-20T08:15:00", recent_calls=None)

        self.assertEqual(forecast["traffic_mode"], "morning-up-peak")
        self.assertIn(1, forecast["predicted_hotspots"])

    def test_model_setting_can_be_changed_by_environment(self) -> None:
        payload = {
            "request": {"origin_floor": 1, "destination_floor": 9},
            "elevators": [{"id": "A", "current_floor": 1, "direction": "idle"}],
        }

        with patch.dict(os.environ, {"AZURE_OPENAI_MODEL": "gpt-4.1"}, clear=False):
            result = build_dispatch_plan(payload)

        self.assertEqual(result["model_used"], "gpt-4.1")
        self.assertEqual(result["ai_insight"]["model"], "gpt-4.1")


if __name__ == "__main__":
    unittest.main()
