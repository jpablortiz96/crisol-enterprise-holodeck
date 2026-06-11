"use client";

import { motion } from "framer-motion";
import { AudioLines, CircleDot } from "lucide-react";
import type { CSSProperties } from "react";

type NpcCardProps = {
  persona: string;
  role: string;
  communicationStyle: string;
  avatarStyle: string;
  pressure: number;
  status: string;
  active?: boolean;
  compact?: boolean;
};

const AVATAR_ACCENTS: Record<string, string> = {
  "holographic-operator": "#22d3ee",
  "holographic-stakeholder": "#fbbf24",
  "holographic-specialist": "#34d399",
  "holographic-observer": "#a78bfa",
  "holographic-customer": "#fb7185",
  "holographic-risk": "#f97316",
  "holographic-controls": "#60a5fa",
  "holographic-service": "#2dd4bf",
};

export function NpcCard({
  persona,
  role,
  communicationStyle,
  avatarStyle,
  pressure,
  status,
  active = false,
  compact = false,
}: NpcCardProps) {
  const accent = AVATAR_ACCENTS[avatarStyle] ?? accentForPersona(persona);

  return (
    <motion.article
      layout
      animate={{
        borderColor: active ? accent : "rgba(90, 105, 120, 0.35)",
        boxShadow: active ? `0 0 26px ${accent}24, inset 0 0 18px ${accent}12` : "0 0 0 rgba(0,0,0,0)",
      }}
      transition={{ duration: 0.25 }}
      className={`npc-card relative overflow-hidden border bg-[#09131b] ${compact ? "p-3" : "p-4"}`}
    >
      <div className="npc-scanline" />
      <div className="flex items-center gap-3">
        <div className="relative shrink-0">
          <motion.div
            animate={active ? { scale: [1, 1.06, 1] } : { scale: [1, 1.02, 1] }}
            transition={{ duration: active ? 1.2 : 3.2, repeat: Infinity }}
            className="npc-avatar"
            style={{ "--npc-accent": accent } as CSSProperties}
          >
            <div className="npc-avatar-head" />
            <div className="npc-avatar-body" />
            <div className="npc-avatar-grid" />
          </motion.div>
          {active && (
            <motion.span
              initial={{ opacity: 0, scale: 0.7 }}
              animate={{ opacity: 1, scale: 1 }}
              className="absolute -bottom-1 -right-1 flex h-6 w-6 items-center justify-center rounded-full border border-white/20 bg-[#071016]"
            >
              <AudioLines className="h-3.5 w-3.5" style={{ color: accent }} />
            </motion.span>
          )}
        </div>

        <div className="min-w-0 flex-1">
          <div className="flex items-start justify-between gap-2">
            <div className="min-w-0">
              <p className="text-sm font-semibold leading-4 text-white">{persona}</p>
              <p className="truncate text-[11px] uppercase text-slate-500">{role}</p>
              <p className="mt-1 line-clamp-1 text-[10px] text-slate-600">{communicationStyle}</p>
            </div>
            <span className="flex items-center gap-1 text-[10px] uppercase text-slate-400">
              <CircleDot className={`h-3 w-3 ${active ? "animate-pulse" : ""}`} style={{ color: accent }} />
              {active ? "Speaking" : status}
            </span>
          </div>

          <div className="mt-3 flex items-center gap-2">
            <div className="flex h-5 flex-1 items-end gap-1">
              {[1, 2, 3, 4, 5].map((level) => (
                <motion.span
                  key={level}
                  animate={
                    active && level <= pressure
                      ? { height: ["30%", "100%", "45%"] }
                      : { height: level <= pressure ? "70%" : "22%" }
                  }
                  transition={{ duration: 0.7 + level * 0.08, repeat: active ? Infinity : 0 }}
                  className="w-full rounded-sm"
                  style={{
                    backgroundColor: level <= pressure ? accent : "rgba(100, 116, 139, 0.2)",
                    opacity: level <= pressure ? 0.9 : 0.5,
                  }}
                />
              ))}
            </div>
            <span className="text-[10px] font-medium text-slate-400">P{pressure}</span>
          </div>
        </div>
      </div>
    </motion.article>
  );
}

function accentForPersona(persona: string): string {
  const palette = ["#22d3ee", "#fbbf24", "#34d399", "#fb7185", "#a78bfa", "#60a5fa"];
  const value = [...persona].reduce((total, character) => total + character.charCodeAt(0), 0);
  return palette[value % palette.length];
}
