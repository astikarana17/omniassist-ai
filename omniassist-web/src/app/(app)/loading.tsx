import { Loader2 } from "lucide-react";

// Shown instantly on every in-app route change, so taps feel responsive even
// while the page compiles (dev) or fetches its data.
export default function Loading() {
  return (
    <div className="flex h-[70vh] items-center justify-center">
      <Loader2 className="h-6 w-6 animate-spin text-ai" />
    </div>
  );
}
