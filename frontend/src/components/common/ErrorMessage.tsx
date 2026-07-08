interface ErrorMessageProps {
  message: string;
}

function ErrorMessage({
  message,
}: ErrorMessageProps) {
  return (
    <div
      style={{
        color: "#dc2626",
        background: "#fee2e2",
        padding: "12px",
        borderRadius: "8px",
      }}
    >
      {message}
    </div>
  );
}

export default ErrorMessage;