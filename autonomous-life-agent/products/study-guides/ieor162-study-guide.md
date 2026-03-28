# IEOR 162 — Linear Programming & Network Flows: Complete Study Guide
## UC Berkeley | Spring 2026

> **Covers all major LP topics: simplex method, duality, sensitivity analysis, network flows, and integer programming.**

---

## Table of Contents

1. [Linear Programming Fundamentals](#1-linear-programming-fundamentals)
2. [Graphical Method](#2-graphical-method)
3. [Simplex Method](#3-simplex-method)
4. [Duality Theory](#4-duality-theory)
5. [Sensitivity Analysis](#5-sensitivity-analysis)
6. [Transportation & Assignment Problems](#6-transportation--assignment-problems)
7. [Network Flow Models](#7-network-flow-models)
8. [Integer Programming](#8-integer-programming)
9. [Game Theory Basics](#9-game-theory-basics)
10. [Exam Cheat Sheet](#10-exam-cheat-sheet)

---

## 1. Linear Programming Fundamentals

### Standard Form

**Maximize:** z = c₁x₁ + c₂x₂ + ... + cₙxₙ

**Subject to:**
- a₁₁x₁ + a₁₂x₂ + ... + a₁ₙxₙ ≤ b₁
- a₂₁x₁ + a₂₂x₂ + ... + a₂ₙxₙ ≤ b₂
- x₁, x₂, ..., xₙ ≥ 0

### Converting to Standard Form

| Original | Conversion |
|----------|-----------|
| Minimize z | Maximize -z |
| ≥ constraint | Multiply by -1 → ≤ |
| = constraint | Replace with ≤ and ≥ |
| Unrestricted xᵢ | Replace with xᵢ⁺ - xᵢ⁻ (both ≥ 0) |

### Assumptions of LP
1. **Proportionality** — contribution is proportional to variable value
2. **Additivity** — total = sum of individual contributions
3. **Divisibility** — variables can be fractional
4. **Certainty** — all parameters are known constants

---

## 2. Graphical Method (2 Variables)

### Steps
1. Plot each constraint as a line
2. Shade the feasible region (intersection of all constraints)
3. Find corner points (vertices) of feasible region
4. Evaluate objective function at each corner point
5. Optimal solution is at the corner with best objective value

### Special Cases

| Case | What happens |
|------|-------------|
| Infeasible | No point satisfies all constraints |
| Unbounded | Objective can increase without limit |
| Multiple optima | Optimal on an entire edge (two corners tie) |
| Degenerate | Corner point has more than n binding constraints |

---

## 3. Simplex Method

### Setting Up the Tableau

Add slack variables to convert ≤ to =:

**Max** z = 5x₁ + 4x₂

- 6x₁ + 4x₂ + s₁ = 24
- x₁ + 2x₂ + s₂ = 6
- x₁, x₂, s₁, s₂ ≥ 0

### Simplex Tableau Format

| BV | z | x₁ | x₂ | s₁ | s₂ | RHS |
|----|---|----|----|----|----|-----|
| z  | 1 | -5 | -4 | 0  | 0  | 0   |
| s₁ | 0 | 6  | 4  | 1  | 0  | 24  |
| s₂ | 0 | 1  | 2  | 0  | 1  | 6   |

### Simplex Algorithm Steps

1. **Check optimality:** All coefficients in z-row ≥ 0? → STOP (optimal)
2. **Entering variable:** Most negative coefficient in z-row
3. **Leaving variable:** Minimum ratio test (RHS ÷ positive column entry)
4. **Pivot:** Row operations to make pivot column a unit vector
5. **Repeat**

### Minimum Ratio Test
- Only divide by **positive** entries in the pivot column
- If all entries ≤ 0 → problem is **unbounded**
- Ties → **degeneracy** (may cycle, but rare in practice)

### Big-M Method (for ≥ and = constraints)

For ≥ constraint: subtract surplus, add artificial variable
- aᵢ₁x₁ + ... ≥ bᵢ → aᵢ₁x₁ + ... - sᵢ + Aᵢ = bᵢ
- Add -MAᵢ to objective (for Max) where M is very large

For = constraint: add artificial variable only

---

## 4. Duality Theory

### Primal-Dual Pairs

| Primal (Max) | Dual (Min) |
|-------------|-----------|
| Max z = cx | Min w = yb |
| Ax ≤ b | yA ≥ c |
| x ≥ 0 | y ≥ 0 |

### Key Theorems

**Weak Duality:** For any feasible x (primal) and y (dual): cx ≤ yb

**Strong Duality:** If either has an optimal solution, both do, and cx* = y*b

**Complementary Slackness:**
- If xⱼ* > 0, then the j-th dual constraint is binding
- If yᵢ* > 0, then the i-th primal constraint is binding

### Reading the Dual Solution from Primal Tableau
The dual optimal values y* appear in the z-row under the slack variable columns of the final simplex tableau.

---

## 5. Sensitivity Analysis

### What Changes Can We Make Without Re-solving?

| Change | What to Check |
|--------|--------------|
| Objective coefficient (non-basic) | Does it stay ≤ its reduced cost? |
| Objective coefficient (basic) | Re-derive using B⁻¹ |
| RHS value bᵢ | New RHS = B⁻¹b still ≥ 0? |
| New variable | Is its reduced cost ≥ 0? |
| New constraint | Does current solution satisfy it? |

### 100% Rule (Simultaneous Changes)
Sum of (change / allowable change) ratios must be ≤ 100%.

### Shadow Prices
- Shadow price of constraint i = yᵢ* (dual variable)
- Interpretation: increasing bᵢ by 1 unit changes z* by yᵢ*
- Valid only within the allowable range

---

## 6. Transportation & Assignment Problems

### Transportation Problem

**Balanced:** Total supply = Total demand
If not balanced, add dummy supply/demand node.

### Northwest Corner Method (Initial BFS)
1. Start at top-left cell
2. Allocate min(supply, demand)
3. Cross out satisfied row or column
4. Move right or down
5. Repeat

### Stepping Stone Method (Optimality Check)
1. For each non-basic cell, find a loop
2. Calculate improvement = Σ(+cells costs) - Σ(-cells costs)
3. If any improvement < 0, current solution is not optimal
4. Enter the most negative, leave the smallest allocation on a minus cell

### Hungarian Algorithm (Assignment)
1. Row reduction (subtract row min from each row)
2. Column reduction (subtract column min from each column)
3. Cover all zeros with minimum number of lines
4. If lines = n → optimal; else adjust and repeat

---

## 7. Network Flow Models

### Max-Flow Min-Cut Theorem
Maximum flow from s to t = Minimum capacity of any s-t cut

### Ford-Fulkerson Algorithm
1. Find an augmenting path from s to t
2. Send maximum possible flow along it
3. Update residual graph
4. Repeat until no augmenting path exists

### Shortest Path
**Dijkstra's Algorithm:**
1. Set d(s) = 0, d(v) = ∞ for all other v
2. Select unvisited vertex u with smallest d(u)
3. For each neighbor v: if d(u) + w(u,v) < d(v), update d(v)
4. Mark u as visited
5. Repeat

### Minimum Spanning Tree
- **Kruskal:** Sort edges by weight, add cheapest that doesn't form a cycle
- **Prim:** Grow tree from a vertex, always add cheapest edge to a new vertex

---

## 8. Integer Programming

### Branch and Bound
1. Solve LP relaxation (ignore integer constraints)
2. If solution is integer → done
3. Pick a fractional variable xⱼ = f
4. Branch: create two subproblems (xⱼ ≤ ⌊f⌋ and xⱼ ≥ ⌈f⌉)
5. Solve each, prune if bound ≤ best known integer solution
6. Repeat

### Cutting Planes (Gomory)
Add constraints that cut off the fractional solution but keep all integer feasible points.

### Common IP Formulations

| Problem | Variables |
|---------|----------|
| Knapsack | xᵢ ∈ {0,1} (take item or not) |
| Set Cover | xⱼ ∈ {0,1} (use set or not) |
| Facility Location | yⱼ ∈ {0,1} (open facility or not) |
| TSP | xᵢⱼ ∈ {0,1} (use edge or not) |

---

## 9. Game Theory Basics

### Two-Person Zero-Sum Games

**Minimax Theorem:** max(min over columns) = min(max over rows) when mixed strategies allowed

**Solving 2×2 Games:**
Payoff matrix: [[a,b],[c,d]]
- Player 1 plays row 1 with probability p = (d-c)/((a-b)-(c-d))
- Value of game: v = (ad-bc)/((a-b)-(c-d))

### LP Formulation of Games
Any two-person zero-sum game can be solved as a pair of dual LPs.

---

## 10. Exam Cheat Sheet

### Must-Know Formulas

```
Standard form:    Max cx, s.t. Ax ≤ b, x ≥ 0
Dual:             Min yb, s.t. yA ≥ c, y ≥ 0
BFS:              x_B = B⁻¹b, x_N = 0
Reduced cost:     c̄ⱼ = cⱼ - c_B B⁻¹ Aⱼ
Shadow price:     y* = c_B B⁻¹
Optimal z:        z* = c_B B⁻¹ b
```

### Quick Decision Tree

```
Is it 2 variables? → Graphical method
Is it LP? → Simplex
Is it network? → Network simplex / Ford-Fulkerson
Integer required? → Branch and bound
Assignment? → Hungarian algorithm
Transportation? → NW corner + stepping stone
```

### Common Exam Mistakes
1. Forgetting to check if transportation problem is balanced
2. Wrong minimum ratio test (dividing by negative numbers)
3. Forgetting complementary slackness conditions
4. Not converting to standard form before applying simplex
5. Shadow price interpretation (per unit of RHS, not per unit of variable)

---

*Created for UC Berkeley IEOR 162 students. Good luck!*
