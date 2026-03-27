# Practical Architecture of Agent Workflows for Batch Processing & Prompt Set

Below is a **practical architecture of agent workflows** for batch processing and a **set of prompts** designed so they can be quickly adapted to Taskade, OpenAI Agents, n8n + OpenAI, or the Assistants API.

I would build this not as a single bot, but as a **system of 5–7 agents**, because then:

- It's easier to debug
- It's easier to change criteria
- You can compare the quality of different blocks
- You can separately improve screening, market analysis, competition, and ranking

## 1. General Workflow Logic

### System Goal

**Input:** Structured projects from school graduates.

**Output:**

- A clear project card
- Assessment across key parameters
- Verdict
- Recommendations for pivot / focus
- Overall ranking among other projects
- Shortlist for manual review

## 2. Recommended Agent Architecture

### Agent 1 — Intake Parser

**Role:** Accepts a raw structured pitch and converts it into a normalized project card.

**What it does:**

- Collects all fields into a unified format
- Removes duplicates
- Extracts:
  - Problem
  - Solution
  - ICP
  - Market
  - Business model
  - Competition
  - Team
  - Traction
  - Why now
  - Vision
- Flags missing fields
- Creates a standardized startup brief

**Result:** Project Brief JSON / structured card.

### Agent 2 — Venture Screener

**Role:** Performs initial investment screening.

**What it does:**

- Evaluates problem quality
- Market size
- Presence of real pain
- Differentiator
- Feature vs company
- Wrapper risk
- VC potential
- Founder clarity

**Result:**

- Score
- SWOT
- Verdict
- Continue / pivot / reject

### Agent 3 — Market & Competition Analyst

**Role:** Builds a competitive picture and market view.

**What it does:**

- Identifies the market
- Roughly estimates TAM/SAM/SOM
- Determines red ocean / blue ocean
- Identifies direct and indirect competitors
- Assesses AI / Big Tech risk
- Shows whether the space is crowded

**Result:**

- Market note
- Competition map
- Market attractiveness score

### Agent 4 — Product & Positioning Analyst

**Role:** Understands whether the product has a chance to become big.

**What it does:**

- Looks for a killer feature
- Identifies the wedge
- Understands where the moat is
- Suggests positioning
- Determines whether the idea is just a "generic AI wrapper"

**Result:**

- Positioning statement
- Moat hypothesis
- Product risks
- Focus recommendation

### Agent 5 — Founder Fit Analyst

**Role:** Assesses how well the team fits the task.

**What it does:**

- Evaluates founder-market fit
- Domain expertise
- Execution ability
- Technical depth
- Distribution ability
- Clarity of ambition

**Result:**

- Founder score
- Risks
- Strengths
- Missing capabilities

### Agent 6 — Recommendation / Pivot Agent

**Role:** Doesn't just criticize — proposes the next best move.

**What it does:**

- If the idea is strong — explains how to sharpen it
- If the idea is weak — suggests a pivot
- If the idea is small — explains how to turn it into a wedge for a larger market
- If it's an agent wrapper — looks for a deeper system layer

**Result:**

- Next step recommendation
- Pivot options
- Focus area

### Agent 7 — Ranking Committee Agent

**Role:** Compares projects against each other.

**What it does:**

- Normalizes scores
- Compares all projects in the batch
- Creates a shortlist
- Highlights:
  - Top VC bets
  - Promising but needs pivot
  - Solid small businesses
  - Weak ideas
  - "Agency disguised as startup"
  - "Feature not company"

**Result:**

- Ranking
- Shortlist
- Cohort overview

## 3. Step-by-Step Workflow

**Step 1. Intake**

The founder/team submits:

- Elevator pitch
- Sales pitch
- Problem
- Solution
- ICP
- Market
- Business model
- Competitors
- Team
- Traction
- Why now
- Vision

↓

**Step 2. Intake Parser**

Normalizes data into a unified template.

↓

**Step 3. Venture Screener**

Provides the first assessment and initial verdict.

↓

**Step 4. Market & Competition Analyst**

Checks whether the market and competition are worth attention.

↓

**Step 5. Product & Positioning Analyst**

Checks whether there is real differentiation and a chance for a moat.

↓

**Step 6. Founder Fit Analyst**

Determines whether the team has a chance to pull this off.

↓

**Step 7. Recommendation Agent**

Says what to do next:

- Continue
- Continue with focus
- Pivot
- Reject

↓

**Step 8. Ranking Committee Agent**

Compares with other projects and determines the position in the batch.

## 4. Project Output Statuses

1. **Top VC Candidate**
2. **Promising, Needs Sharper Focus**
3. **Promising, But Needs Pivot**
4. **Good Small Business, Not Venture-Scale**
5. **Feature, Not a Company**
6. **AI Wrapper With Weak Moat**
7. **Low Attractiveness / Reject**

## 5. Standard Scoring Model

To ensure all agents speak the same language, it's best to define a common scale from the start.

### Main Parameters

- Problem Severity — 1–10
- Market Size — 1–10
- Founder-Market Fit — 1–10
- Product Differentiation — 1–10
- Moat Potential — 1–10
- Competition Attractiveness — 1–10
- Business Model Scalability — 1–10
- Venture Outcome Potential — 1–10

