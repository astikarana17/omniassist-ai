import { Loader2 } from "lucide-react";

/** Full-area loading state shown while live data is being fetched. */
export function PageLoader() {
  return (
    <div className="flex h-[calc(100vh-3.5rem)] items-center justify-center">
      <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
    </div>
  );
}
