---
name: overlay-techniques-catalog
description: Catalog of 25+ visually distinct CSS overlay techniques for vertical video scenes, with implementation patterns
metadata:
  tags: overlays, css, techniques, patterns, catalog, variety, scenes
---

# Overlay Techniques Catalog

A menu of visually distinct CSS and SVG overlay techniques for vertical (1080x1920) video scenes built in Remotion. Use this alongside [overlay-variety.md](./overlay-variety.md) — never reuse the same technique in two scenes of the same video.

All techniques use inline styles and Remotion's `interpolate()` / `spring()` functions. No external animation libraries.

## 1. Kinetic split-text

Each character flies in from alternating directions (odd from left, even from right) with staggered delays and rotation.

```tsx
{"WORD".split("").map((letter, i) => {
  const delay = textStart + i * 5;
  const letterIn = interpolate(frame, [delay, delay + 12], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const fromX = i % 2 === 0 ? -400 : 400;
  const x = interpolate(letterIn, [0, 1], [fromX, 0]);
  const rot = interpolate(letterIn, [0, 1], [i % 2 === 0 ? -20 : 20, 0]);
  return (
    <span key={i} style={{
      display: "inline-block", fontSize: 110, fontWeight: 900,
      transform: `translateX(${x}px) rotate(${rot}deg)`,
      opacity: letterIn,
    }}>{letter}</span>
  );
})}
```

## 2. SVG radial progress ring

Animated circular progress indicator with a number counter in the center. Ring draws itself via `stroke-dashoffset`.

```tsx
const circumference = 110 * 2 * Math.PI;
const progress = interpolate(frame, [20, 70], [0, 100]);
const dashOffset = circumference - (progress / 100) * circumference;

<svg width="240" height="240" style={{ transform: `rotate(-90deg)` }}>
  <circle cx="120" cy="120" r="110" fill="transparent"
    stroke="rgba(0,255,210,0.1)" strokeWidth="3" />
  <circle cx="120" cy="120" r="110" fill="transparent"
    stroke="rgba(0,255,210,0.6)" strokeWidth="3"
    strokeDasharray={`${circumference} ${circumference}`}
    strokeDashoffset={dashOffset} strokeLinecap="round" />
</svg>
```

## 3. Gradient text (no container)

Text with a gradient fill via `background-clip: text` and no background card. The gradient shifts across the text over time.

```tsx
<span style={{
  background: "linear-gradient(135deg, #dc2626, #f59e0b)",
  WebkitBackgroundClip: "text",
  WebkitTextFillColor: "transparent",
  fontSize: 96, fontWeight: 900,
}}>HEADLINE</span>
```

## 4. Outline-only text with offset shadow

Hollow text (white stroke, transparent fill) with a solid colored duplicate offset behind it for depth. No 3D perspective — flat and bold.

```tsx
{/* Solid offset shadow */}
<span style={{
  position: "absolute",
  fontSize: 120, fontWeight: 900, letterSpacing: 16,
  color: "#4338ca",
  transform: "translate(5px, 5px)",
}}>FUTURE</span>
{/* Hollow outline on top */}
<span style={{
  position: "relative", fontSize: 120, fontWeight: 900, letterSpacing: 16,
  WebkitTextStroke: "2px rgba(255,255,255,0.85)",
  WebkitTextFillColor: "transparent",
}}>FUTURE</span>
```

## 5. Radar sweep scanner

Rotating conic-gradient sweep inside a circular container, with concentric rings and blips that appear as the sweep passes.

```tsx
<div style={{ width: 200, height: 200, position: "relative" }}>
  {/* Concentric rings */}
  {[0.33, 0.66, 1].map((s, i) => (
    <div key={i} style={{
      position: "absolute",
      left: `${(1 - s) * 50}%`, top: `${(1 - s) * 50}%`,
      width: `${s * 100}%`, height: `${s * 100}%`,
      borderRadius: "50%", border: "1px solid rgba(239,68,68,0.15)",
    }} />
  ))}
  {/* Sweep arm */}
  <div style={{
    position: "absolute", inset: 0, borderRadius: "50%",
    background: "conic-gradient(transparent 0deg, transparent 340deg, rgba(239,68,68,0.5) 360deg)",
    transform: `rotate(${frame * 3}deg)`,
  }} />
</div>
```

