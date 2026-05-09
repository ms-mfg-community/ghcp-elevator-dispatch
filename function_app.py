from __future__ import annotations

import json

import azure.functions as func

from elevator_dispatch import AzureOpenAISettings, build_dispatch_plan

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


@app.function_name(name="dispatch_elevator")
@app.route(route="dispatch", methods=["POST"])
def dispatch_elevator(req: func.HttpRequest) -> func.HttpResponse:
    try:
        payload = req.get_json()
        result = build_dispatch_plan(payload, AzureOpenAISettings.from_env())
        return func.HttpResponse(
            json.dumps(result, indent=2),
            mimetype="application/json",
            status_code=200,
        )
    except ValueError as exc:
        return func.HttpResponse(
            json.dumps({"error": str(exc)}),
            mimetype="application/json",
            status_code=400,
        )
