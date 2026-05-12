---
applyTo: "workspace/tests/**/*.py"
description: "This file defines conventions and standards for unit tests in the elevator dispatch simulation solution."
---

# Test Conventions

- Use `unittest.TestCase` as the base class for all test
  classes.
- Use specific assert methods (`assertEqual`,
  `assertIsNone`, `assertIn`, `assertRaises`) instead of
  generic `assertTrue` or `assertFalse` comparisons.
- Mock `simulation.simulation.random` with
  `unittest.mock.patch` when testing passenger spawning
  to keep results deterministic.
- Create test fixtures inline in each test method. Do not
  use shared module-level state or `setUp` for building
  or engine instances — each test must be self-contained.
- Do not import or depend on a database, network, or
  filesystem. Tests run against the in-memory simulation
  only.
- Name test methods with the pattern
  `test_<what>_<condition>` — for example,
  `test_assigns_closest_idle_elevator` or
  `test_does_not_spawn_when_random_above_threshold`.
- When constructing test passengers, always supply both
  `origin_floor` and `destination_floor` explicitly.
  Never rely on defaults.
- Prefer testing observable outcomes (snapshot values,
  list lengths, status messages) over internal state that
  may change during refactoring.
