#!/usr/bin/env python3
"""푸시 전 비밀값 검사. 키처럼 보이는 문자열이 있으면 종료 코드 1로 중단.
검사: NAI 키(pst-...), GitHub 토큰(github_pat_ / ghp_ / gho_ ...), 값이 붙은 Bearer, 개인키 블록, 키스토어 파일.
추가로 환경변수 GITHUB_TOKEN / RD_KEYSTORE_PASSWORD 값이 파일에 들어갔는지도 확인(값은 출력하지 않음)."""
import os, re, subprocess, sys
root = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip() or "."
files = subprocess.run(["git", "-C", root, "ls-files", "-co", "--exclude-standard"], capture_output=True, text=True).stdout.split("\n")
PAT = [
    ("NAI key", re.compile(rb"pst-[A-Za-z0-9_\-]{20,}")),
    ("GitHub token", re.compile(rb"(github_pat_|ghp_|gho_|ghu_|ghs_|ghr_)[A-Za-z0-9_]{20,}")),
    ("Bearer value", re.compile(rb"Bearer\s+[A-Za-z0-9_\-\.=]{20,}")),
    ("private key", re.compile(rb"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
]
env_vals = [v.encode() for v in (os.environ.get("GITHUB_TOKEN"), os.environ.get("RD_KEYSTORE_PASSWORD")) if v and len(v) >= 8]
bad = []
for f in filter(None, files):
    p = os.path.join(root, f)
    if not os.path.isfile(p):
        continue
    if re.search(r"\.(jks|keystore|p12|pfx)$", f, re.I) or os.path.basename(f) == "signing.env":
        bad.append((f, "keystore/signing file")); continue
    data = open(p, "rb").read()
    for name, rx in PAT:
        if rx.search(data):
            bad.append((f, name))
    for v in env_vals:
        if v in data:
            bad.append((f, "secret value from environment"))
if bad:
    for f, why in bad:
        print("SECRET-LIKE:", f, "->", why)
    sys.exit(1)
print("secret scan OK:", len([f for f in files if f]), "files")
