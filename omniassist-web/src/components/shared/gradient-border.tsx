import { cn } from "@/lib/utils";

/** Premium animated border — a rotating conic indigo→cyan→emerald glow behind a
 *  glass card. Distinctive, Linear/Vercel-grade. */
export function GradientBorder({
  children,
  className,
  radius = "rounded-3xl",
  inner = "bg-card/85",
}: {
  children: React.ReactNode;
  className?: string;
  radius?: string;
  inner?: string;
}) {
  return (
    <div className={cn("relative overflow-hidden p-[1.5px]", radius, className)}>
      <div
        className="absolute left-1/2 top-1/2 h-[180%] w-[180%] -translate-x-1/2 -translate-y-1/2 animate-[spin_7s_linear_infinite]"
        style={{
          background:
            "conic-gradient(from 0deg, transparent 0%, #4F46E5 18%, #22D3EE 38%, #10B981 54%, transparent 72%)",
        }}
      />
      <div className={cn("relative h-full backdrop-blur-xl", radius, inner)}>{children}</div>
    </div>
  );
}
