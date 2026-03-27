# Agent 7 — Ranking Committee Agent: Full Output

**Subject:** Kiosk-mode focus browser for K-12 students
**Date:** March 27, 2026
**Stage:** Pre-seed (pre-revenue, pre-traction)
**Accelerator context:** AltaLab batch participant

---

## 1. Score Normalization

### 1.1 Raw Scores and Confidence Levels

| Dimension | Raw Score (1-10) | Normalized (1-100) | Confidence | Evidence Basis |
|-----------|-----------------|--------------------|-----------:|----------------|
| Market Attractiveness (Agent 3) | 6.0 | 60 | **HIGH** | Grounded in real market data: TAM figures, competitor funding rounds, regulatory facts (41 state laws, COPPA deadline), industry reports |
| Product Potential — as-is (Agent 4) | 5.0 | 50 | **MEDIUM** | Based on product description + competitive analysis. No user testing data, no engagement metrics. |
| Product Potential — with pivot (Agent 4) | 7.0 | 70 | **LOW-MEDIUM** | Hypothetical — the AI access management pivot hasn't been built or tested. Score reflects potential, not reality. |
| Founder Score (Agent 5) | 4.7 | 47 | **MEDIUM-LOW** | Based on self-reported course materials. May not capture the founder's full capabilities, network depth, or technical skill. No external validation. |
| Composite — as-is (Agent 6) | 5.2 | 52 | **MEDIUM** | Weighted average of above. |
| Composite — with recommendations (Agent 6) | 6.0 | 60 | **LOW-MEDIUM** | Requires the founder to: find a co-founder, pivot the product, validate demand, narrow the wedge. Each step has its own probability of execution. |

**Key observation:** The two highest-confidence scores are the market (60, HIGH confidence) and the current product (50, MEDIUM confidence). The two scores that lift the project most — product-with-pivot (70) and composite-with-recommendations (60) — have the lowest confidence because they depend on changes that haven't happened yet. The ranking committee should weight the HIGH-confidence scores more heavily than the aspirational ones.

### 1.2 Weighted Scoring Model for Pre-Seed

Pre-seed evaluation weights differ from later stages because nearly everything is unproven. The team matters most because the team is the only thing that's real — everything else (product, market capture, revenue) is a bet on the team's ability to figure it out.

| Dimension | Weight | Rationale |
|-----------|--------|-----------|
| **(a) Founder / Team** | **35%** | At pre-seed, the team IS the company. Products pivot, markets shift — can the team adapt? Solo + part-time is the biggest risk factor. |
| **(b) Market Size & Timing** | **25%** | Does a real, growing market exist? Is the timing right? A great team in a dead market still loses. |
| **(c) Product Differentiation** | **20%** | Is the product idea differentiated enough to matter? At pre-seed this is about concept strength, not build quality. |
| **(d) Evidence of Demand** | **15%** | Any signal that real humans want this? Pre-seed has very little, but even a waitlist or LOIs matter. |
| **(e) Business Model Viability** | **5%** | Can this eventually make money? At pre-seed, this is about "is the model plausible?" not "are the unit economics proven?" |

**Applied to this project:**

| Dimension | Weight | Score (as-is) | Weighted | Score (with pivot) | Weighted |
|-----------|--------|---------------|----------|-------------------|----------|
| Founder / Team | 35% | 4.7 | 1.65 | 5.5* | 1.93 |
| Market Size & Timing | 25% | 6.0 | 1.50 | 6.0 | 1.50 |
| Product Differentiation | 20% | 5.0 | 1.00 | 7.0 | 1.40 |
| Evidence of Demand | 15% | 2.0** | 0.30 | 2.0 | 0.30 |
| Business Model Viability | 5% | 6.0 | 0.30 | 6.0 | 0.30 |
| **Weighted Total** | 100% | | **4.75** | | **5.43** |

*\*Assumes co-founder found, which upgrades founder score modestly.*
*\*\*Evidence of demand is the weakest dimension — "polite interest" from interviews rates 2/10. No waitlist, no signups, no payment intent, no LOIs.*

**Pre-seed investability threshold: ~6.0-6.5 weighted.**

