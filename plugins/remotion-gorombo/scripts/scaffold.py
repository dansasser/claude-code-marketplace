#!/usr/bin/env python3
"""Scaffold a new Remotion composition with all boilerplate files.

Usage: python3 scaffold.py <CompositionName>

Creates the full directory structure, template files, project.json,
and registers the composition in Root.tsx. The composition starts
with one placeholder scene — duplicate it for additional scenes.
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
    with open(path, "w") as f:
        f.write(content)
    print(f"  created {os.path.relpath(path)}")


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

    # --- get-audio-duration.ts ---
    write_file(os.path.join(src_dir, "get-audio-duration.ts"), """import { parseMedia } from "@remotion/media-parser";
import { webReader } from "@remotion/media-parser/web";

export const getAudioDuration = async (src: string) => {
  const result = await parseMedia({
    src,
    fields: { durationInSeconds: true },
    reader: webReader,
  });
  return result.durationInSeconds!;
};
""")

    # --- Scene1.tsx ---
    write_file(os.path.join(src_dir, "Scene1.tsx"), """import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  spring,
  interpolate,
} from "remotion";

export const Scene1: React.FC = () => {
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
            1
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
          Scene 1
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
""")

    # --- Captions.tsx ---
    write_file(os.path.join(src_dir, "Captions.tsx"), '''import { useState, useEffect, useCallback, useMemo } from "react";
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
''')

    # --- generate-voiceover.ts ---
    write_file(os.path.join(src_dir, "generate-voiceover.ts"), f'''import {{ writeFileSync, mkdirSync, existsSync, readFileSync }} from "fs";
import path from "path";
import {{ loadEnv }} from "../load-env";

loadEnv();
const API_KEY = process.env.ELEVENLABS_API_KEY!;
const VOICE_ID = "nPczCjzI2devNBz1zQrb"; // Brian

// Read scenes from project.json — single source of truth
const PROJECT_FILE = path.join(path.dirname(new URL(import.meta.url).pathname), "project.json");
const project = JSON.parse(readFileSync(PROJECT_FILE, "utf-8"));
const SCENES = project.scenes
  .filter((s: {{ voiceover: string }}) => s.voiceover)
  .map((s: {{ id: string; voiceover: string }}) => ({{ id: s.id, text: s.voiceover }}));

const OUTPUT_DIR = path.join("public", "{kebab}", "voiceover");

async function generateScene(scene: {{ id: string; text: string }}) {{
  console.log(`Generating ${{scene.id}}...`);

  const response = await fetch(
    `https://api.elevenlabs.io/v1/text-to-speech/${{VOICE_ID}}`,
    {{
      method: "POST",
      headers: {{
        "xi-api-key": API_KEY,
        "Content-Type": "application/json",
        Accept: "audio/mpeg",
      }},
      body: JSON.stringify({{
        text: scene.text,
        model_id: "eleven_multilingual_v2",
        voice_settings: {{
          stability: 0.5,
          similarity_boost: 0.75,
          style: 0.3,
        }},
      }}),
    }}
  );

  if (!response.ok) {{
    const err = await response.text();
    throw new Error(`ElevenLabs API error for ${{scene.id}}: ${{response.status}} ${{err}}`);
  }}

  const audioBuffer = Buffer.from(await response.arrayBuffer());
  const outPath = path.join(OUTPUT_DIR, `${{scene.id}}.mp3`);
  writeFileSync(outPath, audioBuffer);
  console.log(`  → ${{outPath}} (${{(audioBuffer.length / 1024).toFixed(1)}} KB)`);
}}

async function main() {{
  if (!API_KEY) {{
    console.error("ELEVENLABS_API_KEY not set");
    process.exit(1);
  }}

  if (SCENES.length === 0) {{
    console.error("No scenes with voiceover text found in project.json");
    process.exit(1);
  }}

  if (!existsSync(OUTPUT_DIR)) {{
    mkdirSync(OUTPUT_DIR, {{ recursive: true }});
  }}

  for (const scene of SCENES) {{
    await generateScene(scene);
  }}

  console.log("\\nAll voiceover files generated!");
}}

main().catch((err) => {{
  console.error(err);
  process.exit(1);
}});
''')

    # --- generate-captions.ts ---
    write_file(os.path.join(src_dir, "generate-captions.ts"), f'''import path from "path";
import fs from "fs";
import {{ execFileSync }} from "child_process";
import {{
  downloadWhisperModel,
  installWhisperCpp,
  transcribe,
  toCaptions,
}} from "@remotion/install-whisper-cpp";

const PROJECT_DIR = path.resolve(path.dirname(new URL(import.meta.url).pathname), "../..");
const WHISPER_DIR = path.join(PROJECT_DIR, "whisper.cpp");
const VOICEOVER_DIR = path.join(PROJECT_DIR, "public", "{kebab}", "voiceover");
const CAPTIONS_DIR = path.join(PROJECT_DIR, "public", "{kebab}", "captions");

// Read scene IDs from project.json — single source of truth
const PROJECT_FILE = path.join(path.dirname(new URL(import.meta.url).pathname), "project.json");
const project = JSON.parse(fs.readFileSync(PROJECT_FILE, "utf-8"));
const SCENES: string[] = project.scenes.map((s: {{ id: string }}) => s.id);

async function main() {{
  if (SCENES.length === 0) {{
    console.error("No scenes found in project.json");
    process.exit(1);
  }}

  // Install whisper.cpp if needed
  if (!fs.existsSync(path.join(WHISPER_DIR, "main"))) {{
    console.log("Installing whisper.cpp...");
    await installWhisperCpp({{ to: WHISPER_DIR, version: "1.5.5" }});
  }}

  // Download model if needed
  if (!fs.existsSync(path.join(WHISPER_DIR, "models", "ggml-medium.en.bin"))) {{
    console.log("Downloading medium.en model...");
    await downloadWhisperModel({{ model: "medium.en", folder: WHISPER_DIR }});
  }}

  // Create captions output dir
  if (!fs.existsSync(CAPTIONS_DIR)) {{
    fs.mkdirSync(CAPTIONS_DIR, {{ recursive: true }});
  }}

  for (const scene of SCENES) {{
    const mp3Path = path.join(VOICEOVER_DIR, `${{scene}}.mp3`);
    const wavPath = path.join(VOICEOVER_DIR, `${{scene}}.wav`);
    const captionPath = path.join(CAPTIONS_DIR, `${{scene}}.json`);

    if (!fs.existsSync(mp3Path)) {{
      console.log(`Skipping ${{scene}} — no mp3 found`);
      continue;
    }}

    // Convert to 16KHz wav for whisper
    console.log(`Converting ${{scene}} to wav...`);
    execFileSync("ffmpeg", ["-i", mp3Path, "-ar", "16000", wavPath, "-y"], {{
      stdio: "ignore",
    }});

    // Transcribe
    console.log(`Transcribing ${{scene}}...`);
    const whisperOutput = await transcribe({{
      model: "medium.en",
      whisperPath: WHISPER_DIR,
      whisperCppVersion: "1.5.5",
      inputPath: wavPath,
      tokenLevelTimestamps: true,
    }});

    const {{ captions }} = toCaptions({{ whisperCppOutput: whisperOutput }});

    fs.writeFileSync(captionPath, JSON.stringify(captions, null, 2));
    console.log(`  → ${{captionPath}} (${{captions.length}} captions)`);

    // Clean up wav
    fs.unlinkSync(wavPath);
  }}

  console.log("\\nAll captions generated!");
}}

main().catch((err) => {{
  console.error(err);
  process.exit(1);
}});
''')

    # --- index.tsx ---
    write_file(os.path.join(src_dir, "index.tsx"), f'''import {{ TransitionSeries, linearTiming }} from "@remotion/transitions";
import {{ fade }} from "@remotion/transitions/fade";
import {{ loadFont }} from "@remotion/google-fonts/Inter";
import {{ CalculateMetadataFunction }} from "remotion";
import {{ Scene1 }} from "./Scene1";

loadFont("normal", {{ weights: ["400", "600", "800"], subsets: ["latin"] }});

const FPS = 30;
const TRANSITION_DURATION = 36; // 1.2 seconds
const DEFAULT_SCENE_DURATION = 150; // 5 seconds placeholder

export type {name}Props = {{
  scene1Duration: number;
}};

export const calculate{name}Metadata: CalculateMetadataFunction<
  {name}Props
> = async ({{ props }}) => {{
  // When voiceover exists, this will read audio durations.
  // For now, use placeholder durations.
  return {{
    durationInFrames: props.scene1Duration,
    props,
  }};
}};

export const {name}: React.FC<{name}Props> = ({{
  scene1Duration,
}}) => {{
  return (
    <TransitionSeries>
      <TransitionSeries.Sequence durationInFrames={{scene1Duration}}>
        <Scene1 />
      </TransitionSeries.Sequence>

      {{/* Additional scenes and transitions will be added here */}}
    </TransitionSeries>
  );
}};
''')

    # --- project.json ---
    project = {
        "composition": name,
        "format": "portrait",
        "width": 1080,
        "height": 1920,
        "fps": 30,
        "render": "pending",
        "youtube_publish": "pending",
        "background_music": {
            "enabled": False,
            "mood": ""
        },
        "scenes": [
            {
                "id": "scene-01",
                "headline": "",
                "voiceover": "",
                "visual": "",
                "broll": {
                    "type": "",
                    "prompt": ""
                },
                "status": "pending"
            }
        ]
    }
    write_file(os.path.join(src_dir, "project.json"), json.dumps(project, indent=2) + "\n")

    # --- Register in Root.tsx ---
    root_path = os.path.join(root, "src", "Root.tsx")
    if not os.path.exists(root_path):
        print(f"Warning: src/Root.tsx not found — skipping registration", file=sys.stderr)
    else:
        with open(root_path, "r") as f:
            root_content = f.read()

        # Add import after the last import block
        import_line = f'''import {{
  {name},
  calculate{name}Metadata,
  {name}Props,
}} from "./{name}";'''

        # Find the last import statement and insert after it
        last_import = root_content.rfind("} from \"./")
        if last_import == -1:
            print("Warning: Could not find import block in Root.tsx — skipping registration", file=sys.stderr)
        else:
            end_of_import = root_content.index("\n", root_content.index(";", last_import)) + 1
            root_content = root_content[:end_of_import] + import_line + "\n" + root_content[end_of_import:]

            # Add Composition entry before the closing </>
            comp_entry = f'''      <Composition
        id="{name}"
        component={{{name}}}
        durationInFrames={{150}}
        fps={{30}}
        width={{1080}}
        height={{1920}}
        defaultProps={{
          {{
            scene1Duration: 150,
          }} satisfies {name}Props
        }}
        calculateMetadata={{calculate{name}Metadata}}
      />'''

            root_content = root_content.replace("    </>", comp_entry + "\n    </>")

            with open(root_path, "w") as f:
                f.write(root_content)
            print(f"  registered in src/Root.tsx")

    print(f"\nScaffold complete! Open Remotion Studio to preview.")


def main():
    parser = argparse.ArgumentParser(description="Scaffold a new Remotion composition")
    parser.add_argument("name", help="Composition name in PascalCase (e.g. ManagedAiPromo)")
    args = parser.parse_args()

    if not args.name[0].isupper():
        print("Error: Composition name must be PascalCase (start with uppercase).", file=sys.stderr)
        sys.exit(1)

    scaffold(args.name)


if __name__ == "__main__":
    main()
