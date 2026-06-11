import {
  LayoutDashboard,
  Inbox,
  Ticket,
  Target,
  Sparkles,
  BookOpen,
  BarChart3,
  Users,
  Settings,
  HeartPulse,
  AlertTriangle,
  TrendingUp,
  Workflow,
  Bot,
  CreditCard,
  type LucideIcon,
} from "lucide-react";

export interface NavItem {
  label: string;
  href: string;
  icon: LucideIcon;
  badge?: number;
  children?: { label: string; href: string }[];
}

export const navItems: NavItem[] = [
  { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  {
    label: "Inbox",
    href: "/inbox",
    icon: Inbox,
    badge: 6,
    children: [
      { label: "All", href: "/inbox" },
      { label: "AI Support Chat", href: "/inbox/support" },
      { label: "WhatsApp", href: "/inbox/whatsapp" },
      { label: "Email", href: "/inbox/email" },
      { label: "Voice", href: "/inbox/voice" },
    ],
  },
  { label: "Tickets", href: "/tickets", icon: Ticket, badge: 3 },
  {
    label: "Leads",
    href: "/leads",
    icon: Target,
    children: [
      { label: "Lead Dashboard", href: "/leads" },
      { label: "CRM Pipeline", href: "/leads/pipeline" },
    ],
  },
  {
    label: "AI Agents",
    href: "/agents",
    icon: Sparkles,
    children: [
      { label: "Support Agent", href: "/agents/support" },
      { label: "Sales Agent", href: "/agents/sales" },
    ],
  },
  { label: "Knowledge Base", href: "/knowledge-base", icon: BookOpen },
  { label: "Product Expert", href: "/product-expert", icon: Bot },
  { label: "Customer Health", href: "/customer-success", icon: HeartPulse },
  { label: "Knowledge Gaps", href: "/knowledge-gaps", icon: AlertTriangle, badge: 3 },
  { label: "Executive Insights", href: "/insights", icon: TrendingUp },
  { label: "Workflows", href: "/workflows", icon: Workflow },
  { label: "Analytics", href: "/analytics", icon: BarChart3 },
  { label: "Team", href: "/team", icon: Users },
  { label: "Billing", href: "/billing", icon: CreditCard },
  { label: "Settings", href: "/settings", icon: Settings },
];
