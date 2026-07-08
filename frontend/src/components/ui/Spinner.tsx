interface SpinnerProps {
  size?: number;
}

function Spinner({ size = 20 }: SpinnerProps) {
  return (
    <div
      style={{
        width: size,
        height: size,
        border: "3px solid #e5e7eb",
        borderTop: "3px solid #2563eb",
        borderRadius: "50%",
        animation: "spin 1s linear infinite",
      }}
    />
  );
}

export default Spinner;