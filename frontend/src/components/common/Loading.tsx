import { Spinner } from "../ui";

interface LoadingProps {
  message?: string;
}

function Loading({
  message = "Loading...",
}: LoadingProps) {
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: "12px",
      }}
    >
      <Spinner />
      <span>{message}</span>
    </div>
  );
}

export default Loading;