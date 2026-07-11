import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useNavigate } from "react-router-dom";

import {
  loginSchema,
  type LoginFormData,
  useLogin,
  useAuth,
  getCurrentUser,
} from "..";

import { saveTokens } from "../storage/tokenStorage";

function LoginForm() {
  const loginMutation = useLogin();

  const { login } = useAuth();

  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  async function onSubmit(data: LoginFormData) {
    try {
      // 1. Login and receive tokens
      const tokenResponse =
        await loginMutation.mutateAsync(data);

      // 2. Save tokens BEFORE any authenticated request
      saveTokens(
        tokenResponse.access_token,
        tokenResponse.refresh_token,
      );

      // 3. Fetch current user using the new access token
      const user = await getCurrentUser();

      // 4. Update Auth Context
      login(
        user,
        tokenResponse.access_token,
        tokenResponse.refresh_token,
      );

      // 5. Navigate to dashboard
      navigate("/dashboard");
    } catch (error) {
      console.error(error);

      alert("Login Failed");
    }
  }

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      style={{
        display: "flex",
        flexDirection: "column",
        gap: "16px",
        maxWidth: "400px",
      }}
    >
      <div>
        <label>Email</label>

        <input
          type="email"
          {...register("email")}
        />

        {errors.email && (
          <p style={{ color: "red" }}>
            {errors.email.message}
          </p>
        )}
      </div>

      <div>
        <label>Password</label>

        <input
          type="password"
          {...register("password")}
        />

        {errors.password && (
          <p style={{ color: "red" }}>
            {errors.password.message}
          </p>
        )}
      </div>

      <button
        type="submit"
        disabled={loginMutation.isPending}
      >
        {loginMutation.isPending
          ? "Logging in..."
          : "Login"}
      </button>
    </form>
  );
}

export default LoginForm;