import { Network, ShieldCheck } from "lucide-react";
import type { ReactNode } from "react";
import type { ManagerFragilityMap as ManagerFragilityMapType } from "@/lib/types";
import { titleCase } from "@/lib/format";

type ManagerFragilityMapProps = {
  map?: ManagerFragilityMapType | null;
};

export function ManagerFragilityMap({ map }: ManagerFragilityMapProps) {
  return (
    <section className="rounded-lg border border-line bg-panel/80 p-5 shadow-soft-border">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-wide text-slate-400">Synthetic data only</p>
          <h2 className="text-xl font-semibold text-white">Manager Fragility Map</h2>
        </div>
        <Network className="h-6 w-6 text-caution" />
      </div>

      {!map || map.session_count === 0 ? (
        <div className="mt-5 rounded-lg border border-dashed border-slate-700 p-5 text-sm text-slate-400">
          Run a simulation to generate manager-level readiness signals.
        </div>
      ) : (
        <div className="mt-5 space-y-5">
          <div className="grid gap-4 md:grid-cols-4">
            <Metric label="Average score" value={map.team_readiness.average_score.toFixed(1)} />
            <Metric label="Sessions" value={String(map.session_count)} />
            <Metric label="Risk dimension" value={titleCase(map.team_readiness.highest_risk_dimension || "none")} />
            <Metric label="Risk skill" value={map.team_readiness.highest_risk_skill || "None"} />
          </div>

          <div className="grid gap-4 lg:grid-cols-3">
            <Panel title="Role risk">
              {map.role_risk.slice(0, 4).map((role) => (
                <div key={role.role_id} className="rounded-md border border-line bg-ink/60 p-3">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-semibold text-white">{role.role_id}</p>
                    <span className="rounded-full border border-slate-600 px-2 py-0.5 text-[11px] text-slate-300">{role.risk_band}</span>
                  </div>
                  <p className="mt-1 text-sm text-signal">{role.average_score.toFixed(1)}</p>
                  <p className="mt-2 text-xs leading-5 text-slate-400">{role.recommended_manager_action}</p>
                </div>
              ))}
            </Panel>

            <Panel title="Skill fragility">
              {map.skill_fragility.slice(0, 5).map((skill) => (
                <div key={skill.skill_id} className="rounded-md border border-line bg-ink/60 p-3">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-semibold text-white">{skill.skill_id}</p>
                    <span className="text-sm text-caution">{skill.risk_score.toFixed(1)}</span>
                  </div>
                  <p className="mt-1 text-xs text-slate-400">{skill.recommended_intervention}</p>
                </div>
              ))}
            </Panel>

            <Panel title="Certification readiness">
              {map.certification_readiness.slice(0, 5).map((cert) => (
                <div key={cert.certification_id} className="flex items-center justify-between rounded-md border border-line bg-ink/60 p-3">
                  <div>
                    <p className="text-sm font-semibold text-white">{cert.certification_id}</p>
                    <p className="text-xs text-slate-500">{cert.risk}</p>
                  </div>
                  <span className="text-sm text-signal">{cert.alignment_score.toFixed(1)}</span>
                </div>
              ))}
            </Panel>
          </div>

          <div className="flex items-center gap-2 rounded-lg border border-signal/30 bg-signal/10 p-3 text-sm text-emerald-100">
            <ShieldCheck className="h-4 w-4" />
            {map.privacy_note}
          </div>
        </div>
      )}
    </section>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-line bg-ink/60 p-3">
      <p className="text-xs uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-1 text-lg font-semibold text-white">{value}</p>
    </div>
  );
}

function Panel({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div>
      <p className="mb-3 text-sm font-semibold text-white">{title}</p>
      <div className="space-y-2">{children}</div>
    </div>
  );
}
