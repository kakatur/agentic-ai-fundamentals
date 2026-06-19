# Visual Diagrams: Context Windows & Token Budgets

## 1. Context Window Anatomy

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CONTEXT WINDOW                                │
│                    (e.g., 16,384 tokens)                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  SYSTEM PROMPT                                (1,000 tokens)  │  │
│  │  - Instructions                                               │  │
│  │  - Personality                                                │  │
│  │  - Constraints                                                │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  TOOL DEFINITIONS                             (2,000 tokens)  │  │
│  │  - Function schemas                                           │  │
│  │  - Parameters                                                 │  │
│  │  - Descriptions                                               │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  RETRIEVED DOCUMENTS                          (5,000 tokens)  │  │
│  │  - Chunk 1                                                    │  │
│  │  - Chunk 2                                                    │  │
│  │  - Chunk 3                                                    │  │
│  │  - ...                                                        │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  CONVERSATION HISTORY                         (5,000 tokens)  │  │
│  │  - User: "..."                                                │  │
│  │  - Assistant: "..."                                           │  │
│  │  - User: "..."                                                │  │
│  │  - Assistant: "..."                                           │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  CURRENT USER MESSAGE                           (500 tokens)  │  │
│  │  "How do I implement feature X?"                             │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  RESPONSE BUFFER                              (2,000 tokens)  │  │
│  │  (reserved for model's response)                             │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  SAFETY BUFFER                                  (884 tokens)  │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## 2. The "Lost in the Middle" Problem

```
Context Window Attention Pattern:

Position in Context    Attention Level
│                      │
START ────────────────▶│ ████████████ HIGH
                       │
                       │
                       │
MIDDLE ───────────────▶│ ████ LOW (gets ignored!)
                       │
                       │
                       │
END ──────────────────▶│ ████████████ HIGH
                       │
```

**Solution: Position-Aware Placement**

```
┌─────────────────────────────────────────────────────────────┐
│  SYSTEM PROMPT (critical instructions)                      │
│  ↓ HIGH ATTENTION                                           │
├─────────────────────────────────────────────────────────────┤
│  MEDIUM RELEVANCE DOCS                                      │
│  - Doc 4 (score: 0.75)                                      │
│  - Doc 5 (score: 0.70)                                      │
│  - Doc 6 (score: 0.65)                                      │
│  ↓ MEDIUM ATTENTION                                         │
├─────────────────────────────────────────────────────────────┤
│  CONVERSATION HISTORY                                       │
│  ↓ LOW ATTENTION (but less critical)                       │
├─────────────────────────────────────────────────────────────┤
│  HIGHEST RELEVANCE DOCS                                     │
│  - Doc 1 (score: 0.95) ← Place best docs here!            │
│  - Doc 2 (score: 0.90)                                      │
│  - Doc 3 (score: 0.85)                                      │
│  ↓ HIGH ATTENTION                                           │
├─────────────────────────────────────────────────────────────┤
│  CURRENT USER QUERY                                         │
│  ↓ HIGHEST ATTENTION                                        │
└─────────────────────────────────────────────────────────────┘
```

## 3. Token Budget Allocation by Query Complexity

```
SIMPLE QUERY ("What's your return policy?")
┌──────────────────────────────────────────┐
│ System + Tools    ████████ (30%)        │
│ Retrieval         ██ (10%)              │  ← Less retrieval needed
│ History           ████████████ (50%)    │  ← More history for context
│ Response          ██ (5%)               │
│ Buffer            ██ (5%)               │
└──────────────────────────────────────────┘

MEDIUM QUERY ("How does your warranty compare to competitors?")
┌──────────────────────────────────────────┐
│ System + Tools    ████████ (30%)        │
│ Retrieval         ██████ (25%)          │  ← Balanced
│ History           ██████ (30%)          │  ← Balanced
│ Response          ████ (10%)            │
│ Buffer            ██ (5%)               │
└──────────────────────────────────────────┘

COMPLEX QUERY ("Analyze all feedback and identify top 5 trends")
┌──────────────────────────────────────────┐
│ System + Tools    ████████ (30%)        │
│ Retrieval         ████████████ (45%)    │  ← Lots of data needed
│ History           ██ (5%)               │  ← Less history needed
│ Response          ██████ (15%)          │  ← Longer response
│ Buffer            ██ (5%)               │
└──────────────────────────────────────────┘
```

## 4. Conversation History Truncation Strategies

### Strategy A: Sliding Window
```
Original History (30 messages):
[1] [2] [3] [4] [5] [6] [7] [8] [9] [10] ... [28] [29] [30]

After Truncation (keep last 10):
                                             [21] [22] [23] [24] [25] [26] [27] [28] [29] [30]

Pros: Simple, keeps recent context
Cons: Loses all early context
```

### Strategy B: Preserve First + Last
```
Original History (30 messages):
[1] [2] [3] [4] [5] [6] [7] [8] [9] [10] ... [28] [29] [30]

After Truncation (keep first 3 + last 5):
[1] [2] [3]                                  [26] [27] [28] [29] [30]

Pros: Keeps initial context and recent messages
Cons: Loses middle context
```

### Strategy C: Preserve Message Pairs
```
Original History (10 messages):
[U1] [A1] [U2] [A2] [U3] [A3] [U4] [A4] [U5] [A5]
 └─┬─┘     └─┬─┘     └─┬─┘     └─┬─┘     └─┬─┘
  Pair 1   Pair 2   Pair 3   Pair 4   Pair 5

After Truncation (keep last 3 pairs):
                     [U3] [A3] [U4] [A4] [U5] [A5]
                      └─┬─┘     └─┬─┘     └─┬─┘
                      Pair 3   Pair 4   Pair 5

Pros: Maintains Q&A coherence
Cons: Drops complete pairs only
```

## 5. Retrieval Truncation Decision Tree

```
                    Need to Reduce Retrieved Docs?
                                │
                                ├─YES
                                │
                    ┌───────────┴───────────┐
                    │                       │
         Need ALL represented?        Want ONLY best?
                    │                       │
                   YES                     YES
                    │                       │
                    ▼                       ▼
         ┌─────────────────────┐   ┌──────────────────┐
         │  PROPORTIONAL        │   │  TOP-N           │
         │  Trim each equally   │   │  Keep best only  │
         └─────────────────────┘   └──────────────────┘
                    
                    │                       │
         Context > 10K tokens?    Docs redundant?
                    │                       │
                   YES                     YES
                    │                       │
                    ▼                       ▼
         ┌─────────────────────┐   ┌──────────────────┐
         │  POSITION-AWARE      │   │  DIVERSE (MMR)   │
         │  Combat lost-in-mid  │   │  Max coverage    │
         └─────────────────────┘   └──────────────────┘
```

## 6. Cost Calculation

```
Request: 50K input + 2K output tokens

┌──────────────────────────────────────────────────────────┐
│ input_cost  = 50,000 / 1M × current input price         │
│ output_cost =  2,000 / 1M × current output price        │
│ total_cost  = input_cost + output_cost + tool fees      │
└──────────────────────────────────────────────────────────┘

Load current prices from reviewed configuration.
Account for cached input, long-context rates, service tiers, and tool fees.
```

See the current provider pricing page before publishing numeric estimates.

## 7. Context Utilization Over Time

```
Context Utilization (%) over Conversation Length

100% │                                              ╱──  Context Limit
     │                                         ╱────
     │                                    ╱────
     │                               ╱────
 75% │                          ╱────
     │                     ╱────
     │                ╱────  ← Implement truncation here
     │           ╱────
 50% │      ╱────
     │ ╱────
     │─────
     │
 25% │
     │
     └──────────────────────────────────────────────────────
       5    10   15   20   25   30   35   40   45   50
              Number of Conversation Turns
```

## 8. Smart Routing by Context Size

```
Incoming Request
       │
       ▼
┌─────────────────┐
│ Estimate Tokens │
└────────┬────────┘
         │
    ┌────────────┼────────────┐
    │            │            │
 Fits small   Fits medium   Needs large
 safe limit   safe limit    context
    │            │            │
    ▼            ▼            ▼
┌──────────┐ ┌──────────┐ ┌──────────────┐
│ Candidate│ │ Candidate│ │ Large-context│
│ model A  │ │ model B  │ │ candidate    │
└──────────┘ └──────────┘ └──────────────┘

Choose candidates using measured quality, latency, availability, and cost.
Context capacity alone is not a routing strategy.
```

## 9. Message Overhead Visualization

```
Raw Content vs. Formatted Messages

Raw Text Only:
┌─────────────────────────────┐
│ "You are helpful"           │  50 tokens
│ "What is Python?"           │
│ "Python is a language"      │
└─────────────────────────────┘

Provider Request Format:
┌─────────────────────────────┐
│ message wrapper             │  ← variable
│ "You are helpful"           │  50 tokens
│ role and content metadata   │
│ "What is Python?"           │
│ tool schemas, if any        │
│ "Python is a language"      │
└─────────────────────────────┘

Overhead is model- and request-shape-specific.
Use the provider's complete-request token-counting API.
```

## 10. Budget Monitoring Dashboard (Conceptual)

```
┌─────────────────────────────────────────────────────────────┐
│                    TOKEN USAGE DASHBOARD                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Average Input:  12,543 tokens  ████████████░░░░ 78%       │
│  Average Output:  1,234 tokens  ██░░░░░░░░░░░░░░ 8%        │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Utilization Over Time                               │   │
│  │                                                      │   │
│  │  100% │                                          ╱  │   │
│  │       │                                      ╱───   │   │
│  │   75% │                                 ╱────      │   │
│  │       │ Alert threshold ──────────────────────    │   │
│  │   50% │                          ╱────             │   │
│  │       │                     ╱────                  │   │
│  │   25% │                ╱────                       │   │
│  │       │───────────────                             │   │
│  │     0%└────────────────────────────────────────    │   │
│  │        Mon  Tue  Wed  Thu  Fri  Sat  Sun          │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  Token Budget Breakdown:                                    │
│  ┌────────────────────┐  30% System/Tools (4,800)         │
│  ├────────────────────┤  35% Retrieval    (5,600)         │
│  ├────────────────────┤  25% History      (4,000)         │
│  └────────────────────┘  10% Other                         │
│                                                              │
│  ⚠ Alerts:                                                  │
│  • P95 utilization: 89% (threshold: 85%)                   │
│  • Cost/request increased 15% this week                     │
│  • 127 requests hit context limit today                     │
│                                                              │
│  💡 Recommendations:                                        │
│  • Evaluate a larger-context route or stronger compression  │
│  • Implement aggressive history truncation                  │
│  • Review retrieval strategy (too many chunks?)            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 11. Truncation Strategy Performance Matrix

```
┌────────────────┬─────────┬────────────┬───────────┬──────────────┐
│   Strategy     │  Speed  │  Quality   │ Use Case  │ Complexity   │
├────────────────┼─────────┼────────────┼───────────┼──────────────┤
│ Simple         │ ⚡⚡⚡   │ ⭐⭐       │ Speed     │ Easy         │
│ Sliding        │         │            │ priority  │              │
├────────────────┼─────────┼────────────┼───────────┼──────────────┤
│ Preserve       │ ⚡⚡     │ ⭐⭐⭐     │ Chatbots  │ Medium       │
│ Pairs          │         │            │           │              │
├────────────────┼─────────┼────────────┼───────────┼──────────────┤
│ Selective      │ ⚡⚡     │ ⭐⭐⭐⭐   │ Long conv │ Medium       │
│ (First+Last)   │         │            │           │              │
├────────────────┼─────────┼────────────┼───────────┼──────────────┤
│ Position-      │ ⚡       │ ⭐⭐⭐⭐⭐ │ RAG       │ Hard         │
│ Aware          │         │            │           │              │
├────────────────┼─────────┼────────────┼───────────┼──────────────┤
│ Diverse        │ ⚡       │ ⭐⭐⭐⭐   │ Redundant │ Hard         │
│ (MMR)          │         │            │ docs      │              │
└────────────────┴─────────┴────────────┴───────────┴──────────────┘

Choose based on:
• Speed critical? → Simple Sliding
• Chatbot? → Preserve Pairs
• RAG system? → Position-Aware
• Redundant docs? → Diverse (MMR)
• Complex long conversations? → Selective (First+Last)
```

## 12. Token Flow in a Production Request

```
1. User Message Arrives
   ↓
2. Classify Query Complexity
   ├─ Simple:  Small budget
   ├─ Medium:  Medium budget
   └─ Complex: Large budget
   ↓
3. Retrieve Documents
   ├─ Get top N chunks
   ├─ Calculate tokens
   └─ Apply truncation strategy
   ↓
4. Prepare Conversation History
   ├─ Count total tokens
   ├─ Check against budget
   └─ Truncate if needed
   ↓
5. Count All Components
   ├─ System prompt
   ├─ Tools
   ├─ Retrieval
   ├─ History
   └─ Current message
   ↓
6. Validate Against Limit
   ├─ Fits? → Proceed
   └─ Overflow? → Aggressive truncation
   ↓
7. Build API Request
   ↓
8. Send to LLM
   ↓
9. Receive Response
   ↓
10. Log Metrics
    ├─ Input tokens (actual)
    ├─ Output tokens (actual)
    ├─ Cost
    ├─ Utilization %
    └─ Truncation stats
    ↓
11. Update Usage History
    (for future optimization)
```

These diagrams are conceptual. Validate their assumptions with the model,
request shape, and production data used by your application.
