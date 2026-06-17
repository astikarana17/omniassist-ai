"use client";

// Root error boundary — replaces the whole document when the root layout itself
// throws, so it must render its own <html>/<body>.
export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html lang="en">
      <body
        style={{
          margin: 0,
          minHeight: "100vh",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          gap: "16px",
          background: "#0B1220",
          color: "#E5E7EB",
          fontFamily: "system-ui, -apple-system, sans-serif",
          textAlign: "center",
          padding: "24px",
        }}
      >
        <h1 style={{ fontSize: "1.5rem", fontWeight: 600 }}>Something went wrong</h1>
        <p style={{ color: "#94A3B8", maxWidth: "28rem" }}>
          The application hit an unexpected error. Please try again.
        </p>
        <button
          onClick={reset}
          style={{
            cursor: "pointer",
            borderRadius: "10px",
            border: "none",
            background: "linear-gradient(180deg,#4F46E5,#4338CA)",
            color: "white",
            padding: "10px 20px",
            fontSize: "0.875rem",
            fontWeight: 500,
          }}
        >
          Try again
        </button>
      </body>
    </html>
  );
}
