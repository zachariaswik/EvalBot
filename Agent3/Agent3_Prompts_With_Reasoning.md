# Agent 3 — Market & Competition Analyst: Prompts with Reasoning

## Overview

These prompts are designed to extract the information Agent 3 needs to build a competitive landscape and market view. Each prompt is grounded in data points already present in the founder's practice materials (SWOT, Business Model Canvas, One-Pager, Growth Channel work, and Investor Pitch planning) so the agent can cross-reference what the founder has claimed with what the market actually looks like.

---

## Section 1: Market Category Identification

### Prompt 1.1

> Based on the founder's One-Pager and Business Model Canvas, the product is described as a "kiosk-mode learning environment" that blocks distractions for K-12 students. What is the most accurate market category for this product? Consider whether it fits primarily into EdTech, parental controls / digital wellness, student productivity tools, or enterprise device management (MDM/UEM). Explain which category is the best primary fit and which are adjacent categories the product touches.

**Reasoning:** The founder describes the product in multiple ways across the materials — "kiosk mode application," "browser with focus mode," and a tool that "removes harmful and addictive content." These descriptions span several market categories. An investor or analyst needs to know exactly which category this sits in, because TAM estimates, competitor sets, and go-to-market expectations differ drastically between EdTech SaaS, consumer parental controls, and enterprise device management. The SWOT also mentions the product is "not competing against previous workflows," which suggests the founder may not have fully mapped the competitive category yet.

### Prompt 1.2

> The founder positions the product as distinct from existing parental controls ("current tools act like blockers, but they are either insufficient, or they block too much"). Does this positioning place the product in a new sub-category, or is the founder underestimating how existing players already address this middle ground? Search for products that combine content filtering with a focused browsing or learning environment for students.

