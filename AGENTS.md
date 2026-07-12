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

1. v0.1 and earlier Markdown transition work goes in `docs/report/current/`; v0.2+ active正文 work goes in `docs/report/latex/current/`.
2. Frozen versions go in `docs/report/versions/<version>/`, with LaTeX source under `latex/` for v0.2+.
3. Do not overwrite frozen version files by default.
4. Keep chapter drafts split by chapter.
5. v0.1 editable source of truth remains Markdown; v0.2+ editable正文 source of truth is LaTeX, not Word or PDF.
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

1. Keep v0.1 transition writing in split Markdown chapters under `docs/report/current/`; from v0.2 onward edit split LaTeX chapters under `docs/report/latex/current/`.
2. When a version is ready, freeze the chapter set into `docs/report/versions/<version>/`.
3. Only after freezing, run the repo export scripts to generate:
   - merged Markdown for legacy v0.1 exports, or LaTeX build outputs for v0.2+
   - Word (`.docx`) as an optional compatibility artifact for v0.2+
   - PDF (`.pdf`) as the primary v0.2+ release artifact
4. Treat export scripts and templates as reusable project infrastructure under `code/`.
5. Treat generated files under `output/exports/` as disposable/reproducible outputs.
6. Treat Word (`.docx`) as the primary readable release artifact only for the legacy Markdown-based v0.1 workflow.
7. Treat PDF as the primary release artifact for v0.2+ LaTeX versions; Word is optional and complex-formula parity is not guaranteed.
8. For v0.1 use the legacy exporter; for v0.2+ use `run_export.py`/`export_latex.py` and do not route the primary PDF through Word.
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

## LaTeX Report Source (v0.2+)

1. `v0.1` remains a frozen Markdown-based release and is not migrated in place.
2. Starting with `v0.2`, the report's single editable正文 source is `docs/report/latex/current/`.
3. Do not hand-edit both Markdown and LaTeX versions of the same正文. Markdown under `docs/report/current/` is a legacy/transition source unless the active version plan says otherwise.
4. LaTeX chapter sources remain split by chapter and are assembled by `main.tex`; planning, research notes, paper cards, and company cards remain Markdown.
5. Frozen LaTeX versions go to `docs/report/versions/<version>/latex/` with version-specific assets and a manifest.

## LaTeX Export Rules

1. For `v0.2+`, `run_export.py` must support the LaTeX build path; PDF is the primary release artifact and DOCX is optional compatibility output.
2. LaTeX build intermediates belong under ignored build directories, never beside tracked `.tex` sources.
3. A LaTeX release must record the TeX engine, font availability, package versions, build command, and quality-check results.
