# Skill: Eval Scenario Design

Used by: Test/Eval Designer Agent.

## Checklist

- [ ] Each scenario declares `id`, `task_type`, `input`, `expected_tools`, `expected_citations`, `expected_outcome`.
- [ ] Coverage spans the major task types in scope for the current milestone.
- [ ] Edge cases included: low confidence, refund above HITL threshold, missing order ID, ambiguous product question.
- [ ] Expected tool calls are exact enough for programmatic checks but not overfit to ephemeral phrasing.
- [ ] Citation expectations reference synthetic `doc_id`s that exist under `{{project.paths.knowledge_base}}`.
- [ ] Scenarios live under `{{project.paths.evals}}` with a `dataset_version`.
- [ ] No golden scenario text is copied into agent system prompts.
