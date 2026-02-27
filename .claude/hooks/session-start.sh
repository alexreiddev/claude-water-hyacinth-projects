#!/bin/bash
set -euo pipefail

# Only run in remote (Claude Code on the web) environments
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

KTLINT_VERSION="1.1.1"
KTLINT_BIN="/usr/local/bin/ktlint"

echo "==> Setting up expense-tracker development environment"

# ── 1. Ensure JAVA_HOME is set for Gradle ───────────────────────────────────
JAVA_HOME_PATH="/usr/lib/jvm/java-21-openjdk-amd64"
if [ -d "$JAVA_HOME_PATH" ]; then
  export JAVA_HOME="$JAVA_HOME_PATH"
  echo "export JAVA_HOME=\"$JAVA_HOME_PATH\"" >> "${CLAUDE_ENV_FILE:-/dev/null}"
  echo "    Java home: $JAVA_HOME_PATH"
else
  echo "    WARNING: Expected JDK not found at $JAVA_HOME_PATH"
fi

# ── 2. Download ktlint if missing ────────────────────────────────────────────
if ! command -v ktlint &>/dev/null || [[ "$(ktlint --version 2>/dev/null | tr -d '[:space:]')" != "$KTLINT_VERSION" ]]; then
  echo "==> Downloading ktlint $KTLINT_VERSION"
  curl -sSL \
    "https://github.com/pinterest/ktlint/releases/download/${KTLINT_VERSION}/ktlint" \
    -o "$KTLINT_BIN"
  chmod +x "$KTLINT_BIN"
  echo "    ktlint installed at $KTLINT_BIN"
else
  echo "    ktlint $(ktlint --version 2>/dev/null) already installed"
fi

# ── 3. Pre-warm the Gradle dependency cache ──────────────────────────────────
echo "==> Pre-warming Gradle dependency cache"
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}/expense-tracker"

if [ -f "$PROJECT_DIR/settings.gradle.kts" ]; then
  (cd "$PROJECT_DIR" && gradle dependencies --configuration testRuntimeClasspath -q 2>/dev/null || true)
  echo "    Gradle cache warmed"
else
  echo "    expense-tracker project not found at $PROJECT_DIR — skipping Gradle warm-up"
fi

echo "==> Session setup complete"
echo "    Linter : ktlint $KTLINT_VERSION  (ktlint 'expense-tracker/**/*.kt')"
echo "    Tests  : gradle :app:test        (run from expense-tracker/)"
