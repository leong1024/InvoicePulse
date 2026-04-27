import { useQuery } from "@tanstack/react-query";

import { fetchDriftHistory, fetchLatestDriftReport } from "./api";

export function useLatestDriftReport() {
  return useQuery({
    queryKey: ["drift", "latest"],
    queryFn: fetchLatestDriftReport,
  });
}

export function useDriftHistory(limit = 30) {
  return useQuery({
    queryKey: ["drift", "history", limit],
    queryFn: () => fetchDriftHistory(limit),
  });
}
