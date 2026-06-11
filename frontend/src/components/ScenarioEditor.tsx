"use client";

import { useEffect, useMemo, useState } from "react";
import {
  Braces,
  CheckCircle2,
  ChevronDown,
  FileInput,
  Plus,
  Save,
  Trash2,
  UserRound,
} from "lucide-react";
import { useWarRoomStore } from "@/store/warRoomStore";
import type { PersonaMetadata } from "@/lib/types";

type DecisionDraft = {
  id: string;
  label: string;
  description: string;
  action_type: string;
  competencies: string[];
  risk_effect: "increase" | "decrease" | "neutral";
  expected_outcome: string;
};

type TurnDraft = {
  turn_id: string;
  situation: string;
  options: DecisionDraft[];
  evaluation_focus: string[];
};

type ScenarioDraft = {
  scenario_id: string;
  title: string;
  industry: string;
  role_id: string;
  difficulty: string;
  estimated_minutes: number;
  data_classification: "sanitized-training";
  business_context: string;
  systems: string[];
  initial_stakes: string;
  personas: PersonaMetadata[];
  turns: TurnDraft[];
  success_criteria: string[];
  failure_modes: string[];
  knowledge_refs: string[];
  tags: string[];
};

const STARTER_SCENARIO: ScenarioDraft = {
  scenario_id: "SCN-WORKSPACE-001",
  title: "Workspace operations scenario",
  industry: "Digital Services",
  role_id: "ROLE-OPERATIONS-LEAD",
  difficulty: "standard",
  estimated_minutes: 7,
  data_classification: "sanitized-training",
  business_context: "A fictional operational workflow requires a bounded response.",
  systems: ["SVC-orders", "SVC-observability"],
  initial_stakes: "Customer continuity and revenue confidence are at risk.",
  personas: [createPersona(1)],
  turns: [createTurn(1)],
  success_criteria: ["Establish accountable ownership"],
  failure_modes: ["Act before evidence is sufficient"],
  knowledge_refs: ["operations-guide"],
  tags: ["workspace", "operations"],
};

