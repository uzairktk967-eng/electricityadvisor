# Consultation History and Report Exports

## Scope

Phase 9 adds a lightweight history for completed assessments and portable user-controlled report exports. It does not introduce accounts, a server-side database, cross-device synchronization or automatic backups.

## History lifecycle

- Each successful assessment creates a new immutable snapshot with a UUID and UTC timestamp.
- Snapshots include recorded fact values, evidence status, provenance source and notes, plus the complete consultation result (conclusions, fired rules, explanations, recommendations, conflicts, evidence summary and safety notice).
- Raw natural-language paragraphs are not copied into the report snapshot. This follows data-minimization practice; extracted fact values and provenance are retained because they are necessary to explain the result.
- The Streamlit session keeps at most the latest 25 assessments. The user can inspect a previous entry, delete one entry or clear the complete session history.
- Starting a new consultation does not delete the history list in the current browser session.
- History is session-scoped and is lost when the Streamlit session is reset, the browser tab is reloaded/closed or the server process loses the in-memory state. It is not durable storage.

## Export formats

For an individual history entry:

| Format | Contents | Intended use |
|---|---|---|
| JSON | Complete structured snapshot, evidence, findings and explanation records | Backup, programmatic reuse and audit |
| CSV | One row per fact, conclusion, fired-rule explanation, recommendation, conflict or safety notice | Spreadsheet review |
| HTML | Self-contained printable report with findings, evidence, reasoning, recommendations, conflicts and disclosures | Readable report; browser Print → Save as PDF |

The app also offers a JSON export of the full session history. Exports are generated in memory and downloaded directly; the app does not save them to its server filesystem.

## Security and privacy

- HTML output escapes all dynamic values before inserting them into markup.
- CSV output prefixes potentially dangerous spreadsheet formula-leading text (=, +, -, @, tab and carriage return) to reduce formula-injection risk when opened in spreadsheet software.
- No personal name, email, account identifier or address is requested or added to reports.
- Reports include user-entered appliance and tariff facts. Users should protect downloaded files and share them only with intended recipients.
- Streamlit download payloads are held in memory while connected; keep reports compact.
- The application does not send assessment contents to a third-party report service.

## Why no SQLite persistence in this phase?

Streamlit Community Cloud documentation explicitly warns that local file storage is not guaranteed to persist. A SQLite file stored on the app's local filesystem would therefore create a misleading impression of durable history. This phase intentionally uses per-session history and portable downloads instead. Durable multi-session history should be added only with an explicitly configured persistent external database/storage service, access controls, retention rules and a clear privacy notice.

## User workflow

1. Run an assessment.
2. Open the Consultation history and reports section.
3. Select an earlier assessment to inspect its summary.
4. Download JSON for a complete structured snapshot, CSV for tabular analysis or HTML for printing/saving as PDF.
5. Delete selected history or clear the session history when finished.

## Limitations

- History is not shared across browser tabs or users.
- Refreshing or closing the browser tab can clear it.
- Only the latest 25 completed assessments are retained in the active session.
- Exports are user-controlled downloads; the app cannot delete copies already downloaded to the user's device.
- A printed PDF is created by the user's browser, not by a server-side PDF renderer.
