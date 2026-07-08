import axios from "axios";

import { env } from "../config/env";

const apiClient = axios.create({
  baseURL: env.apiBaseUrl,
  timeout: env.requestTimeout,
  headers: {
    "Content-Type": "application/json",
  },
});

export default apiClient;