export function ScenarioEditor() {
  const {
    workspaceTemplates,
    workspaceRoles,
    isWorkspaceSaving,
    validateScenario,
    saveScenario,
  } = useWarRoomStore();
  const [templateId, setTemplateId] = useState("");
  const [draft, setDraft] = useState<ScenarioDraft>(STARTER_SCENARIO);
  const [rawJson, setRawJson] = useState(JSON.stringify(STARTER_SCENARIO, null, 2));
  const [advancedOpen, setAdvancedOpen] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [validationErrors, setValidationErrors] = useState<string[]>([]);

  useEffect(() => {
    if (!workspaceRoles[0] || draft.role_id !== STARTER_SCENARIO.role_id) {
      return;
    }
    setDraft((current) => ({ ...current, role_id: workspaceRoles[0].role_id }));
  }, [draft.role_id, workspaceRoles]);

  useEffect(() => {
    setRawJson(JSON.stringify(draft, null, 2));
  }, [draft]);

  const selectedTemplate = useMemo(
    () => workspaceTemplates?.scenario_templates.find((item) => item.scenario_id === templateId),
    [templateId, workspaceTemplates],
  );

  function loadTemplate() {
    if (!selectedTemplate) {
      setMessage("Select a scenario template first.");
      return;
    }
    const nextDraft = normalizeDraft(selectedTemplate);
    setDraft(nextDraft);
    setRawJson(JSON.stringify(nextDraft, null, 2));
    setValidationErrors([]);
    setMessage("Template loaded. Update its identifier and details before saving.");
  }

  async function validate() {
    const scenario = parseCurrentScenario();
    if (!scenario) {
      return;
    }
    try {
      const result = await validateScenario(scenario);
      setValidationErrors(result.errors);
      setMessage(result.valid ? "Scenario validation passed." : "Resolve the validation issues before saving.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Scenario validation failed.");
    }
  }

  async function submit() {
    const scenario = parseCurrentScenario();
    if (!scenario) {
      return;
    }
    try {
      const result = await validateScenario(scenario);
      if (!result.valid) {
        setValidationErrors(result.errors);
        setMessage("Resolve the validation issues before saving.");
        return;
      }
      await saveScenario(scenario);
      setValidationErrors([]);
      setMessage("Scenario validated and saved.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Scenario could not be saved.");
    }
  }

  function parseCurrentScenario(): Record<string, unknown> | null {
    if (!advancedOpen) {
      return draft as unknown as Record<string, unknown>;
    }
    try {
      const scenario = JSON.parse(rawJson) as Record<string, unknown>;
      setDraft(normalizeDraft(scenario));
      return scenario;
    } catch (error) {
      setMessage(error instanceof Error ? `Invalid JSON: ${error.message}` : "Invalid JSON.");
      return null;
    }
  }

  return (
    <section className="war-panel scenario-builder">
      <div className="panel-header">
        <div>
          <p className="panel-kicker">Guided authoring</p>
          <h2 className="panel-title">Scenario Editor</h2>
        </div>
        <Braces className="h-5 w-5 text-cyan-300" />
      </div>

      <div className="scenario-builder-body">
        <div className="scenario-template-loader">
          <label className="technical-field">
            Scenario template
            <select value={templateId} onChange={(event) => setTemplateId(event.target.value)}>
              <option value="">Select a generic scenario template</option>
              {workspaceTemplates?.scenario_templates.map((template) => (
                <option key={template.scenario_id} value={template.scenario_id}>{template.title}</option>
              ))}
            </select>
          </label>
          <button type="button" className="control-button control-secondary" onClick={loadTemplate}>
            <FileInput className="h-4 w-4" /> Load Template
          </button>
        </div>

        <EditorSection number={1} title="Scenario basics">
          <div className="guided-form-grid">
            <Field label="Scenario ID"><input value={draft.scenario_id} onChange={(event) => setDraft({ ...draft, scenario_id: event.target.value })} /></Field>
            <Field label="Scenario title"><input value={draft.title} onChange={(event) => setDraft({ ...draft, title: event.target.value })} /></Field>
            <Field label="Industry"><input value={draft.industry} onChange={(event) => setDraft({ ...draft, industry: event.target.value })} /></Field>
            <Field label="Evaluated role">
              <select value={draft.role_id} onChange={(event) => setDraft({ ...draft, role_id: event.target.value })}>
                <option value="">Select a role</option>
                {workspaceRoles.map((role) => <option key={role.role_id} value={role.role_id}>{role.title}</option>)}
              </select>
            </Field>
            <Field label="Difficulty">
              <select value={draft.difficulty} onChange={(event) => setDraft({ ...draft, difficulty: event.target.value })}>
                <option value="standard">Standard</option>
                <option value="advanced">Advanced</option>
                <option value="critical">Critical</option>
              </select>
            </Field>
            <Field label="Estimated minutes"><input type="number" min={1} value={draft.estimated_minutes} onChange={(event) => setDraft({ ...draft, estimated_minutes: Number(event.target.value) })} /></Field>
            <Field label="Business context" wide><textarea value={draft.business_context} onChange={(event) => setDraft({ ...draft, business_context: event.target.value })} /></Field>
            <Field label="Initial stakes" wide><textarea value={draft.initial_stakes} onChange={(event) => setDraft({ ...draft, initial_stakes: event.target.value })} /></Field>
          </div>
        </EditorSection>

        <EditorSection number={2} title="Scenario-driven personas">
          <div className="persona-editor-list">
            {draft.personas.map((persona, index) => (
              <article className="persona-editor-card" key={`${persona.persona}-${index}`}>
                <div className="persona-editor-heading">
                  <span><UserRound className="h-4 w-4" /> Persona {index + 1}</span>
                  <button type="button" className="icon-control" disabled={draft.personas.length === 1} onClick={() => setDraft({ ...draft, personas: draft.personas.filter((_, itemIndex) => itemIndex !== index) })} title="Remove persona"><Trash2 className="h-4 w-4" /></button>
                </div>
                <div className="guided-form-grid">
                  <Field label="Persona name"><input value={persona.persona} onChange={(event) => updatePersona(index, "persona", event.target.value)} /></Field>
                  <Field label="Role"><input value={persona.role} onChange={(event) => updatePersona(index, "role", event.target.value)} /></Field>
                  <Field label="Communication style"><input value={persona.communication_style} onChange={(event) => updatePersona(index, "communication_style", event.target.value)} /></Field>
                  <Field label="Pressure profile">
                    <select value={persona.pressure_profile} onChange={(event) => updatePersona(index, "pressure_profile", event.target.value)}>
                      <option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option><option value="critical">Critical</option>
                    </select>
                  </Field>
                  <Field label="Voice style">
                    <select value={persona.voice_style} onChange={(event) => updatePersona(index, "voice_style", event.target.value)}>
                      <option value="calm">Calm</option><option value="urgent">Urgent</option><option value="analytical">Analytical</option><option value="supportive">Supportive</option>
                    </select>
                  </Field>
                  <Field label="Avatar style"><input value={persona.avatar_style} onChange={(event) => updatePersona(index, "avatar_style", event.target.value)} /></Field>
                </div>
              </article>
            ))}
          </div>
          <button type="button" className="control-button control-secondary" onClick={() => setDraft({ ...draft, personas: [...draft.personas, createPersona(draft.personas.length + 1)] })}>
            <Plus className="h-4 w-4" /> Add Persona
          </button>
        </EditorSection>

        <EditorSection number={3} title="Turns and decision options">
          <div className="turn-editor-list">
            {draft.turns.map((turn, turnIndex) => (
              <article className="turn-editor-card" key={turn.turn_id}>
                <div className="persona-editor-heading">
                  <span>Turn {turnIndex + 1}</span>
                  <button type="button" className="icon-control" disabled={draft.turns.length === 1} onClick={() => setDraft({ ...draft, turns: draft.turns.filter((_, itemIndex) => itemIndex !== turnIndex) })} title="Remove turn"><Trash2 className="h-4 w-4" /></button>
                </div>
                <Field label="Situation" wide><textarea value={turn.situation} onChange={(event) => updateTurn(turnIndex, { ...turn, situation: event.target.value })} /></Field>
                <div className="decision-option-grid">
                  {turn.options.map((option, optionIndex) => (
                    <div className="decision-option-card" key={`${turn.turn_id}-${option.id}`}>
                      <div className="persona-editor-heading">
                        <span>Option {optionIndex + 1}</span>
                        <button type="button" className="icon-control" disabled={turn.options.length === 1} onClick={() => updateTurn(turnIndex, { ...turn, options: turn.options.filter((_, itemIndex) => itemIndex !== optionIndex) })} title="Remove option"><Trash2 className="h-4 w-4" /></button>
                      </div>
                      <Field label="Label"><input value={option.label} onChange={(event) => updateOption(turnIndex, optionIndex, { ...option, label: event.target.value })} /></Field>
                      <Field label="Description"><textarea value={option.description} onChange={(event) => updateOption(turnIndex, optionIndex, { ...option, description: event.target.value })} /></Field>
                      <Field label="Risk effect">
                        <select value={option.risk_effect} onChange={(event) => updateOption(turnIndex, optionIndex, { ...option, risk_effect: event.target.value as DecisionDraft["risk_effect"] })}>
                          <option value="decrease">Decrease</option><option value="neutral">Neutral</option><option value="increase">Increase</option>
                        </select>
                      </Field>
                      <Field label="Expected outcome"><textarea value={option.expected_outcome} onChange={(event) => updateOption(turnIndex, optionIndex, { ...option, expected_outcome: event.target.value })} /></Field>
                    </div>
                  ))}
                </div>
                <button type="button" className="control-button control-secondary" onClick={() => updateTurn(turnIndex, { ...turn, options: [...turn.options, createOption(turnIndex + 1, turn.options.length + 1)] })}>
                  <Plus className="h-4 w-4" /> Add Decision Option
                </button>
              </article>
            ))}
          </div>
          <button type="button" className="control-button control-secondary" onClick={() => setDraft({ ...draft, turns: [...draft.turns, createTurn(draft.turns.length + 1)] })}>
            <Plus className="h-4 w-4" /> Add Turn
          </button>
        </EditorSection>

        <details className="advanced-json" open={advancedOpen} onToggle={(event) => setAdvancedOpen(event.currentTarget.open)}>
          <summary><Braces className="h-4 w-4" /> Advanced JSON <ChevronDown className="h-4 w-4" /></summary>
          <textarea className="workspace-textarea workspace-json-textarea" spellCheck={false} value={rawJson} onChange={(event) => setRawJson(event.target.value)} />
        </details>

        <div className="scenario-editor-actions">
          <button type="button" className="control-button control-secondary" disabled={isWorkspaceSaving} onClick={() => void validate()}>
            <CheckCircle2 className="h-4 w-4" /> Validate Scenario
          </button>
          <button type="button" className="control-button control-primary" disabled={isWorkspaceSaving} onClick={() => void submit()}>
            <Save className="h-4 w-4" /> Save Scenario
          </button>
        </div>
        {message && <p className="workspace-form-message">{message}</p>}
        {validationErrors.length > 0 && <ul className="validation-error-list">{validationErrors.map((error) => <li key={error}>{error}</li>)}</ul>}
      </div>
    </section>
  );

  function updatePersona(index: number, field: keyof PersonaMetadata, value: string) {
    setDraft({
      ...draft,
      personas: draft.personas.map((item, itemIndex) => itemIndex === index ? { ...item, [field]: value } : item),
    });
  }

  function updateTurn(index: number, turn: TurnDraft) {
    setDraft({ ...draft, turns: draft.turns.map((item, itemIndex) => itemIndex === index ? turn : item) });
  }

  function updateOption(turnIndex: number, optionIndex: number, option: DecisionDraft) {
    const turn = draft.turns[turnIndex];
    updateTurn(turnIndex, {
      ...turn,
      options: turn.options.map((item, itemIndex) => itemIndex === optionIndex ? option : item),
    });
  }
}

