import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { initials, cn } from "@/lib/utils";

const statusColor: Record<string, string> = {
  online: "bg-success",
  away: "bg-warning",
  offline: "bg-muted-foreground",
};

export function UserAvatar({
  name,
  src,
  status,
  className,
  ring = false,
}: {
  name: string;
  src?: string;
  status?: "online" | "away" | "offline";
  className?: string;
  ring?: boolean;
}) {
  return (
    <div className="relative shrink-0">
      <Avatar className={cn(ring && "ring-2 ring-border-strong", className)}>
        {src && <AvatarImage src={src} alt={name} />}
        <AvatarFallback>{initials(name)}</AvatarFallback>
      </Avatar>
      {status && (
        <span
          className={cn(
            "absolute -bottom-0.5 -right-0.5 h-2.5 w-2.5 rounded-full border-2 border-card",
            statusColor[status]
          )}
        />
      )}
    </div>
  );
}

export function AvatarGroup({
  people,
  max = 4,
  size = "h-7 w-7",
}: {
  people: { name: string; avatar: string }[];
  max?: number;
  size?: string;
}) {
  const shown = people.slice(0, max);
  const extra = people.length - shown.length;
  return (
    <div className="flex items-center -space-x-2">
      {shown.map((p) => (
        <Avatar key={p.name} className={cn(size, "ring-2 ring-card")}>
          <AvatarImage src={p.avatar} alt={p.name} />
          <AvatarFallback>{initials(p.name)}</AvatarFallback>
        </Avatar>
      ))}
      {extra > 0 && (
        <div
          className={cn(
            size,
            "flex items-center justify-center rounded-full bg-secondary text-[10px] font-medium ring-2 ring-card"
          )}
        >
          +{extra}
        </div>
      )}
    </div>
  );
}
