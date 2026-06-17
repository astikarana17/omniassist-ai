"use client";

import { Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";

/** Floating AI orb — gradient core, rotating conic ring, pulsing glow. */
export function AIOrb({
  size = 64,
  className,
  thinking = false,
}: {
  size?: number;
  className?: string;
  thinking?: boolean;
}) {
  return (
    <div className={cn("relative shrink-0", className)} style={{ width: size, height: size }}>
      {/* outer glow */}
      <div className="absolute inset-0 rounded-full bg-gradient-ai opacity-60 blur-xl animate-glow-pulse" />
      {/* rotating conic ring */}
      <div
        className="absolute -inset-[2px] rounded-full animate-spin-slow"
        style={{
          background:
            "conic-gradient(from 0deg, transparent 0%, rgba(34,211,238,0.9) 18%, transparent 40%, rgba(79,70,229,0.9) 70%, transparent 92%)",
        }}
      />
      {/* core */}
      <div className="absolute inset-[3px] rounded-full bg-gradient-to-br from-primary via-primary to-ai" />
      {/* glass highlight */}
      <div className="absolute inset-[3px] rounded-full bg-gradient-to-b from-white/35 to-transparent" />
      {/* depth */}
      <div className="absolute inset-[26%] rounded-full bg-background/25 backdrop-blur-sm" />
      {/* icon */}
      <div className="absolute inset-0 flex items-center justify-center">
        <Sparkles className={cn("text-white", thinking && "animate-pulse")} style={{ width: size * 0.34, height: size * 0.34 }} />
      </div>
      {/* thinking rings */}
      {thinking && (
        <>
          <span className="absolute inset-0 rounded-full border border-ai/50 animate-pulse-ring" />
          <span className="absolute inset-0 rounded-full border border-primary/40 animate-pulse-ring [animation-delay:0.8s]" />
        </>
      )}
    </div>
  );
}
