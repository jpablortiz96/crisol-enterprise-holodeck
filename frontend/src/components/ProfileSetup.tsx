"use client";

import { useEffect, useState } from "react";
import { Save, UserRoundCheck } from "lucide-react";
import { useWarRoomStore } from "@/store/warRoomStore";

export function ProfileSetup() {
  const {
    workspaceProfiles,
    workspaceRoles,
    isWorkspaceSaving,
    saveProfile,
  } = useWarRoomStore();
  const [profileId, setProfileId] = useState("PROFILE-OPERATOR-001");
  const [displayName, setDisplayName] = useState("Operations Lead");
  const [roleId, setRoleId] = useState("");
  const [context, setContext] = useState("Makes operational decisions in sanitized training scenarios.");
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!roleId && workspaceRoles[0]) {
      setRoleId(workspaceRoles[0].role_id);
    }
  }, [roleId, workspaceRoles]);

  async function submit() {
    setMessage(null);
    try {
      await saveProfile({
        profile_id: profileId,
        display_name: displayName,
        role_id: roleId,
        context,
      });
      setMessage("Evaluated profile saved.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Profile could not be saved.");
    }
  }

  return (
    <section className="war-panel workspace-editor-panel">
      <div className="panel-header">
        <div>
          <p className="panel-kicker">Evaluation context</p>
          <h2 className="panel-title">Profile Setup</h2>
        </div>
        <UserRoundCheck className="h-5 w-5 text-cyan-300" />
      </div>
      <div className="workspace-editor-body">
        <label className="technical-field">
          Profile ID
          <input value={profileId} onChange={(event) => setProfileId(event.target.value)} />
        </label>
        <label className="technical-field">
          Display name
          <input value={displayName} onChange={(event) => setDisplayName(event.target.value)} />
        </label>
        <label className="technical-field">
          Evaluated role
          <select value={roleId} onChange={(event) => setRoleId(event.target.value)}>
            <option value="">Select a role</option>
            {workspaceRoles.map((role) => (
              <option key={role.role_id} value={role.role_id}>{role.title}</option>
            ))}
          </select>
        </label>
        <label className="technical-field">
          Context
          <textarea
            className="workspace-textarea workspace-textarea-small"
            value={context}
            onChange={(event) => setContext(event.target.value)}
          />
        </label>
        <button
          type="button"
          className="control-button control-primary workspace-save"
          disabled={isWorkspaceSaving || !roleId}
          onClick={() => void submit()}
        >
          <Save className="h-4 w-4" />
          Save Profile
        </button>
        {message && <p className="workspace-form-message">{message}</p>}
        <div className="workspace-record-list">
          {workspaceProfiles.map((profile) => (
            <button
              type="button"
              key={profile.profile_id}
              onClick={() => {
                setProfileId(profile.profile_id);
                setDisplayName(profile.display_name);
                setRoleId(profile.role_id);
                setContext(profile.context);
              }}
            >
              <strong>{profile.display_name}</strong>
              <span>{profile.role_id}</span>
            </button>
          ))}
          {!workspaceProfiles.length && <p>No evaluated profiles yet.</p>}
        </div>
      </div>
    </section>
  );
}
