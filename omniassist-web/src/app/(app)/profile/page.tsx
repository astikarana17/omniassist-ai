"use client";

import { Camera, Shield, Smartphone, Key, LogOut } from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { UserAvatar } from "@/components/shared/user-avatar";
import { ThemeToggle } from "@/components/shared/theme-toggle";
import { currentUser } from "@/lib/data";
import { toast } from "sonner";

export default function ProfilePage() {
  return (
    <div className="mx-auto max-w-3xl space-y-6 p-4 sm:p-6">
      <PageHeader title="Profile" description="Manage your personal details and preferences." />

      <Card>
        <CardContent className="flex flex-col items-center gap-4 p-6 sm:flex-row sm:items-center">
          <div className="relative">
            <UserAvatar name={currentUser.name} src={currentUser.avatar} className="h-20 w-20" />
            <button className="absolute -bottom-1 -right-1 flex h-7 w-7 items-center justify-center rounded-full bg-primary text-primary-foreground shadow-md">
              <Camera className="h-3.5 w-3.5" />
            </button>
          </div>
          <div className="text-center sm:text-left">
            <p className="text-lg font-semibold">{currentUser.name}</p>
            <p className="text-sm text-muted-foreground">{currentUser.title}</p>
            <Badge variant="default" className="mt-1.5 capitalize">{currentUser.role}</Badge>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle className="text-base">Personal information</CardTitle></CardHeader>
        <CardContent className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <Label>Full name</Label>
            <Input defaultValue={currentUser.name} />
          </div>
          <div className="space-y-2">
            <Label>Email</Label>
            <Input type="email" defaultValue={currentUser.email} />
          </div>
          <div className="space-y-2">
            <Label>Job title</Label>
            <Input defaultValue={currentUser.title} />
          </div>
          <div className="space-y-2">
            <Label>Timezone</Label>
            <Select defaultValue="ist">
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="ist">India (IST)</SelectItem>
                <SelectItem value="pst">Pacific (PST)</SelectItem>
                <SelectItem value="est">Eastern (EST)</SelectItem>
                <SelectItem value="cet">Central Europe (CET)</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label>Language</Label>
            <Select defaultValue="en">
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="en">English</SelectItem>
                <SelectItem value="es">Spanish</SelectItem>
                <SelectItem value="hi">Hindi</SelectItem>
                <SelectItem value="de">German</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle className="text-base">Preferences</CardTitle></CardHeader>
        <CardContent className="space-y-1">
          <div className="flex items-center justify-between rounded-md px-2 py-2.5">
            <div>
              <p className="text-sm font-medium">Theme</p>
              <p className="text-xs text-muted-foreground">Switch between dark and light.</p>
            </div>
            <ThemeToggle />
          </div>
          {[
            { label: "Email notifications", desc: "Handoffs, mentions and daily digest.", on: true },
            { label: "Slack notifications", desc: "Critical alerts to your Slack.", on: true },
            { label: "Desktop notifications", desc: "Browser push for live events.", on: false },
          ].map((p) => (
            <div key={p.label} className="flex items-center justify-between rounded-md px-2 py-2.5">
              <div>
                <p className="text-sm font-medium">{p.label}</p>
                <p className="text-xs text-muted-foreground">{p.desc}</p>
              </div>
              <Switch defaultChecked={p.on} />
            </div>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex-row items-center gap-2 space-y-0">
          <Shield className="h-4 w-4 text-primary" />
          <CardTitle className="text-base">Security</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-center justify-between rounded-lg border border-border p-3">
            <div className="flex items-center gap-3">
              <Key className="h-4 w-4 text-muted-foreground" />
              <div>
                <p className="text-sm font-medium">Password</p>
                <p className="text-xs text-muted-foreground">Last changed 3 months ago</p>
              </div>
            </div>
            <Button size="sm" variant="secondary">Change</Button>
          </div>
          <div className="flex items-center justify-between rounded-lg border border-border p-3">
            <div className="flex items-center gap-3">
              <Smartphone className="h-4 w-4 text-muted-foreground" />
              <div>
                <p className="text-sm font-medium">Two-factor authentication</p>
                <p className="text-xs text-muted-foreground">Add an extra layer of security</p>
              </div>
            </div>
            <Button size="sm" variant="gradient">Enable 2FA</Button>
          </div>
        </CardContent>
      </Card>

      <div className="flex items-center justify-between">
        <Button variant="ghost" className="text-danger"><LogOut className="h-4 w-4" /> Sign out</Button>
        <Button variant="gradient" onClick={() => toast.success("Profile updated")}>Save changes</Button>
      </div>
    </div>
  );
}
