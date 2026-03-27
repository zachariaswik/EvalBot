# Agent 7 — Ranking Committee Agent: Prompts with Reasoning

## Overview

Agent 7 plays the role of the investment committee that sits at the end of an accelerator batch. Its job is not to encourage — that's the mentor's role. Its job is to rank, categorize, and shortlist with brutal clarity. Where Agents 3-6 analyzed this project on its own terms, Agent 7 compares it against external benchmarks: what does a top pre-seed look like? Where does this project land in the distribution of accelerator cohorts? What category does it fall into — and what does that category imply for the path forward?

Since this analysis evaluates a single project rather than a full cohort, Agent 7 must construct the comparison frame itself: benchmark archetypes drawn from pre-seed EdTech data, accelerator cohort patterns, and the six category definitions (top VC bet, promising but needs pivot, solid small business, weak idea, agency disguised as startup, feature not company).

---

## Section 1: Score Normalization

### Prompt 1.1

> Agents 3-6 produced scores across different dimensions using different scales and different standards of evidence. Normalize the following scores into a single comparable framework (1-100 scale): Market Attractiveness (6.0/10), Product Potential as-is (5.0/10), Product Potential with pivot (7.0/10), Founder Score (4.7/10), Composite as-is (5.2/10), Composite with recommendations (6.0/10). For each normalized score, state the confidence level (high, medium, low) based on the quality of underlying evidence. A score based on real user data should have higher confidence than one based on market research alone.

**Reasoning:** Raw scores from different agents aren't directly comparable because they use different evidence bases. Agent 3's market score is grounded in real market data (TAM figures, competitor funding, regulatory facts) — high confidence. Agent 4's product score is partially based on hypothetical pivots (AI access management hasn't been tested) — medium confidence. Agent 5's founder score is based on what the founder wrote in course materials — medium-low confidence because the materials may not reflect the founder's full capabilities. Normalizing with confidence levels makes the ranking framework honest about what it knows vs. what it's guessing.

### Prompt 1.2

> Create a weighted scoring model that an accelerator investment committee would use to evaluate pre-seed startups. Define the weights for: (a) market size and timing, (b) product differentiation and defensibility, (c) founder capability and team, (d) traction and evidence of demand, (e) business model viability. Justify the weights — which dimensions matter most at pre-seed stage, and why? Apply these weights to the project's scores.

**Reasoning:** Pre-seed evaluation is fundamentally different from Series A or later. At pre-seed, there's typically no revenue, minimal traction, and an unproven product. Investors weight dimensions differently: team/founder usually carries the most weight (40-50%) because at pre-seed, the team IS the company — everything else can change. Market matters (20-30%) because even a great team can't fix a bad market. Product matters less (15-20%) because it will iterate. Traction matters least (5-10%) because most pre-seed companies have very little. But the specific weights depend on the accelerator's thesis. Agent 7 needs to define weights and apply them.

### Prompt 1.3

> The project has two versions: the as-is version (current product + current plan) and the recommended version (AI access management pivot + narrowed wedge + co-founder + validation-first approach). Score both versions independently. What is the delta between as-is and recommended? Is the delta realistic — meaning, is the founder likely to actually make the recommended changes — or is the recommended version an idealized scenario that masks a weaker reality?

**Reasoning:** Every accelerator project has a "floor" (what it is today) and a "ceiling" (what it could be with perfect execution). The delta between them matters because it reflects both the upside potential AND the execution risk. A project with a large delta (current: 4/10, potential: 8/10) could be exciting or delusional depending on how realistic the improvements are. Agent 6 recommended specific changes (sharpen product, find co-founder, validate demand). Agent 7 needs to assess whether those changes are realistically achievable by THIS founder in the timeframe available — not just whether they'd be good if they happened.

---

## Section 2: Benchmark Comparison

### Prompt 2.1

> Construct five benchmark archetypes representing the range of pre-seed EdTech startups an accelerator typically sees. For each archetype, define: the team composition, the product stage, the traction level, the market positioning, and the typical outcome (funded, pivoted, died, became lifestyle business). Then place this project among the archetypes. Which archetype does it most closely resemble?