function EditorSection({ number, title, children }: { number: number; title: string; children: React.ReactNode }) {
  return (
    <section className="guided-editor-section">
      <div className="guided-editor-title"><span>{number}</span><h3>{title}</h3></div>
      <div>{children}</div>
    </section>
  );
}

function Field({ label, wide = false, children }: { label: string; wide?: boolean; children: React.ReactNode }) {
  return <label className={wide ? "technical-field guided-field-wide" : "technical-field"}>{label}{children}</label>;
}

function createPersona(index: number): PersonaMetadata {
  return {
    persona: index === 1 ? "Operations Lead" : `Scenario Stakeholder ${index}`,
    role: index === 1 ? "Decision owner" : "Business impact owner",
    communication_style: "direct and evidence-focused",
    pressure_profile: "medium",
    voice_style: "calm",
    avatar_style: index === 1 ? "holographic-operator" : "holographic-stakeholder",
  };
}

function createOption(turnNumber: number, optionNumber: number): DecisionDraft {
  const controlled = optionNumber === 1;
  return {
    id: `OPT-${turnNumber}${String.fromCharCode(64 + optionNumber)}`,
    label: controlled ? "Establish impact and ownership" : "Act before impact is confirmed",
    description: controlled ? "Create one controlled response path." : "Change scope before evidence is available.",
    action_type: controlled ? "workspace_control" : "workspace_risk",
    competencies: ["SK-operational-judgment"],
    risk_effect: controlled ? "decrease" : "increase",
    expected_outcome: controlled ? "The response gains a clear owner and evidence boundary." : "Operational uncertainty expands.",
  };
}

function createTurn(number: number): TurnDraft {
  return {
    turn_id: `T${number}`,
    situation: "A sanitized operational issue is detected with incomplete impact information.",
    options: [createOption(number, 1), createOption(number, 2)],
    evaluation_focus: ["SK-operational-judgment"],
  };
}

function normalizeDraft(value: Record<string, unknown>): ScenarioDraft {
  const source = value as Partial<ScenarioDraft>;
  return {
    ...STARTER_SCENARIO,
    ...source,
    personas: Array.isArray(source.personas) && source.personas.length
      ? source.personas.map((persona, index) => ({ ...createPersona(index + 1), ...persona }))
      : [createPersona(1)],
    turns: Array.isArray(source.turns) && source.turns.length
      ? source.turns.map((turn, index) => ({
          ...createTurn(index + 1),
          ...turn,
          options: Array.isArray(turn.options) && turn.options.length
            ? turn.options.map((option, optionIndex) => ({ ...createOption(index + 1, optionIndex + 1), ...option }))
            : createTurn(index + 1).options,
        }))
      : [createTurn(1)],
  };
}
