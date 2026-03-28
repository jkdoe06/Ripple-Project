# MATH 55 — Discrete Mathematics: Complete Study Guide
## UC Berkeley | Spring 2026

> **This guide covers every major topic in Math 55 with worked examples, proof strategies, and exam tips.**
> Created by a Berkeley student who took the course.

---

## Table of Contents

1. [Logic & Proofs](#1-logic--proofs)
2. [Sets, Functions, Sequences](#2-sets-functions-sequences)
3. [Algorithms & Complexity](#3-algorithms--complexity)
4. [Number Theory & Cryptography](#4-number-theory--cryptography)
5. [Induction & Recursion](#5-induction--recursion)
6. [Counting & Combinatorics](#6-counting--combinatorics)
7. [Discrete Probability](#7-discrete-probability)
8. [Relations](#8-relations)
9. [Graphs & Trees](#9-graphs--trees)
10. [Exam Strategy Guide](#10-exam-strategy-guide)

---

## 1. Logic & Proofs

### Propositional Logic

| Symbol | Name | Meaning |
|--------|------|---------|
| `¬` | Negation | NOT p |
| `∧` | Conjunction | p AND q |
| `∨` | Disjunction | p OR q |
| `→` | Implication | IF p THEN q |
| `↔` | Biconditional | p IF AND ONLY IF q |

### Truth Table Template

| p | q | ¬p | p∧q | p∨q | p→q | p↔q |
|---|---|----|-----|-----|-----|-----|
| T | T | F  | T   | T   | T   | T   |
| T | F | F  | F   | T   | F   | F   |
| F | T | T  | F   | T   | T   | F   |
| F | F | T  | F   | F   | T   | T   |

**Key insight:** `p → q` is only FALSE when p is TRUE and q is FALSE.

### Proof Strategies

**Direct Proof:** Assume p, derive q step by step.
- Example: Prove "if n is even, then n² is even"
- Assume n = 2k for some integer k
- Then n² = (2k)² = 4k² = 2(2k²), which is even ✓

**Proof by Contradiction:** Assume ¬(statement), derive a contradiction.
- Example: Prove √2 is irrational
- Assume √2 = a/b in lowest terms
- Then 2b² = a², so a is even → a = 2c
- Then 2b² = 4c² → b² = 2c², so b is even
- Contradiction: a/b was supposed to be in lowest terms ✓

**Proof by Contrapositive:** To prove p → q, prove ¬q → ¬p instead.

**Proof by Cases:** Split into exhaustive cases, prove each.

---

## 2. Sets, Functions, Sequences

### Set Operations

| Operation | Notation | Meaning |
|-----------|----------|---------|
| Union | A ∪ B | Elements in A or B (or both) |
| Intersection | A ∩ B | Elements in both A and B |
| Difference | A − B | Elements in A but not B |
| Complement | Ā | Elements not in A |
| Symmetric Difference | A ⊕ B | Elements in A or B but not both |
| Power Set | P(A) | Set of all subsets of A |
| Cartesian Product | A × B | Set of all ordered pairs (a,b) |

**Key formulas:**
- |P(A)| = 2^|A|
- |A ∪ B| = |A| + |B| − |A ∩ B|
- |A × B| = |A| · |B|

### Functions

- **Injective (one-to-one):** f(a) = f(b) → a = b
- **Surjective (onto):** For every y in codomain, ∃x such that f(x) = y
- **Bijective:** Both injective and surjective (has an inverse)

### Common Sequences

| Sequence | Formula | First terms |
|----------|---------|-------------|
| Arithmetic | a_n = a₁ + (n-1)d | 1, 3, 5, 7, ... (d=2) |
| Geometric | a_n = a₁ · r^(n-1) | 1, 2, 4, 8, ... (r=2) |
| Fibonacci | F_n = F_{n-1} + F_{n-2} | 0, 1, 1, 2, 3, 5, 8, ... |
| Triangular | T_n = n(n+1)/2 | 1, 3, 6, 10, 15, ... |

---

## 3. Algorithms & Complexity

### Big-O Hierarchy (slowest → fastest growing)

```
O(1) < O(log n) < O(√n) < O(n) < O(n log n) < O(n²) < O(n³) < O(2ⁿ) < O(n!)
```

### Common Algorithm Complexities

| Algorithm | Time | Space |
|-----------|------|-------|
| Linear search | O(n) | O(1) |
| Binary search | O(log n) | O(1) |
| Bubble sort | O(n²) | O(1) |
| Merge sort | O(n log n) | O(n) |
| Dijkstra's | O(E log V) | O(V) |

---

## 4. Number Theory & Cryptography

### Division Algorithm
For any integers a, d (d > 0): a = dq + r, where 0 ≤ r < d

### GCD & Euclidean Algorithm
```
gcd(252, 198):
  252 = 1·198 + 54
  198 = 3·54 + 36
  54  = 1·36 + 18
  36  = 2·18 + 0
  → gcd = 18
```

### Modular Arithmetic

| Property | Rule |
|----------|------|
| Addition | (a + b) mod m = ((a mod m) + (b mod m)) mod m |
| Multiplication | (a · b) mod m = ((a mod m) · (b mod m)) mod m |
| Power | a^n mod m = use repeated squaring |

### RSA Overview
1. Choose primes p, q → n = pq
2. φ(n) = (p-1)(q-1)
3. Choose e coprime to φ(n)
4. Find d such that ed ≡ 1 (mod φ(n))
5. Encrypt: C = M^e mod n
6. Decrypt: M = C^d mod n

---

## 5. Induction & Recursion

### Mathematical Induction Template

1. **Base case:** Verify P(1) [or P(0)]
2. **Inductive hypothesis:** Assume P(k) is true for some arbitrary k
3. **Inductive step:** Prove P(k+1) using the hypothesis
4. **Conclusion:** By PMI, P(n) is true for all n ≥ 1

### Strong Induction
Same, but assume P(1), P(2), ..., P(k) are ALL true to prove P(k+1).

### Example: Prove 1 + 2 + ... + n = n(n+1)/2

**Base:** n=1: 1 = 1(2)/2 = 1 ✓
**IH:** Assume 1 + 2 + ... + k = k(k+1)/2
**IS:** 1 + 2 + ... + k + (k+1) = k(k+1)/2 + (k+1) = (k+1)(k+2)/2 ✓

---

## 6. Counting & Combinatorics

### The Big Four

| Type | Formula | Order matters? | Repetition? |
|------|---------|---------------|-------------|
| Permutation | n!/(n-r)! | Yes | No |
| Combination | n!/r!(n-r)! | No | No |
| Perm. w/ rep | n^r | Yes | Yes |
| Comb. w/ rep | (n+r-1)!/r!(n-1)! | No | Yes |

### Key Formulas

- **Binomial Theorem:** (x+y)^n = Σ C(n,k) · x^(n-k) · y^k
- **Inclusion-Exclusion:** |A₁ ∪ A₂ ∪ ... ∪ Aₙ| = Σ|Aᵢ| − Σ|Aᵢ∩Aⱼ| + ...
- **Pigeonhole Principle:** If n+1 objects go into n boxes, some box has ≥ 2

---

## 7. Discrete Probability

- **P(E)** = |E| / |S| (for equally likely outcomes)
- **P(A ∪ B)** = P(A) + P(B) − P(A ∩ B)
- **Conditional:** P(A|B) = P(A ∩ B) / P(B)
- **Bayes' Theorem:** P(A|B) = P(B|A)·P(A) / P(B)
- **Expected Value:** E(X) = Σ x·P(X=x)
- **Variance:** Var(X) = E(X²) − (E(X))²

---

## 8. Relations

### Properties

| Property | Definition | Example |
|----------|-----------|---------|
| Reflexive | (a,a) ∈ R for all a | ≤ on integers |
| Symmetric | (a,b) ∈ R → (b,a) ∈ R | = on integers |
| Antisymmetric | (a,b) ∈ R and (b,a) ∈ R → a = b | ≤ on integers |
| Transitive | (a,b) ∈ R and (b,c) ∈ R → (a,c) ∈ R | < on integers |

**Equivalence relation** = reflexive + symmetric + transitive
**Partial order** = reflexive + antisymmetric + transitive

---

## 9. Graphs & Trees

### Graph Types

| Type | Edges | Loops? | Multiple edges? |
|------|-------|--------|----------------|
| Simple | Undirected | No | No |
| Multigraph | Undirected | No | Yes |
| Digraph | Directed | Possible | Possible |

### Key Theorems

- **Handshaking:** Σ deg(v) = 2|E|
- **Euler circuit exists ↔** every vertex has even degree
- **Euler path exists ↔** exactly 0 or 2 vertices have odd degree
- **Tree with n vertices has** n-1 edges

### Graph Algorithms

| Algorithm | Purpose | Complexity |
|-----------|---------|-----------|
| BFS | Shortest path (unweighted) | O(V+E) |
| DFS | Connectivity, cycles | O(V+E) |
| Dijkstra | Shortest path (weighted) | O(E log V) |
| Kruskal | Minimum spanning tree | O(E log E) |
| Prim | Minimum spanning tree | O(E log V) |

---

## 10. Exam Strategy Guide

### Time Management
- **Read all problems first** (2 min)
- **Do easy problems first** — bank points
- **Proof problems last** — they take longest
- **Leave 5 min to review**

### Common Mistakes to Avoid
1. Forgetting the base case in induction
2. Confusing permutations and combinations
3. Off-by-one errors in counting
4. Not checking all properties for equivalence relations
5. Assuming p → q means q → p

### Proof Writing Tips
- State what you're proving at the top
- Define variables ("Let n be an arbitrary integer")
- Show every step — don't skip algebra
- End with "Therefore..." restating the conclusion
- Box or underline your final answer

---

*Created for UC Berkeley students by a Berkeley student. Good luck on your exams!*
