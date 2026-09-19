# Privacy and Data Handling Statement

This project uses fully synthetic data created for educational and portfolio purposes. It
does not use employer data, patient information, protected health information, or
confidential business information.

Specifically:

- All records are generated programmatically by `src/generate_data.py`. No file in this
  repository originated from any production system.
- The organization, payers, teams, and reason codes are invented. Any resemblance to a real
  entity is coincidental.
- There are no member, patient, or provider identifiers of any kind. The only identifiers
  are synthetic surrogate keys (`APL-`, `EVT-`, `PAY-`, `TM-`, `RC-`).
- No screenshots of internal systems are included.
- Findings describe the modeled scenario only. They are not evidence about any real
  population, payer, or organization.
- Benefits are expressed as modeled opportunity subject to validation. No savings or
  recovery figures are asserted.

The workflow logic reflects general domain knowledge of healthcare appeals operations, which
is publicly documented in payer manuals and regulatory guidance. It does not reflect any
specific employer's process, metrics, or configuration.
