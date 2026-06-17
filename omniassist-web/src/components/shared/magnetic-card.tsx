"use client";

import { useRef, type ReactNode } from "react";
import gsap from "gsap";
import { cn } from "@/lib/utils";

/** GSAP-powered 3D magnetic tilt — the card subtly leans toward the cursor and
 *  lifts, then springs back. A premium, tactile micro-interaction. */
export function MagneticCard({
  children,
  className,
  strength = 8,
  lift = 6,
}: {
  children: ReactNode;
  className?: string;
  strength?: number;
  lift?: number;
}) {
  const ref = useRef<HTMLDivElement>(null);

  const handleMove = (e: React.MouseEvent) => {
    const el = ref.current;
    if (!el) return;
    const r = el.getBoundingClientRect();
    const px = (e.clientX - r.left) / r.width - 0.5;
    const py = (e.clientY - r.top) / r.height - 0.5;
    gsap.to(el, {
      rotateY: px * strength,
      rotateX: -py * strength,
      y: -lift,
      duration: 0.5,
      ease: "power2.out",
      transformPerspective: 900,
      transformOrigin: "center",
    });
  };

  const handleLeave = () => {
    gsap.to(ref.current, { rotateY: 0, rotateX: 0, y: 0, duration: 0.6, ease: "power3.out" });
  };

  return (
    <div
      ref={ref}
      onMouseMove={handleMove}
      onMouseLeave={handleLeave}
      style={{ transformStyle: "preserve-3d" }}
      className={cn("will-change-transform", className)}
    >
      {children}
    </div>
  );
}
