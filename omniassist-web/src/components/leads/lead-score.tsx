import { Flame } from "lucide-react";
import { cn } from "@/lib/utils";

export function LeadScore({ score }: { score: number }) {
  const hot = score >= 85;
  const warm = score >= 65 && score < 85;
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-semibold tabular-nums",
        hot && "bg-danger/10 text-danger",
        warm && "bg-warning/10 text-warning",
        !hot && !warm && "bg-secondary text-muted-foreground"
      )}
    >
      {hot && <Flame className="h-3 w-3" />}
      {score}
    </span>
  );
}
