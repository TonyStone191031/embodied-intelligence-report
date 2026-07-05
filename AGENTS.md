# Repo Rules

## Read First

1. `docs/planning/项目工作规范.md`
2. `docs/planning/README.md`
3. `docs/planning/current/具身智能报告-当前详细大纲.md`
4. `docs/planning/current/当前版本修订计划.md`
5. `docs/planning/current/当前工作清单.md`

## Workflow

1. Before any report正文 drafting or revision, read every file listed in `Read First`.
2. In the first progress update of a new正文 batch, explicitly state that the pre-read has been completed.
3. Do not write or rewrite report正文 before outline work.
4. For structural changes or new正文 drafting, first create or update the active outline in `docs/planning/current/`.
5. Wait for explicit user approval of the outline before structural drafting.
6. For non-structural maintenance such as wording cleanup, citation normalization, metadata fixes, or export polish, first update `docs/planning/current/当前版本修订计划.md`.
7. For any new正文 batch, also update `docs/planning/current/当前工作清单.md` with task scope, target chapters, and status before drafting.
8. Only then draft or revise report正文.

## Report Files

1. Active work goes in `docs/report/current/`.
2. Frozen versions go in `docs/report/versions/<version>/`.
3. Do not overwrite frozen version files by default.
4. Keep chapter drafts split by chapter.
5. Editable source of truth remains Markdown, not Word or PDF.
6. Exported `.docx` / `.pdf` files are release artifacts, not authoring files.

## Assets

1. Reusable images: `assets/images/`
2. Reusable diagrams: `assets/diagrams/`
3. Screenshots: `assets/screenshots/`
4. Version-specific figures: `docs/report/versions/<version>/figures/`
5. Version-specific snippets: `docs/report/versions/<version>/snippets/`
6. Research notes and source material: `research/`

## Skills

1. Installed Codex skills are user-level.
2. They live in `C:\Users\zhuof\.codex\skills\`.
3. Do not create a repo-level `skills/` folder unless explicitly requested.
4. See `docs/planning/项目工作规范.md` for current skill guidance.

## Versioning

1. Use directory-based report versioning by default.
2. Do not use one git branch per report version by default.
3. Use branches only for isolated feature work or experiments.
4. When a report version is frozen, export artifacts should be generated after freezing `docs/report/versions/<version>/`.
5. Export artifacts should go to `output/exports/<version>/` by default.
6. Do not manually edit exported `.docx` / `.pdf`; regenerate them from Markdown and scripts.

## Export Workflow

1. Keep day-to-day writing in split Markdown chapters under `docs/report/current/`.
2. When a version is ready, freeze the chapter set into `docs/report/versions/<version>/`.
3. Only after freezing, run the repo export scripts to generate:
   - merged Markdown
   - Word (`.docx`)
   - PDF (`.pdf`)
4. Treat export scripts and templates as reusable project infrastructure under `code/`.
5. Treat generated files under `output/exports/` as disposable/reproducible outputs.
6. Treat Word (`.docx`) as the primary readable release artifact by default.
7. Treat PDF as a secondary derivative artifact for distribution/printing; if Word and PDF quality diverge, fix Markdown/assets/export scripts and stabilize Word first.
8. Prefer generating PDF from the exported Word artifact when Microsoft Word automation is available; use direct script rendering only as a fallback.
9. Keep the report export entrypoints consolidated under `code/export/`; future `vX.X` versions should reuse the same scripts via `run_export.py --version vX.X --source current|frozen` instead of creating version-specific exporter copies.

## Quality Gates

1. Source factual claims where possible.
2. Prefer papers, official pages, technical reports, and GitHub repos.
3. Distinguish facts, inferences, and judgments.
4. Before completing major drafting work, check:
   - structure
   - citations
   - asset paths
   - accidental overwrite of old versions