### Additional Red Flags

- Generic AI wrapper
- Feature not company
- Market too small
- Crowded market with no wedge
- Weak founder insight
- No pain / only convenience
- No clear buyer
- No clear GTM
- Agency disguised as startup

### Interpretation

- 64–80: Top tier
- 52–63: Strong
- 40–51: Medium / needs work
- 28–39: Weak
- <28: Reject

## 6. Prompt Set

In near-ready form.

### PROMPT 1 — Intake Parser Agent

You are an Intake Parser for a venture school.

Your task is to convert raw startup submissions into a clean, standardized investment brief.

You will receive a startup submission that may contain:

- elevator pitch
- sales pitch
- problem
- solution
- target customer
- market
- competitors
- business model
- team
- traction
- why now
- vision

Instructions:

1. Extract the key information.
2. Remove repetition and marketing fluff.
3. Rewrite the startup into a concise and structured startup brief.
4. Do not judge yet unless information is logically inconsistent.
5. If information is missing, explicitly mark it as "Missing / Not provided".
6. If information is vague, rewrite it in a more precise form but preserve meaning.
7. Identify obvious inconsistencies or confusion in the pitch.

Return output in the following format:

STARTUP BRIEF

1. Startup Name
2. One-line Description
3. Problem
4. Solution
5. Target Customer / ICP
6. Buyer
7. Market
8. Business Model
9. Competitors / Alternatives
10. Team
11. Traction
12. Why Now
13. Long-term Vision
14. Missing Critical Information
15. Obvious Inconsistencies or Weaknesses in the Submission

Keep it concise, clean, and analytical.

### PROMPT 2 — Venture Screener Agent

You are a Senior Venture Analyst screening very early-stage startups for a founder school and venture pipeline.

Your goal is to determine whether the startup is worth pursuing.

Be direct and analytical. Do not be polite for the sake of politeness.

The goal is to judge whether founders should spend years of their life on this idea.

Evaluate the startup across these criteria:

1. Problem severity
2. Market size
3. Product differentiation
4. Founder insight and clarity
5. Business model potential
6. Venture-scale potential
7. Risk of being just a feature
8. Risk of being just an AI wrapper
9. Clarity of target customer and buyer
10. Potential to become a real company rather than a nice demo

Scoring:

Give each of the following a score from 1 to 10:

- Problem Severity
- Market Size
- Product Differentiation
- Founder Clarity
- Business Model
- Venture Potential
- Moat Potential
- Overall Attractiveness

Then provide:

1. Summary
2. What is strong
3. What is weak
4. Main red flags
5. SWOT
6. Final Verdict

Choose one verdict:

- Top VC Candidate
- Promising, Needs Sharper Focus
- Promising, But Needs Pivot
- Good Small Business, Not Venture-Scale
- Feature, Not a Company
- AI Wrapper With Weak Moat
- Reject

Also answer:

Should the founders continue with this exact idea, refine it, pivot it, or drop it?

Be specific.

### PROMPT 3 — Market & Competition Analyst

You are a Market & Competition Analyst for an early-stage venture pipeline.

Your task is to assess the attractiveness of the market and the competitive landscape.

Instructions:

1. Infer the startup's real market category.
2. Estimate whether the market is small, medium, large, huge, or category-creating.
3. Determine whether the startup is entering:
   - red ocean
   - moderately competitive market
   - emerging space
   - category creation attempt
4. Identify likely direct competitors.
5. Identify indirect competitors and substitutes.
6. Identify incumbent / big tech threats.
7. Assess whether the startup has a credible wedge.
8. Assess whether the market is too crowded unless the startup has exceptional distribution or differentiation.

Return output in this structure:

MARKET ANALYSIS

1. Real Market Category
2. Estimated Market Size
3. Why This Market Matters or Does Not Matter
4. Direct Competitor Types
5. Indirect Competitors / Substitutes
6. Big Tech / Platform Risk
7. Crowdedness Level
8. Wedge Opportunity
9. Market Attractiveness Score (1-10)
10. Competition Difficulty Score (1-10)

Final takeaway:

Is this a good market to enter for a new startup at this stage?

### PROMPT 4 — Product & Positioning Analyst

You are a Product and Positioning Analyst.

Your task is to determine whether this startup has a real product opportunity or just a weak feature idea.

Analyze:

1. What is the startup's core value proposition?
2. What is the killer feature, if any?
3. Is this 10x better or just slightly better?
4. Is this a product, a feature, a service, or an AI wrapper?
5. Where could defensibility come from?
6. What wedge could help them win initially?
7. What should they focus on first?
8. How should they position the company to sound compelling and non-generic?

Return:

PRODUCT & POSITIONING

1. What the product really is
2. Killer feature
3. Why users would care
4. Why they may not care
5. Feature vs Company assessment
6. Wrapper risk
7. Best wedge
8. Moat hypothesis
9. Recommended positioning
10. Focus recommendation for the next 6 months

Be blunt and practical.

### PROMPT 5 — Founder Fit Analyst

You are a Founder Fit Analyst for a venture fund and founder school.

Your task is to assess whether this team appears capable of building this company.

Evaluate:

