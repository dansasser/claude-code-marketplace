#!/usr/bin/env python3
"""Scaffold a new Remotion composition with all boilerplate files.

Usage: python3 scaffold.py <CompositionName>

Creates the full directory structure, template files, project.json,
and registers the composition in Root.tsx. The composition starts
with two placeholder scenes and a fade transition between them.
"""

import argparse
import os
import re
import sys
import json


def find_project_root():
    """Walk up from cwd looking for remotion.config.ts."""
    d = os.getcwd()
    for _ in range(10):
        if os.path.exists(os.path.join(d, "remotion.config.ts")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    print("Error: Could not find remotion.config.ts. Run this from inside a Remotion project.", file=sys.stderr)
    sys.exit(1)


def to_kebab(name):
    """Convert PascalCase to kebab-case for directory names."""
    s = re.sub(r"([A-Z])", r"-\1", name).lstrip("-").lower()
    return s


def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print(f"  created {os.path.relpath(path)}")


# ---------------------------------------------------------------------------
# TSX Templates — use __PLACEHOLDER__ tokens, never Python f-strings,
# to avoid conflicts with JSX curly braces.
# ---------------------------------------------------------------------------

SCENE_TEMPLATE = r"""import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  spring,
  interpolate,
} from "remotion";

export const __COMP__: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleProgress = spring({
    frame,
    fps,
    delay: 0,
    config: { damping: 200 },
  });
  const titleOpacity = interpolate(titleProgress, [0, 0.5], [0.5, 1], {
    extrapolateRight: "clamp",
  });
  const titleScale = interpolate(titleProgress, [0, 1], [0.8, 1]);

  const subtitleProgress = spring({
    frame,
    fps,
    delay: 15,
    config: { damping: 200 },
  });
  const subtitleOpacity = interpolate(subtitleProgress, [0, 0.5], [0, 1], {
    extrapolateRight: "clamp",
  });

  const labelProgress = spring({
    frame,
    fps,
    delay: 30,
    config: { damping: 200 },
  });
  const labelOpacity = interpolate(labelProgress, [0, 0.5], [0, 1], {
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#0a0a0a",
        justifyContent: "center",
        alignItems: "center",
        padding: "210px 60px 320px 120px",
      }}
    >
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 40,
          transform: `scale(${titleScale})`,
          opacity: titleOpacity,
        }}
      >
        <div
          style={{
            width: 120,
            height: 120,
            borderRadius: 24,
            backgroundColor: "rgba(99, 102, 241, 0.15)",
            border: "2px solid rgba(99, 102, 241, 0.4)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <span style={{ fontSize: 56, fontFamily: "Inter", fontWeight: 800, color: "#6366f1" }}>
            __NUM__
          </span>
        </div>

        <h1
          style={{
            color: "white",
            fontSize: 64,
            fontWeight: 800,
            fontFamily: "Inter",
            lineHeight: 1.2,
            margin: 0,
            textAlign: "center",
          }}
        >
          Scene __NUM__
        </h1>
      </div>

      <p
        style={{
          color: "#d1d5db",
          fontSize: 36,
          fontWeight: 400,
          fontFamily: "Inter",
          lineHeight: 1.5,
          margin: 0,
          textAlign: "center",
          opacity: subtitleOpacity,
          marginTop: 30,
        }}
      >
        Replace this with your scene content
      </p>

      <div
        style={{
          position: "absolute",
          bottom: 360,
          left: 0,
          right: 0,
          textAlign: "center",
          opacity: labelOpacity,
        }}
      >
        <span
          style={{
            color: "#6366f1",
            fontSize: 28,
            fontWeight: 600,
            fontFamily: "Inter",
            backgroundColor: "rgba(99, 102, 241, 0.1)",
            padding: "8px 24px",
            borderRadius: 8,
          }}
        >
          PLACEHOLDER
        </span>
      </div>
    </AbsoluteFill>
  );
};
"""

CAPTIONS_TEMPLATE = r"""import { useState, useEffect, useCallback, useMemo } from "react";
import {
  AbsoluteFill,
  Sequence,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
  delayRender,
  continueRender,
  cancelRender,
} from "remotion";
import {
  createTikTokStyleCaptions,
  type Caption,
  type TikTokPage,
} from "@remotion/captions";

const HIGHLIGHT_COLOR = "#22c55e";
const TEXT_COLOR = "white";
const FONT_SIZE = 64;
const SWITCH_CAPTIONS_EVERY_MS = 1800;

const CaptionPage: React.FC<{ page: TikTokPage }> = ({ page }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const currentTimeMs = (frame / fps) * 1000;
  const absoluteTimeMs = page.startMs + currentTimeMs;

  return (
    <AbsoluteFill
      style={{
        justifyContent: "flex-end",
        alignItems: "center",
        paddingBottom: 200,
      }}
    >
      <div
        style={{
          fontSize: FONT_SIZE,
          fontWeight: 800,
          fontFamily: "Inter",
          whiteSpace: "pre-wrap",
          wordBreak: "break-word",
          textAlign: "center",
          maxWidth: 950,
          textShadow: "0 2px 8px rgba(0,0,0,0.8)",
          lineHeight: 1.3,
          padding: "0 40px",
        }}
      >
        {page.tokens.map((token, i) => {
          const isActive =
            token.fromMs <= absoluteTimeMs && token.toMs > absoluteTimeMs;

          return (
            <span
              key={`${token.fromMs}-${i}`}
              style={{ color: isActive ? HIGHLIGHT_COLOR : TEXT_COLOR }}
            >
              {token.text}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

export const Captions: React.FC<{ captionFile: string }> = ({
  captionFile,
}) => {
  const [captions, setCaptions] = useState<Caption[] | null>(null);
  const [handle] = useState(() => delayRender());
  const { fps } = useVideoConfig();

  const fetchCaptions = useCallback(async () => {
    try {
      const response = await fetch(staticFile(captionFile));
      const data = await response.json();
      setCaptions(data);
      continueRender(handle);
    } catch (e) {
      cancelRender(e);
    }
  }, [captionFile, handle]);

  useEffect(() => {
    fetchCaptions();
  }, [fetchCaptions]);

  const pages = useMemo(() => {
    if (!captions) return [];
    const { pages } = createTikTokStyleCaptions({
      captions,
      combineTokensWithinMilliseconds: SWITCH_CAPTIONS_EVERY_MS,
    });
    return pages;
  }, [captions]);

  if (!captions) return null;

  return (
    <AbsoluteFill>
      {pages.map((page, index) => {
        const nextPage = pages[index + 1] ?? null;
        const startFrame = Math.round((page.startMs / 1000) * fps);
        const isLast = index === pages.length - 1;
        const endFrame = isLast
          ? Infinity
          : Math.min(
              nextPage ? Math.round((nextPage.startMs / 1000) * fps) : Infinity,
              startFrame + Math.round((SWITCH_CAPTIONS_EVERY_MS / 1000) * fps)
            );
        const durationInFrames = endFrame - startFrame;

        if (durationInFrames <= 0) return null;

        return (
          <Sequence
            key={index}
            from={startFrame}
            durationInFrames={durationInFrames}
          >
            <CaptionPage page={page} />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
"""

GET_AUDIO_DURATION_TEMPLATE = r"""import { parseMedia } from "@remotion/media-parser";
import { webReader } from "@remotion/media-parser/web";

export const getAudioDuration = async (src: string) => {
  const result = await parseMedia({
    src,
    fields: { durationInSeconds: true },
    reader: webReader,
  });
  return result.durationInSeconds!;
};
"""

# Templates that need __KEBAB__ substitution use plain strings with replace()

GENERATE_VOICEOVER_TEMPLATE = r"""import { writeFileSync, mkdirSync, existsSync, readFileSync } from "fs";
import path from "path";
import { loadEnv } from "../load-env";

loadEnv();
const API_KEY = process.env.ELEVENLABS_API_KEY!;

// Read config from project.json — single source of truth
const PROJECT_FILE = path.join(path.dirname(new URL(import.meta.url).pathname), "project.json");
const project = JSON.parse(readFileSync(PROJECT_FILE, "utf-8"));
const VOICE_ID = project.voice?.voice_id || process.env.ELEVENLABS_VOICE_ID || "";
const SCENES = project.scenes
  .filter((s: { voiceover: string }) => s.voiceover)
  .map((s: { id: string; voiceover: string }) => ({ id: s.id, text: s.voiceover }));

const OUTPUT_DIR = path.join("public", "__KEBAB__", "voiceover");

async function generateScene(scene: { id: string; text: string }) {
  console.log(`Generating ${scene.id}...`);

  const response = await fetch(
    `https://api.elevenlabs.io/v1/text-to-speech/${VOICE_ID}`,
    {
      method: "POST",
      headers: {
        "xi-api-key": API_KEY,
        "Content-Type": "application/json",
        Accept: "audio/mpeg",
      },
      body: JSON.stringify({
        text: scene.text,
        model_id: "eleven_multilingual_v2",
        voice_settings: {
          stability: 0.5,
          similarity_boost: 0.75,
          style: 0.3,
        },
      }),
    }
  );

  if (!response.ok) {
    const err = await response.text();
    throw new Error(`ElevenLabs API error for ${scene.id}: ${response.status} ${err}`);
  }

  const audioBuffer = Buffer.from(await response.arrayBuffer());
  const outPath = path.join(OUTPUT_DIR, `${scene.id}.mp3`);
  writeFileSync(outPath, audioBuffer);
  console.log(`  → ${outPath} (${(audioBuffer.length / 1024).toFixed(1)} KB)`);
}

async function main() {
  if (!API_KEY) {
    console.error("ELEVENLABS_API_KEY not set");
    process.exit(1);
  }

  if (!VOICE_ID) {
    console.error("No voice ID configured. Set voice.voice_id in project.json or ELEVENLABS_VOICE_ID in .env");
    process.exit(1);
  }

  if (SCENES.length === 0) {
    console.error("No scenes with voiceover text found in project.json");
    process.exit(1);
  }

  if (!existsSync(OUTPUT_DIR)) {
    mkdirSync(OUTPUT_DIR, { recursive: true });
  }

  for (const scene of SCENES) {
    await generateScene(scene);
  }

  console.log("\nAll voiceover files generated!");
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
"""

GENERATE_CAPTIONS_TEMPLATE = r"""import path from "path";
import fs from "fs";
import { execFileSync } from "child_process";
import {
  downloadWhisperModel,
  installWhisperCpp,
  transcribe,
  toCaptions,
} from "@remotion/install-whisper-cpp";

const PROJECT_DIR = path.resolve(path.dirname(new URL(import.meta.url).pathname), "../..");
const WHISPER_DIR = path.join(PROJECT_DIR, "whisper.cpp");
const VOICEOVER_DIR = path.join(PROJECT_DIR, "public", "__KEBAB__", "voiceover");
const CAPTIONS_DIR = path.join(PROJECT_DIR, "public", "__KEBAB__", "captions");

// Read scene IDs from project.json — single source of truth
const PROJECT_FILE = path.join(path.dirname(new URL(import.meta.url).pathname), "project.json");
const project = JSON.parse(fs.readFileSync(PROJECT_FILE, "utf-8"));
const SCENES: string[] = project.scenes.map((s: { id: string }) => s.id);

async function main() {
  if (SCENES.length === 0) {
    console.error("No scenes found in project.json");
    process.exit(1);
  }

  // Install whisper.cpp if needed
  if (!fs.existsSync(path.join(WHISPER_DIR, "main"))) {
    console.log("Installing whisper.cpp...");
    await installWhisperCpp({ to: WHISPER_DIR, version: "1.5.5" });
  }

  // Download model if needed
  if (!fs.existsSync(path.join(WHISPER_DIR, "models", "ggml-medium.en.bin"))) {
    console.log("Downloading medium.en model...");
    await downloadWhisperModel({ model: "medium.en", folder: WHISPER_DIR });
  }

  // Create captions output dir
  if (!fs.existsSync(CAPTIONS_DIR)) {
    fs.mkdirSync(CAPTIONS_DIR, { recursive: true });
  }

  for (const scene of SCENES) {
    const mp3Path = path.join(VOICEOVER_DIR, `${scene}.mp3`);
    const wavPath = path.join(VOICEOVER_DIR, `${scene}.wav`);
    const captionPath = path.join(CAPTIONS_DIR, `${scene}.json`);

    if (!fs.existsSync(mp3Path)) {
      console.log(`Skipping ${scene} — no mp3 found`);
      continue;
    }

    // Convert to 16KHz wav for whisper
    console.log(`Converting ${scene} to wav...`);
    execFileSync("ffmpeg", ["-i", mp3Path, "-ar", "16000", wavPath, "-y"], {
      stdio: "ignore",
    });

    // Transcribe
    console.log(`Transcribing ${scene}...`);
    const whisperOutput = await transcribe({
      model: "medium.en",
      whisperPath: WHISPER_DIR,
      whisperCppVersion: "1.5.5",
      inputPath: wavPath,
      tokenLevelTimestamps: true,
    });

    const { captions } = toCaptions({ whisperCppOutput: whisperOutput });

    fs.writeFileSync(captionPath, JSON.stringify(captions, null, 2));
    console.log(`  → ${captionPath} (${captions.length} captions)`);

    // Clean up wav
    fs.unlinkSync(wavPath);
  }

  console.log("\nAll captions generated!");
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
"""

GENERATE_BACKGROUND_MUSIC_TEMPLATE = r"""import { writeFileSync, mkdirSync, existsSync, readFileSync, readdirSync } from "fs";
import path from "path";
import { loadEnv } from "../load-env";
import { parseMedia } from "@remotion/media-parser";
import { nodeReader } from "@remotion/media-parser/node";

loadEnv();
const API_KEY = process.env.ELEVENLABS_API_KEY!;

// Read background music config from project.json
const PROJECT_FILE = path.join(path.dirname(new URL(import.meta.url).pathname), "project.json");
const project = JSON.parse(readFileSync(PROJECT_FILE, "utf-8"));

const PROJECT_DIR = path.resolve(path.dirname(new URL(import.meta.url).pathname), "../..");
const VOICEOVER_DIR = path.join(PROJECT_DIR, "public", "__KEBAB__", "voiceover");
const OUTPUT_PATH = path.join(PROJECT_DIR, "public", "__KEBAB__", "background-music.mp3");

const MOOD_PROMPTS: Record<string, string> = {
  upbeat: "upbeat corporate background music, energetic but not overpowering, modern and clean",
  corporate: "soft corporate background music, professional and clean, subtle piano and light percussion",
  cinematic: "cinematic background music, dramatic and emotional, orchestral strings and atmosphere",
  ambient: "soft ambient background music, gentle and atmospheric, minimal and calming",
};

async function getFileDuration(filePath: string): Promise<number> {
  const result = await parseMedia({
    src: filePath,
    fields: { durationInSeconds: true },
    reader: nodeReader,
  });
  return result.durationInSeconds!;
}

async function getTotalDuration(): Promise<number> {
  const files = readdirSync(VOICEOVER_DIR).filter((f) => f.endsWith(".mp3"));
  if (files.length === 0) {
    throw new Error("No voiceover files found. Generate voiceover first.");
  }
  let total = 0;
  for (const file of files) {
    const duration = await getFileDuration(path.join(VOICEOVER_DIR, file));
    total += duration;
  }
  return total;
}

async function main() {
  if (!API_KEY) {
    console.error("ELEVENLABS_API_KEY not set");
    process.exit(1);
  }

  if (!project.background_music?.enabled) {
    console.log("Background music disabled in project.json — skipping.");
    process.exit(0);
  }

  const mood = project.background_music.mood || "ambient";
  const prompt = MOOD_PROMPTS[mood] || mood;

  console.log(`Generating background music (mood: ${mood})...`);

  const totalDuration = await getTotalDuration();
  const durationMs = Math.ceil(totalDuration * 1000);

  console.log(`  Total voiceover duration: ${totalDuration.toFixed(1)}s → music: ${durationMs}ms`);

  const response = await fetch("https://api.elevenlabs.io/v1/music?output_format=mp3_44100_128", {
    method: "POST",
    headers: {
      "xi-api-key": API_KEY,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      prompt,
      music_length_ms: durationMs,
      force_instrumental: true,
    }),
  });

  if (!response.ok) {
    const err = await response.text();
    throw new Error(`ElevenLabs Music API error: ${response.status} ${err}`);
  }

  const audioBuffer = Buffer.from(await response.arrayBuffer());

  const outputDir = path.dirname(OUTPUT_PATH);
  if (!existsSync(outputDir)) {
    mkdirSync(outputDir, { recursive: true });
  }

  writeFileSync(OUTPUT_PATH, audioBuffer);
  console.log(`  → ${OUTPUT_PATH} (${(audioBuffer.length / 1024).toFixed(1)} KB)`);
  console.log("\nBackground music generated!");
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
"""

INDEX_TEMPLATE = r"""import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { Audio } from "@remotion/media";
import { loadFont } from "@remotion/google-fonts/Inter";
import { AbsoluteFill, CalculateMetadataFunction, staticFile } from "remotion";
import { Scene1 } from "./Scene1";
import { Scene2 } from "./Scene2";

loadFont("normal", { weights: ["400", "600", "800"], subsets: ["latin"] });

const FPS = 30;
const TRANSITION_DURATION = 36; // 1.2 seconds
const PADDING_FRAMES = 45; // silence after voiceover — MUST be >= TRANSITION_DURATION
const DEFAULT_SCENE_DURATION = 150; // 5 seconds placeholder
const BACKGROUND_MUSIC_FILE = "__KEBAB__/background-music.mp3";
const BACKGROUND_MUSIC_VOLUME = 0.15;

export type __NAME__Props = {
  scene1Duration: number;
  scene2Duration: number;
  hasBackgroundMusic: boolean;
};

export const calculate__NAME__Metadata: CalculateMetadataFunction<
  __NAME__Props
> = async ({ props }) => {
  // When voiceover exists, replace placeholder durations with actual audio durations.
  // See rules/voiceover.md for the getAudioDuration + calculateMetadata pattern.
  const totalFrames = props.scene1Duration + props.scene2Duration - TRANSITION_DURATION;
  return {
    durationInFrames: totalFrames,
    props,
  };
};

export const __NAME__: React.FC<__NAME__Props> = ({
  scene1Duration,
  scene2Duration,
  hasBackgroundMusic,
}) => {
  return (
    <AbsoluteFill>
      <TransitionSeries>
        <TransitionSeries.Sequence durationInFrames={scene1Duration}>
          <Scene1 />
        </TransitionSeries.Sequence>

        <TransitionSeries.Transition
          presentation={fade()}
          timing={linearTiming({ durationInFrames: TRANSITION_DURATION })}
        />

        <TransitionSeries.Sequence durationInFrames={scene2Duration}>
          <Scene2 />
        </TransitionSeries.Sequence>

        {/* Additional scenes and transitions follow this same pattern */}
      </TransitionSeries>

      {hasBackgroundMusic && (
        <Audio
          src={staticFile(BACKGROUND_MUSIC_FILE)}
          volume={BACKGROUND_MUSIC_VOLUME}
        />
      )}
    </AbsoluteFill>
  );
};
"""


# ---------------------------------------------------------------------------
# Scaffold function
# ---------------------------------------------------------------------------

def scaffold(name):
    root = find_project_root()
    kebab = to_kebab(name)
    src_dir = os.path.join(root, "src", name)
    pub_dir = os.path.join(root, "public", kebab)

    if os.path.exists(src_dir):
        print(f"Error: src/{name}/ already exists.", file=sys.stderr)
        sys.exit(1)

    print(f"Scaffolding composition: {name}")
    print(f"  src:    src/{name}/")
    print(f"  public: public/{kebab}/")
    print()

    # --- Public directories ---
    for sub in ["voiceover", "broll", "captions"]:
        os.makedirs(os.path.join(pub_dir, sub), exist_ok=True)
        print(f"  created public/{kebab}/{sub}/")

    # --- Static files (no substitution needed) ---
    write_file(os.path.join(src_dir, "get-audio-duration.ts"), GET_AUDIO_DURATION_TEMPLATE)
    write_file(os.path.join(src_dir, "Captions.tsx"), CAPTIONS_TEMPLATE)

    # --- Scene files ---
    write_file(os.path.join(src_dir, "Scene1.tsx"),
               SCENE_TEMPLATE.replace("__COMP__", "Scene1").replace("__NUM__", "1"))
    write_file(os.path.join(src_dir, "Scene2.tsx"),
               SCENE_TEMPLATE.replace("__COMP__", "Scene2").replace("__NUM__", "2"))

    # --- Files needing __KEBAB__ substitution ---
    write_file(os.path.join(src_dir, "generate-voiceover.ts"),
               GENERATE_VOICEOVER_TEMPLATE.replace("__KEBAB__", kebab))
    write_file(os.path.join(src_dir, "generate-captions.ts"),
               GENERATE_CAPTIONS_TEMPLATE.replace("__KEBAB__", kebab))
    write_file(os.path.join(src_dir, "generate-background-music.ts"),
               GENERATE_BACKGROUND_MUSIC_TEMPLATE.replace("__KEBAB__", kebab))

    # --- Files needing __NAME__ and __KEBAB__ substitution ---
    write_file(os.path.join(src_dir, "index.tsx"),
               INDEX_TEMPLATE.replace("__NAME__", name).replace("__KEBAB__", kebab))

    # --- project.json ---
    project = {
        "composition": name,
        "format": "portrait",
        "width": 1080,
        "height": 1920,
        "fps": 30,
        "render": "pending",
        "branding": {
            "company": "",
            "website": "",
            "socials": []
        },
        "voice": {
            "voice_id": ""
        },
        "background_music": {
            "enabled": False,
            "mood": ""
        },
        "youtube": {
            "publish": "pending",
            "links": [],
            "tags": [],
            "category": "",
            "description_notes": ""
        },
        "scenes": [
            {
                "id": "scene-01",
                "headline": "",
                "voiceover": "",
                "visual": "",
                "broll": {"type": "", "prompt": ""},
                "status": "pending"
            },
            {
                "id": "scene-02",
                "headline": "",
                "voiceover": "",
                "visual": "",
                "broll": {"type": "", "prompt": ""},
                "status": "pending"
            }
        ]
    }
    write_file(os.path.join(src_dir, "project.json"), json.dumps(project, indent=2) + "\n")

    # --- Register in Root.tsx ---
    root_path = os.path.join(root, "src", "Root.tsx")
    if not os.path.exists(root_path):
        print("Warning: src/Root.tsx not found — skipping registration", file=sys.stderr)
    else:
        with open(root_path, "r", encoding="utf-8") as f:
            root_content = f.read()

        import_line = (
            f'import {{\n'
            f'  {name},\n'
            f'  calculate{name}Metadata,\n'
            f'  {name}Props,\n'
            f'}} from "./{name}";'
        )

        last_import = root_content.rfind('} from "./')
        if last_import == -1:
            print("Warning: Could not find import block in Root.tsx — skipping registration", file=sys.stderr)
        else:
            end_of_import = root_content.index("\n", root_content.index(";", last_import)) + 1
            root_content = root_content[:end_of_import] + import_line + "\n" + root_content[end_of_import:]

            comp_entry = (
                f'      <Composition\n'
                f'        id="{name}"\n'
                f'        component={{{name}}}\n'
                f'        durationInFrames={{264}}\n'
                f'        fps={{30}}\n'
                f'        width={{1080}}\n'
                f'        height={{1920}}\n'
                f'        defaultProps={{{{\n'
                f'          scene1Duration: 150,\n'
                f'          scene2Duration: 150,\n'
                f'          hasBackgroundMusic: false,\n'
                f'        }} satisfies {name}Props}}\n'
                f'        calculateMetadata={{calculate{name}Metadata}}\n'
                f'      />'
            )

            if "    </>" not in root_content:
                print("Warning: Could not find </> closing tag in Root.tsx — skipping registration", file=sys.stderr)
            else:
                root_content = root_content.replace("    </>", comp_entry + "\n    </>")
                with open(root_path, "w", encoding="utf-8", newline="\n") as f:
                    f.write(root_content)
                print(f"  registered in src/Root.tsx")

    print(f"\nScaffold complete! Start Remotion Studio to preview.")


def main():
    parser = argparse.ArgumentParser(description="Scaffold a new Remotion composition")
    parser.add_argument("name", help="Composition name in PascalCase (e.g. ManagedAiPromo)")
    args = parser.parse_args()

    if not re.match(r'^[A-Z][a-zA-Z0-9]+$', args.name):
        print("Error: Composition name must be PascalCase (e.g. MyVideo). Letters and numbers only, start with uppercase.", file=sys.stderr)
        sys.exit(1)

    scaffold(args.name)


if __name__ == "__main__":
    main()
