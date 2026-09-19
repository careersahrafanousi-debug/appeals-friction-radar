# As-Is Process Map — Appeals Friction Radar

Mermaid renders natively on GitHub. Pain points are marked in red.

```mermaid
flowchart TD
    A[Appeal received] --> B[Intake logged manually]
    B --> C{Documentation complete?}
    C -- No --> P1[Proceed anyway, gap noted in free text]:::pain
    C -- Yes --> D[Type and priority classified by judgment]:::pain
    P1 --> D
    D --> E[Routed to a team]
    E --> F{Correct team?}
    F -- No --> P2[Sits in wrong queue until someone notices]:::pain
    P2 --> G[Reassigned]:::pain
    G --> E
    F -- Yes --> H[Case waits in team queue]:::pain
    H --> I[Review started]
    I --> J{Records needed?}
    J -- Yes --> P3[Information requested, no follow-up cadence]:::pain
    P3 --> K[Wait for provider records]:::pain
    K --> L{Received?}
    L -- No --> P4[Ages past 5 days, escalates]:::pain
    P4 --> M[Escalation queue]
    L -- Yes --> N[Review resumes]
    J -- No --> N
    M --> N
    N --> O{Rework needed?}
    O -- Yes --> P5[Review repeated]:::pain
    P5 --> N
    O -- No --> Q[Decision made]
    Q --> R[Closure fields entered]
    R --> S{Outcome recorded?}
    S -- No --> P6[Closed with blank outcome, breaks reporting]:::pain
    S -- Yes --> T[Monthly report]
    P6 --> T

    classDef pain fill:#fde2e2,stroke:#c0392b,color:#7b241c;
```

## Pain points in words

| # | Pain point | Observed effect in the data |
|---|---|---|
| P1 | Intake accepts incomplete documentation | Rework rate 31.7% vs 7.7% when complete |
| P2 | Routing depends on individual judgment | First-pass accuracy 81.7% on claims payment |
| P3 | Wrong-queue cases are found late | Routing stage carries the second-highest dwell time |
| P4 | No follow-up cadence on records requests | Escalations concentrate past day 5 |
| P5 | Handoffs add time with no tracking | +4.9 days average per additional handoff |
| P6 | Closure fields not enforced | Closed cases with blank outcome, logged as DQ-02 |

## Where the time sits

Average closed-case days by stage: intake 0.9, routing 1.9, waiting for review 1.6,
review 9.1, closure 1.5. About 4.3 days per case is queueing and administration rather
than review work.