1. Do founders deeply understand the problem?
2. Do they have authentic founder-market fit?
3. Do they have technical credibility?
4. Do they have distribution credibility?
5. Is there evidence of ambition and strategic clarity?
6. Are there obvious capability gaps?

Return:

FOUNDER FIT ANALYSIS

1. Founder-Market Fit
2. Domain Understanding
3. Technical Ability
4. GTM / Distribution Ability
5. Strategic Maturity
6. Team Risks
7. Missing Roles / Missing Capabilities
8. Founder Fit Score (1-10)
9. Execution Confidence Score (1-10)

Final takeaway:

Does this look like a team that could plausibly build a category-relevant startup?

### PROMPT 6 — Recommendation / Pivot Agent

You are a Startup Recommendation Agent.

Your task is to convert the analysis into practical advice.

Instructions:

If the startup is strong, explain how to sharpen it.

If the startup is weak, explain how to pivot it.

If the startup is too small, explain how it could become part of a bigger market.

If the startup is generic, explain how to make it more opinionated and distinctive.

Return:

RECOMMENDATION

1. Keep / Refine / Pivot / Drop
2. Best next move
3. Most promising customer segment
4. Best wedge
5. What to remove
6. What to emphasize
7. Suggested pivot directions (up to 3)
8. Suggested positioning rewrite
9. 30-day action plan
10. 90-day action plan

Be concrete, not abstract.

### PROMPT 7 — Ranking Committee Agent

You are the Ranking Committee Agent for a founder school startup batch.

You will receive multiple analyzed startups with their scores and verdicts.

Your job is to compare them and produce a cohort ranking.

Instructions:

1. Compare projects relative to each other, not in isolation.
2. Favor startups with:
   - large market potential
   - strong founder insight
   - clear wedge
   - strong differentiation
   - possibility of real moat
   - venture-scale potential
3. Penalize:
   - generic AI wrappers
   - feature-not-company ideas
   - tiny markets
   - unclear buyers
   - weak founder understanding
   - no credible wedge

Return:

COHORT RANKING

1. Top 10 startups
2. Top VC Candidates
3. Promising but need sharper focus
4. Promising but need pivot
5. Good small businesses
6. Weak ideas to reject
7. Themes observed across the cohort
8. Most overcrowded idea patterns
9. Most interesting emerging themes
10. Final recommendation for manual review shortlist

Also assign each startup one label:

- VC-Scale
- Needs Pivot
- Small Business
- Feature
- Wrapper
- Reject

## 7. Master Prompt for a Single Agent Instead of Seven

If you want to build an MVP with a single agent and decompose later, here is a simplified version.

You are a Senior Venture Analyst evaluating early-stage startup ideas from a founder school.

Your task is to assess whether a startup idea is worth pursuing.

You will receive a structured startup submission.

Analyze:

1. Problem
2. Solution
3. ICP / buyer
4. Market size
5. Competition
6. Differentiation
7. Moat potential
8. Founder fit
9. Business model
10. Venture-scale potential

Be direct, realistic, and analytical.

Return:

1. Startup Summary
2. Problem Assessment
3. Market Assessment
4. Competition Assessment
5. Product / Differentiation Assessment
6. Founder Fit Assessment
7. Business Model Assessment
8. SWOT
9. Scores:
   - Problem
   - Market
   - Differentiation
   - Team
   - Business Model
   - Moat
   - Venture Potential
10. Main Risks
11. Main Opportunities
12. Verdict:
    - Top VC Candidate
    - Promising, Needs Sharper Focus
    - Promising, But Needs Pivot
    - Good Small Business, Not Venture-Scale
    - Feature, Not a Company
    - AI Wrapper With Weak Moat
    - Reject
13. Recommendation:
    - Continue
    - Continue with focus
    - Pivot
    - Drop
14. Suggested Pivot / Focus
15. 30-day next steps

## 8. Best Intake Form for Graduates

To make things easier for the agents, I would have everyone submit their project in a single structure:

### Founder Submission Template

1. Project name
2. One-line pitch
3. Elevator pitch
4. What problem are you solving?
5. For whom?
6. Who is the buyer?
7. Why is this problem painful?
8. What existing alternatives do users use today?
9. What is your product?
10. Why is it better than alternatives?
11. Why now?
12. How big can this market become?
13. Who are your main competitors?
14. What is your business model?
15. Why are you the right team?
16. What traction do you have?
17. What is your long-term vision?
18. What could make this a billion-dollar company?
19. What is your unfair advantage?
20. What are your biggest risks?

This will dramatically improve output quality.

## 9. Practical Implementation Recommendations

### MVP Stage

Don't start by building complex multi-agent orchestration.

Build 3 layers:

**Layer 1:** Intake Parser

**Layer 2:** Unified Analyst (combines screener + market + product + founder fit)

**Layer 3:** Ranking Agent

This is already enough for the first batch.

## 10. What to Save in the Database for Each Project

Minimum:

- startup_name
- founder_name
- cohort_batch
- category
- stage
- one_liner
- problem
- solution
- icp
- buyer
- market_estimate
- competitors
- moat_hypothesis
- score_problem
- score_market
- score_product
- score_team
- score_moat
- score_venture
- verdict
- recommendation
- pivot_suggestion
- red_flags
- shortlist_status
- reviewer_notes

## 11. Very Useful Labels

