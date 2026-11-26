# Knowledge Base Design and Data Dictionary

## Purpose

The project uses a versioned, explainable JSON knowledge base. These records are domain definitions, not executable code.

## Files

- `facts.json`: recognized consultation inputs and their types, units and evidence sources.
- `categories.json`: domain categories.
- `conclusions.json`: the finite set of conclusions the system may derive.
- `recommendations.json`: user-facing actions linked to conclusions, including safety notes.
- `rules.json`: IF–THEN rules, conditions, priority, formula metadata and limitations.
- `schema.json`: JSON Schema (Draft 2020-12) for the file structures.

## Evidence semantics

The fact store carries statuses such as `confirmed`, `rejected`, `uncertain` or `missing`, plus a provenance/source note. Unknown or rejected facts must not satisfy rule conditions. A derived fact records the rule that produced it.

## Calculation conventions

- Energy (kWh) = power (W) × quantity × hours × days ÷ 1000.
- Variable energy cost = energy (kWh) × user-entered marginal rate per kWh.
- Standby energy requires a value that specifically represents standby-mode power. Rated operating power is not a valid substitute.
- These calculations are estimates. Cycling, variable loads, thermostat-controlled equipment and user-input error can affect accuracy.
- A simplified variable-cost estimate is not the complete electricity bill. Fixed charges, taxes, slabs, duties and adjustments may be excluded.

## Rule semantics

- Conditions within a rule are joined using AND (`all`).
- The rule engine supports explicit operators and typed comparisons.
- Missing or uncertain evidence never matches.
- `requires_conclusion` indicates a prerequisite conclusion.
- Priority is metadata for deterministic conflict policy and trace display; it must not erase other valid conclusions or hide conflicting evidence.
- Formula strings are declarative metadata. They are handled through an allow-listed calculation layer, never evaluated as arbitrary Python.

## Initial rule set

The initial rules cover:
1. Monthly energy estimate from rated input power and operating duration.
2. Variable energy-cost estimate from a user-provided rate and an energy estimate.
3. Standby energy estimate only from a standby-specific power reading.
4. A schedule review candidate where the user confirms flexibility.
5. Professional referral for reported electrical warning symptoms.
6. Comparison of verified energy labels/specifications.

The rule set deliberately avoids universal appliance-efficiency thresholds or claims that a particular wattage is inherently wasteful.

## Safety boundary

The advisor must not instruct users to open appliances, touch live wiring, bypass protective devices or perform electrical repairs. Reported sparks, burning smell, electric shock, hot outlets/wiring or repeated breaker trips must trigger a conservative referral to a qualified electrician.

## Validation requirements

The management validator in `knowledge_base/manager.py` checks:
- JSON parses and matches the JSON Schema Draft 2020-12 structure.
- IDs are unique within each collection.
- Every rule category, fact, conclusion and recommendation reference exists.
- Every recommendation's linked conclusions exist and match its supporting rule conclusion.
- Operators are compatible with fact types and comparison values.
- Numeric bounds and allowed enum values are respected.
- Prerequisite conclusions do not create a dependency cycle.
- Formula metadata matches the exact allow-list of implemented calculations.
- Recommendations not referenced by any rule are reported as warnings.

Cross-file semantic validation supplements JSON Schema validation. A schema file is a structural contract, not proof that a draft is valid. The validator does not establish that a domain rule is scientifically correct.

See [Knowledge-Base Management](KNOWLEDGE_BASE_MANAGEMENT.md) for the safe draft-editing and export workflow.
