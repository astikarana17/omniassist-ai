/**
 * Refined, restrained background — a clean dark canvas with a single whisper of
 * brand tint and a faint grid. Professional (Stripe-like), not "space aurora".
 */
export function AuroraBackground() {
  return (
    <div aria-hidden className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
      <div className="absolute inset-0 bg-background" />
      {/* one very subtle brand glow, top */}
      <div className="absolute -top-[20%] left-1/2 h-[50vh] w-[80vw] -translate-x-1/2 rounded-full bg-primary/[0.06] blur-[120px]" />
      {/* faint grid for depth */}
      <div className="absolute inset-0 grid-overlay opacity-[0.35]" />
    </div>
  );
}