This project scores **4.75 as-is** and **5.43 with recommended changes** — both below the threshold. The demand evidence gap (2.0/10) is the single biggest drag. Even with a great market and a sharpened product, the absence of any quantitative demand signal keeps the overall score below investable levels.

### 1.3 Score Profile Pattern

**Pattern: Spiky — strong market, weak founder metrics, near-zero demand evidence.**

```
Market Timing     ██████████████████████████████  6.0  ← Strongest
Product (pivot)   ███████████████████████████████████  7.0  ← Hypothetical
Product (as-is)   █████████████████████████  5.0
Founder           ███████████████████████  4.7
Demand Evidence   ██████████  2.0  ← Critical gap
```

This is the **"right wave, wrong surfboard"** pattern: the founder has identified a real market at the right time, but the product isn't sharp enough and there's no evidence anyone wants it yet. The intervention is clear — sharpen the product and run a demand test BEFORE building more. This is one of the most fixable patterns in an accelerator batch because the market tailwind does much of the work if the founder can catch it.

---

## 2. Benchmark Comparison

### 2.1 Five Pre-Seed EdTech Archetypes

Based on accelerator cohort patterns (Emerge Education selects 6-10 companies from 500+ applicants across 44+ countries; typical accelerators accept 1-3% of applicants):

| Archetype | Team | Product Stage | Traction | Market | Typical Outcome |
|-----------|------|-------------|----------|--------|----------------|
| **1. The Breakout** | 2-3 founders, complementary skills (technical + domain), at least one full-time | Working product, early users | 100+ users, some revenue or strong LOIs, 3x month-over-month growth | Large, timing-aligned | Raises seed within 6 months. Top 10% of batch. |
| **2. The Promising** | 2 founders, some domain connection, at least one half-time committed | MVP or demo, early testing | 20-50 users, qualitative feedback, waitlist building | Growing market, clear niche | Raises pre-seed/seed within 12 months. Top 25%. |
| **3. The Striver** | Solo founder or weak pair, part-time, learning the market | Functional prototype | <20 users, mostly friends/family, verbal interest | Real market, but crowded or complex | 50/50 — either pivots successfully or stalls. Middle of batch. |
| **4. The Hobby Project** | Solo founder, full-time job, building on weekends | Partial build, demo-quality | No real users, no demand testing | May be real, not validated | Usually doesn't raise. Needs to commit or join as employee elsewhere. Bottom 25%. |
| **5. The Zombie** | Any team configuration | Stuck in development, perpetual beta | No traction despite months of work | Unclear or too small | Fades out. Bottom 10%. |

**This project most closely resembles: Archetype 3 — "The Striver."**

Solo founder, part-time, with a functional prototype and verbal interest from a network. The market is real but complex (K-12 with procurement friction, platform risk, regulatory requirements). The founder is learning the market through an accelerator. There's genuine conviction but significant gaps in domain expertise and distribution.

The project is NOT an Archetype 4 ("Hobby Project") because: (a) the founder has enrolled in an accelerator (commitment signal), (b) there's a working demo, (c) there's a relevant network that could be activated, and (d) the market analysis demonstrates real thinking, not wishful thinking. But it's also NOT an Archetype 2 ("Promising") because: (a) there's no co-founder, (b) there are <10 users, (c) there's no quantitative demand evidence, and (d) distribution capability is near-zero.

### 2.2 Dimension-by-Dimension Benchmark

| Comparator | Rating | Evidence |
|-----------|--------|----------|
| **(a) Team size & composition** | **Below Average** | Solo founder with full-time job. Pre-seed EdTech norms: 2 founders, at least one full-time. Emerge Education specifically looks for "complementing team." Solo founders receive 25% lower seed valuations and only 14.7% of priced equity funding. |
| **(b) Traction** | **Well Below Average** | <10 users (friends/family), no waitlist, no revenue, no LOIs. Pre-seed investors increasingly expect "traction with real buyers, not just free users." Less than 20% of pre-seed teams in 2025 had paying customers, down from 31% in 2024 — but even by this lower bar, this project has no paying customers. |
| **(c) Market timing** | **Above Average** | Excellent timing. 41 US states with phone bans, COPPA deadline April 2026, "brain rot" cultural moment, school AI policy chaos. This is among the strongest market timing signals in K-12 EdTech since the COVID-era remote learning boom. |
| **(d) Technical progress** | **Average** | Demo exists (Study Mode button → kiosk mode → filtered search). Functional but not polished. Typical for a solo developer at pre-seed. The "agentic coding" capability is a genuine execution advantage for future development speed. |
| **(e) Go-to-market clarity** | **Below Average** | Primary channel (social media) starts from zero. Campaign plan is a learning plan, not an execution plan. The founder hasn't built presence in target communities. By comparison, stronger pre-seed projects have a clear channel with early evidence of traction (e.g., an educator newsletter with 500 subscribers, a TikTok account with 10K followers, or 3 school pilots in progress). |