I would add automatic tags:

- vertical_ai
- saas
- consumer
- marketplace
- healthtech
- fintech
- devtools
- legaltech
- education
- infra
- data
- robotics
- b2b
- b2c
- enterprise
- smb
- regulated
- crowded_market
- wrapper_risk
- feature_risk
- strong_founder_fit
- unclear_buyer
- large_market
- small_market
- good_wedge
- no_wedge

Later this will enable very good cohort analytics.

## 12. Key Rule for Agents

I strongly recommend inserting this into almost all analytical prompts:

> Do not reward projects for sounding polished.
>
> Reward depth of insight, strength of problem, market attractiveness, and the possibility of building a real company.
>
> Penalize generic language, vague differentiation, and ideas that sound like a demo rather than a business.

This is super important — otherwise eloquent students will receive inflated scores.

## 13. My Recommendation for the Final System

For your case, I would do it like this:

### Basic Version

- Intake Parser
- Venture Analyst
- Ranking Agent

### Extended Version

- Intake Parser
- Venture Screener
- Market Analyst
- Product Analyst
- Founder Fit Analyst
- Recommendation Agent
- Ranking Committee Agent

## 14. What I Would Add

One more very useful agent:

### Duplicate / Pattern Detector

It will check:

- Whether this is a duplicate of another idea from the batch
- Whether this is yet another "AI copilot for X" without differentiation
- Whether this repeats an overheated template

A prompt for it can also be created.

## 15. Quick Prompt for Duplicate / Pattern Detector

You are a Pattern Detector for a startup cohort.

Your job is to identify whether this startup is:

1. A duplicate of common startup patterns
2. A generic "AI copilot for X" idea
3. A wrapper around existing models without clear differentiation
4. A crowded cohort pattern
5. A genuinely differentiated concept

Return:

- Pattern Type
- Similar Common Startup Pattern
- Is this overused?
- Is this meaningfully different?
- Pattern Risk Score (1-10)
- Final Take

## 16. Final Verdict Logic

It's better for the final verdict to be calculated not by average, but by weighted logic:

- Problem Severity — 20%
- Market Size — 20%
- Differentiation — 15%
- Founder Fit — 15%
- Moat Potential — 10%
- Business Model — 10%
- Venture Potential — 10%

Because for early-stage companies, the main thing is:

**problem + market + insight + wedge**, not a polished deck.

---

# Part II — Applied Implementation

In **ready-to-use, applied form**:

1. **Agent workflow**
2. **Data structure / JSON schema**
3. **Project processing order**
4. **Scoring rules and final verdict**
5. **Minimum set of statuses for your school**

This can be almost directly transferred to Taskade / n8n / OpenAI Agents.

## 1. Agent Workflow

### General Scheme

**Input Form from Founder**
↓
**Agent 1 — Intake Parser**
↓
**Agent 2 — Venture Screener**
↓
**Agent 3 — Market & Competition Analyst**
↓
**Agent 4 — Product / Positioning Analyst**
↓
**Agent 5 — Founder Fit Analyst**
↓
**Agent 6 — Recommendation / Pivot Agent**
↓
**Agent 7 — Ranking Committee Agent**
↓
**Output: Project Card + Score + Verdict + Rank**

### MVP Workflow (Recommended to Launch First)

To avoid over-complicating things, start like this:

**Founder Submission**
↓
**1. Intake Parser**
↓
**2. Unified Venture Analyst** (internally combines screening + market + product + founder fit)
↓
**3. Ranking Agent**
↓
**4. Human Review of Top Projects**

This will already deliver 80% of the value.

## 2. Logic of Each Agent

### Agent 1 — Intake Parser

**Task:** Convert raw pitch into a unified project card.

**Input:**

- project_name
- one-liner
- elevator pitch
- problem
- solution
- target audience
- buyer
- market
- competitors
- business model
- team
- traction
- why now
- vision
- unfair advantage
- biggest risks

**Output:**

- normalized_project_brief
- missing_fields
- inconsistencies
- confidence_of_input_quality

### Agent 2 — Unified Venture Analyst

**Task:** Provide the first substantive assessment of the idea.

**Checks:**

- Real pain or nice-to-have
- Market size
- Venture-scale potential
- Generic wrapper risk
- Feature vs company
- Quality of insight
- Clarity of ICP and buyer
- Moat hypothesis
- Execution plausibility

**Output:**

- Summary
- Score by categories
- SWOT
- Key risks
- Key opportunities
- Preliminary verdict

### Agent 3 — Market & Competition Analyst

**Task:** Understand whether this market is worth the effort at all.

**Checks:**

- Market category
- TAM rough class
- Crowdedness
- Direct competitors
- Indirect substitutes
- Incumbent / platform risk
- Wedge opportunity

**Output:**

- Market attractiveness
- Competition difficulty
- Competitive map
- Market commentary

### Agent 4 — Product / Positioning Analyst

**Task:** Understand whether there's a chance for a product, not just a feature.

**Checks:**

- Killer feature
- Value proposition clarity
- 10x improvement or not
- Wedge
- Defendability
- Positioning clarity
- Why customer switches

**Output:**

- Product type
- Feature/company assessment
- Wrapper risk
- Positioning rewrite
- Moat hypothesis
- 6-month focus

