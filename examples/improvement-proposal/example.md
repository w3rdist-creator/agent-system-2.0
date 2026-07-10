# Improvement Proposal — Add a Wikilink Gate

## Problem observed

The base vault can accumulate broken navigation links as notes move.

## Evidence

Phase 4 advertises sixteen local maps and a connected seed chain, so a moved or misspelled target would break a user-visible route.

## Who should notice improvement

The vault operator should be able to open every intentional wikilink without finding a missing note.

## Proposed destination

`scripts/verify_wikilinks.py` and its unit-test coverage.

## What it replaces or merges

It replaces manual link spot-checking during each release review.

## Context, storage, and review cost

One deterministic script, one test module, and a few seconds per gate run.

## Blast radius

The check reads vault, pack, and example Markdown; it does not rewrite notes.

## Verification method

All shipped links resolve, a synthetic missing target fails, and an explicit planned marker passes.

## Kill or rollback condition

Remove or narrow the gate if valid Obsidian links cannot be represented without repository-specific exceptions.

## Why a simpler location is insufficient

Editorial guidance cannot detect link drift mechanically across installed content.

## Disposition

Act: implement the bounded read-only gate in Phase 4.
