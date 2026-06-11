"use client";

import { Cell, Pie, PieChart, ResponsiveContainer, RadialBar, RadialBarChart, PolarAngleAxis } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { UserAvatar } from "@/components/shared/user-avatar";
import { aiVsHuman, users } from "@/lib/data";
import { useCountUp } from "@/hooks/use-count-up";

export function AiVsHumanDonut() {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">AI vs Human Resolution</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="relative h-[180px]">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={aiVsHuman}
                dataKey="value"
                innerRadius={58}
                outerRadius={78}
                paddingAngle={3}
                startAngle={90}
                endAngle={450}
                strokeWidth={0}
                animationDuration={900}
              >
                {aiVsHuman.map((entry) => (
                  <Cell key={entry.name} fill={entry.fill} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
          <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
            <span className="font-mono text-2xl font-medium">68%</span>
            <span className="text-[11px] text-muted-foreground">AI handled</span>
          </div>
        </div>
        <div className="mt-2 flex justify-center gap-4">
          {aiVsHuman.map((d) => (
            <span key={d.name} className="flex items-center gap-1.5 text-xs text-muted-foreground">
              <span className="h-2 w-2 rounded-full" style={{ background: d.fill }} />
              {d.name}
            </span>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

export function DeflectionGauge() {
  const value = useCountUp(72.4, 1200);
  const data = [{ name: "deflection", value: 72.4, fill: "url(#gaugeGrad)" }];
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Deflection Rate</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="relative h-[180px]">
          <ResponsiveContainer width="100%" height="100%">
            <RadialBarChart
              innerRadius="72%"
              outerRadius="100%"
              data={data}
              startAngle={220}
              endAngle={-40}
            >
              <defs>
                <linearGradient id="gaugeGrad" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" stopColor="#6366F1" />
                  <stop offset="100%" stopColor="#8B5CF6" />
                </linearGradient>
              </defs>
              <PolarAngleAxis type="number" domain={[0, 100]} angleAxisId={0} tick={false} />
              <RadialBar dataKey="value" cornerRadius={12} background={{ fill: "hsl(var(--secondary))" }} animationDuration={1100} />
            </RadialBarChart>
          </ResponsiveContainer>
          <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
            <span className="font-mono text-3xl font-medium tabular-nums">{value.toFixed(1)}%</span>
            <span className="text-[11px] text-success">↑ 4.2% vs last month</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export function TeamPresence() {
  const online = users.filter((u) => u.status === "online");
  return (
    <Card>
      <CardHeader className="flex-row items-center justify-between space-y-0">
        <CardTitle className="text-base">Team Presence</CardTitle>
        <span className="text-xs text-muted-foreground">
          {online.length} online
        </span>
      </CardHeader>
      <CardContent className="space-y-3">
        {users.slice(0, 5).map((u) => (
          <div key={u.id} className="flex items-center gap-3">
            <UserAvatar name={u.name} src={u.avatar} status={u.status} className="h-8 w-8" />
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium">{u.name}</p>
              <p className="truncate text-xs text-muted-foreground">{u.title}</p>
            </div>
            <span className="text-[11px] capitalize text-muted-foreground">{u.status}</span>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