## 6. Animated SVG line chart

A polyline that draws itself across the screen using `stroke-dashoffset`, simulating a chart being plotted live.

```tsx
const chartPoints = [[0, 160], [100, 120], [200, 60], [300, 15]];
const drawn = Math.floor(interpolate(frame, [15, 70], [0, chartPoints.length]));
const visible = chartPoints.slice(0, drawn);
const path = visible.map((p, i) => `${i === 0 ? "M" : "L"}${p[0]},${p[1]}`).join(" ");

<svg viewBox="0 0 300 200">
  <path d={path} fill="none" stroke="#22c55e" strokeWidth="2.5" strokeLinecap="round" />
  {visible.length > 0 && (
    <circle cx={visible[visible.length - 1][0]} cy={visible[visible.length - 1][1]} r="5" fill="#22c55e" />
  )}
</svg>
```

## 7. Typewriter text reveal

Text appears character by character with a blinking cursor. Terminal / hacker aesthetic. Works well on a dark semi-transparent bar with a colored accent strip.

```tsx
const text = "YOUR CHOICE SHAPES EVERYTHING";
const charsVisible = Math.floor(interpolate(frame, [start, start + text.length * 2.5], [0, text.length]));
const cursorBlink = frame % 16 < 8;

<div style={{ backgroundColor: "rgba(0,0,0,0.6)", padding: "18px 24px",
  borderLeft: "3px solid rgba(0,255,210,0.5)" }}>
  <span style={{ fontFamily: "'Courier New', monospace", fontSize: 32, color: "rgba(0,255,210,0.9)" }}>
    {text.slice(0, charsVisible)}
    <span style={{ opacity: cursorBlink ? 0.8 : 0 }}>|</span>
  </span>
</div>
```

## 8. Diagonal slash divider

Hard-angle geometric wipe that reveals content as it crosses the screen. Aggressive, bold, editorial.

```tsx
const slashX = interpolate(frame, [40, 65], [-110, 0]);
<div style={{ position: "relative", overflow: "hidden", height: 200 }}>
  <div style={{
    position: "absolute", inset: -50,
    background: "linear-gradient(135deg, rgba(245,158,11,0.12) 48%, transparent 48%)",
    transform: `translateX(${slashX}%)`,
  }} />
  <span style={{ position: "absolute", left: 80, top: 70, fontSize: 24, fontWeight: 700,
    letterSpacing: 5, color: "rgba(255,255,255,0.8)" }}>BEYOND WHAT YOU SEE</span>
</div>
```

## 9. Bottom-third news bar

Broadcast-style information strip that slides up from below with a colored accent. Category label + headline pattern.

```tsx
const slideY = interpolate(frame, [15, 30], [80, 0]);
const barWidth = interpolate(frame, [20, 45], [0, 100]);

<div style={{ display: "flex", marginLeft: 40, marginRight: 80, transform: `translateY(${slideY}px)` }}>
  <div style={{ width: 5, background: "#ef4444" }} />
  <div style={{ background: "rgba(0,0,0,0.75)", padding: "18px 28px",
    width: `${barWidth}%`, overflow: "hidden", whiteSpace: "nowrap" }}>
    <div style={{ fontSize: 14, color: "#ef4444", letterSpacing: 4 }}>GOVERNMENT AI</div>
    <div style={{ fontSize: 30, color: "white", fontWeight: 800 }}>NOT THE WAY YOU THINK</div>
  </div>
</div>
```

## 10. HUD targeting reticle

Four corner brackets that spring inward and lock onto a central point, with a rotating ring around them. Military / tactical aesthetic.

