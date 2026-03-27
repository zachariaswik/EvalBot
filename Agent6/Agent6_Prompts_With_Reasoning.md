# Agent 6 — Recommendation/Pivot Agent: Prompts with Reasoning

## Overview

Agent 6 is the synthesizer. It consumes the outputs of Agents 3 (Market), 4 (Product/Positioning), and 5 (Founder Fit), and answers the most important question: **What should the founder actually DO next?** This agent doesn't just critique — it prescribes. Each prompt forces a concrete recommendation grounded in the accumulated evidence. The prompts are structured around four scenarios (strong idea → sharpen, weak idea → pivot, too small → expand, wrapper → find depth) and a final synthesis that delivers the actionable output.

---

## Section 1: Strength Assessment — Is the Idea Strong Enough?

### Prompt 1.1

> Synthesize the scores from Agents 3-5: Market Attractiveness (6.0/10), Product Potential (5/10 as-is, 7/10 with changes), Founder Score (4.7/10). Taken together, does this constellation represent a viable startup? What is the minimum threshold across these three dimensions for a pre-seed investment decision? Where does this startup fall relative to that threshold — above, at, or below?

**Reasoning:** Each agent scored independently. But the real question is whether the COMBINATION works. A 6/10 market with a 7/10 product and a 3/10 founder is different from a 6/10 market with a 5/10 product and a 7/10 founder. The interaction effects matter. Agent 3 found the market is real but competitive. Agent 4 found the product needs sharpening but has a viable pivot. Agent 5 found the founder is mission-driven but under-resourced. The synthesis should determine whether the weak link (founder capacity) is fixable or fatal, and whether the strong links (market timing, mission conviction) are enough to compensate.

### Prompt 1.2

> Across all three agents, what is the single strongest signal that this startup could work? And what is the single strongest signal that it won't? Be specific — cite the evidence, not just the conclusion.

**Reasoning:** Before recommending next steps, Agent 6 needs to identify the most important positive and negative signals. This forces ranking across all the findings. The strongest positive might be market timing (41 states with phone bans, COPPA deadline, "brain rot" cultural peak). The strongest negative might be founder capacity (solo, part-time, no domain expertise, no distribution capability). By naming these explicitly, the recommendation can be anchored to reality rather than optimism.

### Prompt 1.3

> Agent 3 rated market attractiveness at 6.0/10, noting excellent regulatory tailwinds but high platform risk. Agent 4 rated product potential at 7/10 WITH the AI access management pivot, but only 5/10 as-is. Agent 5 rated the founder at 4.7/10, with distribution (3/10) and domain expertise (3/10) as the weakest dimensions. If you could change ONE thing about this startup to maximally improve its chances, what would it be? Not three things, not a roadmap — one thing.

**Reasoning:** This forces Agent 6 to make a single high-leverage recommendation rather than a scattershot list. The constraint of "one thing" is deliberate — it mirrors the founder's situation (limited time, limited resources, can only do one thing well at a time). The answer should emerge from the intersection of what's most broken and what's most fixable. Founder capacity is the lowest score but may not be the most fixable in the short term. Product sharpness is lower-hanging fruit. The right answer depends on which lever has the highest ROI on a 30-day timescale.

---

## Section 2: If Strong — How to Sharpen

### Prompt 2.1

> Agents 3 and 4 both identified that the product's strongest differentiated angle is AI access management for students (allowing educational AI, blocking unrestricted AI). Agent 3 found no existing product does this well. Agent 4 rated it as the potential killer feature (7/10 with pivot). If the founder leans into this angle, what does the sharpened version of the product look like? Describe: the core experience, the target user's first interaction, the "aha moment," and what the parent sees that makes them say "I need this."

**Reasoning:** Multiple agents converged on the same recommendation: AI access management is the sharpest wedge. But the recommendation is abstract until it's translated into a concrete product experience. The founder needs to visualize what "AI access management" looks and feels like as a product — not just as a strategy document. This prompt forces Agent 6 to paint that picture: what does the parent download, what happens when the student opens it, what does the dashboard show, what makes this feel indispensable?

### Prompt 2.2

> Agent 4 recommended positioning as a "digital study room" but selling with "parental control" language. Agent 3 found the B2C niche (parent-facing, high-restriction) is less crowded than the institutional market. Agent 5 found the founder's educator network is the warmest distribution channel. If all three findings are correct, design the first 30 days of a sharpened go-to-market: what does the founder build, who do they talk to, what do they post, what do they measure, and what decision do they make at the end of 30 days?

