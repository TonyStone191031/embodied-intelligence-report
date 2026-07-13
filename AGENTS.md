# Repository Entry Rules

This file is the repository's single rule entry. Detailed and long-lived requirements live only in [`docs/planning/项目工作规范.md`](docs/planning/项目工作规范.md); this file defines authority, routing, and the minimum start gate rather than repeating those requirements.

## Authority order

When active documents conflict, apply them in this order:

1. this file's entry and routing rules;
2. `docs/planning/项目工作规范.md`;
3. `docs/planning/current/当前版本工作台.md`;
4. `docs/planning/current/具身智能报告-当前详细大纲.md`;
5. directory-local README and toolchain records.

Archived plans, frozen report versions, and generated exports record historical state; they do not override active rules.

## Task routing

1. Every task starts here.
2. Planning, research, report, versioning, asset, build, or export work must then read the relevant sections of `docs/planning/项目工作规范.md`.
3. Work that changes or advances the active version must also read `docs/planning/current/当前版本工作台.md`.
4. Structural work or report drafting must additionally read the relevant part of `docs/planning/current/具身智能报告-当前详细大纲.md`, including its evidence and asset plan.
5. Build or export work must finally read the target directory's README and toolchain record for commands and environment facts.

## Minimum start gate

1. Do not draft or rewrite report text before completing the routed pre-read and the planning gate defined in the project handbook.
2. Structural changes and new drafting require an updated active outline and explicit user approval before report text changes.
3. A new report-text batch must be registered in the current-version workbench before drafting; its first progress update must explicitly confirm that the routed pre-read is complete.
4. Non-structural maintenance must be registered in the workbench before implementation.
5. Do not overwrite frozen versions, edit generated PDF/DOCX artifacts as sources, or maintain parallel Markdown and LaTeX copies of v0.2+ report text.

## Governance

Do not create another parallel normative document by default. New durable rules belong in `docs/planning/项目工作规范.md`; version-specific decisions and execution state belong in the two active files under `docs/planning/current/`. Directory README files contain only local operational guidance.
