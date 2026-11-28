# My Builder v3.3.11 · Smoothflow

Base: main `05b5e5e0340eb5c024f3fa0ece4996f4f1bf005e` (v3.3.10). User requested start of combined UX optimization, including earlier A/B placement decision.

Neon cover spec: 7-item horizontal detail quick switcher (style/count/char/cloth/pose/env/light), 44px touch, aria-current, selected item centered; previous/next chain across detail subpages; immediate atomic detail close and hub restoration; studio result full width; exclude default active scene phase from summary count when pose and shot absent. No engine/state mutations in navigation.

A/B: move existing settings/preview to merged composition/scene detail, default OFF, accessible switch; no duplicate controls in image generation. Existing explicit Generate action dispatches existing A/B pair only when builder source and valid distinct pair, otherwise normal single generation (with notice when ON but no distinct pair). Keep seed, sequential calls, results, cancellation and cooldown unchanged. Manual source stays single. No new API calls in QA. Toggle session-only, preserved across navigation, not saved in clean HTML. Label reflects mode. No new engine or data changes.

UI-only cover items FAST_TRACK; combined A/B generation dispatch merits DEEP_TRACK independent review. Preserve 15 protected blocks; fixed auto-qa, official checks, relevant navigation/render and mocked generation regression. No main deployment until required gates and approval. Actual NAI and Fold8 not tested by QA.
