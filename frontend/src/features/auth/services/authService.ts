import { apiClient } from "../../../api";

import type {
  LoginRequest,
  LoginResponse,
  AuthUser,
} from "../types/auth";

export async function login(
  data: LoginRequest,
): Promise<LoginResponse> {
  const response = await apiClient.post<LoginResponse>(
    "/auth/login",
    data,
  );

  return response.data;
}

export async function getCurrentUser(): Promise<AuthUser> {
  const response =
    await apiClient.get<AuthUser>("/users/me");

  return response.data;
}