**Reasoning:** Strategy is worthless without a concrete execution plan. The agents have produced ~100 pages of analysis. The founder needs a 1-page action plan for the next 30 days. This prompt forces Agent 6 to translate all the strategic recommendations into specific, time-bound, measurable actions. The "decision at the end of 30 days" element is critical — it creates a forcing function that the founder's current soft milestones lack.

### Prompt 2.3

> Agent 4 identified that the current user evidence is 3/10 ("polite interest"). Agent 5 found the waitlist target of 100+ users in two weeks is the only quantitative, falsifiable metric. Design a validation experiment that the founder can run in the next 14 days — without writing any code — that would either confirm or refute the core demand hypothesis. The experiment should answer: "Do parents of middle-schoolers actually want a tool that manages their child's AI access and blocks distractions during homework time?"

**Reasoning:** The founder's instinct is to build first, validate second (the roadmap starts with alpha testing, not demand testing). But the biggest risk isn't technical — it's demand. Will parents actually pay for this? The founder could spend months building a product no one wants. A no-code validation experiment (landing page, social media post, direct outreach to parents) can test demand in days. This prompt forces Agent 6 to design the fastest, cheapest possible validation — before any more engineering time is invested.

---

## Section 3: If Weak — Pivot Options

### Prompt 3.1

> If the core concept (kiosk-mode browser for students) proves unviable — parents don't pay, students bypass it easily, or platforms ship native alternatives — what are the three most promising pivot directions the founder could take, using the same technical skills, network, and market knowledge they've already built? For each pivot, describe: what the product becomes, who the target user is, why it's better than the current concept, and what the first validation step would be.

**Reasoning:** The founder hasn't considered pivot scenarios — the materials show conviction in a single concept. But responsible analysis requires contingency planning. Agent 5 found the founder is mission-driven (6/10 on clarity of ambition) which means they'll persist even when the data says pivot. Having pre-defined pivot options makes it easier to change direction without feeling like failure. The pivots should leverage what the founder already has: technical skills, educator network, understanding of student digital wellness, and the "brain rot" cultural moment.

### Prompt 3.2

> Agent 3 identified the homeschool market (3.7-4M students, 8.5% CAGR, families spending $700-$1,800/year on EdTech) as a potentially sharper wedge. Agent 4 noted that homeschool parents are buyer AND administrator — no IT department, no procurement cycle. Agent 5 found the founder's biggest distribution gap is in reaching customers at scale. Would pivoting to "the study browser for homeschool families" be a stronger starting point than "the study browser for all K-12 students"? Analyze the trade-offs.

**Reasoning:** The homeschool angle emerged independently in Agent 3 (market data) and Agent 4 (wedge analysis). Homeschool families are a compelling niche: they have high autonomy over tool choice, active online communities (word-of-mouth spreads), and no institutional gatekeeping. The founder's distribution weakness (3/10) is partially mitigated because homeschool communities are concentrated online — exactly where the founder plans to market. This isn't a pivot away from the core product; it's a narrower wedge for the same product. But there may be trade-offs (smaller total market, different feature needs, potential stigma of being "just a homeschool tool").

### Prompt 3.3

> Agent 5 found the founder's technical depth (6/10) is the strongest dimension. If the consumer product fails, could the founder pivot to a B2B infrastructure play — building the underlying technology (kiosk mode engine, AI content classifier, student browsing analytics) and licensing it to existing EdTech platforms (GoGuardian, Securly, Bark) rather than competing with them? Evaluate the viability of a "picks and shovels" pivot.

**Reasoning:** The founder is strongest as a builder, weakest as a seller. A B2B infrastructure/licensing play inverts the distribution problem: instead of reaching millions of parents, the founder sells to 5-10 EdTech platforms who already have distribution. The AI content classifier (auto-categorize websites and AI tools as educational vs. distracting) is a component that every filtering product needs but is expensive to build and maintain. If the founder can build a best-in-class classifier, it could be licensed to GoGuardian, Securly, or Bark as an API. This leverages the founder's strengths (technical, AI-literate) and avoids the weaknesses (distribution, sales, domain expertise in school procurement).

---

