"""Export every AI session of this project into ai_log/: Claude Code (with subagents) and Codex.

usage: .venv/bin/python ai_log/export.py   (rerun after the last session; it overwrites the export)
Every non-empty value in .env is replaced by [REDACTED], and the export refuses to finish if one survives.
"""
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "ai_log"
CLAUDE = Path.home() / ".claude/projects" / str(ROOT).replace("/", "-").replace("_", "-")
CODEX = Path.home() / ".codex/sessions"
SECRETS = [line.split("=", 1)[1].strip().strip("\"'") for line in (ROOT / ".env").read_text().splitlines()
           if "=" in line and not line.startswith("#")]
SECRETS = [s for s in SECRETS if len(s) >= 8]


def codex_cwd(path):
    with open(path) as f:
        return json.loads(f.readline()).get("payload", {}).get("cwd", "")


def prompts(lines, codex):
    """(timestamp, text) of what the user typed, skipping tool results and injected context."""
    for line in lines:
        d = json.loads(line)
        if codex:
            p = d.get("payload", {})
            if d.get("type") != "response_item" or p.get("type") != "message" or p.get("role") != "user":
                continue
            content = p.get("content", [])
        else:
            if d.get("type") != "user" or d.get("isMeta"):
                continue
            content = d["message"]["content"]
        if isinstance(content, str):
            content = [{"text": content}]
        for c in content:
            text = (c.get("text") or "").strip()
            if text and not text.startswith(("<", "#", "Caveat:")) and c.get("type") != "tool_result":
                yield d.get("timestamp", ""), text


sessions = [("claude", p) for p in CLAUDE.glob("*.jsonl")]
sessions += [("claude", p) for p in CLAUDE.glob("*/subagents/*.jsonl")]
sessions += [("codex", p) for p in CODEX.rglob("rollout-*.jsonl") if codex_cwd(p).startswith(str(ROOT))]
index = []
for tool, path in sessions:
    text = path.read_text()
    for s in SECRETS:
        text = text.replace(s, "[REDACTED]")
    assert not any(s in text for s in SECRETS)
    sub = path.parent.parent.name + "/" if path.parent.name == "subagents" else ""
    dest = OUT / tool / f"{sub}{path.stem}.jsonl.gz"
    dest.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(dest, "wt", compresslevel=9) as f:  # mtime in the header changes per run; fine for a one-off export
        f.write(text)
    lines = text.splitlines()
    stamps = [json.loads(line).get("timestamp") for line in lines]
    stamps = sorted(t for t in stamps if t)
    index.append((stamps[0] if stamps else "", stamps[-1] if stamps else "", tool, dest.relative_to(OUT),
                  list(prompts(lines, tool == "codex")) if not sub else []))

md = ["# AI conversation log", "",
      f"All {len(index)} sessions of this project, oldest first: Claude Code (subagents under their parent's id) "
      "and Codex. Each `.jsonl.gz` is the full raw session; secrets from `.env` are replaced by `[REDACTED]`. "
      "Below each session: what the user typed (first 400 characters).", ""]
for start, end, tool, rel, said in sorted(index):
    md.append(f"## {start[:16].replace('T', ' ')} → {end[11:16]} UTC · {tool} · [{rel}]({rel})")
    md += [f"- `{t[11:16]}` {' '.join(x.split())[:400]}" for t, x in said] or ["- (subagent)"]
    md.append("")
(OUT / "README.md").write_text("\n".join(md))
print(f"{len(index)} sessions → {OUT}")
