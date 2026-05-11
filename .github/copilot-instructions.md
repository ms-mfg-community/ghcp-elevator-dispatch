# Copilot Instructions

This repository is a workshop project for an elevator dispatch simulation. Keep generated application code under the top-level `workspace/` directory unless the user explicitly asks to change repository-level docs, prompt files, or configuration.

## Project Shape

- Treat `workspace/` as the application root.
- The backend is a Python 3.10+ FastAPI app in `workspace/api/`.
- The simulation domain model lives in `workspace/simulation/`.
- Browser UI files live in `workspace/ui/`; `workspace/ui/templates/index.html` serves the page and `workspace/ui/static/` contains served assets.
- Tests live in `workspace/tests/` and use the Python standard library `unittest` framework.

## Architecture Guidelines

- Keep simulation state in memory. Do not add a database, authentication system, queue service, or persistent storage unless the user asks.
- Preserve the educational starter-project style: small modules, clear names, explicit state transitions, and simple heuristics that are easy to explain in a workshop.
- Keep dispatch behavior isolated in `workspace/simulation/dispatcher.py` and simulation tick/lifecycle behavior in `workspace/simulation/simulation.py`.
- Keep API request validation in `workspace/api/server.py` using Pydantic models and FastAPI route handlers.
- Maintain the 5-floor, 4-elevator default scenario unless a prompt explicitly changes those requirements.
- Use straightforward scheduling heuristics; do not introduce ML or optimization libraries for dispatch logic.

## Python Conventions

- Always use a Python virtual environment (`python -m venv .venv`) inside `workspace/`. Do not install packages into the global Python environment.
- Use type hints and dataclasses consistently with the existing simulation modules.
- Prefer async-safe access through `SimulationEngine` methods when API code reads or mutates building state.
- Do not bypass the engine lock for state mutations that can be reached from FastAPI routes or WebSocket updates.
- Raise clear validation errors for invalid floor numbers and same-floor passenger trips.
- Add or update `unittest` tests for dispatch, passenger validation, simulation ticks, and API-adjacent behavior when changing those areas.

## Frontend Conventions

- Keep the UI framework-free unless the user asks for a framework.
- The served JavaScript is `workspace/ui/static/main.js`. If changing TypeScript source in `workspace/ui/main.ts`, also ensure the served JavaScript stays in sync by running the TypeScript build or making the equivalent update.
- Preserve the dashboard plus live building visualization: elevator cabs, floors, shafts, waiting passenger dots, riding passenger dots, and status controls.
- Keep CSS responsive and compatible with modern desktop and mobile browsers.

## Product Requirements Documents

- Store product requirements documents in the top-level `docs/` folder.
- Name PRD files with the pattern `prd-document-name.md`, using lowercase kebab-case after the `prd-` prefix. Examples: `docs/prd-postgres-event-log.md`, `docs/prd-dashboard-analytics.md`.
- Keep PRDs implementation-oriented enough for Copilot to generate code, tests, and documentation from them, but avoid prescribing unnecessary internal details before the design is understood.
- Treat PRDs as living documents. Update acceptance criteria, risks, dependencies, and decisions when requirements change.
- Link related prompts, issues, screenshots, diagrams, or prototype assets when they materially affect the requirements.

Use this template when the user asks to create a PRD or when a feature request is broad enough to need product-level clarification:

