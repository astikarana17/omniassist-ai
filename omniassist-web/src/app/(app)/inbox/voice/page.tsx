"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import {
  Phone,
  PhoneOff,
  Mic,
  MicOff,
  Sparkles,
  User,
  PauseCircle,
  ArrowRightLeft,
  FileText,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { UserAvatar } from "@/components/shared/user-avatar";
import { conversations } from "@/lib/data";

const transcript = [
  { who: "customer", text: "Hi, I'm locked out of my account — the 2FA isn't working." },
  { who: "ai", text: "I can help with that. For security, can you confirm the email on the account?" },
  { who: "customer", text: "Sure, it's tom@voice.de." },
  { who: "ai", text: "Thanks Tom. I've sent a one-time code to that email. Please read it back to me." },
  { who: "customer", text: "It's 4-8-2-9-1-7." },
  { who: "ai", text: "Verified. I've reset your authenticator — you can set it up fresh now. Anything else?" },
];

function Waveform({ active }: { active: boolean }) {
  return (
    <div className="flex h-12 items-center justify-center gap-1">
      {Array.from({ length: 32 }).map((_, i) => (
        <motion.span
          key={i}
          className="w-1 rounded-full bg-gradient-ai"
          animate={
            active
              ? { height: [6, 8 + ((i * 7) % 28), 6] }
              : { height: 6 }
          }
          transition={{
            duration: 0.8 + (i % 5) * 0.12,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
      ))}
    </div>
  );
}

export default function VoiceSupportPage() {
  const [seconds, setSeconds] = useState(252);
  const [muted, setMuted] = useState(false);
  const [onCall, setOnCall] = useState(true);
  const [visible, setVisible] = useState(1);
  const contact = conversations.find((c) => c.channel === "voice")!.contact;

  useEffect(() => {
    if (!onCall) return;
    const t = setInterval(() => setSeconds((s) => s + 1), 1000);
    return () => clearInterval(t);
  }, [onCall]);

  useEffect(() => {
    if (visible >= transcript.length) return;
    const t = setTimeout(() => setVisible((v) => v + 1), 1600);
    return () => clearTimeout(t);
  }, [visible]);

  const mm = String(Math.floor(seconds / 60)).padStart(2, "0");
  const ss = String(seconds % 60).padStart(2, "0");

  return (
    <div className="mx-auto max-w-5xl space-y-6 p-4 sm:p-6">
      <div className="flex items-center gap-2">
        <h1 className="text-lg font-semibold">Voice Support</h1>
        <Badge variant="warning">Preview</Badge>
        <span className="text-xs text-muted-foreground">
          Interactive simulation — live calls connect via Twilio Voice on the Enterprise plan.
        </span>
      </div>
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Call card */}
        <Card className="lg:col-span-1">
          <CardContent className="flex flex-col items-center p-6 text-center">
            <div className="relative">
              {onCall && (
                <span className="absolute inset-0 animate-ping rounded-full bg-ai/20" />
              )}
              <UserAvatar name={contact.name} src={contact.avatar} className="h-24 w-24 ring-4 ring-ai/20" />
            </div>
            <p className="mt-4 text-lg font-semibold">{contact.name}</p>
            <p className="text-sm text-muted-foreground">{contact.phone}</p>
            <Badge variant={onCall ? "ai" : "secondary"} className="mt-3">
              {onCall ? "● In call" : "Call ended"} · {mm}:{ss}
            </Badge>

            <div className="mt-6 w-full">
              <Waveform active={onCall && !muted} />
            </div>

            <div className="mt-6 flex items-center gap-3">
              <Button
                variant="secondary"
                size="icon"
                className="h-12 w-12 rounded-full"
                onClick={() => setMuted((m) => !m)}
              >
                {muted ? <MicOff className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
              </Button>
              <Button variant="secondary" size="icon" className="h-12 w-12 rounded-full">
                <PauseCircle className="h-5 w-5" />
              </Button>
              <Button
                variant="destructive"
                size="icon"
                className="h-14 w-14 rounded-full"
                onClick={() => setOnCall(false)}
              >
                <PhoneOff className="h-6 w-6" />
              </Button>
            </div>

            <Button variant="outline" className="mt-6 w-full">
              <ArrowRightLeft className="h-4 w-4" /> Warm transfer to human
            </Button>
          </CardContent>
        </Card>

        {/* Live transcript */}
        <Card className="lg:col-span-2">
          <CardHeader className="flex-row items-center justify-between space-y-0">
            <CardTitle className="flex items-center gap-2 text-base">
              <Sparkles className="h-4 w-4 text-ai" /> Live Transcription
            </CardTitle>
            <Badge variant="ai" className="gap-1">
              <span className="relative flex h-1.5 w-1.5">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-ai opacity-75" />
                <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-ai" />
              </span>
              Transcribing
            </Badge>
          </CardHeader>
          <CardContent className="space-y-3">
            {transcript.slice(0, visible).map((line, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex gap-3 ${line.who === "customer" ? "" : ""}`}
              >
                <span
                  className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full ${
                    line.who === "ai" ? "bg-gradient-ai" : "bg-secondary"
                  }`}
                >
                  {line.who === "ai" ? (
                    <Sparkles className="h-3.5 w-3.5 text-white" />
                  ) : (
                    <User className="h-3.5 w-3.5" />
                  )}
                </span>
                <div>
                  <p className="text-[11px] font-medium text-muted-foreground">
                    {line.who === "ai" ? "OmniAssist AI" : contact.name}
                  </p>
                  <p className="text-sm">{line.text}</p>
                </div>
              </motion.div>
            ))}
            {visible < transcript.length && (
              <div className="flex gap-3 pl-10 text-sm text-muted-foreground">
                <span className="animate-pulse">● ● ●</span>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* AI call summary */}
      <Card className="border-ai/20 bg-ai/5">
        <CardHeader className="flex-row items-center gap-2 space-y-0">
          <FileText className="h-4 w-4 text-ai" />
          <CardTitle className="text-base">AI Call Summary (auto-generated)</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          <p><span className="font-medium">Reason:</span> Customer locked out due to failing 2FA.</p>
          <p><span className="font-medium">Resolution:</span> Verified identity via email OTP, reset authenticator on the call.</p>
          <p><span className="font-medium">Next steps:</span> Customer to re-enroll authenticator app. Ticket #1039 auto-created and resolved.</p>
          <div className="flex gap-2 pt-2">
            <Button size="sm" variant="ai"><Phone className="h-4 w-4" /> Create ticket</Button>
            <Button size="sm" variant="secondary">Edit summary</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
