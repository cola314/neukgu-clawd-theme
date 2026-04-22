#!/usr/bin/env python3
"""
Nano Banana single-frame generator for neukgu theme.

Usage:
  OPENROUTER_API_KEY=sk-... python gen-frame.py \\
      --prompt prompts/typing-f1.txt \\
      --reference ../../themes/neukgu/assets/idle.png \\
      --out ../../themes/neukgu/assets/typing-f1.png

Safety:
  - Requires --confirm flag to actually hit the API (dry-run by default)
  - Prints expected cost before call
  - Saves response image to --out path
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import pathlib
import sys
import urllib.request
import urllib.error

MODEL = "google/gemini-2.5-flash-image"
ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
COST_PER_IMAGE_USD = 0.04  # approx, based on 1290 output tokens × $30/1M


def load_image_b64(path: pathlib.Path) -> str:
    with path.open("rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def build_payload(prompt: str, image_b64: str) -> dict:
    return {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{image_b64}"},
                    },
                ],
            }
        ],
        "modalities": ["image", "text"],
    }


def call_openrouter(api_key: str, payload: dict) -> dict:
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/rullerzhou-afk/clawd-on-desk",
            "X-Title": "Clawd on Desk - neukgu theme",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"ERROR {e.code}: {e.read().decode('utf-8', errors='replace')}", file=sys.stderr)
        raise


def extract_image_b64(resp: dict) -> str | None:
    # OpenRouter returns image in choices[0].message.images[0].image_url.url
    # as data URL: data:image/png;base64,....
    try:
        msg = resp["choices"][0]["message"]
        images = msg.get("images") or []
        if images:
            url = images[0].get("image_url", {}).get("url", "")
            if url.startswith("data:"):
                return url.split(",", 1)[1]
        # Fallback: some responses put base64 in content
        content = msg.get("content")
        if isinstance(content, list):
            for part in content:
                if part.get("type") == "image_url":
                    url = part.get("image_url", {}).get("url", "")
                    if url.startswith("data:"):
                        return url.split(",", 1)[1]
    except (KeyError, IndexError, TypeError):
        pass
    return None


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--prompt", required=True, help="Path to prompt .txt file")
    p.add_argument("--reference", required=True, help="Path to reference PNG")
    p.add_argument("--out", required=True, help="Output PNG path")
    p.add_argument("--confirm", action="store_true", help="Actually call the API (otherwise dry-run)")
    args = p.parse_args()

    prompt_path = pathlib.Path(args.prompt)
    ref_path = pathlib.Path(args.reference)
    out_path = pathlib.Path(args.out)

    if not prompt_path.exists():
        print(f"prompt not found: {prompt_path}", file=sys.stderr)
        return 1
    if not ref_path.exists():
        print(f"reference not found: {ref_path}", file=sys.stderr)
        return 1

    prompt = prompt_path.read_text(encoding="utf-8").strip()
    ref_size_kb = ref_path.stat().st_size / 1024

    print(f"Model:     {MODEL}")
    print(f"Prompt:    {prompt_path} ({len(prompt)} chars)")
    print(f"Reference: {ref_path} ({ref_size_kb:.1f} KB)")
    print(f"Output:    {out_path}")
    print(f"Est. cost: ~${COST_PER_IMAGE_USD:.3f}")
    print()

    if not args.confirm:
        print("DRY RUN - add --confirm to actually call the API.")
        return 0

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("OPENROUTER_API_KEY env var not set.", file=sys.stderr)
        return 1

    image_b64 = load_image_b64(ref_path)
    payload = build_payload(prompt, image_b64)

    print("Calling OpenRouter...")
    resp = call_openrouter(api_key, payload)

    out_b64 = extract_image_b64(resp)
    if not out_b64:
        print("No image in response. Full response:", file=sys.stderr)
        print(json.dumps(resp, indent=2)[:4000], file=sys.stderr)
        return 2

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("wb") as f:
        f.write(base64.b64decode(out_b64))

    usage = resp.get("usage") or {}
    print(f"Saved: {out_path} ({out_path.stat().st_size / 1024:.1f} KB)")
    if usage:
        print(f"Tokens: prompt={usage.get('prompt_tokens')} completion={usage.get('completion_tokens')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
