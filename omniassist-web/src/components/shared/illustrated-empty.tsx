"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

const DIM = {
  sm: "h-24 w-24",
  md: "h-36 w-36 sm:h-40 sm:w-40",
  lg: "h-44 w-44 sm:h-52 sm:w-52",
} as const;

/**
 * Framed illustration. The illustrations are designed for light backgrounds
 * (white fills + dark linework), so we sit them on a soft light card that looks
 * crisp on both light and dark themes, with a gentle float animation.
 */
export function Illustration({
  src,
  size = "md",
  className,
}: {
  src: string;
  size?: keyof typeof DIM;
  className?: string;
}) {
  return (
    <motion.img
      src={src}
      alt=""
      aria-hidden
      draggable={false}
      initial={{ opacity: 0, scale: 0.92, y: 6 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      transition={{ delay: 0.06, type: "spring", stiffness: 200, damping: 18 }}
      className={cn("animate-float select-none object-contain drop-shadow-xl", DIM[size], className)}
    />
  );
}

/** Friendly, illustrated empty state (Google/Notion style) used across the app. */
export function IllustratedEmpty({
  src,
  title,
  description,
  className,
  size = "md",
  children,
}: {
  src: string;
  title: string;
  description?: string;
  className?: string;
  size?: keyof typeof DIM;
  children?: React.ReactNode;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className={cn(
        "flex flex-col items-center justify-center rounded-2xl border border-dashed border-border-strong bg-subtle/30 px-6 py-12 text-center",
        className
      )}
    >
      <Illustration src={src} size={size} className="mb-5" />
      <h3 className="text-lg font-semibold">{title}</h3>
      {description && <p className="mt-1.5 max-w-sm text-sm text-muted-foreground">{description}</p>}
      {children && <div className="mt-6 flex items-center gap-2">{children}</div>}
    </motion.div>
  );
}
