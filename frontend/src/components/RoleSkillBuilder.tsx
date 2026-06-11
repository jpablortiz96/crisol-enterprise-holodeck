"use client";

import { useState } from "react";
import { Save, UsersRound, Wrench } from "lucide-react";
import { useWarRoomStore } from "@/store/warRoomStore";

export function RoleSkillBuilder() {
  const {
    workspaceRoles,
    workspaceSkills,
    isWorkspaceSaving,
    saveRole,
    saveSkill,
  } = useWarRoomStore();
  const [skillId, setSkillId] = useState("SK-operational-judgment");
  const [skillName, setSkillName] = useState("Operational judgment");
  const [skillDescription, setSkillDescription] = useState("");
  const [roleId, setRoleId] = useState("ROLE-OPERATIONS-LEAD");
  const [roleTitle, setRoleTitle] = useState("Operations Lead");
  const [roleDescription, setRoleDescription] = useState("");
  const [requiredSkills, setRequiredSkills] = useState("SK-operational-judgment");
  const [message, setMessage] = useState<string | null>(null);

  async function submitSkill() {
    setMessage(null);
    try {
      await saveSkill({
        skill_id: skillId,
        name: skillName,
        description: skillDescription,
      });
      setMessage("Skill saved.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Skill could not be saved.");
    }
  }

  async function submitRole() {
    setMessage(null);
    try {
      await saveRole({
        role_id: roleId,
        title: roleTitle,
        description: roleDescription,
        required_skills: requiredSkills
          .split(",")
          .map((value) => value.trim())
          .filter(Boolean),
      });
      setMessage("Role saved.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Role could not be saved.");
    }
  }

  return (
    <section className="war-panel workspace-editor-panel workspace-role-skill-panel">
      <div className="panel-header">
        <div>
          <p className="panel-kicker">Organization model</p>
          <h2 className="panel-title">Role &amp; Skill Builder</h2>
        </div>
        <UsersRound className="h-5 w-5 text-cyan-300" />
      </div>
      <div className="workspace-editor-body">
        <div className="workspace-form-split">
          <div className="workspace-subform">
            <h3><Wrench className="h-4 w-4" /> Add skill</h3>
            <label className="technical-field">
              Skill ID
              <input value={skillId} onChange={(event) => setSkillId(event.target.value)} />
            </label>
            <label className="technical-field">
              Name
              <input value={skillName} onChange={(event) => setSkillName(event.target.value)} />
            </label>
            <label className="technical-field">
              Description
              <input
                value={skillDescription}
                onChange={(event) => setSkillDescription(event.target.value)}
              />
            </label>
            <button
              type="button"
              className="control-button control-secondary workspace-save"
              disabled={isWorkspaceSaving}
              onClick={() => void submitSkill()}
            >
              <Save className="h-4 w-4" />
              Save Skill
            </button>
          </div>
          <div className="workspace-subform">
            <h3><UsersRound className="h-4 w-4" /> Add role</h3>
            <label className="technical-field">
              Role ID
              <input value={roleId} onChange={(event) => setRoleId(event.target.value)} />
            </label>
            <label className="technical-field">
              Title
              <input value={roleTitle} onChange={(event) => setRoleTitle(event.target.value)} />
            </label>
            <label className="technical-field">
              Description
              <input
                value={roleDescription}
                onChange={(event) => setRoleDescription(event.target.value)}
              />
            </label>
            <label className="technical-field">
              Required skill IDs
              <input
                value={requiredSkills}
                onChange={(event) => setRequiredSkills(event.target.value)}
                placeholder="SK-one, SK-two"
              />
            </label>
            <button
              type="button"
              className="control-button control-primary workspace-save"
              disabled={isWorkspaceSaving}
              onClick={() => void submitRole()}
            >
              <Save className="h-4 w-4" />
              Save Role
            </button>
          </div>
        </div>
        {message && <p className="workspace-form-message">{message}</p>}
        <div className="workspace-record-columns">
          <div>
            <span className="workspace-list-label">Roles</span>
            {workspaceRoles.map((role) => (
              <p key={role.role_id}><strong>{role.title}</strong><span>{role.role_id}</span></p>
            ))}
            {!workspaceRoles.length && <p>No roles saved.</p>}
          </div>
          <div>
            <span className="workspace-list-label">Skills</span>
            {workspaceSkills.map((skill) => (
              <p key={skill.skill_id}><strong>{skill.name}</strong><span>{skill.skill_id}</span></p>
            ))}
            {!workspaceSkills.length && <p>No skills saved.</p>}
          </div>
        </div>
      </div>
    </section>
  );
}