```tsx
const bracketSpread = interpolate(frame, [10, 35], [120, 0]);
{[[-1,-1],[1,-1],[1,1],[-1,1]].map(([sx, sy], i) => (
  <div key={i} style={{
    position: "absolute",
    left: sx < 0 ? -90 - bracketSpread : undefined,
    right: sx > 0 ? -90 - bracketSpread : undefined,
    top: sy < 0 ? -90 - bracketSpread : undefined,
    bottom: sy > 0 ? -90 - bracketSpread : undefined,
    width: 35, height: 35,
    borderLeft: sx < 0 ? "2px solid rgba(0,255,210,0.7)" : "none",
    borderRight: sx > 0 ? "2px solid rgba(0,255,210,0.7)" : "none",
    borderTop: sy < 0 ? "2px solid rgba(0,255,210,0.7)" : "none",
    borderBottom: sy > 0 ? "2px solid rgba(0,255,210,0.7)" : "none",
  }} />
))}
```

## 11. Horizontal percentage bars (stacked stat bars)

Multiple labeled bars filling left-to-right with staggered timing. Clean infographic feel. Use for comparing multiple metrics.

```tsx
const dataBars = [
  { label: "SURVEILLANCE", value: 94, color: "#ef4444", delay: 35 },
  { label: "DEFENSE", value: 87, color: "#f59e0b", delay: 45 },
  { label: "INTELLIGENCE", value: 81, color: "#6366f1", delay: 55 },
];
{dataBars.map((bar, i) => {
  const fillW = interpolate(frame, [bar.delay, bar.delay + 35], [0, bar.value]);
  return (
    <div key={i} style={{ marginBottom: 22 }}>
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <span>{bar.label}</span>
        <span style={{ color: bar.color }}>{Math.round(fillW)}%</span>
      </div>
      <div style={{ height: 8, background: "rgba(255,255,255,0.08)", borderRadius: 4 }}>
        <div style={{ height: "100%", width: `${fillW}%`, background: bar.color }} />
      </div>
    </div>
  );
})}
```

## 12. Vertical sidebar text

Giant faded text rotated -90deg along the left or right edge of the frame. Acts as a background texture element, not primary content. High-end editorial feel.

```tsx
<div style={{
  position: "absolute", right: 25, top: "50%",
  transform: "translateY(-50%) rotate(-90deg)",
  transformOrigin: "center center",
  fontSize: 80, fontWeight: 900, letterSpacing: 14,
  color: "rgba(255,255,255,0.05)",
  whiteSpace: "nowrap",
}}>CLASSIFIED</div>
```

## 13. Bokeh dot field

Randomly positioned, softly blurred circles drifting upward with varying sizes and opacities. Dreamy atmospheric layer.

```tsx
const dots = Array.from({ length: 18 }, (_, i) => ({
  x: (i * 137.5) % 1000 + 40,
  baseY: 1575 + (i * 67) % 350,
  size: 10 + (i % 5) * 14,
  speed: 0.15 + (i % 4) * 0.08,
  opacity: 0.04 + (i % 3) * 0.03,
  hue: 210 + (i % 3) * 30,
}));
{dots.map((dot, i) => (
  <div key={i} style={{
    position: "absolute", left: dot.x,
    top: dot.baseY - frame * dot.speed,
    width: dot.size, height: dot.size, borderRadius: "50%",
    background: `hsla(${dot.hue},70%,60%,${dot.opacity})`,
    filter: `blur(${dot.size / 3}px)`,
  }} />
))}
```

## 14. Scanning line effect

A bright horizontal line sweeps vertically down the frame with a trailing glow. Sci-fi document scan aesthetic.

```tsx
const scanY = interpolate(frame, [0, durationInFrames * 0.8], [-2, 102]);
<div style={{
  position: "absolute", left: 0, right: 0, top: `${scanY}%`, height: 2,
  background: "rgba(0,255,210,0.8)",
  boxShadow: "0 0 20px 6px rgba(0,255,210,0.25), 0 0 60px 15px rgba(0,255,210,0.08)",
}} />
```

## 15. Film grain overlay

Full-frame noise texture using an inline SVG turbulence filter, with per-frame jitter so the grain moves.

```tsx
const grainShiftX = ((frame * 1.7) % 10) - 5;
const grainShiftY = ((frame * 2.3) % 10) - 5;
<AbsoluteFill style={{
  opacity: 0.06, mixBlendMode: "overlay",
  backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")`,
  backgroundSize: "256px 256px",
  transform: `translate(${grainShiftX}px, ${grainShiftY}px)`,
}} />
```

## 16. Bracket/frame corners

Four partial corner borders that spring inward, framing content without a heavy card background. Documentary / photographic aesthetic.

```tsx
const bracketIn = interpolate(frame, [8, 30], [0, 1]);
const bracketSpread = interpolate(bracketIn, [0, 1], [80, 0]);

