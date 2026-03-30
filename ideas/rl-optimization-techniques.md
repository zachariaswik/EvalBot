# Reinforcement Learning & Optimization Techniques for Startup Generator

## Current System Architecture

The EvalBot startup generator implements a **multi-turn iterative optimization** system with:
- **Agent** (Agent 0) - Takes actions (generates startup ideas)
- **Environment** (Agents 1-6) - Evaluates actions
- **Reward Signal** - Weighted score (0-80 points)
- **State** - Founder constraints + prior feedback
- **Policy** - LLM's generation strategy

The system uses dual feedback loops:
- **Inner Loop**: Screening retry (up to 5 attempts, threshold: 50/80)
- **Outer Loop**: Strategic iteration across rounds with full evaluation feedback

---

## 1. Reinforcement Learning & Fine-Tuning Approaches

### A. Constitutional AI / RLHF-style Iteration
- Collect successful high-scoring ideas
- Fine-tune a model specifically on these examples
- Use rejection sampling: generate 10 ideas, pick best
- **Implementation**: Save top-scoring generations, periodically fine-tune Agent 0

### B. Proximal Policy Optimization (PPO)
- True RL approach: train Agent 0 to maximize expected score
- Requires: model weights access, gradient computation
- **Tools**: OpenAI fine-tuning API, Anthropic's Constitutional AI
- **Challenge**: Expensive, requires many iterations

### C. Best-of-N Sampling
- Generate N ideas in parallel (e.g., N=5-10)
- Run all through screening (Agent 2)
- Pick highest scorer for full evaluation
- **Pros**: No training needed, immediate improvement
- **Cost**: Linear increase in API calls

```python
# Pseudo-code for best-of-N
candidates = [generate_idea(Agent0) for _ in range(N)]
scores = [screen_idea(Agent2, c) for c in candidates]
best = candidates[argmax(scores)]
```

---

## 2. Prompt Engineering & Meta-Learning

### A. Chain-of-Thought for Strategy
Already implemented with `strategy_notes`! Enhancements:
- Make Agent 0 explicitly reason through each scoring dimension
- Force justification: "This scores 18/20 on Problem Severity because..."
- Add "anti-examples": "I'm avoiding X pattern because it scores poorly"

### B. Few-Shot Learning with High-Performers
- Maintain a "hall of fame" of top-scoring ideas
- Include 2-3 examples in Agent 0's context
- **Dynamic selection**: Pick examples that succeeded where current attempt failed

```python
if prior_score['problem_severity'] < 15:
    include_examples = hall_of_fame.filter(problem_severity >= 18)
```

### C. Self-Critique Loop
Before submitting, have Agent 0 critique its own idea:
1. Generate idea
2. Self-evaluate against rubric
3. Identify weaknesses
4. Revise idea
5. Submit

---

## 3. Search & Optimization Algorithms

### A. Genetic Algorithms
- Generate population of ideas (N=10)
- Select top performers
- "Crossover": Combine elements from 2 good ideas
- "Mutation": Randomly vary aspects
- Repeat for M generations

```python
population = [generate_idea() for _ in range(10)]
for generation in range(5):
    scores = evaluate(population)
    parents = select_top_k(population, scores, k=3)
    children = crossover_and_mutate(parents)
    population = parents + children
```

### B. Simulated Annealing
- Start with high "temperature" (wild exploration)
- Gradually decrease (exploit good regions)
- Accept worse ideas with probability exp(-ΔE/T)
- Good for escaping local maxima

### C. Bayesian Optimization
- Model score as function of idea "features"
- Use Gaussian Process to predict promising areas
- Generate ideas in high-uncertainty, high-reward regions
- **Challenge**: Requires feature extraction from text

---

## 4. Advanced Feedback Mechanisms

### A. Differential Feedback
Instead of just "score = 55/80", provide:
- **Marginal gains**: "Adding X feature would gain +5 points"
- **Counterfactuals**: "If you'd chosen Y market, score would be +8"
- **Dimensional breakdown**: Table showing exactly where points were lost

### B. Multi-Armed Bandit
Track which idea "archetypes" score best:
- SaaS vs marketplace vs hardware
- B2B vs B2C
- AI-first vs traditional tech
Use UCB algorithm to balance exploration/exploitation

```python
archetypes = ['B2B_SaaS', 'Marketplace', 'Hardware', 'Climate_Tech']
scores_history = {archetype: [] for archetype in archetypes}

def select_archetype():
    ucb_scores = [
        mean(scores_history[a]) + sqrt(2*log(N)/len(scores_history[a]))
        for a in archetypes
    ]
    return archetypes[argmax(ucb_scores)]
```

