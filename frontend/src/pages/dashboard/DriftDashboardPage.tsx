import { useState } from "react";

import { runDriftNow } from "../../features/drift/api";
import { DataWindowInfo } from "../../features/drift/components/DataWindowInfo";
import { DriftFlagCard } from "../../features/drift/components/DriftFlagCard";
import { DriftMetricsPanel } from "../../features/drift/components/DriftMetricsPanel";
import { HistoryTimeline } from "../../features/drift/components/HistoryTimeline";
import {
  useDriftHistory,
  useLatestDriftReport,
} from "../../features/drift/hooks";

export function DriftDashboardPage() {
  const latestQuery = useLatestDriftReport();
  const historyQuery = useDriftHistory(30);
  const [runError, setRunError] = useState<string | null>(null);
  const [isRunning, setIsRunning] = useState(false);

  async function handleRefreshDrift() {
    try {
      setRunError(null);
      setIsRunning(true);
      await runDriftNow();
      await Promise.all([latestQuery.refetch(), historyQuery.refetch()]);
    } catch (error) {
      setRunError(
        error instanceof Error
          ? error.message
          : "Unable to run drift analysis right now.",
      );
    } finally {
      setIsRunning(false);
    }
  }

  return (
    <main className="notebook-page">
      <header className="dashboard-header">
        <p className="note-eyebrow">InvoicePulse</p>
        <h1>Invoice Quality Monitoring</h1>
        <p>
          Powered by Evidently AI to detect distribution shifts and data quality
          changes before they impact financial reporting, automation accuracy,
          and downstream decisions.
        </p>
        <div className="dashboard-actions">
          <button
            type="button"
            className="refresh-button"
            onClick={handleRefreshDrift}
            disabled={isRunning}
          >
            {isRunning ? "Running Drift..." : "Refresh Drift"}
          </button>
          {runError ? <p className="dashboard-error">{runError}</p> : null}
        </div>
      </header>

      <section className="notebook-grid">
        <DriftFlagCard
          report={latestQuery.data ?? null}
          isLoading={latestQuery.isLoading}
          error={latestQuery.error}
        />
        <DriftMetricsPanel report={latestQuery.data ?? null} />
      </section>

      <section className="notebook-grid notebook-grid--secondary">
        <DataWindowInfo />
        <HistoryTimeline reports={historyQuery.data?.reports ?? []} />
      </section>
    </main>
  );
}
