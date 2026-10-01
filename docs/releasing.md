# Releasing

1. Update `VERSION` and add the matching `CHANGELOG.md` heading.
2. Run `python3 tools/build_skills.py` and `python3 tools/verify_producer.py`.
3. Commit every change to `skills/adw/adw-core/assets/mise/v2/`. Record that commit as the `ref` for the new entry in `releases/adw-mise-v2.json`, with the SHA-256 of `tasks.toml` and the unchanged snapshot path.
4. In a later commit, add the release-index entry. Do not change the snapshot after the referenced commit.
5. Merge the pull request without squash so the indexed commit remains reachable.
6. Tag the merge result as `v<VERSION>` and push the tag. The release workflow verifies the version and index, packages `skills/adw/` plus `LICENSE`, writes `SHA256SUMS`, extracts the matching changelog section, computes the immutable codeload checksum, and creates the GitHub Release with a pinned Hermes command.

The release is incomplete unless the Git tag, GitHub Release assets, changelog entry, and v2 release-index entry all exist.
