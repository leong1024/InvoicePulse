import { NotepadPanel } from "./NotepadPanel";

export function DataWindowInfo() {
  return (
    <NotepadPanel eyebrow="Monitoring overview" title="Why Drift Monitoring Matters">
      <ol className="window-steps">
        <li>
          Detect silent changes in invoice patterns early with Evidently AI.
        </li>
        <li>
          Protect extraction accuracy and reconciliation reliability over time.
        </li>
        <li>
          Reduce operational risk by surfacing quality degradation quickly.
        </li>
        <li>
          Maintain confidence in analytics, alerts, and finance workflows.
        </li>
      </ol>
    </NotepadPanel>
  );
}