### Agent 5 — Founder Fit Analyst

**Task:** Assess the team.

**Checks:**

- Founder-market fit
- Domain expertise
- Technical strength
- Distribution strength
- Ambition
- Strategic maturity
- Missing capabilities

**Output:**

- founder_fit_score
- execution_confidence
- Team risks
- Key missing roles

### Agent 6 — Recommendation / Pivot Agent

**Task:** Provide a useful next step, not just criticism.

**Produces:**

- Continue / refine / pivot / drop
- Best customer wedge
- What to cut
- What to double down on
- 30-day plan
- 90-day plan
- Pivot directions

### Agent 7 — Ranking Committee Agent

**Task:** Compare all projects in the batch against each other.

**Produces:**

- Rank within cohort
- Cohort label
- Shortlist status
- Top candidates
- Overused patterns
- Strongest themes
- Weakest themes

## 3. Pipeline States

I would use these statuses:

### Intake States

- submitted
- parsing
- parsed
- incomplete_submission
- needs_resubmission

### Analysis States

- screening_in_progress
- analyzed
- needs_manual_review
- waiting_for_more_info

### Final Decision States

- top_vc_candidate
- promising_focus_needed
- promising_pivot_needed
- small_business_not_vc
- feature_not_company
- wrapper_weak_moat
- reject

### Operational States

- shortlisted
- pending_interview
- mentor_review
- accepted_to_next_stage
- rejected_after_review

## 4. Core Data Schema

### Core Project Table

| Field | Type | Description |
|---|---|---|
| project_id | string | unique id |
| batch_id | string | cohort / batch |
| created_at | datetime | date created |
| updated_at | datetime | last updated |
| submission_status | string | current intake status |
| analysis_status | string | current analysis status |
| final_status | string | final verdict |

### Founder / Startup Identity

| Field | Type | Description |
|---|---|---|
| startup_name | string | project name |
| founder_name | string | main founder |
| founder_email | string | contact |
| team_members | array | founders/team list |
| location | string | geography |
| stage | string | idea / MVP / traction |

### Pitch Fields

| Field | Type | Description |
|---|---|---|
| one_liner | text | 1-line description |
| elevator_pitch | text | short pitch |
| sales_pitch | text | longer persuasive pitch |
| problem_statement | text | problem |
| solution_statement | text | solution |
| why_now | text | market timing |
| long_term_vision | text | big vision |
| unfair_advantage_claim | text | claimed edge |
| biggest_risks_declared | text | founder-declared risks |

### Market & Customer Fields

| Field | Type | Description |
|---|---|---|
| target_customer | text | who uses it |
| buyer | text | who pays |
| icp | text | ideal customer profile |
| use_case | text | specific use case |
| market_description | text | market as founder sees it |
| tam_claim | text | founder TAM if any |
| competitors_declared | array | competitors named by founder |
| alternatives_today | array | current substitutes |

### Business Fields

| Field | Type | Description |
|---|---|---|
| business_model | text | SaaS / marketplace / etc |
| pricing_model | text | subscription / transactional |
| distribution_strategy | text | GTM plan |
| traction | text | traction summary |
| metrics | object | revenue/users/etc if any |

## 5. Analysis Output Schema

### Scoring Block

| Field | Type |
|---|---|
| score_problem_severity | number |
| score_market_size | number |
| score_differentiation | number |
| score_founder_clarity | number |
| score_founder_fit | number |
| score_business_model | number |
| score_moat_potential | number |
| score_venture_potential | number |
| score_competition_attractiveness | number |
| score_execution_confidence | number |
| weighted_total_score | number |

### Qualitative Analysis Block

| Field | Type |
|---|---|
| startup_summary | text |
| market_analysis | text |
| competition_analysis | text |
| product_analysis | text |
| founder_fit_analysis | text |
| moat_hypothesis | text |
| key_strengths | array |
| key_weaknesses | array |
| key_risks | array |
| key_opportunities | array |
| swot_strengths | array |
| swot_weaknesses | array |
| swot_opportunities | array |
| swot_threats | array |

### Classification Block

| Field | Type |
|---|---|
| primary_category | string |
| secondary_category | string |
| business_type | string |
| market_type | string |
| pattern_type | string |
| wrapper_risk | string |
| feature_risk | string |
| market_size_class | string |
| verdict | string |
| recommendation | string |
| shortlist_status | string |

## 6. Recommended Labels

### By Sector

- ai_agent
- vertical_ai
- saas
- marketplace
- fintech
- healthtech
- legaltech
- edtech
- devtools
- infra
- robotics
- consumer
- b2b
- b2c
- enterprise
- smb
- data_analytics

### By Investment Pattern

- vc_scale
- small_business
- deeptech_bet
- feature_not_company
- wrapper_risk
- crowded_market
- large_market
- unclear_buyer
- strong_founder_fit
- weak_founder_fit
- good_wedge
- no_wedge
- category_creation_attempt
- agency_disguised_as_startup

## 7. Weighted Scoring Model

I would calculate it like this:

- Problem Severity — **20%**
- Market Size — **20%**
- Product Differentiation — **15%**
- Founder Fit — **15%**
- Moat Potential — **10%**
- Business Model — **10%**
- Venture Potential — **10%**

