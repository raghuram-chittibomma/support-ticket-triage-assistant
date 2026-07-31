# Skill: DynamoDB Data Model Review

Used by: Solution Architect Agent.

## Checklist

- [ ] Table keys and GSIs match access patterns in `{{project.docs.data_model}}` (sessions, orders, routing table, scorecards, approvals).
- [ ] Routing table lookup is a single deterministic GetItem/Query by `task_type` (no scan).
- [ ] Refund tool IAM cannot write to unrelated tables.
- [ ] Version fields exist for `routing_table_version` and scorecard identity.
- [ ] TTL or archival strategy considered for sessions/scorecards to control cost.
- [ ] Local fixtures under `{{project.paths.sample_data}}` mirror production attribute names for tests.
