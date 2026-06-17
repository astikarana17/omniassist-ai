"use client";

import { useRef, type ReactNode } from "react";
import { motion, useScroll, useTransform } from "framer-motion";
import { cn } from "@/lib/utils";

/**
 * One card in a sticky-stacking "deck". As you scroll:
 *  - the card pins near the top with an offset that GROWS per index, so the
 *    cards fan into a stack instead of pinning on the same line;
 *  - the card underneath scales down (origin-top) so its bottom tucks behind the
 *    next one — a layered deck-of-cards depth.
 */
export function StackCard({
  index,
  total,
  children,
  className,
  baseTop = 96,
  topStep = 28,
  scaleStep = 0.03,
}: {
  index: number;
  total: number;
  children: ReactNode;
  className?: string;
  baseTop?: number;
  topStep?: number;
  scaleStep?: number;
}) {
  const ref = useRef<HTMLDivElement>(null);
  // 0 when the card's top hits the viewport bottom → 1 when it hits the top
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "start start"],
  });
  // earlier cards (lower index) shrink more so they sit deeper in the stack
  const targetScale = 1 - (total - 1 - index) * scaleStep;
  const scale = useTransform(scrollYProgress, [0, 1], [1, targetScale]);

  return (
    <div ref={ref} className="sticky" style={{ top: `${baseTop + index * topStep}px` }}>
      <motion.article style={{ scale }} className={cn("origin-top will-change-transform", className)}>
        {children}
      </motion.article>
    </div>
  );
}

/** Scroll fade-in wrapper — content rises + fades the first time it enters view. */
export function FadeIn({
  children,
  delay = 0,
  className,
}: {
  children: ReactNode;
  delay?: number;
  className?: string;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-80px" }}
      transition={{ duration: 0.7, delay, ease: [0.25, 0.1, 0.25, 1] }}
      className={className}
    >
      {children}
    </motion.div>
  );
}
