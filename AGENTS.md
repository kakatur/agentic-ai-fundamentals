# Agentic AI Fundamentals

This repository contains the public, learner-facing course material: lesson
documentation, runnable examples, tests, dependencies, and website source.

The sibling `../agentic-ai-fundamentals-bts` repository contains private
production assets such as narration, audio, rendering scripts, captions,
thumbnails, and publishing metadata. Keep that boundary intact.

## Lesson conventions

- Name lesson directories `{module}_{video}_{slug}`.
- Express lesson IDs as `{module}.{video}`.
- Keep public lessons focused on durable learner value.
- Do not add narration, audio, video, captions, thumbnails, production notes,
  generated summaries, or other BTS artifacts here.

Each public lesson should contain:

- `README.md` covering the mental model, design implications, code map,
  production trade-offs, interview questions, and commands to install, run,
  and test.
- Focused, working implementation files.
- `requirements.txt`.
- Passing `test_*.py` tests.
- Optional `QUICK_REFERENCE.md` and `DIAGRAMS.md` only when they add distinct
  value.

## Quality gates

- Run the lesson code and tests before declaring work complete.
- Verify volatile technical claims against current primary sources.
- Demonstrate claimed production behavior rather than presenting pseudocode as
  executable code.
- Keep dependencies and imports minimal and current.

## Cross-repository workflow

Use the repository skill `$create-lesson` when the user asks to work on a
lesson by ID or title. It defines the public-content, narration, and rendering
phases and the required stop point before approved audio exists.

When production work is required, read the current guidance in:

- `../agentic-ai-fundamentals-bts/docs/VIDEO_PRODUCTION_GUIDE.md`
- `../agentic-ai-fundamentals-bts/templates/production/README.md`

## Git hygiene

Do not commit build output, caches, `.DS_Store`, rejected media, or final MP4
files. Preserve unrelated user changes in both repositories.
