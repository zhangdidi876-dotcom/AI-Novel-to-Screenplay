// ── 剧本 YAML Schema 对应的 TypeScript 类型 ──

export type CharacterRole =
  | "protagonist"
  | "antagonist"
  | "supporting"
  | "minor"
  | "extra";

export type ElementType =
  | "action"
  | "dialogue"
  | "parenthetical"
  | "transition"
  | "shot";

export interface Relationship {
  target: string;
  relation: string;
}

export interface ChapterSource {
  number: number;
  title: string;
}

export interface Meta {
  title: string;
  original_novel: string;
  original_author: string;
  adapted_by: string;
  version: string;
  created_at: string;
  description: string;
  source_chapters: ChapterSource[];
  notes: string;
}

export interface Character {
  id: string;
  name: string;
  aliases: string[];
  role: CharacterRole;
  age: string;
  gender: string;
  occupation: string;
  description: string;
  traits: string[];
  relationships: Relationship[];
  arc_summary: string;
  notes: string;
}

export interface SourceReference {
  chapter: number;
  paragraphs: string;  // "1-5" = 第1段到第5段
}

export interface ContentElement {
  element_type: ElementType;
  text: string;
  character_id: string;
  parenthetical: string;
}

export interface Scene {
  id: string;
  scene_number: number;
  slug_line: string;  // 好莱坞标准: "INT./EXT. 地点 - 时间"
  characters_present: string[];
  summary: string;
  content: ContentElement[];
  transition: string;
  source_reference: SourceReference | null;
  notes: string;
}

export interface Screenplay {
  meta: Meta;
  characters: Character[];
  scenes: Scene[];
}

// ── 转换流程中的步骤状态 ──

export type StepStatus = "idle" | "loading" | "done" | "error";

export interface ConversionState {
  chapters: string;
  characters: Character[];
  scenes: Scene[];
  screenplay: Screenplay | null;
  currentStep: "input" | "characters" | "scenes" | "script" | "export";
  stepStatus: Record<string, StepStatus>;
}
