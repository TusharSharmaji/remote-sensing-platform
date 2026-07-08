import { useQuery, type UseQueryResult } from "@tanstack/react-query";

import { fetchHealthStatus } from "../services/healthService";
import type { HealthStatus } from "../types";

export function useHealthCheck(): UseQueryResult<HealthStatus> {
  return useQuery({
    queryKey: ["health", "live"],
    queryFn: fetchHealthStatus,
  });
}