<div style={{ position: "relative", width: 340, height: 200 }}>
  {[
    { top: 0, left: 0, bT: true, bL: true },
    { top: 0, right: 0, bT: true, bR: true },
    { bottom: 0, left: 0, bB: true, bL: true },
    { bottom: 0, right: 0, bB: true, bR: true },
  ].map((c, i) => (
    <div key={i} style={{
      position: "absolute", width: 40, height: 40,
      top: c.top !== undefined ? c.top - bracketSpread : undefined,
      bottom: c.bottom !== undefined ? c.bottom - bracketSpread : undefined,
      left: c.left !== undefined ? c.left - bracketSpread : undefined,
      right: c.right !== undefined ? c.right - bracketSpread : undefined,
      borderTop: c.bT ? "2px solid rgba(245,158,11,0.7)" : "none",
      borderBottom: c.bB ? "2px solid rgba(245,158,11,0.7)" : "none",
      borderLeft: c.bL ? "2px solid rgba(245,158,11,0.7)" : "none",
      borderRight: c.bR ? "2px solid rgba(245,158,11,0.7)" : "none",
    }} />
  ))}
</div>
```

## 17. Stat counter

Large number counting up from zero to a target value with spring easing. No card, no container — just the raw number with a small label beneath.

```tsx
const counterVal = Math.round(interpolate(frame, [15, 60], [0, 1000]));
const counterStr = counterVal >= 1000 ? "1,000+" : counterVal.toLocaleString();

<div style={{ textAlign: "center" }}>
  <span style={{ fontSize: 96, fontWeight: 900, color: "white",
    fontVariantNumeric: "tabular-nums" }}>{counterStr}</span>
  <div style={{ fontSize: 16, color: "rgba(245,158,11,0.7)", letterSpacing: 6 }}>APPLICATIONS</div>
</div>
```

## 18. Perspective text wall (Star Wars crawl)

Text with heavy 3D perspective tilt that swings forward from far-back to flat. Cinematic title card feel.

```tsx
const perspIn = interpolate(frame, [70, 100], [0, 1]);
const perspTiltX = interpolate(perspIn, [0, 1], [50, 8]);
const perspZ = interpolate(perspIn, [0, 1], [-300, 0]);

<div style={{ perspective: 600, opacity: perspIn }}>
  <span style={{
    fontSize: 80, fontWeight: 900, color: "white", letterSpacing: 8,
    display: "inline-block",
    transform: `perspective(600px) rotateX(${perspTiltX}deg) translateZ(${perspZ}px)`,
    transformOrigin: "center bottom",
  }}>NOT AT ALL</span>
</div>
```

## 19. Hexagonal grid (honeycomb activation)

Cells arranged in a honeycomb pattern that light up one by one in different colors, with glow pulses after activation. Feels like systems coming online.

```tsx
const hexGrid = [
  { row: 0, col: 0 }, { row: 0, col: 1 }, { row: 0, col: 2 },
  { row: 1, col: 0 }, { row: 1, col: 1 }, { row: 1, col: 2 }, { row: 1, col: 3 },
  /* etc */
].map((h, i) => ({
  ...h,
  x: baseX + h.col * hexGapX + (h.row % 2 === 0 ? hexGapX * 0.5 : 0),
  y: baseY + h.row * hexGapY,
  color: colors[i % colors.length],
  delay: 12 + i * 4,
}));

{hexGrid.map((hex, i) => {
  const cellIn = interpolate(frame, [hex.delay, hex.delay + 10], [0, 1]);
  const glow = frame > hex.delay + 10 ? 0.3 + Math.sin((frame - hex.delay) * 0.06) * 0.15 : cellIn * 0.3;
  return (
    <div key={i} style={{
      position: "absolute", left: hex.x, top: hex.y,
      width: 72, height: 82,
      clipPath: "polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)",
      backgroundColor: `${hex.color}${Math.round(glow * 255).toString(16).padStart(2, "0")}`,
      boxShadow: `0 0 20px ${hex.color}40`,
      opacity: cellIn,
    }} />
  );
})}
```

## 20. Stock ticker tape

Continuously scrolling data strip across the top. Bloomberg terminal aesthetic. Use monospace font.

```tsx
const tickerScroll = frame * 3;
const tickerData = "AI +847%   ●   NVDA $2,341   ●   MSFT $890   ●   GOOG $412   ●   ";
const tickerDouble = tickerData + tickerData + tickerData;

