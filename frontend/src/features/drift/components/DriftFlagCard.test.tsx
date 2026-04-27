import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { DriftFlagCard } from "./DriftFlagCard";
import type { DriftStatusResponse } from "../types";

const baseReport: DriftStatusResponse = {
  status: "success",
  computed_at: "2026-04-27T12:00:00Z",
  drift_flag: false,
  drift_share: 0,
  drifted_columns: [],
  reference_count: 100,
  current_count: 20,
  insufficient_data: false,
  error: null,
  flag_reason: "No dataset drift detected in the latest invoice window.",
  columns: [],
};

describe("DriftFlagCard", () => {
  it("renders healthy state when there is no drift", () => {
    render(<DriftFlagCard report={baseReport} isLoading={false} error={null} />);

    expect(screen.getByText("No Drift")).toBeInTheDocument();
    expect(screen.getByText("20")).toBeInTheDocument();
    expect(screen.getByText("100")).toBeInTheDocument();
  });

  it("renders drift alert state", () => {
    render(
      <DriftFlagCard
        report={{
          ...baseReport,
          drift_flag: true,
          drift_share: 0.33,
          drifted_columns: ["vendor"],
          flag_reason: "Dataset drift detected in: vendor",
        }}
        isLoading={false}
        error={null}
      />,
    );

    expect(screen.getByText("Drift Detected")).toBeInTheDocument();
    expect(screen.getByText("Dataset drift detected in: vendor")).toBeInTheDocument();
  });

  it("renders insufficient data state", () => {
    render(
      <DriftFlagCard
        report={{
          ...baseReport,
          status: "insufficient_data",
          insufficient_data: true,
          reference_count: 10,
          flag_reason: "Need 120 invoice rows for drift analysis; found 30.",
        }}
        isLoading={false}
        error={null}
      />,
    );

    expect(screen.getByText("Need Baseline")).toBeInTheDocument();
  });
});
