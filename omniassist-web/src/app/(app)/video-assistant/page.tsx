"use client";

import { Camera, Mic, ShieldAlert, ExternalLink } from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

// Public Trugen agent id (safe to expose — it only renders the embed). Override
// via NEXT_PUBLIC_TRUGEN_AGENT_ID without a code change.
const AGENT_ID =
  process.env.NEXT_PUBLIC_TRUGEN_AGENT_ID ?? "77fe4d05-c38c-48bc-9aa0-8f7394e4f07d";
const EMBED_URL = `https://app.trugen.ai/embed/${AGENT_ID}`;

export default function VideoAssistantPage() {
  return (
    <div className="mx-auto flex h-[calc(100vh-5rem)] max-w-5xl flex-col p-4 sm:p-6">
      <PageHeader
        title="Video Assistant"
        description="Have a face-to-face conversation with our AI health assistant — ask about medicines, reports or appointments."
      >
        <Button variant="gradient" className="gap-2" asChild>
          <a href={EMBED_URL} target="_blank" rel="noopener noreferrer">
            <ExternalLink className="h-4 w-4" /> Open in new tab
          </a>
        </Button>
      </PageHeader>

      <Card className="mt-3 border-ai/20 bg-ai/5">
        <CardContent className="flex flex-wrap items-center gap-x-5 gap-y-1.5 p-3 text-xs text-muted-foreground">
          <span className="flex items-center gap-1.5"><Camera className="h-3.5 w-3.5 text-ai" /> Allow camera</span>
          <span className="flex items-center gap-1.5"><Mic className="h-3.5 w-3.5 text-ai" /> Allow microphone</span>
          <span className="flex items-center gap-1.5"><ShieldAlert className="h-3.5 w-3.5" /> AI assistant — not a diagnosis. Consult a doctor for medical advice.</span>
        </CardContent>
      </Card>

      {/* Trugen video avatar embed */}
      <div className="mt-3 flex-1 overflow-hidden rounded-2xl border border-border bg-card">
        <iframe
          src={EMBED_URL}
          title="AI Video Assistant"
          className="h-full w-full"
          style={{ minHeight: 520, border: 0 }}
          allow="camera *; microphone *; autoplay; fullscreen; display-capture"
          allowFullScreen
        />
      </div>

      <p className="mt-2 text-center text-xs text-muted-foreground">
        Mic or camera not working in the embed?{" "}
        <a href={EMBED_URL} target="_blank" rel="noopener noreferrer" className="text-ai hover:underline">
          Open it in a new tab
        </a>{" "}
        — that usually fixes browser permission issues.
      </p>
    </div>
  );
}
