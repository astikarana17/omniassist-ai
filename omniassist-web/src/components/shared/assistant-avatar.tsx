"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

/** Premium 3D avatar for the AI assistant. Soft brand glow + gentle float, and an
 *  optional `speaking` mode that makes her look like she's actively explaining:
 *  a subtle head-sway, a stronger pulsing glow, and animated voice-wave bars. */
export function AssistantAvatar({
  size = 64,
  className,
  thinking = false,
  speaking = false,
  src = "/3d/doctor.png",
}: {
  size?: number;
  className?: string;
  thinking?: boolean;
  speaking?: boolean;
  src?: string;
}) {
  return (
    <div className={cn("relative shrink-0", className)} style={{ width: size, height: size }}>
      {/* soft brand glow — breathes a little stronger while speaking */}
      <motion.div
        className="absolute inset-[-12%] rounded-full bg-gradient-ai blur-xl"
        animate={speaking ? { opacity: [0.35, 0.6, 0.35], scale: [1, 1.08, 1] } : { opacity: 0.4 }}
        transition={speaking ? { duration: 1.6, repeat: Infinity, ease: "easeInOut" } : { duration: 0.4 }}
      />

      {/* 3D avatar — gentle float, with a subtle 'explaining' head-sway when speaking */}
      <motion.img
        src={src}
        alt=""
        aria-hidden
        draggable={false}
        className="relative h-full w-full select-none object-contain drop-shadow-[0_8px_22px_rgba(79,70,229,0.45)]"
        style={{ transformOrigin: "50% 82%" }}
        animate={
          speaking
            ? { y: [0, -3, 0, -2, 0], rotate: [0, -2.5, 1.5, -1, 0] }
            : { y: [0, -5, 0], rotate: 0 }
        }
        transition={{ duration: speaking ? 2.4 : 4, repeat: Infinity, ease: "easeInOut" }}
      />

      {/* speaking — animated voice/sound-wave bars (like a voice assistant talking) */}
      {speaking && (
        <div
          aria-hidden
          className="absolute left-1/2 flex -translate-x-1/2 items-end gap-[2px] rounded-full border border-border bg-card/90 px-1.5 py-1 shadow-md backdrop-blur"
          style={{ bottom: -Math.round(size * 0.05) }}
        >
          {[0, 1, 2, 3, 4].map((i) => (
            <motion.span
              key={i}
              className="w-[2.5px] rounded-full bg-ai"
              animate={{ height: [3, 11, 5, 13, 4] }}
              transition={{ duration: 0.85, repeat: Infinity, delay: i * 0.11, ease: "easeInOut" }}
            />
          ))}
        </div>
      )}

      {/* thinking pulse rings */}
      {thinking && (
        <>
          <span className="absolute inset-0 rounded-full border border-ai/40 animate-pulse-ring" />
          <span className="absolute inset-0 rounded-full border border-primary/30 animate-pulse-ring [animation-delay:0.9s]" />
        </>
      )}
    </div>
  );
}
