# Knowledge Base Design and Data Dictionary

## Purpose

Phase 2 establishes a versioned, explainable JSON knowledge base for the Smart Home Electricity Advisor. These records are domain knowledge definitions, not executable code. The inference engine will be implemented in a later phase.

## Files

- `facts.json`: recognized consultation inputs and their types, units and evidence sources.
- `categories.json`: domain categories.
- `conclusions.json`: the finite set of conclusions the system may derive.
- `recommendations.json`: user-facing actions linked to conclusions, including safety notes.
- `rules.json`: IF–THEN rules, conditions, priority, formula metadata and limitations.
- `schema.json`: JSON Schema (Draft 2020-12) for the file structures.

## Evidence semantics

A fact is not simply true or false. The future fact store must carry a status such as `confirmed`, `rejected`, `uncertain` or `missing`, plus a provenance/source note. Unknown or rejected facts must not satisfy rule conditions. A derived fact must record the rule that produced it.

## Calculation conventions

- Energy (kWh) = power (W) × quantity × hours × days ÷ 1000.
- Variable energy cost = energy (kWh) × user-entered marginal rate per kWh.
- Standby energy requires a value that specifically represents standby-mode power. Rated operating power is not a valid substitute.
- These calculations are estimates. Cycling, variable loads, thermostat-controlled equipment and user-input error can affect accuracy.
- A simplified variable-cost estimate is not the complete electricity bill. Fixed charges, taxes, slabs, duties and adjustments may be excluded.

## Rule semantics

- Conditions within a rule are joined using AND (`all`).
- The rule engine must support explicit operators and typed comparisons.
- Missing or uncertain evidence never matches.
- `requires_conclusion` indicates a prerequisite conclusion.
- Priority is metadata for deterministic conflict policy and trace display; it must not erase other valid conclusions or hide conflicting evidence.
- Formula strings are declarative metadata. They must be parsed/implemented through a safe, allow-listed calculation layer, never evaluated as arbitrary Python.

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

A knowledge-base validator must check:
- JSON parses and matches the appropriate schema.
- IDs are unique within each collection.
- Every rule category, fact, conclusion and recommendation reference exists.
- Every recommendation's linked conclusions exist.
- Operators are compatible with fact types.
- Numeric bounds and allowed enum values are respected.
- Prerequisite conclusions exist and do not create an accidental dependency cycle.
- Formula references use known facts and approved calculation names.
- No recommendation is orphaned without a supporting conclusion/rule path.

Cross-file semantic validation is required in addition to JSON Schema validation. The schema file is a structural contract; it is not itself proof that these checks have been executed.

## Scope and limitations

The initial catalogue is a starter knowledge base, not an exhaustive engineering standard or a tariff database. It contains no hard-coded Pakistan tariff, appliance benchmarks or regulatory limits. Local tariffs and appliance-specific performance data must be entered or verified from authoritative current sources before use.
