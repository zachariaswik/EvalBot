# Agent Model Recommendations

Recommended LLM model assignment per agent, optimised for quality-per-dollar.
Models are passed to CrewAI via litellm — any litellm-compatible model string works.

## Available Providers

### Anthropic (needs `ANTHROPIC_API_KEY`)

| Model             | Model string                           | Input   | Output   | Notes                         |
|-------------------|----------------------------------------|---------|----------|-------------------------------|
| Opus 4.6          | `anthropic/claude-opus-4-6`            | $15.00  | $75.00   | Top-tier reasoning            |
| Sonnet 4.6        | `anthropic/claude-sonnet-4-6`          | $3.00   | $15.00   | Strong all-rounder            |
| Sonnet 4 (May 25) | `anthropic/claude-sonnet-4-20250514`   | $3.00   | $15.00   | Previous Sonnet release       |
| Haiku 4.5         | `anthropic/claude-haiku-4-5`           | $1.00   | $5.00    | Fast & cheap extraction       |

### OpenAI (needs `OPENAI_API_KEY`)

| Model        | Model string   | Input  | Output  | Notes                              |
|--------------|----------------|--------|---------|------------------------------------|
| GPT-4o       | `gpt-4o`       | $2.50  | $10.00  | Flagship multimodal                |
| GPT-4o mini  | `gpt-4o-mini`  | $0.15  | $0.60   | Cheap general-purpose              |
| GPT-4.1      | `gpt-4.1`      | $2.00  | $8.00   | Latest flagship                    |
| GPT-4.1 mini | `gpt-4.1-mini` | $0.40  | $1.60   | Good balance of cost & quality     |
| GPT-4.1 nano | `gpt-4.1-nano` | $0.10  | $0.40   | Ultra-cheap extraction             |
| o3-mini      | `o3-mini`      | $1.10  | $4.40   | Reasoning model                    |

### MiniMax (needs `MINIMAX_API_KEY`)

| Model      | Model string            | Input  | Output  | Notes                            |
|------------|-------------------------|--------|---------|----------------------------------|
| MiniMax M2.7 | `minimax/MiniMax-M2.7` | $0.30  | $1.20  | Strong reasoning, very low cost  |

*All prices per 1M tokens.*

---

## Single-Provider Profiles

### Anthropic

Best analytical depth and strategic reasoning. Opus on the three critical agents,
Sonnet for mid-tier analysis, Haiku for extraction.

```python
AGENT_MODELS: dict[int, str | None] = {
    0: "anthropic/claude-opus-4-6",              # Startup Idea Generator (generate mode only)
    1: "anthropic/claude-haiku-4-5",             # Intake Parser
    2: "anthropic/claude-opus-4-6",              # Venture Analyst
    3: "anthropic/claude-sonnet-4-6",            # Market & Competition Analyst
    4: "anthropic/claude-sonnet-4-6",            # Product & Positioning Analyst
    5: "anthropic/claude-sonnet-4-6",            # Founder Fit Analyst
    6: "anthropic/claude-opus-4-6",              # Recommendation / Pivot Agent
    7: "anthropic/claude-sonnet-4-6",            # Ranking Committee Agent
}
```

| Agent | Model      | ~Input | ~Output | ~Cost   |
|-------|------------|--------|---------|---------|
| 0     | Opus 4.6   | 3K     | 4K      | $0.345  |
| 1     | Haiku 4.5  | 2K     | 1K      | $0.007  |
| 2     | Opus 4.6   | 5K     | 2K      | $0.225  |
| 3     | Sonnet 4.6 | 8K     | 2K      | $0.054  |
| 4     | Sonnet 4.6 | 10K    | 2K      | $0.060  |
| 5     | Sonnet 4.6 | 12K    | 2K      | $0.066  |
| 6     | Opus 4.6   | 14K    | 2K      | $0.360  |

**Eval mode** (Agents 1-6 per startup): **~$0.77** | Batch of 10 + ranking: **~$8.30**

**Generate mode** (3 rounds, default settings):

| Scenario             | Cost    | Notes                                              |
|----------------------|---------|----------------------------------------------------|
| Inner screening pass | $0.58   | One attempt of Agent 0 + 1 + 2                     |
| Full round (1 pass)  | $1.12   | Screening + Agents 3-6                             |
| 3 rounds (1 attempt) | ~$3.35  | Best case — every idea passes screening first try  |
| 3 rounds (~2 attempts)| ~$5.10 | Typical — avg 2 inner attempts before passing      |

### OpenAI

GPT-4.1 for critical agents, mini for mid-tier, nano for extraction.

```python
AGENT_MODELS: dict[int, str | None] = {
    0: "gpt-4.1",                                # Startup Idea Generator (generate mode only)
    1: "gpt-4.1-nano",                           # Intake Parser
    2: "gpt-4.1",                                # Venture Analyst
    3: "gpt-4.1-mini",                           # Market & Competition Analyst
    4: "gpt-4.1-mini",                           # Product & Positioning Analyst
    5: "gpt-4.1-mini",                           # Founder Fit Analyst
    6: "gpt-4.1",                                # Recommendation / Pivot Agent
    7: "gpt-4.1-mini",                           # Ranking Committee Agent
}
```

