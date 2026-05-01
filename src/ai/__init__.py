"""Couche IA (Anthropic Claude scoring) — stub Phase 2a, rempli Phase 2c.

Spec : docs/ia/ai-architecture.md + docs/ia/prompt-library.md (PROMPT_VERSION=signal-scoring-v1.0).
Approche hybride : Claude (score brut + raison) + 5 sanity checks deterministes
(cf docs/ia/edge-scoring-model.md scoring-model-v1.1).

Modele live : claude-sonnet-4-5-20250929 (tag exact, jamais alias — cf L002).
Modele R&D : claude-haiku-4-5 (Batch + Cache, cap 100 ap/j).
"""
