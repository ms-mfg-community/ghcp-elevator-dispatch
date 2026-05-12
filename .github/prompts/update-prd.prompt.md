---
name: update-prd
description: "Update the repository PRD with recent product, implementation, testing, risk, and decision changes while preserving the established PRD format."
agent: agent
model: GPT-5.5 (copilot)
argument-hint: "optional summary of the feature, prompt, PR, issue, commit range, or change set that should drive the PRD update"
---

# Update the PRD (Product Requirements Document)

Update the product requirements document for this repository based on the current implementation state and any details I
provide in the prompt arguments.

The canonical PRD lives at `docs/prd-elevator-dispatch.md`. If a different PRD is clearly referenced in my request, use
that document instead. Do not create a new PRD unless no suitable PRD exists or I explicitly ask for a new one.

## Inputs

Use all relevant context available in this order:

1. Any details I provide after this prompt command, including feature descriptions, issue or PR context, branch names,
	 screenshots, commit ranges, or acceptance criteria.
2. The current repository state under `workspace/`, `.github/prompts/`, `.github/instructions/`, `.github/skills/`,
	 `.github/agents/`, `docs/`, and `README.md`.
3. The existing PRD content and its current document control metadata.
4. Repository-specific Copilot instructions and path-specific instructions that apply to documentation or PRD files.

If my prompt arguments are vague, infer likely changes from the repository, but clearly separate verified facts from
reasonable assumptions in your final response. Ask a clarifying question only when the PRD cannot be updated safely
without the missing information.

## Discovery Workflow

Before editing the PRD:

1. Inspect the existing PRD structure, document control fields, functional requirements, acceptance criteria, testing
	 strategy, risks, open questions, decisions, implementation plan, and appendix.
2. Inspect recent or relevant project artifacts that may change product requirements, such as:
	 - application code in `workspace/api/`, `workspace/simulation/`, and `workspace/ui/`;
	 - tests in `workspace/tests/`;
	 - prompt files under `.github/prompts/`;
	 - instruction files, skills, and agents under `.github/`;
	 - documentation in `README.md` and `docs/`.
3. Identify what has changed since the PRD was last updated, including new capabilities, behavior changes, validation
	 rules, setup requirements, developer workflows, data model changes, API changes, UI changes, deployment changes,
	 testing changes, risks, and decisions.
4. Check whether the README or prompt inventory implies lab milestones or workflows that should be reflected in the PRD.

Do not treat files under `completed/` as source material for new requirements unless I explicitly ask you to compare
against the facilitator reference solution.

## Update Requirements

Revise the PRD so it accurately describes the current and intended product state. Keep the update focused on product
requirements and implementation-relevant planning details, not low-level code narration.

Update these sections when applicable:

- `Document Control`: set `Last updated` to today's date and adjust status, milestone, owner, or stakeholders only when
	the change justifies it.
- `Summary`: reflect major capability additions or scope changes in one or two clear paragraphs.
- `Problem Statement`: update only if the user problem or workshop need has changed.
- `Goals` and `Non-Goals`: add, remove, or refine outcomes based on the change set.
- `Users and Personas`: update when a new user type, facilitator workflow, operator workflow, or learner need appears.
- `Use Cases`: add or revise concrete user/system flows for new behavior.
- `Functional Requirements`: add stable requirement IDs for new product behavior and preserve existing IDs where the
	meaning has not changed.
- `Non-Functional Requirements`: update performance, reliability, security, accessibility, maintainability, or workshop
	usability targets when affected.
- `User Experience Requirements`: update required screens, UI states, labels, accessibility expectations, and responsive
	behavior for dashboard or workflow changes.
- `Data Requirements`: update entities, fields, validation rules, lifecycle, seed data, privacy, and retention behavior.
- `API and Integration Requirements`: update routes, payloads, response shapes, internal module boundaries, external
	services, configuration, and failure handling.
- `Technical Approach`: keep the architecture aligned with this repository: FastAPI in `workspace/api/`, simulation logic
	in `workspace/simulation/`, framework-free UI files in `workspace/ui/`, tests in `workspace/tests/`, and product docs in
	`docs/`.
- `Acceptance Criteria`: add or revise testable, observable criteria for the change set.
- `Metrics and Success Criteria`: add meaningful measures only when the change introduces a measurable outcome.
- `Testing Strategy`: add focused unit, integration, manual, and regression coverage expectations.
- `Rollout and Operations`: update setup, migration, backward compatibility, observability, and runbook notes.
- `Security, Privacy, and Compliance`: update authentication, authorization, secrets, data protection, or misuse risks
	when affected.
- `Dependencies`: record internal, external, and stakeholder dependencies.
- `Risks and Mitigations`: add realistic risks introduced by the change and practical mitigations.
- `Open Questions`: add unresolved questions that block product clarity; remove or resolve stale questions when evidence
	exists.
- `Decisions`: record material decisions with today's date, rationale, and owner when the repository reflects a clear
	decision.
- `Implementation Plan`: keep steps small, ordered, and verifiable.
- `Appendix`: link related prompts, docs, screenshots, issues, or PRs when materially relevant.

## Editing Rules

- Preserve the PRD's existing heading hierarchy and table style unless a section needs to be added from the repository
	PRD template.
- Keep requirement IDs stable. Add new IDs sequentially within the relevant table.
- Prefer concise, implementation-oriented prose that Copilot can use to generate code, tests, and documentation.
- Use repository-relative Markdown links for local files.
- Avoid narrow line wrapping in prose; prefer readable lines around 110 to 120 columns unless preserving an existing
	table or code block.
- Do not add speculative commitments, production infrastructure, authentication, databases, queues, ML, or framework
	changes unless they are present in the repository or explicitly requested.
- Do not modify unrelated application code while updating the PRD.
- Do not rewrite unrelated PRD sections just for style.

## Consistency Checks

After editing, review the PRD for consistency:

- The summary, goals, requirements, acceptance criteria, testing strategy, risks, decisions, and implementation plan all
	describe the same scope.
- Functional requirements are testable and not duplicated.
- New requirements do not contradict existing non-goals or repository conventions.
- API, data, and UI requirements match the implementation or the explicitly requested target state.
- Dates, milestone references, prompt names, file paths, and links are accurate.
- Open questions are genuinely unresolved and not already answered elsewhere in the repository.

## Validation

For a documentation-only PRD update, no application test run is required unless the update depends on verifying code
behavior. If verification is needed, run the narrowest useful checks from the `workspace/` directory, such as:

```bash
python -m compileall .
python -m unittest discover -s tests -v
```

If UI TypeScript source changed as part of the underlying feature and you need to confirm current state, also consider:

```bash
npm run build
```

Do not run expensive or destructive commands unless necessary for confidence.

## Final Response

When finished, summarize:

1. Which PRD file was updated.
2. The main product areas changed.
3. Any assumptions, unresolved questions, or sections intentionally left unchanged.
4. Any validation performed, or why validation was not run.

If the PRD cannot be updated safely, leave files unchanged and explain the blocker with the smallest useful set of next
steps.

