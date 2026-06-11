"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

/** OmniAssist "Orbit" mark — central node + orbiting dot. */
export function OrbitMark({
  className,
  animate = true,
}: {
  className?: string;
  animate?: boolean;
}) {
  return (
    <span
      className={cn(
        "relative inline-flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-brand shadow-glow-brand",
        className
      )}
    >
      <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5">
        <circle cx="12" cy="12" r="3.5" fill="white" />
        <circle
          cx="12"
          cy="12"
          r="8"
          stroke="white"
          strokeOpacity="0.5"
          strokeWidth="1.5"
        />
      </svg>
      {animate && (
        <motion.span
          className="absolute inset-0"
          animate={{ rotate: 360 }}
          transition={{ duration: 6, repeat: Infinity, ease: "linear" }}
        >
          <span className="absolute left-1/2 top-[3px] h-1.5 w-1.5 -translate-x-1/2 rounded-full bg-white shadow" />
        </motion.span>
      )}
    </span>
  );
}

export function Logo({ collapsed = false }: { collapsed?: boolean }) {
  return (
    <div className="flex items-center gap-2.5">
      <OrbitMark />
      {!collapsed && (
        <span className="text-[15px] font-semibold tracking-tight">
          Omni<span className="text-gradient">Assist</span>
        </span>
      )}
    </div>
  );
}