**Reasoning:** Without a real cohort to compare against, Agent 7 needs to construct the comparison frame. The five archetypes should span the full distribution: (1) the breakout — strong team, hot market, early traction; (2) the promising — good concept, needs refinement, some evidence; (3) the struggling — real problem but execution gaps; (4) the hobby project — solo founder, part-time, unclear ambition; (5) the zombie — no traction, no pivot, won't die but won't grow. This project has elements of multiple archetypes — Agent 7 needs to be honest about which one it matches most closely.

### Prompt 2.2

> Compare this project's metrics to pre-seed EdTech benchmarks. Use the following comparators: (a) team size and composition vs. typical pre-seed EdTech teams, (b) traction at this stage vs. what pre-seed investors expect, (c) market timing vs. historical EdTech waves (COVID-era boom, AI-era), (d) technical progress vs. comparable products at similar stage, (e) clarity of go-to-market vs. typical pre-seed pitch quality. For each comparator, rate this project as: above average, average, or below average.

**Reasoning:** Pre-seed investors see hundreds of startups per year and develop pattern recognition. They know what "average" looks like at pre-seed — how many users, how much revenue, how clear the pitch. Agent 7 applies that pattern recognition. The COVID-era comparison is relevant because EdTech saw massive investment in 2020-2021, then a crash in 2022-2024 — the current environment (2025-2026) is a different market with tighter standards and fewer checks. What was fundable in 2021 may not be fundable today.

### Prompt 2.3

> If this project were in a batch of 10 typical accelerator startups, where would it rank? Construct a hypothetical cohort of 10 EdTech pre-seed startups with varying strengths and weaknesses. Place this project in the ranking. Is it top quartile, middle of the pack, or bottom quartile? Be candid.

**Reasoning:** Accelerators accept 10-20 projects per batch and typically invest follow-on capital in 2-4 of them. The question isn't "is this a good idea?" — it's "is this in the top 20-30% of ideas we see?" This prompt forces Agent 7 to construct a realistic cohort and rank honestly. The hypothetical projects should reflect real EdTech startup patterns: the AI tutor play, the LMS feature, the teacher tool, the assessment platform, the credentialing startup, etc.

---

## Section 3: Category Classification

### Prompt 3.1

> Classify this project into one of six categories. For each category, explain why the project does or does not fit. Then select the single best-fit category.

> Categories:
> 1. **Top VC Bet** — Large market, differentiated product, strong team, clear path to $100M+ revenue. The kind of startup top-tier VCs would compete to fund.
> 2. **Promising but Needs Pivot** — Real insight, real market, but current execution or positioning won't get there. Needs a specific change to unlock potential.
> 3. **Solid Small Business** — Viable product, real customers, but market or ambition ceiling limits venture-scale outcomes. Could be a great $1-5M ARR business.
> 4. **Weak Idea** — Fundamental problems with the market thesis, product concept, or team. Unlikely to work regardless of execution.
> 5. **Agency Disguised as Startup** — What looks like a product is actually a service or consulting business. Revenue comes from custom work, not scalable software.
> 6. **Feature, Not a Company** — The product is a single feature that belongs inside a larger platform. Will either be copied by an incumbent or acquired for parts.

**Reasoning:** This is Agent 7's most important classification. It determines the honest assessment of what this project IS — not what it aspires to be. The category has direct implications for next steps: a "Top VC Bet" should raise aggressively, a "Promising but Needs Pivot" should experiment, a "Solid Small Business" should bootstrap, a "Feature Not Company" should either find the company underneath or consider selling to an acquirer. The founder's materials suggest venture-scale ambition, but does the evidence support venture-scale categorization?

### Prompt 3.2

> Agent 4 explicitly flagged the risk that this product is "a feature, not a company" — the kiosk mode / content filtering functionality is a feature that GoGuardian, Securly, or Apple could add in a single product update. Agent 6 identified a potential escape from "feature" status through the AI access management platform and community trust moat. Evaluate: is the "feature not company" risk resolved by the recommended pivot, or does it persist even with the changes? What would definitively move this project from "feature" to "company"?

