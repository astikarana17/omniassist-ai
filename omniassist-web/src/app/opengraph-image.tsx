import { ImageResponse } from "next/og";

export const runtime = "edge";
export const alt = "OmniAssist Health — understand your prescriptions and lab reports";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

// Branded social-share card (used for OpenGraph and Twitter).
export default function Image() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          alignItems: "flex-start",
          justifyContent: "center",
          background: "linear-gradient(135deg, #0B1220 0%, #131A2E 100%)",
          padding: "80px",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 24, marginBottom: 44 }}>
          <div
            style={{
              width: 72,
              height: 72,
              borderRadius: 18,
              background: "linear-gradient(135deg,#4F46E5,#22D3EE)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <div style={{ width: 26, height: 26, borderRadius: 999, background: "white" }} />
          </div>
          <div style={{ fontSize: 40, fontWeight: 700, color: "white", display: "flex" }}>
            OmniAssist Health
          </div>
        </div>
        <div style={{ fontSize: 66, fontWeight: 700, color: "white", lineHeight: 1.08, maxWidth: 920, display: "flex" }}>
          Understand your health, in plain language.
        </div>
        <div style={{ fontSize: 30, color: "#94A3B8", marginTop: 30, maxWidth: 860, display: "flex" }}>
          AI explanations for your prescriptions, lab reports and health questions.
        </div>
      </div>
    ),
    { ...size }
  );
}
