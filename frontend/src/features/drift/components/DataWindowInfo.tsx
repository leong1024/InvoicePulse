import { NotepadPanel } from "./NotepadPanel";

export function DataWindowInfo() {
  return (
    <NotepadPanel eyebrow="Window recipe" title="How the flag is computed">
      <ol className="window-steps">
        <li>
          Query the newest <strong>120</strong> invoice extraction rows.
        </li>
        <li>
          Compare the newest <strong>20</strong> rows as current data.
        </li>
        <li>
          Use the next <strong>100</strong> rows as reference data.
        </li>
        <li>
          Run Evidently <strong>DataDriftPreset</strong> and store the summary.
        </li>
      </ol>
    </NotepadPanel>
  );
}