## Section 4: If Too Small — Expand the Wedge

### Prompt 4.1

> Agent 3 estimated SOM at $500K-$1M ARR in 3 years — which is a lifestyle business, not a venture-scale outcome. If the product works in the initial wedge (parents of middle-schoolers, home computers), what is the realistic expansion path to $10M+ ARR? Map the concentric circles of expansion: wedge → adjacent segments → broader market. For each circle, identify: new customer segment, required product changes, and approximate revenue potential.

**Reasoning:** The TAM ($500-600M) is large enough for a venture-scale business, but the SOM ($500K-$1M) is not. Investors will ask "how does this become big?" The founder needs an expansion narrative that's credible, not just aspirational. The natural expansion path might be: (1) parents of middle-schoolers → (2) parents of all K-12 students → (3) homeschool families → (4) individual school pilots → (5) district-wide B2B contracts → (6) international expansion. Each circle multiplies the addressable market but requires new capabilities.

### Prompt 4.2

> Agent 4 identified "AI access management" as the killer feature pivot. If this feature proves successful, it could apply far beyond the kiosk browser — any device, any browser, any operating system could use an "AI gatekeeper" that manages which AI tools are accessible. Could "AI access management for students" become the platform, with the kiosk browser as just the first product? What would the expanded product vision look like: API, browser extension, MDM plugin, school-wide policy engine?

**Reasoning:** The most successful startups start with a wedge product and expand into a platform. If AI access management is the killer feature, the kiosk browser is just the delivery vehicle. The real value is the classification engine (which AI tools are safe, which are restricted, which need teacher approval) and the policy layer (each school or family configures their own rules). This could be delivered as: a standalone browser (current concept), a browser extension (lighter weight, wider reach), an API (licensed to existing platforms), or an MDM plugin (integrated into GoGuardian/Securly/Jamf). Each delivery mechanism addresses a different market segment. This prompt asks Agent 6 to map the platform potential.

### Prompt 4.3

> Agent 3 noted the "brain rot" cultural moment is driving real institutional change (41 states with phone bans, COPPA enforcement). Agent 4 found the product's timing is excellent. Is there a version of this company that becomes the "brand of record" for student digital wellness — the Common Sense Media of focus tools? If the founder builds the trusted community first (parent reviews, educator endorsements, AI tool ratings) and the product second, could the brand become larger than any single product? Evaluate a brand-first, product-second strategy.

**Reasoning:** Agent 4's moat analysis concluded that brand/trust + community is the founder's most realistic moat. Agent 5 found the founder is mission-driven, which supports long-term brand building. Common Sense Media started as a review/rating site and became THE trusted voice for parents navigating children's media. A "Common Sense Media for student digital tools" — rating AI tools, focus apps, browsers, and content filters — could become a powerful brand that then launches its own products with built-in trust and distribution. This inverts the usual startup sequence (product → users → brand) into (brand → community → product). It's unconventional but might suit the founder's constraints (brand-building can be done part-time and doesn't require deep technical infrastructure).

---

## Section 5: If Just a Wrapper — Find the Deeper Layer

### Prompt 5.1

> Agent 4 concluded the product is NOT an AI wrapper (score: LOW risk). But it may be a "browser wrapper" — a thin UX layer on top of existing content filtering technology. The underlying components (DNS filtering, HTTPS inspection, kiosk mode, whitelist management) are all available as open-source libraries or existing services. Is the product just repackaging existing technology in a slightly nicer form? If so, where is the deeper systemic layer that creates unique value?

**Reasoning:** "Not an AI wrapper" doesn't mean "not a wrapper." The kiosk browser's core technology (content filtering + locked browsing session) is well-established and commoditized. If the product is just a UI shell around existing filtering tech, it has zero technical moat and can be cloned in weeks. The deeper systemic layer — the thing that makes this more than a wrapper — might be: the AI classification engine, the community-curated policies, the parent analytics dashboard, or the adaptive restriction system. Agent 6 needs to identify which layer creates genuine unique value.

### Prompt 5.2

> The founder's SWOT identifies the core insight as: "Current tools act like blockers, but they are either insufficient, or they block too much. My application has a significantly different design and finds the sweet spot." Is "finding the sweet spot" a systemic insight or a feature preference? In other words, does the founder understand WHY current tools fail at the sweet spot — is there a structural reason (misaligned incentives, wrong architecture, wrong customer focus) — or is this just "I think I can do it better"? If there's a structural insight, articulate it. If not, the product is a feature, not a company.