### 2.3 Hypothetical Cohort Ranking

To calibrate where this project sits, here is a hypothetical 10-startup EdTech cohort:

| Rank | Project | Composite | Category | Key Strength |
|------|---------|-----------|----------|-------------|
| 1 | **AI Reading Coach** — 2 founders (ex-teacher + ML engineer), 500 student users, 3 school pilots, $2K MRR | 7.8 | Top VC Bet | Strong team + real traction |
| 2 | **Teacher Copilot** — 2 founders, Chrome extension for lesson planning, 200 teacher signups, Product Hunt launch | 7.2 | Top VC Bet | Product-led growth evidence |
| 3 | **Student Mental Health Platform** — 3 founders (incl. psychologist), pilot with 2 districts, FERPA compliant | 6.8 | Promising | Domain expertise + institutional traction |
| 4 | **Gamified Math App** — solo founder (ex-game designer), 1,000 downloads, strong retention but no revenue | 6.3 | Promising, Needs Pivot | User engagement but no monetization path |
| 5 | **Parent Homework Dashboard** — 2 founders, beta with 80 families, $500/mo revenue | 6.1 | Promising, Needs Pivot | Early revenue but small market |
| **6** | **Kiosk Focus Browser (THIS PROJECT)** — solo founder, demo, verbal interest, strong market timing | **5.2** | **Promising, Needs Pivot** | **Market timing + technical capability** |
| 7 | **AI Essay Grader** — solo founder, working product, 30 teacher signups, but GPT wrapper risk | 5.0 | Feature, Not Company | Functional but no moat |
| 8 | **School Communication App** — 2 founders, competing with ClassDojo/Remind, 15 users | 4.5 | Weak Idea | Crowded market, no differentiation |
| 9 | **VR Science Lab** — solo founder, concept only, hardware dependency | 3.8 | Weak Idea | Cool concept, impractical execution |
| 10 | **Freelance Tutoring Marketplace** — solo founder, each tutor is custom-matched, no scalable product | 3.2 | Agency Disguised as Startup | Service business, not software |

**This project ranks 6th out of 10 — lower middle of the pack.** Above the clearly weak ideas and the non-scalable plays, but below the projects with real traction, strong teams, or institutional validation. In a batch where the top 3-4 get follow-on funding, this project is on the bubble — not in, not out, dependent on what happens in the next 90 days.

---

## 3. Category Classification

### 3.1 Classification: Fit Assessment for All Six Categories

| Category | Fit? | Evidence |
|----------|------|----------|
| **Top VC Bet** | ❌ NO | Market is real (6.0) but founder score is too low (4.7), no traction, no co-founder, no revenue. Top VC bets have strong teams AND early evidence. This has neither. |
| **Promising but Needs Pivot** | ✅ **YES — BEST FIT** | Real market insight + genuine technical capability + identified pivot path (AI access management). The current product is undifferentiated (5.0) but the sharpened version (7.0) addresses a real gap. The founder is in an accelerator and demonstrated self-awareness ("NOT READY FOR INVESTORS"). The pivot is specific, testable, and time-bounded. |
| **Solid Small Business** | ⚠️ PARTIAL FIT | If the B2B path fails, this could become a niche B2C tool generating $200-500K ARR. The founder's part-time commitment and low burn rate are compatible with a bootstrapped lifestyle business. But the founder's stated ambition (VC targets, AltaLab participation) and the market opportunity (regulatory tailwind) suggest aiming higher is appropriate. |
| **Weak Idea** | ❌ NO | The idea is not weak. The market is real and growing, the problem is validated by cultural and regulatory forces, and the product concept solves a genuine pain point. The weakness is in execution configuration, not the idea itself. |
| **Agency Disguised as Startup** | ❌ NO | The product is software, not a service. Each customer gets the same product. There's no custom work per client. Clean pass. |
| **Feature, Not a Company** | ⚠️ SIGNIFICANT RISK | This is the second-most-plausible classification. Kiosk mode + content filtering IS a feature that GoGuardian, Apple, or Google could ship. Platform risk is 7/10 (Agent 3). Agent 4 flagged this explicitly. The escape from "feature" status depends entirely on whether the AI access management pivot + community moat materialize. If they don't, this reverts to "feature." |

