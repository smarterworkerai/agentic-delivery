# Changelog

All notable changes follow [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and Semantic Versioning.

## [2.2.0] - 2026-10-01

### Added

- Standards-conformant, agent-neutral Agent Skills metadata and package validation.
- `.adw/` project-directory support alongside `.hermes/`, with conflicts rejected.
- Claude Code plugin and marketplace manifests, release archives, and generated package content.

### Changed

- Merged feature and bugfix planning into `adw-plan` while retaining both router tokens.
- Moved skill-owned templates beside their skills and reduced copied workflow boilerplate.
- Split the Hermes integration from the portable skill package while retaining thin root discovery shims.

## [2.1.2] - 2026-09-29

### Fixed

- Reserved stdout for machine-readable task payloads and published the corrected immutable v2 snapshot.

## [2.1.1] - 2026-09-28

### Changed

- Extended the environment task ABI with validated optional flags while preserving the canonical task set.

## [2.1.0] - 2026-09-26

### Added

- Single-owner source registries, provenance validation, and the bounded `adw:local:clean` capability.

## [2.0.0] - 2026-09-22

### Added

- The fail-closed v2 mise task contract, fixed side-effect classes, evidence schemas, hotfix restore, and full quality task graph.

[2.2.0]: https://github.com/smarterworkerai/agentic-delivery/compare/v2.1.2...v2.2.0
[2.1.2]: https://github.com/smarterworkerai/agentic-delivery/compare/v2.1.1...v2.1.2
[2.1.1]: https://github.com/smarterworkerai/agentic-delivery/compare/v2.1.0...v2.1.1
[2.1.0]: https://github.com/smarterworkerai/agentic-delivery/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/smarterworkerai/agentic-delivery/releases/tag/v2.0.0
