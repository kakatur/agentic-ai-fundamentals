---
name: create-lesson
description: Create or update an Agentic AI Fundamentals course lesson across the public and BTS repositories. Use when the user says "let's work on" a lesson ID or title, asks to create a lesson, requests narration or production assets for a lesson, or provides approved audio and asks to render or publish the corresponding video.
---

# Create an Agentic AI Fundamentals Lesson

Coordinate lesson work across two sibling repositories while preserving their
content boundary:

- Public: `~/github/agentic-ai-fundamentals`
- Production: `~/github/agentic-ai-fundamentals-bts`

Name lesson directories `{module}_{video}_{slug}` and express lesson IDs as
`{module}.{video}`. Resolve the requested lesson ID, title, and slug from the
user's prompt and existing repository content. Ask only when the identity is
genuinely ambiguous.

## Phase 1: Build the public lesson

Work in
`~/github/agentic-ai-fundamentals/{module}_{video}_{slug}/`.

Create or update:

- `README.md` with core concepts, mental model, design implications, code map,
  production considerations, basic/intermediate/advanced interview questions,
  and install/run/test commands.
- Focused, production-relevant implementation files.
- `requirements.txt`.
- Passing `test_*.py` tests.
- `QUICK_REFERENCE.md` or `DIAGRAMS.md` only when they add non-duplicative
  value.

Do not place narration, production notes, captions, audio, video, thumbnails,
or generated summaries in the public repository.

Before continuing:

- Run the lesson code.
- Run the tests.
- Verify volatile claims against current primary sources.
- Confirm the implementation demonstrates the claimed behavior.

## Phase 2: Create production narration

Read the current BTS guidance before editing:

- `~/github/agentic-ai-fundamentals-bts/docs/VIDEO_PRODUCTION_GUIDE.md`
- `~/github/agentic-ai-fundamentals-bts/templates/production/README.md`

Work in
`~/github/agentic-ai-fundamentals-bts/productions/{module}_{video}_{slug}/`.
Create or update:

- `README.md` based on the production template.
- `narration/narration.json` as the canonical scene source.
- `narration/tts-script.txt`, generated from the canonical JSON.
- `publishing/youtube.json` for editable publishing metadata.
- Production-specific scripts only when the standard tooling is insufficient.

For each narration scene, define:

- `title`
- `section`
- `visual`
- `bullets`
- `narration`
- optional `actions` for narration-aligned highlights, pointer movement, or
  temporary ink annotations
- optional `sound_cues` that reference reusable `intro`, `section-transition`,
  or `keyword-soft` assets and identify the related action and placement
- optional `code_file`
- optional `code_lines`

Target 130–150 spoken words per minute and roughly 12–20 minutes for a normal
lesson. Go longer only when the learning objectives require it. Use short,
natural sentences and speak directly to the viewer with a warm, confident
tone. Follow the coffee-shop rule: explain the topic as you would to an
interested friend, using purposeful bridges such as “let’s say,” “now,” and
“here’s the useful part” when they establish context or guide attention. Keep
one idea per scene and use concrete examples before abstraction. Remove empty
filler, hype, unnecessary previews, repeated points, and redundant summaries.

Use the public lesson's terminology. Read short, relevant code fragments when
they orient the viewer, then explain their behavior, purpose, and trade-offs.
Do not read entire visible blocks line by line. Keep only sentences that teach,
connect, clarify, or prepare the next point. End when the learning objectives
are complete.

Use visual actions to direct attention or explain relationships, not as
decoration.

Stop after Phase 2 unless approved `audio/audio.mp3` already exists or the user
explicitly says it is ready. Tell the user that approved audio is the input
required for Phase 3.

## Phase 3: Render and validate the video

Start only after approved `audio/audio.mp3` exists.

1. Generate fresh Whisper word-level alignment from the approved MP3.
2. Render from the current public lesson and canonical narration.
3. Add two seconds of opening silence.
4. Use the standard presenter overlay from
   `~/github/agentic-ai-fundamentals-bts/assets/krishna-face-circle.png` at
   180×180 pixels, 48 pixels from the right and bottom.
5. Fit the main content within a centered safe area covering 90% of the frame
   width and 90% of the height above the footer.
6. Synchronize restrained visual actions with the narration: reveal bullets,
   highlight key phrases or code lines, dim inactive content, and use pointer
   or temporary ink annotations where they clarify the explanation.
7. Add restrained, licensed sound cues when specified: a 1–2 second opening
   cue, 500 ms–1 second section transitions, and 100–300 ms keyword accents.
   Place them in pauses or well below narration; do not add a transition sound
   between every slide.
8. Show `agenticaifundamentals.com` at bottom left,
   `https://github.com/kakatur/agentic-ai-fundamentals` at bottom center, and
   `<lesson title> • Chapter <module.video>` at bottom right.
9. Produce 1920×1080, 30 FPS, H.264 video with AAC audio normalized near
   -16 LUFS.
10. Generate:
   - `deliverables/{slug}-1080p.mp4`
   - `deliverables/{slug}-1080p.en.srt`
   - `deliverables/youtube-chapters.txt`
   - `deliverables/thumbnail-1920x1080.png`
   - `deliverables/youtube-title-description.txt`
11. Run the production validation script when present.
12. Review the final mix with headphones and laptop speakers, then inspect
   representative opening, concept, code, demo, test, and closing
   frames.

Never reuse alignment, caption timing, or chapter timing after audio changes.
Regenerate all downstream artifacts from the new master audio.

## Preserve repository boundaries

- Keep public code, documentation, tests, and dependencies in the public repo.
- Keep narration, audio, render scripts, captions, chapters, thumbnails,
  publishing metadata, and video artifacts in BTS.
- Treat `narration.json` as the sole narration source of truth.
- Do not commit `build/`, caches, `.DS_Store`, rejected media, or final MP4
  files.
- Preserve unrelated changes in both working trees.