| Agent | Model        | ~Input | ~Output | ~Cost   |
|-------|--------------|--------|---------|---------|
| 0     | GPT-4.1      | 3K     | 4K      | $0.038  |
| 1     | GPT-4.1 nano | 2K     | 1K      | $0.001  |
| 2     | GPT-4.1      | 5K     | 2K      | $0.026  |
| 3     | GPT-4.1 mini | 8K     | 2K      | $0.006  |
| 4     | GPT-4.1 mini | 10K    | 2K      | $0.007  |
| 5     | GPT-4.1 mini | 12K    | 2K      | $0.008  |
| 6     | GPT-4.1      | 14K    | 2K      | $0.044  |

**Eval mode** (Agents 1-6 per startup): **~$0.09** | Batch of 10 + ranking: **~$1.05**

**Generate mode** (3 rounds, default settings):

| Scenario             | Cost    | Notes                                              |
|----------------------|---------|----------------------------------------------------|
| Inner screening pass | $0.07   | One attempt of Agent 0 + 1 + 2                     |
| Full round (1 pass)  | $0.13   | Screening + Agents 3-6                             |
| 3 rounds (1 attempt) | ~$0.39  | Best case — every idea passes screening first try  |
| 3 rounds (~2 attempts)| ~$0.59 | Typical — avg 2 inner attempts before passing      |

### MiniMax

M2.7 across the board. Best for rapid iteration and testing when cost needs to
stay minimal. Only requires a `MINIMAX_API_KEY`.

```python
AGENT_MODELS: dict[int, str | None] = {
    0: "minimax/MiniMax-M2.7",                   # Startup Idea Generator (generate mode only)
    1: "minimax/MiniMax-M2.7",                   # Intake Parser
    2: "minimax/MiniMax-M2.7",                   # Venture Analyst
    3: "minimax/MiniMax-M2.7",                   # Market & Competition Analyst
    4: "minimax/MiniMax-M2.7",                   # Product & Positioning Analyst
    5: "minimax/MiniMax-M2.7",                   # Founder Fit Analyst
    6: "minimax/MiniMax-M2.7",                   # Recommendation / Pivot Agent
    7: "minimax/MiniMax-M2.7",                   # Ranking Committee Agent
}
```

| Agent | Model        | ~Input | ~Output | ~Cost   |
|-------|--------------|--------|---------|---------|
| 0     | MiniMax M2.7 | 3K     | 4K      | $0.006  |
| 1     | MiniMax M2.7 | 2K     | 1K      | $0.002  |
| 2     | MiniMax M2.7 | 5K     | 2K      | $0.004  |
| 3     | MiniMax M2.7 | 8K     | 2K      | $0.005  |
| 4     | MiniMax M2.7 | 10K    | 2K      | $0.005  |
| 5     | MiniMax M2.7 | 12K    | 2K      | $0.006  |
| 6     | MiniMax M2.7 | 14K    | 2K      | $0.007  |

**Eval mode** (Agents 1-6 per startup): **~$0.03** | Batch of 10 + ranking: **~$0.35**

**Generate mode** (3 rounds, default settings):

| Scenario             | Cost    | Notes                                              |
|----------------------|---------|----------------------------------------------------|
| Inner screening pass | $0.01   | One attempt of Agent 0 + 1 + 2                     |
| Full round (1 pass)  | $0.04   | Screening + Agents 3-6                             |
| 3 rounds (1 attempt) | ~$0.11  | Best case — every idea passes screening first try  |
| 3 rounds (~2 attempts)| ~$0.14 | Typical — avg 2 inner attempts before passing      |

---

## Mixed-Provider Profiles

### Mix Premium — Best quality across providers

Cherry-pick the best model from each provider per agent. Opus for the three critical
reasoning agents, MiniMax for mid-tier analysis, nano for extraction.

```python
AGENT_MODELS: dict[int, str | None] = {
    0: "anthropic/claude-opus-4-6",              # Startup Idea Generator — top-tier creative reasoning
    1: "gpt-4.1-nano",                           # Intake Parser — ultra-cheap extraction
    2: "anthropic/claude-opus-4-6",              # Venture Analyst — best-in-class reasoning
    3: "minimax/MiniMax-M2.7",                   # Market & Competition — good value reasoning
    4: "minimax/MiniMax-M2.7",                   # Product & Positioning — good value reasoning
    5: "minimax/MiniMax-M2.7",                   # Founder Fit — good value reasoning
    6: "anthropic/claude-opus-4-6",              # Recommendation — best strategic synthesis
    7: "minimax/MiniMax-M2.7",                   # Ranking Committee — structured comparison
}
```