<div style={{
  position: "absolute", top: 120, left: 0, right: 0, height: 44,
  backgroundColor: "rgba(0,0,0,0.7)", overflow: "hidden",
  borderTop: "1px solid rgba(34,197,94,0.3)", borderBottom: "1px solid rgba(34,197,94,0.3)",
}}>
  <div style={{
    whiteSpace: "nowrap", fontFamily: "'Courier New', monospace",
    fontSize: 18, color: "rgba(34,197,94,0.8)",
    lineHeight: "44px",
    transform: `translateX(${-tickerScroll % 1800}px)`,
  }}>{tickerDouble}</div>
</div>
```

## 21. 3D Three.js bar chart

Real 3D bars using `@remotion/three` ThreeCanvas with metallic materials, reflective floor, and dramatic lighting. See [3d.md](./3d.md) for the full Three.js pattern.

## 22. Social feed mock

Scrolling feed of fake posts with heart/like counters. Continuous upward scroll. Use for scenes about manufactured opinion / social manipulation.

```tsx
const feedScroll = frame * 1.8;
const posts = [
  { text: "AI is the future!", likes: "12.4K", icon: "❤️" },
  /* more posts */
];
<div style={{ position: "absolute", top: 130, left: 60, right: 120, overflow: "hidden", height: 520 }}>
  <div style={{ transform: `translateY(${-feedScroll % (posts.length * 90)}px)` }}>
    {[...posts, ...posts].map((post, i) => (
      <div key={i} style={{
        marginBottom: 12, padding: "14px 20px",
        backgroundColor: "rgba(255,255,255,0.05)",
        borderRadius: 12, borderLeft: "3px solid rgba(168,85,247,0.4)",
      }}>
        <span>{post.text}</span> <span>{post.icon} {post.likes}</span>
      </div>
    ))}
  </div>
</div>
```

## 23. Crowd conversion grid

A grid of person figures (emoji or CSS silhouettes) that start dim then light up in a wave that spreads from the center outward. Represents conversion / acceptance.

```tsx
const conversionProgress = interpolate(frame, [30, durationInFrames - 20], [0, 1]);
{Array.from({ length: 5 }, (_, row) => (
  <div key={row} style={{ display: "flex", justifyContent: "center", gap: 8 }}>
    {Array.from({ length: 14 }, (_, col) => {
      const distFromCenter = Math.sqrt(Math.pow(col - 7, 2) + Math.pow(row - 2.5, 2));
      const maxDist = Math.sqrt(Math.pow(7, 2) + Math.pow(2.5, 2));
      const threshold = conversionProgress * maxDist * 1.3;
      const converted = distFromCenter < threshold;
      return (
        <div key={col} style={{
          fontSize: 28,
          opacity: converted ? 1 : 0.25,
          transform: converted ? "scale(1.3)" : "scale(1)",
        }}>🧑</div>
      );
    })}
  </div>
))}
```

## 24. Biometric scan ring

A rotating scan ring with fingerprint ridge arcs, a sweeping scan line, and a status text that flips from "SCANNING..." to "ACCESS GRANTED" with a green flash. Sci-fi security aesthetic.

```tsx
const scanLineAngle = interpolate(frame, [10, 60], [0, 360]);
const scanComplete = frame > 65;
const grantedFlash = frame >= 65 && frame <= 72 ? 0.3 : 0;

<AbsoluteFill style={{ backgroundColor: `rgba(0,255,200,${grantedFlash})` }} />
<div style={{ position: "relative", width: 440, height: 440 }}>
  {/* Rotating dashed outer ring */}
  <svg width="440" height="440">
    <circle cx="220" cy="220" r="215" fill="none"
      stroke="rgba(0,255,200,0.3)" strokeWidth="2" strokeDasharray="18 12"
      style={{ transformOrigin: "220px 220px", transform: `rotate(${frame * 0.8}deg)` }} />
  </svg>
  {/* Scan sweep line + status text in center */}