**Reasoning:** The "feature, not a company" risk is the existential question for this project. A kiosk browser with content filtering IS a feature — GoGuardian already has it as one of many features. The pivot to AI access management adds differentiation, but is "AI tool whitelist/blacklist" also just a feature that platforms will copy? The community trust moat is the strongest counter-argument, but it's hypothetical — no community exists yet. Agent 7 needs to assess whether the escape plan is credible or whether the project is fundamentally a feature regardless of how it's positioned.

### Prompt 3.3

> The project currently sits between "Promising but Needs Pivot" and "Solid Small Business." What would need to be true in 6 months for it to move UP to "Top VC Bet"? And what would confirm that it's actually a "Solid Small Business" with no venture path? Define specific, falsifiable criteria for each upgrade/downgrade.

**Reasoning:** Categories aren't permanent — they're assessments at a point in time. A "Promising but Needs Pivot" project that executes the pivot brilliantly can become a "Top VC Bet." A "Solid Small Business" that discovers a viral growth mechanism can break out. Conversely, a "Promising" project that fails to pivot in time slides to "Weak" or "Feature." This prompt asks Agent 7 to define the criteria for movement between categories — giving the founder clear, measurable gates to aim for.

---

## Section 4: Shortlist Decision

### Prompt 4.1

> As an accelerator investment committee, you must make a binary decision: does this project make the shortlist for follow-on funding, or does it not? The shortlist typically includes the top 20-30% of the batch. The decision must be based on: (a) current state, (b) trajectory — is progress accelerating or stalling, (c) founder coachability — will they actually implement feedback, (d) risk-adjusted upside — does the best case justify the investment given the risks? Make the call and explain the reasoning.

**Reasoning:** This is the practical output of Agent 7 — a yes/no shortlist decision. Accelerators must allocate scarce follow-on capital. The decision isn't "is this a good project?" — it's "is this a better use of capital than the alternatives?" The four criteria reflect real investment committee thinking: current state shows where you are, trajectory shows direction, coachability determines whether advice will be taken, and risk-adjusted upside determines whether the payoff is worth the bet.

### Prompt 4.2

> If this project is NOT shortlisted for follow-on funding, what is the recommended next path? Options include: (a) continue in accelerator without funding but with mentorship, (b) bootstrap with clear milestones, (c) seek non-dilutive funding (grants, competitions), (d) find a co-founder and reapply, (e) join an existing EdTech company to learn the market before re-starting. Recommend one and explain why.

**Reasoning:** "Not shortlisted" doesn't mean "give up." It means "not ready yet." The recommended path should be constructive and specific — not "keep going" but "here's exactly what to do before the next funding opportunity." The options range from continued acceleration to strategic retreat (joining an existing company to learn the market). For a solo part-time founder with low domain expertise and low distribution capability, some of these paths may be more productive than continuing to grind alone.

---

## Section 5: Cohort Overview

### Prompt 5.1

> Write a 300-word "Cohort Overview" memo as if this project were one of 10 in an accelerator batch. Summarize the project in the context of broader EdTech trends: AI in education, student digital wellness, regulatory shifts, and the post-COVID EdTech funding correction. Position the project within these trends. Is it riding the right wave, or swimming against the current?

**Reasoning:** Investors and accelerator managers think in trends, not individual projects. They ask: "Does this project fit the macro thesis?" The current EdTech macro is: (1) AI is reshaping education, (2) regulators are cracking down on children's tech, (3) parents are spending more on digital wellness, (4) VC funding is at a 10-year low (selectivity is very high). This project sits at the intersection of trends 1-3 (positive) while entering a hostile funding environment (negative). The cohort overview contextualizes the project within these forces.

### Prompt 5.2

> Produce the final ranking output for this project in a standardized format that could be compared across any accelerator batch. Include: (a) Project name and one-line description, (b) Category classification, (c) Normalized composite score, (d) Key strength (one line), (e) Key risk (one line), (f) Shortlist decision (yes/no), (g) Recommended next action, (h) 6-month check-in criteria — what should be true at the next review.

**Reasoning:** This is Agent 7's primary deliverable — a standardized ranking card. It should be compact enough to fit on one page alongside 9 other project cards. The format is designed for comparison: an investment committee scanning 10 cards should be able to quickly identify the top projects, the borderline cases, and the ones that need more time. The 6-month check-in criteria are critical — they transform a one-time evaluation into a longitudinal tracking system.
