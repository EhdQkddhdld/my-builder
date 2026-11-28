# v3.3.17 A/B independent seeds

Base: v3.3.16, 7c4f15f575646f0515afd48ec82e126789b44708.
User approves different random seeds for A and B. In paired generation both seeds are drawn before generation and are guaranteed distinct; single generation retains existing seed-lock behavior. A/B temporarily ignores seed lock without modifying the stored lock; per-result request and metadata seeds must match. All other generation parameters and sequencing, cancellation and error handling remain unchanged. DEEP_TRACK, fixed Auto QA and independent review required before deployment.
