import type { DriftStatusResponse } from "../types";
import { NotepadPanel } from "./NotepadPanel";

type DriftFlagCardProps = {
  report: DriftStatusResponse | null;
  isLoading: boolean;
  error: Error | null;
};

export function DriftFlagCard({
  report,
  isLoading,
  error,
}: DriftFlagCardProps) {
  const state = getFlagState(report, isLoading, error);

  return (
    <NotepadPanel
      eyebrow="Latest signal"
      title="Drift Flag"
      className={`flag-card flag-card--${state.variant}`}
    >
      <div className="flag-card__status">
        <span className={`sticky-badge sticky-badge--${state.variant}`}>
          {state.label}
        </span>
      </div>
      <p className="flag-card__reason">{state.reason}</p>
      <dl className="note-metrics">
        <div>
          <dt>Current rows</dt>
          <dd>{report?.current_count ?? "--"}</dd>
        </div>
        <div>
          <dt>Reference rows</dt>
          <dd>{report?.reference_count ?? "--"}</dd>
        </div>
        <div>
          <dt>Last computed</dt>
          <dd>{formatDate(report?.computed_at)}</dd>
        </div>
      </dl>
    </NotepadPanel>
  );
}

function getFlagState(
  report: DriftStatusResponse | null,
  isLoading: boolean,
  error: Error | null,
) {
  if (isLoading) {
    return {
      variant: "pending",
      label: "Checking",
      reason: "Reading the latest drift notebook entry.",
    };
  }
  if (error) {
    return {
      variant: "error",
      label: "API Error",
      reason: error.message,
    };
  }
  if (!report || report.status === "not_available") {
    return {
      variant: "pending",
      label: "No Report",
      reason: "Run the drift job to create the first report.",
    };
  }
  if (report.insufficient_data) {
    return {
      variant: "warning",
      label: "Need Baseline",
      reason: report.flag_reason ?? "At least 120 invoice rows are required.",
    };
  }
  if (report.status === "error") {
    return {
      variant: "error",
      label: "Job Error",
      reason: report.error ?? "The drift job could not complete.",
    };
  }
  if (report.drift_flag) {
    return {
      variant: "alert",
      label: "Drift Detected",
      reason: report.flag_reason ?? "Evidently detected invoice data drift.",
    };
  }
  return {
    variant: "healthy",
    label: "No Drift",
    reason:
      report.flag_reason ?? "The latest invoice window matches the baseline.",
  };
}

function formatDate(value: string | null | undefined) {
  if (!value) {
    return "--";
  }
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}
