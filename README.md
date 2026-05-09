# elevator-dispatch

Azure-hosted AI-enabled elevator dispatch sample built for Azure Functions.

## Lab tasks

- [ ] 00.00.add-meta-prompt
- [ ] 01.00.initialize-project
- [ ] 02.00 randomize-passenger-appearance

## What it does

This project exposes a `POST /api/dispatch` Azure Function that:

- scores a bank of elevators against a hall call
- predicts short-term traffic hotspots from time-of-day and recent demand
- surfaces an AI insight summary
- lets you change the Azure OpenAI model with configuration instead of code edits

## Configuration

Set these environment variables when deploying to Azure:

- `AZURE_OPENAI_MODEL` - model name to report and use for Azure OpenAI requests (default: `gpt-4.1-mini`)
- `AZURE_OPENAI_ENDPOINT` - optional Azure OpenAI endpoint
- `AZURE_OPENAI_API_KEY` - optional Azure OpenAI API key
- `AZURE_OPENAI_DEPLOYMENT` - optional Azure OpenAI deployment name
- `AZURE_OPENAI_API_VERSION` - optional API version override

If Azure OpenAI credentials are not provided, the app still returns a dispatch decision and a heuristic AI summary.

## Local development

Install dependencies:

```bash
python -m pip install -r /home/runner/work/elevator-dispatch/elevator-dispatch/requirements.txt
```

Run tests:

```bash
cd /home/runner/work/elevator-dispatch/elevator-dispatch && python -m unittest tests/test_dispatch.py -v
```

Example payload:

```json
{
  "request_time": "2026-04-20T08:55:00",
  "request": {
    "origin_floor": 1,
    "destination_floor": 14,
    "passengers": 3
  },
  "elevators": [
    {
      "id": "A",
      "current_floor": 1,
      "direction": "idle",
      "capacity": 12,
      "load": 0,
      "queued_stops": []
    },
    {
      "id": "B",
      "current_floor": 9,
      "direction": "down",
      "capacity": 12,
      "load": 8,
      "queued_stops": [7, 4]
    }
  ],
  "recent_calls": [
    {"origin_floor": 1, "destination_floor": 8},
    {"origin_floor": 1, "destination_floor": 16}
  ]
}
```

The response includes the assigned elevator, ranked alternatives, demand forecast, AI insight, and the active model setting.