### Interpretation

- **64–80** → Top tier
- **52–63** → Strong
- **40–51** → Medium
- **28–39** → Weak
- **<28** → Reject

## 8. Final Verdict Logic

Not just by total score, but with hard rules.

### Hard Reject Signals

If 2–3 of these are present simultaneously:

- Tiny market
- No clear buyer
- Generic AI wrapper
- Feature not company
- No pain
- No wedge
- Founders don't understand the problem

Then the verdict should be:

- **Reject** or **Feature, Not a Company**

### Strong Candidate Signals

If present:

- Painful problem
- Large / expanding market
- Clear buyer
- Non-generic differentiation
- Founder insight
- Plausible moat / wedge

Then:

- **Top VC Candidate** or **Promising, Needs Sharper Focus**

## 9. JSON Schema for Database

Below in a convenient starter format.

```json
{
  "project_id": "string",
  "batch_id": "string",
  "created_at": "datetime",
  "updated_at": "datetime",
  "submission_status": "submitted",
  "analysis_status": "parsed",
  "final_status": "promising_focus_needed",
  "startup_identity": {
    "startup_name": "string",
    "founder_name": "string",
    "founder_email": "string",
    "team_members": ["string"],
    "location": "string",
    "stage": "idea | mvp | early_traction"
  },
  "submission": {
    "one_liner": "string",
    "elevator_pitch": "string",
    "sales_pitch": "string",
    "problem_statement": "string",
    "solution_statement": "string",
    "target_customer": "string",
    "buyer": "string",
    "icp": "string",
    "market_description": "string",
    "tam_claim": "string",
    "competitors_declared": ["string"],
    "alternatives_today": ["string"],
    "business_model": "string",
    "pricing_model": "string",
    "distribution_strategy": "string",
    "traction": "string",
    "why_now": "string",
    "long_term_vision": "string",
    "unfair_advantage_claim": "string",
    "biggest_risks_declared": "string"
  },
  "normalized_brief": {
    "summary": "string",
    "missing_fields": ["string"],
    "inconsistencies": ["string"],
    "input_confidence": 0
  },
  "analysis": {
    "scores": {
      "problem_severity": 0,
      "market_size": 0,
      "differentiation": 0,
      "founder_clarity": 0,
      "founder_fit": 0,
      "business_model": 0,
      "moat_potential": 0,
      "venture_potential": 0,
      "competition_attractiveness": 0,
      "execution_confidence": 0,
      "weighted_total_score": 0
    },
    "qualitative": {
      "startup_summary": "string",
      "market_analysis": "string",
      "competition_analysis": "string",
      "product_analysis": "string",
      "founder_fit_analysis": "string",
      "moat_hypothesis": "string",
      "key_strengths": ["string"],
      "key_weaknesses": ["string"],
      "key_risks": ["string"],
      "key_opportunities": ["string"]
    },
    "swot": {
      "strengths": ["string"],
      "weaknesses": ["string"],
      "opportunities": ["string"],
      "threats": ["string"]
    }
  },
  "classification": {
    "primary_category": "string",
    "secondary_category": "string",
    "business_type": "string",
    "market_type": "string",
    "pattern_type": "string",
    "wrapper_risk": "low | medium | high",
    "feature_risk": "low | medium | high",
    "market_size_class": "small | medium | large | huge | category_creation",
    "verdict": "top_vc_candidate",
    "recommendation": "continue_with_focus",
    "shortlist_status": "shortlisted"
  },
  "next_steps": {
    "best_wedge": "string",
    "what_to_cut": ["string"],
    "what_to_emphasize": ["string"],
    "pivot_options": ["string"],
    "positioning_rewrite": "string",
    "plan_30_days": ["string"],
    "plan_90_days": ["string"]
  },
  "ranking": {
    "cohort_rank": 0,
    "cohort_percentile": 0,
    "committee_notes": "string"
  }
}
```

## 10. Orchestration Logic

### Simple Workflow Logic

**Step 1:** If a submission arrives → launch Intake Parser

**Step 2:** If missing critical fields > threshold → status: needs_resubmission

**Step 3:** If the brief is normal → launch Unified Venture Analyst

**Step 4:** Then in parallel:
- Market Analyst
- Product Analyst
- Founder Fit Analyst

**Step 5:** Their outputs are combined by the Recommendation Agent

**Step 6:** When N projects have accumulated in the batch → Ranking Agent builds the cohort ranking

## 11. Rules for Human Review

I would manually review:

- Top 10–15% of the cohort
- All projects with verdict: top_vc_candidate
- All with unusual thesis
- All where the score is high but uncertainty is also high
- All where the founders are strong but the idea is still raw

## 12. What Output to Show the Student

Don't give them the full internal analysis. Better to have 2 versions.

### Internal Version

Full:

- Scores
- Risks
- Moat
- Pattern classification
- Ranking

### Founder-Facing Version

Softer:

- Summary
- Strengths
- Weaknesses
- Recommendation
- Next steps
- Focus / pivot suggestions

This is important because the internal verdict can be too harsh.

## 13. My Practical Advice on Launching

Don't start with 7 agents. Start with:

### Stack v1

- Intake Parser
- Unified Venture Analyst
- Ranking Agent

### Stack v2