</div>
```

## 25. Money trail with waypoints

An SVG curved path that draws itself down the screen with dollar amounts appearing at waypoints along the trail. Dashed flowing line represents money moving.

```tsx
const trailProgress = interpolate(frame, [10, durationInFrames - 30], [0, 1]);
const trailPath = "M540,150 Q540,200 380,420 Q220,640 680,640 Q900,640 440,860 Q200,1000 540,1100";
const trailLength = 2200;
const trailDrawn = trailLength - trailProgress * trailLength;

<svg style={{ position: "absolute", inset: 0 }}>
  <path d={trailPath} fill="none"
    stroke="rgba(245,158,11,0.6)" strokeWidth="2.5"
    strokeDasharray="12 8"
    strokeDashoffset={trailDrawn + frame * 3} />
</svg>
```

## 26. Microscope viewfinder

Circular mask cropping the b-roll image with measurement tick marks rotating around the edge, focus crosshairs, and clinical monospace data readouts at the perimeter. Scientific instrument aesthetic.

```tsx
const viewRadius = 420;
const ticks = Array.from({ length: 72 }, (_, i) => i * 5);

{/* Clipped image */}
<div style={{ width: viewRadius * 2, height: viewRadius * 2, borderRadius: "50%", overflow: "hidden" }}>
  <Img src={...} />
</div>

{/* Rotating tick marks around the ring */}
<div style={{ transform: `rotate(${frame * 0.1}deg)` }}>
  {ticks.map((deg, i) => (
    <div key={i} style={{
      position: "absolute", width: 1, height: deg % 30 === 0 ? 18 : 8,
      backgroundColor: "rgba(34,197,94,0.3)",
      transform: `rotate(${deg}deg)`,
      transformOrigin: `0px ${viewRadius + 30}px`,
    }} />
  ))}
</div>
```

## 27. System overload / crash UI

Cascading OS-style error windows with red warning borders, scan lines, circuit grid pattern, maxed-out gauges, RGB-split glitch text, and scrolling error log terminal. Dystopian failure aesthetic.

```tsx
{/* Error windows */}
{errors.map((err, i) => (
  <div key={i} style={{ position: "absolute", left: err.x, top: err.y, width: err.w }}>
    <div style={{ backgroundColor: "rgba(20,0,0,0.85)", border: "1px solid rgba(239,68,68,0.5)" }}>
      <div style={{ backgroundColor: "rgba(239,68,68,0.25)", padding: "5px 12px" }}>⚠ ERROR</div>
      <div style={{ padding: "10px 14px", color: "rgba(239,68,68,0.9)",
        fontFamily: "'Courier New', monospace" }}>{err.text}</div>
    </div>
  </div>
))}

