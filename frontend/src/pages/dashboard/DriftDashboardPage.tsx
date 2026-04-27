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

  return (
    <main className="notebook-page">
      <header className="dashboard-header">
        <p className="note-eyebrow">InvoicePulse</p>
        <h1>Supabase Invoice Drift Notebook</h1>
        <p>
          A notepad-style monitor for invoice extraction records, powered by
          Evidently and the latest 20 vs prior 100 Supabase row comparison.
        </p>
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
