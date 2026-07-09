#!/bin/bash
set -uo pipefail

# Only needed in Claude Code on the web's ephemeral containers.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"

# 1. ffmpeg (system dependency for the video-use skill)
if ! command -v ffmpeg >/dev/null 2>&1; then
  apt-get update -qq && apt-get install -y -qq ffmpeg
fi

# 2. Python deps for the video-use skill (uv-managed)
VIDEO_USE_DIR="$PROJECT_DIR/.claude/skills/video-use"
if [ -f "$VIDEO_USE_DIR/pyproject.toml" ] && command -v uv >/dev/null 2>&1; then
  (cd "$VIDEO_USE_DIR" && uv sync) || true
fi

exit 0