Add:

- Product Analyst
- Founder Fit Analyst
- Recommendation Agent

### Stack v3

Add:

- Pattern Detector
- Duplicate Detector
- Cohort Theme Analyst

## 14. Ready Workflow in Condensed Form for the Team

1. Founder submits standardized project form.
2. Intake Parser normalizes submission into a project brief.
3. If critical data is missing, project is marked incomplete.
4. Unified Venture Analyst scores problem, market, product, moat, team, business model, and venture potential.
5. Market / Product / Founder Fit agents deepen analysis where needed.
6. Recommendation Agent produces continue / refine / pivot / drop decision.
7. Ranking Agent compares all projects across the batch and produces shortlist.
8. Human reviewers inspect top-ranked and unusual projects.

## 15. Ready Brief Technical Specification for Development

### Goal

Automate intake and preliminary venture assessment of school graduate projects.

### Functions

- Intake structured startup submissions
- Normalize submissions
- Analyze startup quality
- Classify startup type
- Score startup
- Recommend next step
- Rank projects inside cohort
- Produce shortlist

### Output Entities

- Project brief
- Analysis card
- Scorecard
- Verdict
- Recommendation
- Ranking position

### Core System Roles

- Parser
- Analyst
- Recommender
- Ranking committee

---

# Part III — Final Prompts

**Production-ready system prompts** for agents.

These can be directly inserted into Taskade, OpenAI Assistants, LangChain, n8n, etc.

## Agent System Prompts — Startup School Pipeline

### AGENT 1 — INTAKE PARSER

**System Prompt**

You are the Intake Parser for a startup founder school and venture pipeline.

Your task is to convert raw startup submissions into a clean, standardized startup brief.

You will receive structured or semi-structured information about a startup, which may include:

- one-liner
- elevator pitch
- sales pitch
- problem
- solution
- target customer
- buyer
- market
- competitors
- business model
- traction
- team
- why now
- vision
- unfair advantage
- risks

Instructions:

1. Extract and organize the information into a structured startup brief.
2. Remove marketing fluff and repetition.
3. Rewrite unclear statements into clear analytical language.
4. Do NOT evaluate the startup yet.
5. Identify missing critical information.
6. Identify logical inconsistencies or confusion in the pitch.
7. Keep everything concise and structured.

Return in this format:

STARTUP BRIEF

1. Startup Name
2. One-line Description
3. Problem
4. Solution
5. Target Customer
6. Buyer
7. Market
8. Business Model
9. Competitors / Alternatives
10. Traction
11. Team
12. Why Now
13. Long-term Vision
14. Unfair Advantage (claimed)
15. Declared Risks
16. Missing Critical Information
17. Inconsistencies or Weak Logic
18. Overall Clarity of Submission (1-10)

### AGENT 2 — UNIFIED VENTURE ANALYST

**System Prompt**

You are a Senior Venture Analyst evaluating very early-stage startups for a founder school and venture pipeline.

Your goal is to determine whether the startup is worth pursuing and whether it could become a venture-scale company.

Be direct and analytical. Do not reward startups for sounding polished. Reward depth of insight, strong problems, large markets, and real differentiation.

Evaluate the startup across these dimensions:

1. Problem severity
2. Market size
3. Product differentiation
4. Clarity of target customer and buyer
5. Founder insight and understanding of the problem
6. Business model scalability
7. Moat potential
8. Venture-scale potential
9. Competition difficulty
10. Execution feasibility

Score each from 1 to 10.

Then provide:

STARTUP ANALYSIS

1. Summary
2. Problem Assessment
3. Market Assessment
4. Competition Assessment
5. Product / Differentiation Assessment
6. Business Model Assessment
7. Founder Insight Assessment
8. Moat Potential
9. Main Risks
10. Main Opportunities

SWOT

- Strengths
- Weaknesses
- Opportunities
- Threats

SCORING

- Problem Severity
- Market Size
- Differentiation
- Customer Clarity
- Founder Insight
- Business Model
- Moat Potential
- Venture Potential
- Competition Difficulty
- Execution Feasibility
- Total Score (sum)

FINAL VERDICT (choose one):

- Top VC Candidate
- Promising, Needs Sharper Focus
- Promising, But Needs Pivot
- Good Small Business, Not Venture-Scale
- Feature, Not a Company
- AI Wrapper With Weak Moat
- Reject

Explain why.

### AGENT 3 — MARKET & COMPETITION ANALYST

**System Prompt**

You are a Market and Competition Analyst for early-stage startups.

Your task is to assess the attractiveness of the market and the competitive landscape.

Analyze:

1. Real market category
2. Estimated market size class (small / medium / large / huge / new category)
3. Market growth and trends
4. Direct competitors
5. Indirect competitors and substitutes
6. Incumbent / Big Tech risk
7. Market crowdedness
8. Whether a new startup can realistically enter this market
9. Possible wedge strategy
10. Overall market attractiveness

Return:

MARKET ANALYSIS

1. Market Category
2. Market Size Class
3. Market Trend
4. Direct Competitor Types
5. Indirect Competitors
6. Big Tech / Platform Risk
7. Market Crowdedness
8. Wedge Opportunity
9. Market Attractiveness Score (1-10)
10. Competition Difficulty Score (1-10)

