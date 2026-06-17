"use client";

import { cn } from "@/lib/utils";

/** Premium floating 3D avatar for the AI assistant (replaces the gradient orb).
 *  Soft brand glow + gentle float + optional thinking pulse. Self-hosted 3D PNG. */
export function AssistantAvatar({
  size = 64,
  className,
  thinking = false,
  src = "/3d/doctor.png",
}: {
  size?: number;
  className?: string;
  thinking?: boolean;
  src?: string;
}) {
  return (
    <div className={cn("relative shrink-0", className)} style={{ width: size, height: size }}>
      {/* soft brand glow */}
      <div className="absolute inset-[-10%] rounded-full bg-gradient-ai opacity-40 blur-xl animate-glow-pulse" />
      {/* 3D avatar */}
      <img
        src={src}
        alt=""
        aria-hidden
        draggable={false}
        className="relative h-full w-full select-none object-contain animate-float drop-shadow-[0_8px_22px_rgba(79,70,229,0.45)]"
      />
      {/* thinking pulse */}
      {thinking && (
        <>
          <span className="absolute inset-0 rounded-full border border-ai/40 animate-pulse-ring" />
          <span className="absolute inset-0 rounded-full border border-primary/30 animate-pulse-ring [animation-delay:0.9s]" />
        </>
      )}
    </div>
  );
}
