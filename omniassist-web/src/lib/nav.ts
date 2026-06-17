import {
  LayoutDashboard,
  Settings,
  Users,
  CreditCard,
  Pill,
  FlaskConical,
  MessageCircleHeart,
  UsersRound,
  Stethoscope,
  CalendarClock,
  Video,
  type LucideIcon,
} from "lucide-react";

export interface NavItem {
  label: string;
  href: string;
  icon: LucideIcon;
  badge?: number;
  children?: { label: string; href: string }[];
}

// Healthcare AI Copilot — focused navigation (AI tools → clinic → workspace).
export const navItems: NavItem[] = [
  { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },

  // AI tools
  { label: "Prescription AI", href: "/prescriptions", icon: Pill },
  { label: "Report Analyzer", href: "/reports", icon: FlaskConical },
  { label: "Health Assistant", href: "/health-assistant", icon: MessageCircleHeart },
  { label: "Video Assistant", href: "/video-assistant", icon: Video },

  // Clinic
  { label: "Patients", href: "/patients", icon: UsersRound },
  { label: "Doctors", href: "/doctors", icon: Stethoscope },
  { label: "Appointments", href: "/appointments", icon: CalendarClock },

  // Workspace
  { label: "Staff", href: "/team", icon: Users },
  { label: "Billing", href: "/billing", icon: CreditCard },
  { label: "Settings", href: "/settings", icon: Settings },
];
