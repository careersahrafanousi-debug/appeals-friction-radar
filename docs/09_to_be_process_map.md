# To-Be Process Map — Appeals Friction Radar

```mermaid
flowchart TD
    A[Appeal received] --> B[Structured intake form]
    B --> C{Required fields and documents present?}
    C -- No --> D[Intake exception queue with named owner]:::ctrl
    D --> E[Outreach for missing items, SLA clock flagged]
    E --> C
    C -- Yes --> F[Rules-based classification: type, priority, SLA target]:::ctrl
    F --> G[Routing decision rules: type + priority + payer + skill]:::ctrl
    G --> H{Rule matched?}
    H -- No --> I[Supervisor routing exception queue]:::ctrl
    I --> G
    H -- Yes --> J[Assigned to team]
    J --> K[Friction and SLA risk scored on assignment]:::ctrl
    K --> L{Critical friction or under 2 days to SLA?}
    L -- Yes --> M[Supervisor alert, priority placement]:::ctrl
    L -- No --> N[Standard queue]
    M --> O[Review]
    N --> O
    O --> P{Records needed?}
    P -- Yes --> Q[Request logged with day 3 and day 5 follow-up tasks]:::ctrl
    Q --> R{Received by day 5?}
    R -- No --> S[Auto-escalate with documented reason]:::ctrl
    R -- Yes --> T[Review resumes]
    S --> T
    P -- No --> T
    T --> U[Decision]
    U --> V[Closure form: outcome and reason mandatory]:::ctrl
    V --> W[Certified reporting layer]
    W --> X[Weekly routing and quality review]:::ctrl
    X --> G

    classDef ctrl fill:#e8f4ea,stroke:#1e7b34,color:#14532d;
```

## Controls introduced

| Control | Addresses | Owner |
|---|---|---|
| Blocking intake validation with exception queue | P1 | Intake Supervisor |
| Rules-based classification and SLA assignment | P1, P2 | Appeals Ops Manager |
| Documented routing rules with supervisor exception path | P2, P3 | Appeals Ops Manager |
| Friction and SLA scoring at assignment | P3, P4 | Reporting Analyst |
| Day 3 / day 5 follow-up tasks on records requests | P4 | Clinical Review Lead |
| Auto-escalation with reason capture | P4 | Clinical Review Lead |
| Mandatory closure fields | P6 | Quality Lead |
| Weekly review that feeds rules back into routing | P2, P5 | Operations Director |

The feedback loop from the weekly review back to the routing rules is the part that keeps
this from decaying. Rules set once and never revisited are how the current state happened.
