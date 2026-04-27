export type DriftStatus =
  | "success"
  | "insufficient_data"
  | "error"
  | "not_available";

export type DriftColumnSummary = {
  name: string;
  drift_detected: boolean;
  score: number | null;
  stattest_name: string | null;
};

export type DriftStatusResponse = {
  status: DriftStatus;
  computed_at: string | null;
  drift_flag: boolean;
  drift_share: number | null;
  drifted_columns: string[];
  reference_count: number;
  current_count: number;
  insufficient_data: boolean;
  error: string | null;
  flag_reason: string | null;
  columns: DriftColumnSummary[];
};

export type DriftHistoryResponse = {
  reports: DriftStatusResponse[];
};
