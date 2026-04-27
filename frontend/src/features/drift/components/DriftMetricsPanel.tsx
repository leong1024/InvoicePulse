import type { DriftStatusResponse } from "../types";
import { NotepadPanel } from "./NotepadPanel";

type DriftMetricsPanelProps = {
  report: DriftStatusResponse | null;
};

export function DriftMetricsPanel({ report }: DriftMetricsPanelProps) {
  const driftSharePercent =
    report?.drift_share == null
      ? "--"
      : `${Math.round(report.drift_share * 100)}%`;
  const columns = report?.columns ?? [];

  return (
    <NotepadPanel eyebrow="Evidently report" title="Metric Notes">
      <div className="metric-hero">
        <span>Drift share</span>
        <strong>{driftSharePercent}</strong>
      </div>
      <div className="drifted-columns">
        <p className="note-label">Drifted fields</p>
        {report?.drifted_columns.length ? (
          <div className="chip-row">
            {report.drifted_columns.map((column) => (
              <span className="paper-chip paper-chip--alert" key={column}>
                {column}
              </span>
            ))}
          </div>
        ) : (
          <p className="muted-text">No drifted fields recorded.</p>
        )}
      </div>
      <div className="column-table" aria-label="Column drift details">
        <div className="column-table__header">
          <span>Field</span>
          <span>Status</span>
          <span>Score</span>
        </div>
        {columns.length ? (
          columns.map((column) => (
            <div className="column-table__row" key={column.name}>
              <span>{column.name}</span>
              <span>
                {column.drift_detected ? "Drifted" : "Stable"}
              </span>
              <span>{formatScore(column.score)}</span>
            </div>
          ))
        ) : (
          <div className="column-table__empty">No per-column details yet.</div>
        )}
      </div>
    </NotepadPanel>
  );
}

function formatScore(score: number | null) {
  if (score == null) {
    return "--";
  }
  return score.toFixed(3);
}
