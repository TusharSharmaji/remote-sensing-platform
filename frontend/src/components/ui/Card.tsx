import type { ReactNode } from "react";

interface CardProps {
  title?: string;
  children: ReactNode;
}

function Card({ title, children }: CardProps) {
  return (
    <div
      style={{
        border: "1px solid #e5e7eb",
        borderRadius: "10px",
        padding: "20px",
        marginTop: "20px",
        background: "#ffffff",
      }}
    >
      {title && <h3>{title}</h3>}
      {children}
    </div>
  );
}

export default Card;