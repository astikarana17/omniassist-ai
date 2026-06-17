"use client";

import { useLayoutEffect, useRef } from "react";
import gsap from "gsap";

/** GSAP staggered entrance for any descendants marked `data-reveal`. Returns a
 *  ref to attach to the container. No flash (runs before paint), self-cleaning. */
export function useReveal<T extends HTMLElement = HTMLDivElement>() {
  const ref = useRef<T>(null);
  useLayoutEffect(() => {
    const el = ref.current;
    if (!el) return;
    const ctx = gsap.context(() => {
      gsap.from("[data-reveal]", {
        opacity: 0,
        y: 26,
        duration: 0.7,
        ease: "power3.out",
        stagger: 0.07,
        clearProps: "transform,opacity",
      });
    }, el);
    return () => ctx.revert();
  }, []);
  return ref;
}
