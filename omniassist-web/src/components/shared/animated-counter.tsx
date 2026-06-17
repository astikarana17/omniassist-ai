"use client";

import { useEffect, useState } from "react";
import { animate } from "framer-motion";

/** Counts up from 0 to `value` on mount with a premium ease. */
export function AnimatedCounter({
  value,
  className,
  format,
}: {
  value: number | null | undefined;
  className?: string;
  format?: (n: number) => string;
}) {
  const [display, setDisplay] = useState(0);

  useEffect(() => {
    if (value == null) return;
    const controls = animate(0, value, {
      duration: 1.1,
      ease: [0.22, 1, 0.36, 1],
      onUpdate: (v) => setDisplay(Math.round(v)),
    });
    return () => controls.stop();
  }, [value]);

  if (value == null) return <span className={className}>—</span>;
  return (
    <span className={className}>
      {format ? format(display) : display.toLocaleString()}
    </span>
  );
}
