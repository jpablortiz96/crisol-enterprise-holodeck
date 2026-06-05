import type {
  PlaybackSpeed,
  PlaybackStatus,
  StreamEventEnvelope,
  VoiceSynthesisResult,
} from "@/lib/types";

type PlaybackDirectorHooks = {
  onEvent: (event: StreamEventEnvelope) => void;
  onStatus: (status: PlaybackStatus) => void;
  onSpeaker: (persona: string | null) => void;
  playVoice: (voice: VoiceSynthesisResult, speed: PlaybackSpeed) => Promise<void>;
  shouldPlayVoice: () => boolean;
};

const EVENT_PACING_MS: Record<StreamEventEnvelope["event"], number> = {
  session_started: 450,
  scenario_intro: 1300,
  turn_started: 900,
  decision_selected: 700,
  npc_reaction: 1250,
  consequence_delta: 1100,
  timeline_updated: 850,
  score_final: 1800,
  coach_plan: 1000,
  manager_snapshot: 1000,
  session_completed: 500,
};

export class PlaybackDirector {
  private queue: StreamEventEnvelope[] = [];
  private archive: StreamEventEnvelope[] = [];
  private speed: PlaybackSpeed = 1;
  private status: PlaybackStatus = "idle";
  private inputComplete = false;
  private running = false;
  private stopped = false;
  private generation = 0;
  private resumeResolvers: Array<() => void> = [];

  constructor(private readonly hooks: PlaybackDirectorHooks) {}

  reset(): void {
    this.generation += 1;
    this.stopped = true;
    this.queue = [];
    this.archive = [];
    this.inputComplete = false;
    this.running = false;
    this.releasePauseWaiters();
    this.setStatus("idle");
    this.hooks.onSpeaker(null);
    this.stopped = false;
  }

  enqueue(event: StreamEventEnvelope): void {
    if (this.archive.some((item) => item.session_id === event.session_id && item.sequence === event.sequence)) {
      return;
    }
    this.archive.push(event);
    this.queue.push(event);
    if (event.event === "session_completed") {
      this.inputComplete = true;
    }
    void this.pump();
  }

  replay(): boolean {
    if (!this.archive.length) {
      return false;
    }
    this.generation += 1;
    this.stopped = true;
    this.queue = [...this.archive];
    this.inputComplete = true;
    this.running = false;
    this.releasePauseWaiters();
    this.hooks.onSpeaker(null);
    this.stopped = false;
    this.setStatus("buffering");
    void this.pump();
    return true;
  }

  pause(): void {
    if (this.status === "playing" || this.status === "buffering") {
      this.setStatus("paused");
    }
  }

  resume(): void {
    if (this.status !== "paused") {
      return;
    }
    this.setStatus(this.queue.length ? "playing" : "buffering");
    this.releasePauseWaiters();
    void this.pump();
  }

  setSpeed(speed: PlaybackSpeed): void {
    this.speed = speed;
  }

  getArchive(): StreamEventEnvelope[] {
    return [...this.archive];
  }

  private async pump(): Promise<void> {
    if (this.running || this.stopped) {
      return;
    }

    const generation = this.generation;
    this.running = true;
    try {
      while (!this.stopped && generation === this.generation) {
        await this.waitWhilePaused();
        if (this.stopped || generation !== this.generation) {
          break;
        }

        const event = this.queue.shift();
        if (!event) {
          if (this.inputComplete) {
            this.setStatus("completed");
          } else {
            this.setStatus("buffering");
          }
          break;
        }

        this.setStatus("playing");
        this.hooks.onEvent(event);

        if (event.event === "npc_reaction") {
          await this.playNpcEvent(event, generation);
        } else {
          await this.waitPaced(EVENT_PACING_MS[event.event], generation);
        }

        if (event.event === "session_completed") {
          this.setStatus("completed");
          break;
        }
      }
    } catch {
      if (generation === this.generation) {
        this.setStatus("error");
        this.hooks.onSpeaker(null);
      }
    } finally {
      if (generation !== this.generation) {
        return;
      }
      this.running = false;
      if (
        !this.stopped &&
        generation === this.generation &&
        this.queue.length &&
        this.status !== "paused" &&
        this.status !== "error"
      ) {
        void this.pump();
      }
    }
  }

  private async playNpcEvent(event: StreamEventEnvelope, generation: number): Promise<void> {
    const reaction = event.data.reaction as { persona?: string } | undefined;
    const voice = (event.data.voice ?? event.data.speech) as VoiceSynthesisResult | undefined;
    this.hooks.onSpeaker(reaction?.persona ?? null);

    if (voice?.audio_url && voice.enabled && this.hooks.shouldPlayVoice()) {
      await this.hooks.playVoice(voice, this.speed);
    } else {
      await this.waitPaced(EVENT_PACING_MS.npc_reaction, generation);
    }

    if (generation === this.generation) {
      this.hooks.onSpeaker(null);
    }
  }

  private async waitPaced(durationMs: number, generation: number): Promise<void> {
    let remaining = durationMs / this.speed;
    while (remaining > 0 && !this.stopped && generation === this.generation) {
      await this.waitWhilePaused();
      const slice = Math.min(remaining, 100);
      await new Promise<void>((resolve) => {
        window.setTimeout(resolve, slice);
      });
      remaining -= slice;
    }
  }

  private async waitWhilePaused(): Promise<void> {
    while (this.status === "paused" && !this.stopped) {
      await new Promise<void>((resolve) => {
        this.resumeResolvers.push(resolve);
      });
    }
  }

  private releasePauseWaiters(): void {
    const resolvers = [...this.resumeResolvers];
    this.resumeResolvers = [];
    resolvers.forEach((resolve) => resolve());
  }

  private setStatus(status: PlaybackStatus): void {
    if (this.status === status) {
      return;
    }
    this.status = status;
    this.hooks.onStatus(status);
  }
}
