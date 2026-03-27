export interface MacroStudyHandoff {
  studyId: string | null;
  name: string;
  objective: string;
  conclusionSummary: string;
  actionBias: string | null;
  linkedAssets: string[];
  featureArtifactPath: string | null;
  asOfPolicy: string;
  exportedAt: string;
}

const MACRO_STUDY_HANDOFF_KEY = "macro.studyHandoff";

export function readMacroStudyHandoff(): MacroStudyHandoff | null {
  try {
    const raw = window.localStorage.getItem(MACRO_STUDY_HANDOFF_KEY);
    if (!raw) {
      return null;
    }
    return JSON.parse(raw) as MacroStudyHandoff;
  } catch {
    return null;
  }
}

export function writeMacroStudyHandoff(handoff: MacroStudyHandoff): void {
  try {
    window.localStorage.setItem(MACRO_STUDY_HANDOFF_KEY, JSON.stringify(handoff));
  } catch {
    // Local storage is best-effort only.
  }
}

export function clearMacroStudyHandoff(): void {
  try {
    window.localStorage.removeItem(MACRO_STUDY_HANDOFF_KEY);
  } catch {
    // Local storage is best-effort only.
  }
}