### **Classification: PROMISING BUT NEEDS PIVOT**

With a secondary risk flag: **Feature, Not a Company** — unless the pivot is executed.

### 3.2 Standard Playbook for "Promising but Needs Pivot"

Projects in this category typically need a focused 90-day sprint to validate the pivot and demonstrate traction. The standard playbook:

1. **Define the pivot clearly** (done — Agent 4/6 identified AI access management + middle-school wedge)
2. **Run a demand validation test** (not done — Agent 6 designed a 14-day no-code experiment)
3. **Narrow the target radically** (not done — founder still targeting "K-12 students" broadly)
4. **Find a co-founder or key hire** (not done — founder acknowledged needing a developer and designer, but the real gap is distribution/sales)
5. **Hit one quantitative milestone** (not done — 50+ waitlist signups or 10+ paying users would change the story)
6. **Return to the ranking committee with evidence** (the 90-day review)

**What would promote this to "Top VC Bet":**

| Condition | Current State | Required State |
|-----------|--------------|---------------|
| Team | Solo, part-time | 2+ founders, at least one full-time |
| Traction | ~5 friends/family users | 200+ active users, 50+ paying |
| Revenue | $0 | $500+ MRR (even small) |
| Demand evidence | Verbal interest | 100+ waitlist, 10%+ conversion rate, payment intent |
| Differentiation | Generic kiosk browser | AI access management with community-curated policies |
| Institutional signal | None | 1+ school pilot or LOI |

### 3.3 Misclassification Risk and Movement Criteria

**Could this actually be "Feature, Not a Company"?**

Yes — this is the most likely misclassification. If any of the following happen within 6 months, the project should be reclassified:

- Google ships a "Study Mode" or "AI Management" feature for Chromebooks
- Apple enhances Screen Time with AI tool-specific controls
- GoGuardian adds an "AI access management" module (they have the distribution to make it standard overnight)
- The demand validation returns <20 signups and <5% conversion

**What would confirm "Promising" (or upgrade to "Top VC Bet"):**

- 50+ waitlist signups in the first 14-day test (confirms demand)
- 200+ active users within 6 months (confirms retention)
- Co-founder joins with education/distribution background (confirms team)
- One school expresses formal interest in piloting (confirms institutional path)
- No major platform ships the feature natively in the next 6 months (confirms window remains open)

**Falsifiable 6-month test:** If by September 2026 the project has <100 users, no co-founder, and no school pilot, reclassify as "Solid Small Business" (if revenue exists) or "Feature, Not a Company" (if no revenue). If it has 200+ users, a co-founder, and one school pilot, upgrade to "Top VC Bet."

---

## 4. Shortlist Decision

### 4.1 Decision: **CONDITIONAL — Not Yet, But Reviewable in 90 Days**

In a batch of 10, the top 3-4 get shortlisted for follow-on. This project currently ranks 6th — below the shortlist line. However, the gap is closable, and the market timing creates urgency to give the project a fair runway.

**Three strongest arguments FOR shortlisting:**

1. **Market timing is exceptional and perishable.** 41 US states with device bans, COPPA deadline imminent, "brain rot" in mainstream vocabulary, school AI policy chaos. This is a window that won't stay open indefinitely. The product sits squarely in the path of a structural shift. Few other batch projects may have this level of macro tailwind.

2. **The pivot path is specific and testable.** Agent 6 designed a 14-day, $19 validation experiment. The AI access management angle is genuinely differentiated — no existing product manages student AI tool access at the granular level proposed. If the demand test works, this jumps from "interesting" to "investable" quickly.

