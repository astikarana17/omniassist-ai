import { Globe, MessageCircle, Mail, Phone } from "lucide-react";
import type { Channel } from "@/types";
import { cn } from "@/lib/utils";

const config: Record<
  Channel,
  { icon: typeof Globe; label: string; className: string }
> = {
  web: { icon: Globe, label: "Website", className: "text-info bg-info/10" },
  whatsapp: { icon: MessageCircle, label: "WhatsApp", className: "text-success bg-success/10" },
  email: { icon: Mail, label: "Email", className: "text-primary bg-primary/10" },
  voice: { icon: Phone, label: "Voice", className: "text-ai bg-ai/10" },
};

export function ChannelIcon({
  channel,
  className,
  withBg = true,
}: {
  channel: Channel;
  className?: string;
  withBg?: boolean;
}) {
  const { icon: Icon, label, className: c } = config[channel];
  return (
    <span
      title={label}
      className={cn(
        "inline-flex items-center justify-center rounded-md",
        withBg ? cn("h-6 w-6", c) : "text-current",
        className
      )}
    >
      <Icon className="h-3.5 w-3.5" />
    </span>
  );
}

export const channelLabel = (channel: Channel) => config[channel].label;
