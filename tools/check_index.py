#!/usr/bin/env python3
"""docs/index.html 안전 검사.

비밀값처럼 보이는 문자열, HTML 형태, 앱 계약 문자열, 인라인 JS 문법을 확인합니다.
사용: python3 tools/check_index.py [경로]

종료 코드 0 = 통과, 1 = 실패. 비밀값 내용은 출력하지 않습니다.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path

MIN_BYTES = 200_000
MAX_BYTES = 5_000_000

SECRET_PATTERNS = [
    ("NAI key", re.compile(rb"pst-[A-Za-z0-9_\-]{20,}")),
    ("GitHub token", re.compile(rb"(github_pat_|ghp_|gho_|ghu_|ghs_|ghr_)[A-Za-z0-9_]{20,}")),
    ("Bearer value", re.compile(rb"Bearer\s+[A-Za-z0-9_\-\.=]{20,}")),
    ("private key", re.compile(rb"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
]

# 앱·저장 계약. contiguous "AndroidBridge.saveBase64" 는 코드가
# window.AndroidBridge 와 B.saveBase64 로 나뉘어 있어 따로 검사합니다.
REQUIRED = [
    "rd_nai_key_v1",
    "rdHandleBack",
    "AndroidBridge",
    "saveBase64",
    "rd-nai-gallery",
    "rd-nai-history",
    "rd-pose-thumbs",
    'createObjectStore("meta"',
    'createObjectStore("full"',
    'createObjectStore("img"',
    'createObjectStore("thumbs"',
]

SCRIPT_OPEN = re.compile(r"<script(\b[^>]*)>", re.I)
SCRIPT_CLOSE = re.compile(r"</script\s*>", re.I)
SRC_ATTR = re.compile(r"\bsrc\s*=", re.I)
TYPE_ATTR = re.compile(r"""\btype\s*=\s*["']([^"']+)["']""", re.I)
JS_TYPES = {
    "",
    "text/javascript",
    "application/javascript",
    "module",
    "text/ecmascript",
    "application/ecmascript",
}


class FormParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tags: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        self.tags.append(tag)


def repo_root() -> Path:
    here = Path(__file__).resolve().parent.parent
    return here


def fail(msg: str, errors: list[str]) -> None:
    errors.append(msg)


def check_secrets(data: bytes, label: str, errors: list[str]) -> None:
    for name, rx in SECRET_PATTERNS:
        if rx.search(data):
            fail(f"비밀값처럼 보이는 문자열({name})이 {label}에 있습니다. 값은 출력하지 않습니다.", errors)


def check_html(text: str, size: int, errors: list[str]) -> None:
    if size < MIN_BYTES:
        fail(f"파일이 너무 작습니다 ({size}바이트). 잘렸거나 빈 파일일 수 있습니다. 최소 {MIN_BYTES}바이트.", errors)
    if size > MAX_BYTES:
        fail(f"파일이 너무 큽니다 ({size}바이트). 이미지가 파일 안에 들어갔을 수 있습니다. 최대 {MAX_BYTES}바이트.", errors)
    if "\x00" in text:
        fail("파일에 NUL 바이트가 있습니다. 이진 파일이 섞인 것 같습니다.", errors)
    low = text.lower()
    if "<html" not in low:
        fail("<html> 태그가 없습니다.", errors)
    if "</html>" not in low:
        fail("</html> 종료 태그가 없습니다. 업로드가 중간에 끊겼을 수 있습니다.", errors)
    if "<head" not in low or "<body" not in low:
        fail("<head> 또는 <body>가 없습니다.", errors)
    opens = SCRIPT_OPEN.findall(text)
    closes = SCRIPT_CLOSE.findall(text)
    if len(opens) != len(closes):
        fail(f"<script> 태그가 짝이 맞지 않습니다 (열림 {len(opens)}, 닫힘 {len(closes)}).", errors)
    try:
        parser = FormParser()
        parser.feed(text)
        parser.close()
    except Exception as exc:  # noqa: BLE001 — HTMLParser 오류만 모음
        fail(f"HTML 파싱에 실패했습니다: {exc}", errors)
        return
    if "html" not in parser.tags:
        fail("파서가 html 요소를 찾지 못했습니다.", errors)


def check_contracts(text: str, errors: list[str]) -> None:
    missing = [s for s in REQUIRED if s not in text]
    if missing:
        fail("필수 앱 계약 문자열이 없습니다: " + ", ".join(missing), errors)


def iter_inline_scripts(text: str):
    pos = 0
    index = 0
    while True:
        m = SCRIPT_OPEN.search(text, pos)
        if not m:
            break
        attrs = m.group(1) or ""
        close = SCRIPT_CLOSE.search(text, m.end())
        if not close:
            break
        body = text[m.end():close.start()]
        pos = close.end()
        index += 1
        if SRC_ATTR.search(attrs):
            continue
        typ = (TYPE_ATTR.search(attrs).group(1).strip().lower() if TYPE_ATTR.search(attrs) else "")
        if typ not in JS_TYPES:
            continue
        if not body.strip():
            continue
        line = text[:m.start()].count("\n") + 1
        yield index, line, body


def check_js(text: str, errors: list[str]) -> None:
    scripts = list(iter_inline_scripts(text))
    if not scripts:
        fail("검사할 인라인 스크립트가 없습니다.", errors)
        return
    with tempfile.TemporaryDirectory(prefix="rd-js-") as td:
        for index, line, body in scripts:
            path = Path(td) / f"script-{index}.js"
            path.write_text(body, encoding="utf-8")
            try:
                proc = subprocess.run(
                    ["node", "--check", str(path)],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
            except FileNotFoundError:
                fail("node를 찾을 수 없습니다. 인라인 JS 문법 검사를 건너뛸 수 없습니다.", errors)
                return
            except subprocess.TimeoutExpired:
                fail(f"스크립트 #{index} (대략 {line}행) node --check 가 시간 초과했습니다.", errors)
                continue
            if proc.returncode != 0:
                detail = (proc.stderr or proc.stdout or "").strip().splitlines()
                hint = next((row.strip() for row in detail if "SyntaxError" in row or "Error" in row), None)
                if not hint:
                    hint = detail[-2].strip() if len(detail) >= 2 else (detail[-1] if detail else "문법 오류")
                fail(f"스크립트 #{index} (대략 {line}행) JS 문법 오류: {hint}", errors)


def main() -> int:
    parser = argparse.ArgumentParser(description="docs/index.html 안전 검사")
    parser.add_argument("path", nargs="?", default=str(repo_root() / "docs" / "index.html"))
    args = parser.parse_args()
    path = Path(args.path)
    errors: list[str] = []
    if not path.is_file():
        print(f"FAIL: 파일이 없습니다: {path}", file=sys.stderr)
        return 1
    data = path.read_bytes()
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        print(f"FAIL: UTF-8이 아닙니다: {path}", file=sys.stderr)
        return 1
    label = str(path)
    check_secrets(data, label, errors)
    check_html(text, len(data), errors)
    check_contracts(text, errors)
    check_js(text, errors)
    if errors:
        print(f"FAIL: {path} ({len(errors)}건)")
        for item in errors:
            print(" -", item)
        return 1
    print(f"OK: {path} ({len(data)}바이트, 계약 {len(REQUIRED)}개, 인라인 스크립트 문법 통과)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