3. **The founder is self-aware and coachable.** "NOT READY FOR INVESTORS" three times. Acknowledging "covering too much at the same time." Enrolling in an accelerator. These are signals of a founder who will implement feedback — a critical predictor of accelerator ROI. Accelerated startups raise $1.8M more on average in their first year post-graduation, and the effect is strongest for founders who are receptive to course correction.

**Three strongest arguments AGAINST shortlisting:**

1. **No demand evidence whatsoever.** Every other dimension is theoretical until someone signs up and pays. The user evidence is 2/10 — "polite interest" from a small network. Emerge Education explicitly requires "evidence of initial users/customers." This project has neither. In 2025, less than 20% of pre-seed teams had paying customers, but even by that low bar, this project has none.

2. **Solo founder with a full-time job.** Accelerator investment is a bet on execution speed. A solo part-time founder is the lowest-bandwidth configuration possible. The recommended next steps (demand validation, community building, co-founder recruiting, COPPA compliance) all compete for the same 15-20 hours/week. Something will be deprioritized. Historically, solo EdTech founders face the steepest odds — long sales cycles, regulatory complexity, and multiple stakeholder management require a team.

3. **The "feature, not a company" risk is unresolved.** The product's core value (content filtering + kiosk mode) is a feature set that any platform could ship. The escape plan (AI access management + community moat) is conceptually strong but entirely unbuilt. If Google announces an AI management feature for Classroom at their next education event, the competitive window snaps shut.

**Decision: NOT SHORTLISTED — conditionally reviewable at 90-day checkpoint (late June 2026).**

### 4.2 Recommended Path (Since Not Shortlisted)

**Recommendation: (B) Bootstrap with clear milestones + (D) Find a co-founder.**

Not "(A) continue in accelerator without funding" because the founder needs accountability structures beyond the accelerator. Not "(C) seek grants" because grant cycles are slow and the market window is now. Not "(E) join an existing EdTech company" because the timing window and the founder's conviction argue against a strategic retreat.

**Specific 90-day path:**

| Period | Action | Success Criterion |
|--------|--------|-------------------|
| **Days 1-14** | Run the demand validation experiment: landing page + Reddit posts + network outreach. $19 investment. | 50+ waitlist signups at 10%+ conversion |
| **Days 15-30** | Customer discovery calls with 10 waitlist signees. Publish "AI Tool Report Card for Students" as content marketing. | 3+ parents express payment intent. Report card gets 500+ views. |
| **Days 30-60** | Begin co-founder search through AltaLab network, educator contacts, EdTech communities. Start COPPA compliance review. | 3+ co-founder conversations with qualified candidates. COPPA requirements documented. |
| **Days 60-90** | Build MVP (if demand confirmed): AI tool whitelist/blacklist + locked study session + parent report. Ship to first 10 paying users. | 10+ paying users at $5-7/month. Co-founder identified or committed. |

**90-day review criteria for re-evaluation:**

| Metric | Threshold to Re-Shortlist |
|--------|--------------------------|
| Active users | 50+ (at least 10 paying) |
| Revenue | $50+ MRR (even tiny signal matters) |
| Co-founder | Identified and committed (or near-committed) |
| Waitlist / demand evidence | 100+ signups with measured conversion rate |
| COPPA status | Compliance plan documented, implementation started |

If these thresholds are met at the 90-day review, upgrade the classification to **"Top VC Bet candidate"** and shortlist for follow-on funding. If not, reclassify based on what DID happen and recommend the appropriate path.

### 4.3 If Shortlisted (Conditional Scenario)

If the ranking committee decides to shortlist this project despite the gaps (e.g., due to portfolio diversity needs or conviction about market timing), the conditions would be:

**Confidence: LOW**

**Conditions to maintain shortlist position:**

| Milestone | Deadline | Consequence if Missed |
|-----------|----------|----------------------|
| 50+ waitlist signups | April 15, 2026 (2 weeks) | Remove from shortlist |
| Co-founder identified | June 1, 2026 | Flag for review |
| 10+ paying users | June 30, 2026 | Remove from shortlist if <5 users |
| COPPA compliance plan | May 1, 2026 | Block any funding disbursement |

