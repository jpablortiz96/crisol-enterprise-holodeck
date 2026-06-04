import { ClipboardCheck, FileText } from "lucide-react";
import type { ReactNode } from "react";
import type { CompetenceReport as CompetenceReportType } from "@/lib/types";
import { bandLabel, titleCase } from "@/lib/format";

type CompetenceReportProps = {
  report?: CompetenceReportType | null;
};

export function CompetenceReport({ report }: CompetenceReportProps) {
  return (
    <section className="rounded-lg border border-line bg-panel/80 p-5 shadow-soft-border">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-wide text-slate-400">Cited evidence trail</p>
          <h2 className="text-xl font-semibold text-white">Competence Report</h2>
        </div>
        <ClipboardCheck className="h-6 w-6 text-signal" />
      </div>

      {!report ? (
        <div className="mt-5 rounded-lg border border-dashed border-slate-700 p-5 text-sm text-slate-400">
          Run a simulation to generate the first competence report.
        </div>
      ) : (
        <div className="mt-5 space-y-6">
          <div className="grid gap-4 md:grid-cols-4">
            <Metric label="Overall score" value={report.overall_score.toFixed(1)} />
            <Metric label="Readiness band" value={bandLabel(report.readiness_band)} />
            <Metric label="Evidence items" value={String(report.evidence_trail.length)} />
            <Metric label="Citations" value={String(report.citations.length)} />
          </div>

          <p className="rounded-lg border border-line bg-ink/60 p-4 text-sm leading-6 text-slate-300">
            {report.executive_summary}
          </p>

          <div>
            <h3 className="text-sm font-semibold text-white">Dimensions</h3>
            <div className="mt-3 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
              {Object.entries(report.dimensions).map(([id, dimension]) => (
                <div key={id} className="rounded-lg border border-line bg-ink/60 p-3">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-medium text-white">{dimension.label || titleCase(id)}</p>
                    <span className="text-sm text-signal">{dimension.score.toFixed(1)}</span>
                  </div>
                  <div className="mt-2 h-1.5 rounded-full bg-slate-800">
                    <div className="h-1.5 rounded-full bg-signal" style={{ width: `${dimension.score}%` }} />
                  </div>
                  <p className="mt-2 text-xs text-slate-500">Weight {(dimension.weight * 100).toFixed(0)}%</p>
                </div>
              ))}
            </div>
          </div>

          <div className="grid gap-4 lg:grid-cols-2">
            <Panel title="Evidence trail" icon={<FileText className="h-4 w-4" />}>
              {report.evidence_trail.slice(0, 5).map((item) => (
                <div key={item.evidence_id} className="rounded-md border border-line bg-slate-950/60 p-3">
                  <p className="text-xs uppercase tracking-wide text-slate-500">{item.evidence_id} / {titleCase(item.linked_dimension)}</p>
                  <p className="mt-1 text-sm text-white">{item.observation}</p>
                  <p className="mt-1 text-xs leading-5 text-slate-400">{item.impact}</p>
                </div>
              ))}
            </Panel>

            <Panel title="Skill gaps" icon={<ClipboardCheck className="h-4 w-4" />}>
              {report.skill_gaps.slice(0, 5).map((gap) => (
                <div key={`${gap.skill_id}-${gap.dimension_id}`} className="rounded-md border border-line bg-slate-950/60 p-3">
                  <div className="flex items-center justify-between gap-3">
                    <p className="text-sm font-medium text-white">{gap.skill_id}</p>
                    <span className="rounded-full border border-slate-600 px-2 py-0.5 text-[11px] text-slate-300">{gap.severity}</span>
                  </div>
                  <p className="mt-1 text-xs text-slate-400">{gap.rationale}</p>
                </div>
              ))}
            </Panel>
          </div>

          <div className="grid gap-4 lg:grid-cols-2">
            <Panel title="Certification alignment" icon={<ClipboardCheck className="h-4 w-4" />}>
              {report.certification_alignment.slice(0, 5).map((cert) => (
                <div key={cert.certification_id} className="flex items-center justify-between rounded-md border border-line bg-slate-950/60 p-3">
                  <div>
                    <p className="text-sm font-medium text-white">{cert.certification_id}</p>
                    <p className="text-xs text-slate-500">{cert.note}</p>
                  </div>
                  <span className="text-sm text-signal">{cert.alignment_score.toFixed(1)}</span>
                </div>
              ))}
            </Panel>

            <Panel title="Next best actions" icon={<FileText className="h-4 w-4" />}>
              {report.next_best_actions.slice(0, 5).map((action) => (
                <div key={action.action_id} className="rounded-md border border-line bg-slate-950/60 p-3">
                  <p className="text-sm font-medium text-white">{action.title}</p>
                  <p className="mt-1 text-xs leading-5 text-slate-400">{action.rationale}</p>
                  <p className="mt-2 text-[11px] uppercase tracking-wide text-slate-500">{action.estimated_minutes} minutes</p>
                </div>
              ))}
            </Panel>
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
      <p className="mt-1 text-xl font-semibold text-white">{value}</p>
    </div>
  );
}

function Panel({ title, icon, children }: { title: string; icon: ReactNode; children: ReactNode }) {
  return (
    <div>
      <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-white">
        <span className="text-slate-400">{icon}</span>
        {title}
      </div>
      <div className="space-y-2">{children}</div>
    </div>
  );
}