```markdown
# Product Requirements Document: <Feature or Initiative Name>

## Document Control

- File name: `docs/prd-<document-name>.md`
- Owner: <name or role>
- Stakeholders: <names or roles>
- Status: Draft | In review | Approved | Deprecated
- Created: <YYYY-MM-DD>
- Last updated: <YYYY-MM-DD>
- Target release or lab milestone: <release, sprint, workshop lab, or N/A>

## Summary

Briefly describe the feature, initiative, or product change in one or two paragraphs. State what will exist when the work is done and why it matters to the workshop or product.

## Problem Statement

Describe the user, learner, operator, or developer problem being solved. Include current pain points, limitations, missing capabilities, or learning gaps.

## Goals

- <Goal 1: measurable or observable outcome>
- <Goal 2>
- <Goal 3>

## Non-Goals

- <Explicitly out-of-scope item 1>
- <Explicitly out-of-scope item 2>
- <Explicitly out-of-scope item 3>

## Users and Personas

| Persona | Needs | Success Looks Like |
| --- | --- | --- |
| <persona> | <need> | <observable result> |

## Use Cases

### Use Case 1: <Name>

- Actor: <user or system>
- Trigger: <event or action>
- Preconditions: <required state>
- Main flow:
	1. <step>
	2. <step>
	3. <step>
- Alternate or error flows:
	- <condition and expected behavior>
- Outcome: <expected result>

### Use Case 2: <Name>

- Actor: <user or system>
- Trigger: <event or action>
- Preconditions: <required state>
- Main flow:
	1. <step>
	2. <step>
	3. <step>
- Alternate or error flows:
	- <condition and expected behavior>
- Outcome: <expected result>

## Functional Requirements

| ID | Requirement | Priority | Notes |
| --- | --- | --- | --- |
| FR-001 | <The system shall...> | Must | <notes> |
| FR-002 | <The system shall...> | Should | <notes> |
| FR-003 | <The system shall...> | Could | <notes> |

## Non-Functional Requirements

| ID | Category | Requirement | Target |
| --- | --- | --- | --- |
| NFR-001 | Performance | <requirement> | <target> |
| NFR-002 | Reliability | <requirement> | <target> |
| NFR-003 | Security | <requirement> | <target> |
| NFR-004 | Accessibility | <requirement> | <target> |
| NFR-005 | Maintainability | <requirement> | <target> |

## User Experience Requirements

- Primary screens or surfaces: <screens, API endpoints, commands, docs, or workflows>
- Required states: <loading, empty, success, error, paused, disabled, validation>
- Content requirements: <labels, help text, table columns, chart labels, messages>
- Accessibility requirements: <keyboard, contrast, focus, semantic HTML, screen reader behavior>
- Responsive behavior: <desktop, tablet, mobile expectations>

## Data Requirements

- Entities: <domain objects, tables, events, or documents>
- Required fields: <field list and meaning>
- Data lifecycle: <create, read, update, delete, archive, retention>
- Validation rules: <required values, ranges, uniqueness, relationships>
- Seed or fixture data: <whether static data, generated data, CSV, SQL seed, or test factories are expected>
- Privacy or sensitivity: <PII, secrets, operational data, or none>

## API and Integration Requirements

- API endpoints or contracts: <routes, methods, payloads, response shapes>
- Internal module boundaries: <simulation, API, UI, database, tests>
- External services: <databases, queues, cloud services, containers, or none>
- Configuration: <environment variables, feature flags, ports, connection strings>
- Failure handling: <timeouts, retries, validation errors, unavailable dependencies>

## Technical Approach

Describe the preferred architecture at a high level. Keep this section aligned with repository conventions. For this project, keep core simulation logic in `workspace/simulation/`, API logic in `workspace/api/`, UI files in `workspace/ui/`, and tests in `workspace/tests/`.

### Proposed Components

| Component | Responsibility | Files or Location |
| --- | --- | --- |
| <component> | <responsibility> | <path> |

### Data Model or Schema

```text
<tables, dataclasses, JSON shape, event shape, or other model details>
```

### Key Flows

```text
<sequence, lifecycle, or state transition description>
```

## Acceptance Criteria

- [ ] AC-001: Given <context>, when <action>, then <observable result>.
- [ ] AC-002: Given <context>, when <action>, then <observable result>.
- [ ] AC-003: Given <context>, when <action>, then <observable result>.

## Metrics and Success Criteria

| Metric | Baseline | Target | Measurement Method |
| --- | --- | --- | --- |
| <metric> | <current value or N/A> | <target> | <how measured> |

## Testing Strategy

- Unit tests: <what must be covered>
- Integration tests: <API, database, WebSocket, or UI boundaries>
- Manual validation: <commands and user flows>
- Test data: <inline fixtures, generated data, CSV, SQL seed, or scenario files>
- Regression risks: <areas most likely to break>

## Rollout and Operations

- Deployment or setup steps: <local, Codespaces, containers, or cloud>
- Migration plan: <schema migration, data migration, or none>
- Backward compatibility: <API, data, UI, or docs considerations>
- Observability: <logs, metrics, traces, dashboard values>
- Runbook notes: <common failures and recovery steps>

## Security, Privacy, and Compliance

- Authentication and authorization: <requirements or N/A>
- Secrets management: <environment variables, local-only values, or managed secrets>
- Data protection: <sensitive fields, retention, deletion>
- Abuse or misuse cases: <risks and mitigations>

## Dependencies

- Internal dependencies: <modules, prompts, docs, tests>
- External dependencies: <packages, containers, services>
- Team or stakeholder dependencies: <reviews, approvals, design input>

## Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
| --- | --- | --- | --- |
| <risk> | High | Medium | <mitigation> |

## Open Questions

- [ ] <question and owner>
- [ ] <question and owner>

## Decisions

| Date | Decision | Rationale | Owner |
| --- | --- | --- | --- |
| <YYYY-MM-DD> | <decision> | <why> | <owner> |

## Implementation Plan

1. <small, verifiable step>
2. <small, verifiable step>
3. <small, verifiable step>
4. <validation and documentation step>

## Appendix

- Related screenshots: <links>
- Related issues or prompts: <links>
- Reference docs: <links>
- Glossary: <terms and definitions>
```

## Validation Commands

Run commands from the `workspace/` directory with the
virtual environment activated unless noted otherwise.

```bash
python -m venv .venv          # create (first time)
# Windows: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
```

```bash
python -m compileall .
python -m unittest discover -s tests -v
```

For UI TypeScript changes, run:

```bash
npm install
npm run build
```

To run the app locally:

```bash
python -m uvicorn api.server:app --reload --port 7000
```

## Change Discipline

- Keep changes focused on the current lab prompt or user request.
- Do not rewrite unrelated generated files or prompt files.
- Do not modify files under `completed/` unless the user explicitly asks.
- Preserve existing user or formatter edits when updating files.