# Skill: Observability Dashboard Review

Used by: Solution Architect Agent, Release Manager Agent.

## Checklist

- [ ] Every agent step can be traced (classify, route, retrieve, tool, draft, guardrail, confidence, HITL).
- [ ] Token counts and estimated/measured cost per conversation are logged structurally.
- [ ] Dashboards distinguish runtime vs eval-plane spend.
- [ ] Alarms exist for error rate, throttle, and unexpected cost spikes (even if simple).
- [ ] Correlation IDs link API request → session_id → tool calls → scorecard_id when applicable.
- [ ] No sensitive real PII in logs; synthetic data still minimized in production-like traces.
