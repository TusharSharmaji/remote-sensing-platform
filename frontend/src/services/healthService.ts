import { apiClient } from "../api";
import type { HealthStatus } from "../types";

export async function fetchHealthStatus(): Promise<HealthStatus> {
  const response = await apiClient.get<HealthStatus>("/health/live");
  return response.data;
}