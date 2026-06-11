"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  Upload,
  Globe,
  FileText,
  HelpCircle,
  Plus,
  Search,
  Sparkles,
  CheckCircle2,
  Loader2,
  AlertCircle,
  MoreVertical,
} from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { kbDocuments as mockKb } from "@/lib/data";
import type { KbDocument } from "@/types";
import { relativeTime } from "@/lib/utils";
import { useKbDocuments, useKbSearch, useKbCrawl, apiConfigured } from "@/lib/api-hooks";
import { toast } from "sonner";

const sourceIcon = { upload: FileText, crawl: Globe, faq: HelpCircle };

const statusConfig: Record<
  KbDocument["status"],
  { label: string; icon: typeof CheckCircle2; variant: React.ComponentProps<typeof Badge>["variant"] }
> = {
  ready: { label: "Ready", icon: CheckCircle2, variant: "success" },
  processing: { label: "Indexing", icon: Loader2, variant: "warning" },
  failed: { label: "Failed", icon: AlertCircle, variant: "danger" },
};

export default function KnowledgeBasePage() {
  const [query, setQuery] = useState("");
  const { data: liveDocs } = useKbDocuments();
  const kbDocuments = liveDocs ?? (apiConfigured() ? [] : mockKb);
  const search = useKbSearch();
  const crawl = useKbCrawl();
  const [crawlUrl, setCrawlUrl] = useState("");
  const tested = search.isSuccess || search.isPending;
  const testChunks = search.data ?? [];

  const startCrawl = () => {
    const url = crawlUrl.trim();
    if (!/^https?:\/\/.+/.test(url)) {
      toast.error("Enter a full URL starting with https://");
      return;
    }
    crawl.mutate(url, {
      onSuccess: () => {
        toast.success("Crawl started — the page will be indexed shortly");
        setCrawlUrl("");
      },
      onError: () => toast.error("Could not crawl that URL"),
    });
  };

  const totalChunks = kbDocuments.reduce((s, d) => s + (d.chunks || 0), 0);
  const coverage = Math.min(95, 40 + kbDocuments.length * 5);

  const runSearch = () => {
    if (query.trim()) search.mutate(query.trim());
  };

  return (
    <div className="mx-auto max-w-[1400px] space-y-6 p-4 sm:p-6">
      <PageHeader title="Knowledge Base" description="Feed your AI agents. Upload docs, crawl sites, sync FAQs." />

      {/* KB health */}
      <Card className="border-ai/20 bg-ai/5">
        <CardContent className="flex flex-col gap-4 p-5 sm:flex-row sm:items-center">
          <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-gradient-ai">
            <Sparkles className="h-5 w-5 text-white" />
          </span>
          <div className="flex-1">
            <p className="text-sm font-medium">
              Your AI can confidently answer ~{coverage}% of common questions
            </p>
            <p className="text-xs text-muted-foreground">
              {totalChunks} chunks indexed across {kbDocuments.length} sources — these power every AI agent.
            </p>
          </div>
          <div className="w-full sm:w-48">
            <Progress value={coverage} className="h-2" />
          </div>
        </CardContent>
      </Card>

      {/* Upload dropzone */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <div className="flex flex-col items-center justify-center rounded-xl border-2 border-dashed border-border-strong bg-subtle/40 p-6 text-center transition-colors hover:border-primary/40">
          <Upload className="h-7 w-7 text-muted-foreground" />
          <p className="mt-2 text-sm font-medium">Drag & drop files</p>
          <p className="text-xs text-muted-foreground">PDF, DOCX, MD up to 25MB</p>
          <Button size="sm" variant="secondary" className="mt-3">Browse files</Button>
        </div>
        <div className="flex flex-col justify-center rounded-xl border border-border bg-card p-6">
          <Globe className="h-7 w-7 text-info" />
          <p className="mt-2 text-sm font-medium">Crawl a website</p>
          <p className="mb-3 text-xs text-muted-foreground">We&apos;ll index your docs & help center.</p>
          <div className="flex gap-2">
            <Input
              placeholder="https://docs.yoursite.com"
              className="h-8 text-xs"
              value={crawlUrl}
              onChange={(e) => setCrawlUrl(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && startCrawl()}
            />
            <Button size="sm" onClick={startCrawl} loading={crawl.isPending}>Crawl</Button>
          </div>
        </div>
        <div className="flex flex-col justify-center rounded-xl border border-border bg-card p-6">
          <HelpCircle className="h-7 w-7 text-ai" />
          <p className="mt-2 text-sm font-medium">Add FAQ pairs</p>
          <p className="mb-3 text-xs text-muted-foreground">Manually add question & answer entries.</p>
          <Button size="sm" variant="secondary">New FAQ</Button>
        </div>
      </div>

      {/* Documents grid */}
      <div>
        <h2 className="mb-3 text-sm font-semibold">Sources ({kbDocuments.length})</h2>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {kbDocuments.map((doc, i) => {
            const Icon = sourceIcon[doc.sourceType];
            const status = statusConfig[doc.status];
            const StatusIcon = status.icon;
            return (
              <motion.div
                key={doc.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
              >
                <Card interactive className="p-4">
                  <div className="flex items-start justify-between">
                    <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-secondary">
                      <Icon className="h-4 w-4" />
                    </span>
                    <button className="text-muted-foreground hover:text-foreground">
                      <MoreVertical className="h-4 w-4" />
                    </button>
                  </div>
                  <p className="mt-3 truncate text-sm font-medium">{doc.title}</p>
                  <p className="text-xs text-muted-foreground">{doc.sizeLabel}</p>
                  {doc.status === "processing" && doc.progress != null && (
                    <Progress value={doc.progress} className="mt-3 h-1.5" />
                  )}
                  <div className="mt-3 flex items-center justify-between">
                    <Badge variant={status.variant} className="gap-1">
                      <StatusIcon className={`h-3 w-3 ${doc.status === "processing" ? "animate-spin" : ""}`} />
                      {status.label}
                    </Badge>
                    <span className="text-[11px] text-muted-foreground">
                      {doc.chunks > 0 ? `${doc.chunks} chunks` : relativeTime(doc.updatedAt)}
                    </span>
                  </div>
                </Card>
              </motion.div>
            );
          })}
        </div>
      </div>

      {/* Retrieval playground */}
      <Card>
        <CardContent className="space-y-4 p-5">
          <div className="flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-ai" />
            <h2 className="text-sm font-semibold">Retrieval Playground</h2>
            <span className="text-xs text-muted-foreground">Test what your AI retrieves for a query</span>
          </div>
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && runSearch()}
                placeholder="e.g. How do refunds work?"
                className="pl-8"
              />
            </div>
            <Button variant="gradient" onClick={runSearch} loading={search.isPending}>
              Test retrieval
            </Button>
          </div>
          {tested && (
            <div className="space-y-2">
              {search.isPending && (
                <p className="text-xs text-muted-foreground">Searching the vector knowledge base…</p>
              )}
              {!search.isPending && testChunks.length === 0 && (
                <p className="text-xs text-muted-foreground">No matching chunks found.</p>
              )}
              {testChunks.map((chunk, i) => (
                <motion.div
                  key={`${chunk.title}-${i}`}
                  initial={{ opacity: 0, x: 8 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.08 }}
                  className="rounded-lg border border-border bg-subtle/50 p-3"
                >
                  <div className="flex items-center justify-between">
                    <span className="flex items-center gap-1.5 text-xs font-medium text-ai">
                      <FileText className="h-3.5 w-3.5" /> {chunk.title}
                    </span>
                    <Badge variant="ai" className="font-mono">{chunk.score.toFixed(2)}</Badge>
                  </div>
                  <p className="mt-1.5 text-xs text-muted-foreground">{chunk.text}</p>
                </motion.div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
