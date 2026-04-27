import type { DriftStatusResponse } from "../types";
import { NotepadPanel } from "./NotepadPanel";

type HistoryTimelineProps = {
  reports: DriftStatusResponse[];
};

export function HistoryTimeline({ reports }: HistoryTimelineProps) {
  return (
    <NotepadPanel eyebrow="Notebook trail" title="Recent Runs">
      {reports.length ? (
        <div className="timeline">
          {reports.slice(0, 10).map((report, index) => (
            <article className="timeline-entry" key={`${report.computed_at}-${index}`}>
              <span className={`timeline-dot timeline-dot--${dotVariant(report)}`} />
              <div>
                <strong>{formatDate(report.computed_at)}</strong>
                <p>
                  {report.status === "success"
                    ? report.drift_flag
                      ? `Drift in ${report.drifted_columns.join(", ")}`
                      : "No drift detected"
                    : report.flag_reason ?? report.status}
                </p>
              </div>
            </article>
          ))}
        </div>
      ) : (
        <p className="muted-text">No historical drift reports yet.</p>
      )}
    </NotepadPanel>
  );
}

function dotVariant(report: DriftStatusResponse) {
  if (report.status === "error") {
    return "error";
  }
  if (report.insufficient_data) {
    return "warning";
  }
  if (report.drift_flag) {
    return "alert";
  }
  return "healthy";
}

function formatDate(value: string | null) {
  if (!value) {
    return "Not computed";
  }
  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}
