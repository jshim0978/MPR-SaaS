# version: v1.0
# stage: describer
# rules:
# - Emit JSON spec + ≤120-word summary; no unverifiable assertions.
Given a user prompt, output:
{
 "task": "...",
 "entities": [...],
 "constraints": [...],
 "acceptance_criteria": [...]
}
Then a concise summary (<=120 words).
PROMPT: "{{INPUT}}"
