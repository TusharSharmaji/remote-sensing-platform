export const env = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL,
  appName: import.meta.env.VITE_APP_NAME,
  requestTimeout: Number(import.meta.env.VITE_REQUEST_TIMEOUT),
} as const;