| Agent | Model        | ~Input | ~Output | ~Cost   |
|-------|--------------|--------|---------|---------|
| 0     | Opus 4.6     | 3K     | 4K      | $0.345  |
| 1     | GPT-4.1 nano | 2K     | 1K      | $0.001  |
| 2     | Opus 4.6     | 5K     | 2K      | $0.225  |
| 3     | MiniMax M2.7 | 8K     | 2K      | $0.005  |
| 4     | MiniMax M2.7 | 10K    | 2K      | $0.005  |
| 5     | MiniMax M2.7 | 12K    | 2K      | $0.006  |
| 6     | Opus 4.6     | 14K    | 2K      | $0.360  |

**Eval mode** (Agents 1-6 per startup): **~$0.60** | Batch of 10 + ranking: **~$6.10**

**Generate mode** (3 rounds, default settings):

| Scenario             | Cost    | Notes                                              |
|----------------------|---------|----------------------------------------------------|
| Inner screening pass | $0.57   | One attempt of Agent 0 + 1 + 2                     |
| Full round (1 pass)  | $0.95   | Screening + Agents 3-6                             |
| 3 rounds (1 attempt) | ~$2.85  | Best case — every idea passes screening first try  |
| 3 rounds (~2 attempts)| ~$4.55 | Typical — avg 2 inner attempts before passing      |

### Mix Normal — Quality-conscious on a budget

Sonnet replaces Opus on the critical agents — still strong reasoning, at a fraction
of the cost. Keeps MiniMax and nano elsewhere for maximum savings.

```python
AGENT_MODELS: dict[int, str | None] = {
    0: "anthropic/claude-sonnet-4-6",            # Startup Idea Generator — strong creative reasoning
    1: "gpt-4.1-nano",                           # Intake Parser — ultra-cheap extraction
    2: "anthropic/claude-sonnet-4-6",            # Venture Analyst — strong analytical depth
    3: "minimax/MiniMax-M2.7",                   # Market & Competition — good value reasoning
    4: "minimax/MiniMax-M2.7",                   # Product & Positioning — good value reasoning
    5: "minimax/MiniMax-M2.7",                   # Founder Fit — good value reasoning
    6: "anthropic/claude-sonnet-4-6",            # Recommendation — solid strategic synthesis
    7: "minimax/MiniMax-M2.7",                   # Ranking Committee — structured comparison
}
```

| Agent | Model        | ~Input | ~Output | ~Cost   |
|-------|--------------|--------|---------|---------|
| 0     | Sonnet 4.6   | 3K     | 4K      | $0.069  |
| 1     | GPT-4.1 nano | 2K     | 1K      | $0.001  |
| 2     | Sonnet 4.6   | 5K     | 2K      | $0.045  |
| 3     | MiniMax M2.7 | 8K     | 2K      | $0.005  |
| 4     | MiniMax M2.7 | 10K    | 2K      | $0.005  |
| 5     | MiniMax M2.7 | 12K    | 2K      | $0.006  |
| 6     | Sonnet 4.6   | 14K    | 2K      | $0.072  |

**Eval mode** (Agents 1-6 per startup): **~$0.13** | Batch of 10 + ranking: **~$1.40**

**Generate mode** (3 rounds, default settings):

| Scenario             | Cost    | Notes                                              |
|----------------------|---------|----------------------------------------------------|
| Inner screening pass | $0.12   | One attempt of Agent 0 + 1 + 2                     |
| Full round (1 pass)  | $0.20   | Screening + Agents 3-6                             |
| 3 rounds (1 attempt) | ~$0.61  | Best case — every idea passes screening first try  |
| 3 rounds (~2 attempts)| ~$0.95 | Typical — avg 2 inner attempts before passing      |

---

## Agent Reasoning Requirements

| Agent | Role                      | Reasoning Complexity | What it does                                    |
|-------|---------------------------|----------------------|-------------------------------------------------|
| 0     | Startup Idea Generator    | Very High            | Generate startup ideas optimized for evaluation |
| 1     | Intake Parser             | Low                  | Extract & structure raw submission data         |
| 2     | Venture Analyst           | Very High            | Score 10 dimensions, produce verdict            |
| 3     | Market & Competition      | Medium-High          | Market dynamics, competitive landscape          |
| 4     | Product & Positioning     | Medium               | Feature vs company, wrapper risk, positioning   |
| 5     | Founder Fit               | Medium               | Team assessment, execution confidence           |
| 6     | Recommendation / Pivot    | Very High            | Strategic synthesis, pivot options, action plans |
| 7     | Ranking Committee         | Medium               | Comparative ranking across batch                |

**Guidelines for choosing models:**

- **Agent 0** generates full startup submissions and must reason strategically about which ideas will score well. Needs top-tier creative and analytical capability. Only used in `generate` mode. This is the most cost-sensitive agent in generate mode since it runs on every inner-loop attempt.
- **Agent 1** needs only extraction — use the cheapest model that follows instructions reliably.
- **Agents 2 & 6** are the quality bottleneck. Agent 2's scores cascade through the entire pipeline; Agent 6's recommendations are what users act on. Use the best model your budget allows here. In generate mode, Agent 2 also runs on every inner-loop attempt.
- **Agents 3-5** do focused analysis on a narrower scope. Mid-tier models work well.
- **Agent 7** needs consistency across a large context more than deep reasoning. Mid-tier is fine; cost matters because input context grows with batch size.