---

## 5. Cohort Overview

### 5.1 Cohort Context Memo

**To:** AltaLab Investment Committee
**From:** Agent 7 — Ranking Committee
**Re:** Batch Assessment — Kiosk Focus Browser for K-12 Students (Single-Project Evaluation)

This project enters the evaluation at an unusual moment for EdTech. Venture funding in the sector hit $1 billion in 2024 — down 95% from the $20.8B peak in 2021. Q1 2025 saw the lowest EdTech funding in over a decade. European EdTech funding dropped to $0.8B in 2024. The bar for pre-seed investment has risen sharply: investors now demand "traction with real buyers, not just free users," and the days of funding ideas alone are over.

Against this backdrop, this project has one exceptional asset: market timing. The regulatory, cultural, and institutional forces behind student digital wellness are the strongest they've been since the COVID-era remote learning wave. But unlike COVID (which created temporary demand), the current wave — phone bans, AI governance, privacy enforcement — is structural and deepening. This is the kind of market tailwind that creates lasting companies if founders can catch it.

The project's weaknesses — solo founder, no traction, undifferentiated product, low domain expertise — are common in pre-seed EdTech batches and are addressable within an accelerator program. The critical question is whether the founder can compress enough execution into the next 90 days to validate demand and recruit a co-founder before the market timing advantage is absorbed by incumbents or better-resourced entrants. The recommended pivot (AI access management for students) is differentiated and timely, but it remains hypothetical until tested.

Classification: **Promising but Needs Pivot**, with elevated **Feature, Not a Company** risk. Not shortlisted for immediate follow-on, but conditionally reviewable at 90-day checkpoint with specific, measurable criteria.

### 5.2 Final Ranking Card

---