**Reasoning:** This is the deepest question Agent 6 asks. The difference between a feature and a company is structural insight. Slack wasn't "better IRC" — it was built on the insight that work communication should be persistent, searchable, and integrated. Figma wasn't "better Sketch" — it was built on the insight that design tools should be multiplayer and browser-native. If the founder's insight is just "blockers block too much, so I'll block less" — that's a feature preference, not a structural insight. But if the insight is deeper — for example, "parental controls fail because they're built for surveillance, not for learning; a tool built for learning looks fundamentally different" — then there's a company underneath.

### Prompt 5.3

> If the product is currently a "thin wrapper," what would the "thick platform" version look like? Map the evolution from wrapper → tool → platform → ecosystem. For each stage, identify: what new capability is added, what new data is generated, what new stakeholder is served, and what new lock-in mechanism is created. Define the minimum viable platform — the simplest version that goes beyond "just a browser."

**Reasoning:** This prompt forces Agent 6 to sketch the product roadmap from today's MVP to a defensible platform. The wrapper → tool → platform → ecosystem framework is a standard venture playbook. At the wrapper stage, the product is a browser with filtering. At the tool stage, it adds analytics, AI classification, and adaptive restrictions. At the platform stage, it becomes an operating system for student digital wellness — managing multiple devices, integrating with LMS platforms, providing school-wide policy management. At the ecosystem stage, third-party developers build on it (content providers, tutoring services, assessment tools). Each stage creates new value and new lock-in. The founder doesn't need to build the ecosystem today, but investors want to see the vision.

---

## Section 6: Synthesis — The Next Step

### Prompt 6.1

> Based on everything from Agents 3-5 and the analysis above, write a single-page "Next Move" document for the founder. This should contain: (a) One sentence: what the startup IS (clear positioning), (b) One sentence: who the first 100 customers are (specific wedge), (c) Three bullet points: what to do in the next 30 days (concrete actions), (d) One sentence: the decision gate at day 30 (what determines if you continue, pivot, or stop), (e) Three bullet points: what NOT to do in the next 30 days (common traps to avoid), (f) One sentence: what "ready for investors" looks like and when to target it.

**Reasoning:** This is Agent 6's primary deliverable — the most actionable output in the entire system. After ~150 pages of analysis across Agents 3-6, the founder needs ONE PAGE they can tape to their wall. The format is deliberately constrained: single sentences force clarity, three-bullet limits force prioritization, and the "what NOT to do" section is as important as the "what to do" section because the founder's biggest risk is trying to do too many things at once.

### Prompt 6.2

> The founder has three options: (A) Continue with the current product and plan, accelerating the timeline. (B) Sharpen the product around AI access management and narrow the wedge to parents of middle-schoolers. (C) Pivot to a brand/community-first approach ("Common Sense Media for student focus tools") and build the product later. Evaluate each option on: probability of reaching 200+ users in 6 months, probability of raising pre-seed funding in 12 months, alignment with founder's strengths, and risk level. Recommend one.

**Reasoning:** This prompt forces a clean decision between three viable paths. Option A is the path of least change (the founder keeps doing what they're doing, just faster). Option B is the path of product sharpening (the recommendation from Agent 4). Option C is the path of brand building (the moat hypothesis from Agent 4 + the community strategy). Each is internally consistent but leads to a different company. The evaluation criteria (users, funding, founder fit, risk) are the dimensions that matter most at this stage. Agent 6 must pick one — not hedge with "it depends."

### Prompt 6.3

> Write a candid 200-word message to the founder — not an analysis, not a report, but a direct human-to-human message that says: here's where you stand, here's your biggest blind spot, and here's the single most important thing you should do this week. Be honest, be kind, be specific.

**Reasoning:** After hundreds of pages of analysis, the founder needs to hear one clear, direct voice. This prompt asks Agent 6 to drop the analytical framework and speak plainly. The most impactful accelerator mentorship happens in moments of candid, caring directness — not in slide decks. The 200-word limit forces brutal prioritization. The "this week" timeframe forces immediate action, not strategic planning. The "biggest blind spot" element ensures the message isn't just encouraging — it surfaces the thing the founder isn't seeing.
