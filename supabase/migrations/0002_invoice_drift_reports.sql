create table if not exists public.invoice_drift_reports (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  reference_count integer not null default 0,
  current_count integer not null default 0,
  drift_detected boolean not null default false,
  drift_share numeric,
  drifted_columns text[] not null default '{}',
  report_json jsonb not null default '{}'::jsonb,
  summary_json jsonb not null default '{}'::jsonb,
  status text not null default 'success',
  error text,
  constraint invoice_drift_reports_status_check
    check (status in ('success', 'insufficient_data', 'error')),
  constraint invoice_drift_reports_counts_check
    check (reference_count >= 0 and current_count >= 0),
  constraint invoice_drift_reports_drift_share_check
    check (drift_share is null or (drift_share >= 0 and drift_share <= 1))
);

create index if not exists invoice_drift_reports_created_at_idx
  on public.invoice_drift_reports (created_at desc);

create index if not exists invoice_drift_reports_drift_detected_idx
  on public.invoice_drift_reports (created_at desc)
  where drift_detected = true;

alter table public.invoice_drift_reports enable row level security;