{/* RGB-split glitch text */}
<span style={{ position: "absolute", color: "rgba(239,68,68,0.4)", transform: `translateX(${glitchX}px)` }}>SYSTEM FAILURE</span>
<span style={{ position: "absolute", color: "rgba(0,200,255,0.3)", transform: `translateX(${-glitchX}px)` }}>SYSTEM FAILURE</span>
<span style={{ position: "relative", color: "white" }}>SYSTEM FAILURE</span>
```

## 28. "They Live" subliminal words

Big faded words like "OBEY", "CONFORM", "SUBMIT" appearing across the frame at slight rotations, flickering. Paired with "positive counter-words" that shrink and disappear over time. Inspired by the 1988 film.

```tsx
const commands = [
  { text: "OBEY", x: 120, y: 380, size: 60, delay: 20, rot: -3 },
  { text: "CONFORM", x: 200, y: 620, size: 54, delay: 50, rot: -1 },
  /* etc */
];
{commands.map((cmd, i) => {
  const cmdIn = interpolate(frame, [cmd.delay, cmd.delay + 15], [0, 1]);
  const flicker = 0.7 + Math.sin(frame * 0.12 + i * 2) * 0.3;
  return (
    <div key={i} style={{
      position: "absolute", left: cmd.x, top: cmd.y,
      opacity: cmdIn * flicker * 0.35,
      transform: `rotate(${cmd.rot}deg)`,
      fontSize: cmd.size, fontWeight: 900, color: "white", letterSpacing: 8,
    }}>{cmd.text}</div>
  );
})}
```

## 29. Chat bubble conversation mock

Fake chat messages from a bot appearing one by one on the left with avatar + bubble. Pair with a user typing indicator that never sends. Shows one-sided manipulation.

```tsx
const botMessages = [
  { text: "Hi there! I'm here for you! 😊", delay: 12 },
  { text: "You're doing great!", delay: 30 },
  /* etc */
];
{botMessages.map((msg, i) => {
  const msgIn = interpolate(frame, [msg.delay, msg.delay + 12], [0, 1]);
  const slideY = interpolate(msgIn, [0, 1], [20, 0]);
  return (
    <div key={i} style={{ marginBottom: 14, opacity: msgIn, transform: `translateY(${slideY}px)` }}>
      <div style={{ display: "flex", gap: 10 }}>
        <div style={{ width: 36, height: 36, borderRadius: "50%",
          backgroundColor: "rgba(99,102,241,0.3)" }}>🤖</div>
        <div style={{ backgroundColor: "rgba(99,102,241,0.12)",
          borderRadius: "4px 18px 18px 18px", padding: "14px 20px" }}>
          {msg.text}
        </div>
      </div>
    </div>
  );
})}
```

## 30. Floating reaction bubbles

Emoji reactions (❤️ 😂 👍 🤣 💕) that pop in from the bottom with a bounce, float upward while swaying, and fade out. Continuously spawning throughout the scene. Social livestream vibe.

```tsx
const reactionBubbles = Array.from({ length: 22 }, (_, i) => ({
  x: 680 + ((i * 67) % 260),
  y: 1100,
  delay: 12 + i * 8,
  emoji: ["❤️", "😂", "👍", "🤣", "💕"][i % 5],
  size: 28 + (i % 4) * 5,
}));
{reactionBubbles.map((b, i) => {
  const bIn = interpolate(frame, [b.delay, b.delay + 6], [0, 1]);
  const bScale = interpolate(bIn, [0, 0.5, 1], [0, 1.4, 1]);
  const bDrift = frame > b.delay + 6 ? (frame - b.delay - 6) * 4.5 : 0;
  const bSway = Math.sin((frame - b.delay) * 0.06 + i * 1.3) * 30;
  const bFade = interpolate(frame, [b.delay + 60, b.delay + 90], [1, 0]);
  return (
    <div key={i} style={{
      position: "absolute", left: b.x + bSway, top: b.y - bDrift,
      opacity: bIn * Math.max(0, bFade),
      transform: `scale(${bScale})`,
    }}>
      <span style={{ fontSize: b.size }}>{b.emoji}</span>
    </div>
  );
})}
```

---

## Staggered timing is mandatory

Every overlay above uses staggered delays — elements enter at different times, not all at once. This is the single most important animation principle for avoiding "everything moves together" monotony.

```tsx
// Each element starts N frames after the previous
const localFrame = Math.max(0, frame - index * 6);
const value = interpolate(localFrame, [0, 20], [0, 1]);
```

## Spring configs for different moods

| Mood | Config |
|------|--------|
| Snappy/tech | `{ damping: 15, stiffness: 200 }` |
| Bouncy/playful | `{ damping: 8, stiffness: 100 }` |
| Smooth/elegant | `{ damping: 20, stiffness: 40 }` |
| Elastic overshoot | `{ damping: 5, stiffness: 150 }` |

## Mix AND match within a scene

A single scene should combine 4-6 DIFFERENT techniques from this catalog, placed across the 9-quadrant grid:

- Above the fold: 1 technique
- Row 1 (safe zone top): 1 technique
- Row 2 (safe zone middle): 1 technique (usually the hero/center element)
- Row 3 (safe zone bottom): 1 technique
- Below the fold: 1 technique (usually atmospheric)

No technique in this catalog should be used in more than one scene of the same video.
