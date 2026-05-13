# Coding Agent Handoff

Use this handoff when delegating the basement-level feature to GitHub Copilot Coding Agent.

## Task

Add basement support to the elevator dispatch simulation. Use floor `-1` as the internal and API value, and display it
as `B1` in the dashboard and any user-facing labels.

## Read First

- `.github/skills/add-basement-level/SKILL.md`
- `.github/skills/add-basement-level/assets/basement-floor-contract.md`
- `.github/copilot-instructions.md`

## Change Areas

- `workspace/simulation/`: building floor list, elevator allowed floors, passenger validation, dispatcher decisions,
  plus simulation ticks.
- `workspace/api/`: state response and WebSocket state serialization.
- `workspace/ui/`: TypeScript rendering, served JavaScript, and CSS for the B1 row.
- `workspace/tests/`: focused `unittest` coverage for basement passenger trips, dispatcher assignment,
  simulation lifecycle, and API state shape.
- `workspace/README.md` and `docs/prd-elevator-dispatch.md`: supported-floor documentation when relevant.

## Validation Commands

```bash
bash .github/skills/add-basement-level/scripts/validate-basement-support.sh
python -m uvicorn api.server:app --reload --port 7000
bash .github/skills/add-basement-level/scripts/check-api-basement-state.sh
```

Run the `uvicorn` command from `workspace/`, or keep using the validation script for repository-root execution.

## Pull Request Summary Checklist

- Confirm B1 is stored as floor `-1` and displayed as `B1`.
- Confirm all elevators can serve B1 and floors 1 through 5.
- Confirm passengers can start or end trips at B1.
- Confirm `/api/state` includes basement floor data.
- Confirm dashboard renders B1 at the bottom with distinct styling.
- Report validation command results.