**Reasoning:** The SWOT Strengths section claims the application "finds the sweet spot" between too-fragile and too-restrictive controls. This is a core differentiation claim that needs market validation. If existing products already occupy this middle ground, the positioning collapses. If no one does, it may signal a genuine gap — or a gap that exists for a reason (e.g., the market doesn't want it).

---

## Section 2: TAM / SAM / SOM Estimation

### Prompt 2.1

> The founder states there are "roughly 100 million devices used by K-12 students in Europe + USA." Using this as a starting point, estimate the Total Addressable Market (TAM), Serviceable Addressable Market (SAM), and Serviceable Obtainable Market (SOM) for a subscription-based focus/kiosk browser for students. Assume B2C pricing to parents/teachers and B2B school-wide licensing as the two revenue streams. Use current market data for EdTech and digital wellness spending in K-12.

**Reasoning:** The founder provides one raw data point (100M devices) but no revenue-based market sizing. The Business Model Canvas mentions both B2C subscriptions and B2B school-wide licenses, and the Cost Structure notes minimal costs. An investor needs to see whether the addressable market is large enough to justify venture-scale ambition, or whether this is a lifestyle business. The 100M device figure is a useful anchor but needs conversion into revenue terms at realistic price points and adoption rates.

### Prompt 2.2

> The founder plans to start B2C (parents/teachers) then move to B2B (school-wide licenses). Given that the SWOT Threats section notes "education institutions are tight on budget," what is the realistic willingness-to-pay for each segment? Find comparable pricing for similar EdTech or parental control tools targeting K-12 and estimate a reasonable price range for both B2C and B2B.

**Reasoning:** The founder acknowledges budget constraints in schools but hasn't quantified pricing. The Business Model Canvas lists "subscriptions" without dollar figures. Market sizing is meaningless without a price assumption, and the B2C-to-B2B pivot path needs validation — many EdTech startups fail in the transition because schools have procurement cycles, compliance requirements, and drastically different willingness-to-pay compared to individual parents.

---

## Section 3: Red Ocean vs. Blue Ocean Positioning

### Prompt 3.1

> Is the market for student-focused browsing tools / digital wellness tools for K-12 a red ocean (crowded, commoditized, competing on features and price) or a blue ocean (underserved, with room for a new value proposition)? Consider both the parental control space (Bark, Qustodio, Net Nanny, Securly, GoGuardian) and the student productivity/focus space (Forest, Freedom, Cold Turkey). Map which of these compete on blocking vs. enabling focused work, and where the founder's "kiosk-mode browser" concept sits.

**Reasoning:** The founder's SWOT identifies an opportunity ("current tools just don't cut it") but doesn't map the competitive density. The parental control space is well-established with mature players, while the "focus tool for students" niche may be thinner. The distinction matters enormously: in a red ocean, the founder needs a very sharp wedge to enter; in a blue ocean, the risk is more about whether the market actually exists. The Day 4 materials show the founder plans social media as the primary channel (Reddit, TikTok, Discord study communities), which works better in a blue ocean where organic community building matters more than outspending incumbents.

### Prompt 3.2

> The founder claims the application has "a significantly different design" from current tools. Evaluate whether this constitutes a genuine blue ocean value innovation (creating new demand) or simply a feature improvement within an existing red ocean category. What would need to be true for this to be a blue ocean play?

**Reasoning:** The One-Pager and SWOT both emphasize differentiation through the "kiosk mode" approach vs. traditional blockers. But blue ocean strategy requires more than a feature difference — it requires creating demand that didn't previously exist. The founder's interview evidence (parents and teachers expressing interest) suggests existing demand, which points more toward a better mousetrap in an existing category. This distinction affects how the agent should score market attractiveness.

---

## Section 4: Direct and Indirect Competitors

### Prompt 4.1

> Identify the direct competitors to a kiosk-mode focus browser for K-12 students. For each competitor, note: product name, what it does, target user (parent/school/student), pricing model, and approximate scale (users, revenue, or funding if available). Focus on products that combine content filtering with a structured browsing or learning environment — not just generic content blockers.

**Reasoning:** The founder's materials mention no competitors by name. The SWOT references "current tools" generically. Agent 3 needs a concrete competitor map. Direct competitors are those that a buyer would evaluate side-by-side with this product. The key filter is "content filtering + structured learning environment" — pure blockers are indirect competitors, and pure LMS platforms are adjacent but different.

### Prompt 4.2

> Identify the indirect competitors — products that solve the same underlying problem (student distraction / lack of focus during study time) but through a different approach. This includes: general focus apps (Forest, Freedom), school device management platforms (GoGuardian, Securly, Jamf School), browser extensions for focus, and even hardware solutions like dedicated learning tablets. For each, note how a parent or school might choose that solution instead of a kiosk-mode browser.

**Reasoning:** The founder's Business Model Canvas and Sales Pitch focus on the direct value prop (removing distractions), but buyers have many substitute options. A parent might buy a Chromebook with GoGuardian already installed by the school. A student might use Forest voluntarily. A school might already have Securly deployed district-wide. Understanding indirect competition reveals the real switching cost and adoption barriers — which connects directly to the SWOT Threat about "users locked into old workflows or long-term contracts."

### Prompt 4.3

> Create a competition map that plots the identified competitors on two axes: (1) degree of restriction (light nudge vs. full lockdown) and (2) target buyer (consumer/parent vs. institutional/school). Where does the founder's product sit on this map, and is there an underserved quadrant?

**Reasoning:** A two-axis map is a standard deliverable for Agent 3's "competition map" output. The axes are chosen based on what the founder's materials reveal as the key differentiators: the SWOT explicitly contrasts "too fragile" vs. "too restrictive" (restriction axis), and the Business Model Canvas separates B2C from B2B (buyer axis). If the map shows an empty quadrant where the founder's product sits, that's strong evidence for market opportunity. If it's crowded, that changes the strategy.

---

## Section 5: AI / Big Tech Risk Assessment

### Prompt 5.1

> Assess the risk that major technology platforms (Google, Apple, Microsoft) will build native focus/kiosk mode features into their operating systems or browsers that would make a standalone product like this unnecessary. Consider: Google's Family Link, Apple's Screen Time and Managed Apple IDs, Microsoft's Family Safety, and ChromeOS's built-in school management features. How close are these built-in tools to replicating the founder's value proposition?

**Reasoning:** The SWOT Threats section asks "Is a big platform gearing up to enter your space?" but the founder didn't answer this directly. This is arguably the single biggest existential risk for the product. Google already controls ChromeOS (dominant in K-12) and has Family Link. Apple has Screen Time with increasing focus features. If any of these platforms ships a "study mode" natively, it eliminates the need for a third-party tool overnight. The founder's technical advantage (agentic coding / fast development) means nothing against a platform that ships the feature to 100M devices for free.

### Prompt 5.2

> Beyond platform risk, assess whether AI-native startups could leapfrog this product. For example, could an AI tutor (like Khanmigo, or a future GPT-based study assistant) make the "blocking" approach obsolete by providing a more engaging alternative that keeps students focused through positive reinforcement rather than restriction? The founder's SWOT notes that "AI being used by students for cheating rather than for learning" is an opportunity — but could AI tutors flip this into a threat?

**Reasoning:** The founder identifies AI cheating as an opportunity, but the AI landscape is moving fast. If AI tutors become the standard study interface, the browser itself becomes less relevant — students would work inside an AI environment rather than a traditional browser. This is a second-order threat that the founder hasn't considered in the materials. It's critical for the market attractiveness score because it affects the product's shelf life.

---

## Section 6: Market Crowdedness and Attractiveness Score

### Prompt 6.1

> Based on all the competitive analysis above, rate the overall market crowdedness on a scale of 1-10 (1 = virtually no competition, 10 = saturated). Consider: number of funded competitors, presence of platform-native solutions, ease of switching for buyers, and whether new entrants are still emerging. Provide the score with a brief justification.

**Reasoning:** This directly feeds Agent 3's "market attractiveness score" output. Crowdedness is one component. The scoring needs to be grounded in the competitor count and platform risk analysis, not just a gut feeling.

### Prompt 6.2

> Compile a final Market Attractiveness Score (1-10) that weighs the following factors: (a) TAM size and growth trajectory, (b) competitive density / crowdedness, (c) platform / Big Tech risk, (d) buyer willingness to pay, (e) regulatory tailwinds or headwinds (e.g., children's privacy laws like COPPA/GDPR-K), and (f) timing — whether the "brain rot" and screen time cultural moment creates a real demand window. Explain how each factor contributes to the final score.

**Reasoning:** This is the capstone output for Agent 3. The factor list is drawn directly from what the founder's materials surface: TAM from the One-Pager (100M devices), competition from the SWOT gaps, platform risk from the Threats section, pricing from the Business Model Canvas, privacy from the SWOT Threats ("privacy concern that needs to be handled correctly"), and timing from the Opportunities ("big worry about shortened attention span" and "brain-rot"). By making each factor explicit, the score becomes transparent and actionable rather than arbitrary.

---

## Section 7: Market Note Synthesis

### Prompt 7.1

> Write a concise market note (300-500 words) summarizing: the market category, the TAM/SAM/SOM estimates, whether this is a red or blue ocean, the top 3-5 competitors and their positioning, the AI/Big Tech risk level, and the overall market attractiveness score. Frame this as an internal analyst note for an investment committee evaluating this startup at pre-seed stage. Be candid about both the opportunities and the risks.

**Reasoning:** This is Agent 3's primary deliverable. The prompt asks for investment-committee framing because the founder is in an accelerator (AltaLab, mentioned in Day 5) and will face investor scrutiny. The word limit forces conciseness. "Be candid" is included because the Day 2 materials explicitly warn against "nice clichés and a dream story" — the founder values honest analysis. The note should synthesize all previous prompts into a single coherent view.