```
┌─────────────────────────────────────────────────────────────────┐
│  AGENT 7 — PROJECT RANKING CARD                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Project:    Kiosk Focus Browser for K-12 Students               │
│  One-liner:  Homework browser that manages student AI access     │
│              and blocks distractions, with parent reporting.      │
│                                                                  │
│  Category:   PROMISING BUT NEEDS PIVOT                           │
│  Risk flag:  Feature, Not a Company (unless pivot executes)      │
│                                                                  │
│  ┌─────────────────────────────────────────────────────┐        │
│  │  SCORES (weighted pre-seed model)                    │        │
│  │                                                      │        │
│  │  Market & Timing:         6.0 / 10   ████████████   │        │
│  │  Product (as-is):         5.0 / 10   ██████████     │        │
│  │  Product (with pivot):    7.0 / 10   ██████████████ │        │
│  │  Founder / Team:          4.7 / 10   █████████      │        │
│  │  Demand Evidence:         2.0 / 10   ████           │        │
│  │  ─────────────────────────────────────────────────  │        │
│  │  Weighted Composite:      4.75 (as-is)               │        │
│  │                           5.43 (with pivot)          │        │
│  │  Investability threshold: ~6.0-6.5                   │        │
│  └─────────────────────────────────────────────────────┘        │
│                                                                  │
│  Batch Rank:  6 of 10 (hypothetical cohort)                      │
│  Archetype:   "The Striver" — right wave, needs better surfboard │
│                                                                  │
│  Key Strength:   Exceptional market timing — 41 state phone      │
│                  bans, COPPA deadline, AI policy chaos in         │
│                  schools. Product sits in the path of a           │
│                  structural shift in student tech governance.     │
│                                                                  │
│  Key Risk:       No demand evidence + solo part-time founder     │
│                  + platform can ship competing feature anytime.   │
│                  Distribution capability is 3/10.                 │
│                                                                  │
│  Shortlist:  NOT SHORTLISTED                                     │
│              Conditionally reviewable at 90-day checkpoint.       │
│                                                                  │
│  Recommended Action:                                             │
│    1. Run 14-day demand validation ($19 landing page)            │
│    2. Find a co-founder with distribution/education background   │
│    3. If demand confirmed: build MVP with AI access management   │
│       as the killer feature, target parents of 11-14 yr olds     │
│                                                                  │
│  6-Month Check-In Criteria (September 2026):                     │
│    □ 200+ active users (50+ paying)                              │
│    □ Co-founder recruited                                        │
│    □ 1+ school pilot or LOI                                      │
│    □ COPPA compliant                                             │
│    □ No major platform shipped competing feature                 │
│    If met → Upgrade to "Top VC Bet candidate"                    │
│    If not → Reclassify as "Solid Small Business" or "Feature"    │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│  BATCH COMPARISON (hypothetical 10-project cohort)               │
├──────┬───────────────────────┬───────┬──────────────────────────┤
│ Rank │ Project               │ Score │ Category                 │
├──────┼───────────────────────┼───────┼──────────────────────────┤
│  1   │ AI Reading Coach      │  7.8  │ Top VC Bet               │
│  2   │ Teacher Copilot       │  7.2  │ Top VC Bet               │
│  3   │ Student Mental Health  │  6.8  │ Promising                │
│  4   │ Gamified Math App     │  6.3  │ Promising, Needs Pivot   │
│  5   │ Parent Homework Dash  │  6.1  │ Promising, Needs Pivot   │
│ *6*  │ *Kiosk Focus Browser* │ *5.2* │ *Promising, Needs Pivot* │
│  7   │ AI Essay Grader       │  5.0  │ Feature, Not Company     │
│  8   │ School Comms App      │  4.5  │ Weak Idea                │
│  9   │ VR Science Lab        │  3.8  │ Weak Idea                │
│ 10   │ Tutoring Marketplace  │  3.2  │ Agency as Startup        │
└──────┴───────────────────────┴───────┴──────────────────────────┘
│                                                                  │
│  Shortlist line: Top 3-4 (scores ≥ 6.5)                         │
│  This project: below the line, but closest viable candidate      │
│  for promotion if 90-day milestones are met.                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Appendix: All Agent Scores Summary

| Agent | Dimension | Score | Confidence | Key Finding |
|-------|-----------|-------|------------|-------------|
| 3 | Market Attractiveness | 6.0/10 | HIGH | Real market, strong timing, high platform risk |
| 3 | Market Crowdedness | 6.5/10 | HIGH | Red ocean institutionally; niche gap in B2C |
| 4 | Product (as-is) | 5.0/10 | MEDIUM | Utility feature, not killer feature |
| 4 | Product (with pivot) | 7.0/10 | LOW-MED | AI access management is differentiated but unbuilt |
| 4 | Killer Feature | 4/10→7/10 | LOW-MED | Current: generic. With AI gatekeeper: strong |
| 4 | Wedge Clarity | 3/10→7/10 | MEDIUM | "K-12" too broad. "Parents of 11-14, home" is sharp |
| 4 | Moat Potential | 4/10→6/10 | LOW | No moat today. Brand/community is best hypothesis |
| 5 | Founder-Market Fit | 5/10 | MED-LOW | Adjacent via network, not embedded |
| 5 | Domain Expertise | 3/10 | MEDIUM | Surface-level; COPPA gap is critical |
| 5 | Execution Ability | 5/10 | MEDIUM | Structured but solo + part-time |
| 5 | Technical Depth | 6/10 | MED-LOW | Strongest founder dimension; type unknown |
| 5 | Distribution Ability | 3/10 | MEDIUM | Primary channel starts from zero |
| 5 | Clarity of Ambition | 6/10 | MEDIUM | Mission-driven, venture-aspiring, lifestyle-paced |
| 5 | **Overall Founder** | **4.7/10** | MED-LOW | Capable but under-configured |
| 6 | Composite (as-is) | 5.2/10 | MEDIUM | Below pre-seed threshold |
| 6 | Composite (with recs) | 6.0/10 | LOW-MED | Approaching threshold; needs execution |
| 7 | Weighted Composite (as-is) | 4.75/10 | MEDIUM | Demand evidence gap drags score |
| 7 | Weighted Composite (pivot) | 5.43/10 | LOW-MED | Still below 6.0-6.5 investability line |
| 7 | **Classification** | **Promising, Needs Pivot** | MEDIUM | With Feature-Not-Company risk flag |
| 7 | **Shortlist** | **NOT SHORTLISTED** | — | Conditionally reviewable at 90 days |
