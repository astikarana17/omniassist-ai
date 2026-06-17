import { Card, CardContent } from "@/components/ui/card";
import { Label } from "@/components/ui/label";

export function Field({
  label,
  children,
  className = "",
}: {
  label: string;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={`space-y-1.5 ${className}`}>
      <Label className="text-xs text-muted-foreground">{label}</Label>
      {children}
    </div>
  );
}

export function DemoNote() {
  return (
    <Card className="border-warning/30 bg-warning/5">
      <CardContent className="p-4 text-sm text-muted-foreground">
        Demo mode — set <code className="rounded bg-secondary px-1">NEXT_PUBLIC_API_URL</code> to manage real records.
      </CardContent>
    </Card>
  );
}
