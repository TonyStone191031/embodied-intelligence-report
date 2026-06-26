# Embodied Intelligence Report Working Rules

This repository is a long-term research and writing project for the report
`《具身智能行业和技术发展调研报告》`.

These rules apply to all future Codex sessions working in this repo.

## Primary Workflow

1. Do not start writing or rewriting report正文 directly.
2. First create or revise an outline in `docs/planning/`.
3. Wait for the user's approval of the outline.
4. Only after outline approval may report drafting begin.

## Canonical Process Files

- Primary project workflow spec:
  `docs/planning/项目工作规范.md`
- Preparation and project setup:
  `docs/planning/具身智能报告-V0.0-准备方案.md`
- Writing-grade outline:
  `docs/planning/具身智能报告-V0.0-详细大纲.md`

Always read `docs/planning/项目工作规范.md` before making structural decisions.

## Report Storage Rules

- Report drafts live under `docs/report/`.
- Keep chapter drafts split by chapter rather than maintaining one giant file.
- Each report version gets its own folder under `docs/report/versions/`.
- Never overwrite an older version's released files.

## Assets And Sources

- Store reusable images in `assets/images/`
- Store self-made diagrams in `assets/diagrams/`
- Store screenshots in `assets/screenshots/`
- Store report-specific figures in the matching version folder under
  `docs/report/versions/<version>/figures/`
- Store report-specific code snippets in the matching version folder under
  `docs/report/versions/<version>/snippets/`
- Store paper notes, company notes, dataset notes, and timelines under `research/`

## Skills

Installed Codex skills are user-level, not repo-level.
They live in `C:\Users\zhuof\.codex\skills\`.

Do not create a top-level repo `skills/` folder unless the user explicitly asks
for project-local custom skills.

The currently relevant installed skills and usage guidance are documented in:
`docs/planning/项目工作规范.md`

## Versioning Rule

Use directory-based versioning inside the repo, not one git branch per report
version by default.

- Branches are for feature work or experiments.
- Report versions are managed by files and folders.
- Each version should have its own folder and changelog entry.

## Quality Gates

- Every factual claim should be sourced.
- Use official pages, papers, technical reports, and GitHub repos where possible.
- Distinguish facts, inferences, and judgments.
- Before concluding a major drafting task, check structure, missing citations,
  missing figures, and whether referenced assets are stored in the correct
  directories.