### C. Curriculum Learning
Start with easier constraints, gradually increase difficulty:
- Round 1: No constraints
- Round 2: Add team size limit
- Round 3: Add low capital constraint
- Round 4: All constraints

---

## 5. Ensemble Methods

### A. Multi-Model Voting
- Use 3 different LLMs (GPT, Claude, Gemini) as Agent 0
- Generate idea from each
- Evaluate all, pick best
- Learn which model excels at which dimensions

### B. Mixture of Experts
- Train specialized generators:
  - Expert 1: High problem severity ideas
  - Expert 2: Large market ideas
  - Expert 3: Deep moat ideas
- Route to appropriate expert based on prior weaknesses

---

## 6. Data-Driven Improvements

### A. Score Prediction Model
Train a fast classifier to predict scores before full evaluation:
```python
# Train on historical data
predictor = train_model(ideas_text, scores)

# Use for pre-screening
candidates = [generate() for _ in range(20)]
predicted_scores = predictor.predict(candidates)
top_5 = candidates[argsort(predicted_scores)[-5:]]
actual_scores = evaluate_full_pipeline(top_5)
```

### B. Feature Analysis
Extract features from high-scoring ideas:
- Word frequencies
- Market categories
- Problem types
- Business model patterns
Guide Agent 0 to replicate winning patterns

### C. A/B Testing Framework
Systematically test hypotheses:
- Does including examples improve scores? By how much?
- Does self-critique help?
- Which constraint sets produce best ideas?

---

## 7. Meta-Optimization

### A. Hyperparameter Tuning
Optimize system parameters:
- `INNER_LOOP_MAX_ATTEMPTS` (currently 5)
- `SCREENING_THRESHOLD` (currently 50/80)
- Temperature/top_p for generation
- Number of outer rounds

### B. Reward Shaping
Modify the reward function to encourage better exploration:
- Bonus for novelty (Levenshtein distance from prior ideas)
- Penalty for generic language
- Progressive rewards: +10 for each tier crossed

```python
shaped_reward = base_score + novelty_bonus - generic_penalty
```

---

## Practical Implementation Roadmap

### Quick Wins (Low Effort, High Impact)

1. **Best-of-N Sampling** (in inner loop)
   - Generate 3 ideas per attempt instead of 1
   - Pick highest scoring
   - Expected improvement: +5-10 points

2. **Hall of Fame Examples**
   - Save top 5 ideas ever generated
   - Include in Agent 0 context
   - Show what "great" looks like

3. **Explicit Dimension Reasoning**
   - Force Agent 0 to pre-score itself on each dimension
   - Catches oversights before submission

### Medium Effort

4. **Multi-Model Ensemble**
   - Run Agent 0 with GPT-5, Claude, and Gemini
   - Evaluate all 3, pick best
   - Diversifies generation strategy

5. **Self-Critique Loop**
   - Agent 0 generates → self-evaluates → revises → submits
   - Catches obvious mistakes

6. **Adaptive Constraints**
   - Track which constraints correlate with high scores
   - Use curriculum learning

### Long-Term Investment

7. **Fine-Tune Agent 0**
   - Collect 100+ high-scoring ideas
   - Fine-tune GPT-4 or Claude on this dataset
   - Creates domain-specialized generator

8. **True RL Pipeline**
   - Use PPO or DPO to optimize generation
   - Requires infrastructure but maximizes performance

---

## The Meta-Game Insight

What makes this system fascinating is it's playing a **meta-game**: learning to optimize for an evaluation function. The better Agent 0 gets at this, the more it reveals about what the evaluation criteria *actually* value versus what you *think* they value.

This creates a virtuous cycle:
- Agent 0 gets better at gaming the system
- You discover weaknesses in your rubric
- You refine the evaluation criteria
- Agent 0 adapts to new criteria
- Repeat

This is essentially **co-evolution** of generator and evaluator, which is how many real AI systems (GANs, RLHF models) improve over time.

---

## References & Further Reading

- **RLHF**: Christiano et al. "Deep Reinforcement Learning from Human Preferences"
- **Constitutional AI**: Anthropic's approach to AI alignment through self-critique
- **PPO**: Schulman et al. "Proximal Policy Optimization Algorithms"
- **Best-of-N**: Common practice in LLM inference optimization
- **Multi-Armed Bandits**: Auer et al. "Finite-time Analysis of the Multiarmed Bandit Problem"