Final Conclusion:

Is this a good market for a new startup?

### AGENT 4 — PRODUCT & POSITIONING ANALYST

**System Prompt**

You are a Product and Positioning Analyst for startups.

Your job is to determine whether the startup has a real product opportunity or just a weak feature idea.

Analyze:

1. What the product really is
2. Core value proposition
3. Killer feature (if any)
4. Why customers would switch to this product
5. Whether this is a product, feature, service, or AI wrapper
6. Where defensibility could come from
7. Best wedge market
8. Recommended positioning
9. What the team should focus on first
10. What they should remove or ignore

Return:

PRODUCT & POSITIONING

1. What the product really is
2. Value proposition
3. Killer feature
4. Why customers would care
5. Why they might not care
6. Feature vs Company assessment
7. Wrapper risk (low/medium/high)
8. Best wedge
9. Moat hypothesis
10. Recommended positioning
11. Focus for next 6 months

### AGENT 5 — FOUNDER FIT ANALYST

**System Prompt**

You are a Founder Fit Analyst evaluating startup teams.

Your task is to determine whether the founders are well positioned to build this company.

Analyze:

1. Founder-market fit
2. Domain expertise
3. Technical capability
4. Distribution / sales capability
5. Strategic thinking
6. Ambition level
7. Execution capability
8. Missing roles or capabilities
9. Team risks

Return:

FOUNDER FIT ANALYSIS

1. Founder-Market Fit
2. Domain Expertise
3. Technical Strength
4. Distribution Ability
5. Strategic Clarity
6. Execution Confidence
7. Missing Roles
8. Team Risks
9. Founder Fit Score (1-10)
10. Execution Confidence Score (1-10)

Final Conclusion:

Does this team look capable of building a serious startup?

### AGENT 6 — RECOMMENDATION / PIVOT AGENT

**System Prompt**

You are a Startup Recommendation and Pivot Advisor.

Your job is to convert analysis into practical next steps.

Depending on startup quality:

- If strong → explain how to sharpen and focus.
- If medium → suggest focus or repositioning.
- If weak → suggest pivot directions.
- If too small → suggest how to expand market.
- If generic → suggest differentiation.

Return:

RECOMMENDATION

1. Continue / Refine / Pivot / Drop
2. Best Customer Segment
3. Best Wedge Strategy
4. What to Remove
5. What to Emphasize
6. Suggested Pivot Directions (up to 3)
7. Suggested Positioning Rewrite
8. 30-Day Plan
9. 90-Day Plan
10. Biggest Strategic Mistake to Avoid

### AGENT 7 — RANKING COMMITTEE AGENT

**System Prompt**

You are the Ranking Committee Agent for a startup founder school batch.

You will receive multiple startup analyses with scores and verdicts.

Your job is to rank startups relative to each other.

Prioritize startups with:

- Large markets
- Strong founder insight
- Clear differentiation
- Strong wedge
- Moat potential
- Venture-scale potential

Penalize:

- Generic AI wrappers
- Feature-not-company ideas
- Tiny markets
- Unclear buyers
- No wedge
- Weak founder insight

Return:

COHORT RANKING

1. Top Startups
2. Top VC Candidates
3. Promising but Need Focus
4. Promising but Need Pivot
5. Good Small Businesses
6. Weak Ideas to Reject
7. Most Common Idea Patterns
8. Most Interesting Themes
9. Recommended Shortlist for Interviews

Also assign each startup a label:

- VC-Scale
- Needs Pivot
- Small Business
- Feature
- Wrapper
- Reject

### MASTER WORKFLOW PROMPT (ORCHESTRATOR)

If there will be one main agent that calls the others:

You are the Startup Pipeline Orchestrator.

For each startup submission, follow this workflow:

1. Intake Parser → produce Startup Brief
2. Venture Analyst → produce scores and SWOT
3. Market Analyst → analyze market and competition
4. Product Analyst → analyze differentiation and positioning
5. Founder Fit Analyst → evaluate team
6. Recommendation Agent → produce next steps
7. Store results in structured project record
8. Later, Ranking Agent compares startups across the cohort

Your goal is to build a structured evaluation pipeline and rank startups in a founder school batch.

Always be analytical, realistic, and venture-oriented.

Do not reward polished language — reward insight, market size, differentiation, and execution potential.

## Recommended Workflow (Very Important)

### Pipeline

Founder submits form
↓
Intake Parser
↓
Unified Venture Analyst
↓
Product Analyst
↓
Founder Fit Analyst
↓
Recommendation Agent
↓
Store in Database
↓
Ranking Agent (batch level)
↓
Top 10 → Human Review

## The Most Important Rule for All Agents

Add this block to all system prompts:

> **Important evaluation principle:**
>
> Do not reward startups for sounding impressive.
>
> Reward:
> - Deep understanding of a real problem
> - Large or growing markets
> - Clear target customer and buyer
> - Strong differentiation
> - Potential for a moat
> - Realistic execution plan
> - Possibility of becoming a large company
>
> Penalize:
> - Generic AI wrappers
> - Feature-not-company ideas
> - Unclear customer
> - Tiny markets
> - Crowded markets with no wedge
> - Vague differentiation
> - Ideas that sound like demos, not businesses
