# DHM Scoring Criteria Specification

**Document Version:** 1.0
**Date:** 27 January 2026
**Status:** Current Implementation + Identified Improvements

---

## Executive Summary

The Dependency Health Monitor (DHM) uses a weighted composite scoring algorithm to evaluate Python package health. This document defines the current scoring criteria, identifies issues discovered through analysis, and proposes improvements based on industry best practices.

---

## Table of Contents

1. [Scoring Philosophy](#scoring-philosophy)
2. [Current Algorithm Overview](#current-algorithm-overview)
3. [Component Scores](#component-scores)
   - [Security Score (35%)](#security-score-35)
   - [Maintenance Score (30%)](#maintenance-score-30)
   - [Community Score (20%)](#community-score-20)
   - [Popularity Score (15%)](#popularity-score-15)
   - [Code Quality Score (unused)](#code-quality-score-unused)
4. [Grade Thresholds](#grade-thresholds)
5. [Maintenance Status Classification](#maintenance-status-classification)
6. [Identified Issues](#identified-issues)
7. [Industry Comparison](#industry-comparison)
8. [Proposed Improvements](#proposed-improvements)
9. [Implementation Roadmap](#implementation-roadmap)

---

## Scoring Philosophy

DHM's scoring philosophy prioritizes **actionable security information** while providing a holistic view of package health:

1. **Security First**: Security vulnerabilities, especially open ones, should heavily impact scores
2. **Open vs Fixed Distinction**: Historical vulnerabilities that are patched should not penalize a package the same as active threats
3. **Maintenance Matters**: Abandoned packages pose long-term risk regardless of current security status
4. **Community Signals Quality**: Active communities correlate with faster bug fixes and better support
5. **Popularity as Validation**: High adoption provides implicit peer review

---

## Current Algorithm Overview

### Weighted Composite Formula

```
Overall Score = (Security × 0.35) + (Maintenance × 0.30) + (Community × 0.20) + (Popularity × 0.15)
```

### Weight Rationale

| Component    | Weight | Rationale                                                |
|--------------|--------|----------------------------------------------------------|
| Security     | 35%    | Direct risk impact; most immediate concern               |
| Maintenance  | 30%    | Long-term sustainability; affects future security        |
| Community    | 20%    | Support availability; bug fix velocity                   |
| Popularity   | 15%    | Peer validation; implicit vetting                        |

---

## Component Scores

### Security Score (35%)

**Purpose**: Evaluate current security posture based on known vulnerabilities.

**Key Innovation**: DHM distinguishes between **OPEN** vulnerabilities (affecting installed version) and **FIXED** vulnerabilities (historical, already patched).

#### Scoring Logic

| Condition                     | Score Impact                    |
|-------------------------------|---------------------------------|
| No vulnerabilities            | 100 (perfect)                   |
| OPEN Critical vulnerability   | -40 per vulnerability           |
| OPEN High vulnerability       | -25 per vulnerability           |
| OPEN Medium vulnerability     | -10 per vulnerability           |
| OPEN Low vulnerability        | -5 per vulnerability            |
| OPEN Info vulnerability       | -1 per vulnerability            |
| FIXED vulnerability           | -10% of above values (minor)    |

**Example Calculation**:
```
Package with 2 OPEN High + 5 FIXED Critical:
- OPEN penalty: 2 × 25 = 50
- FIXED penalty: 5 × 40 × 0.1 = 20
- Final score: 100 - 50 - 20 = 30
```

**Rationale for Open vs Fixed**:
- FIXED vulnerabilities indicate the package HAD issues but maintainers addressed them
- Many fixes may actually be a POSITIVE signal of responsive maintenance
- Historical vulns should be visible but not penalize current usage

#### Version Comparison

DHM performs version comparison to determine if vulnerabilities affect the installed version:

```python
def _is_version_fixed(installed_version, fixed_version):
    """Check if installed version >= fixed version."""
    # Uses semantic version comparison
    # Handles pre-release markers (alpha, beta, rc)
```

---

### Maintenance Score (30%)

**Purpose**: Evaluate ongoing maintenance activity and project sustainability.

**Base Score**: 50 (neutral starting point)

#### Scoring Factors

| Factor                        | Condition              | Points  |
|-------------------------------|------------------------|---------|
| **Release Recency**           |                        |         |
|                               | < 30 days              | +20     |
|                               | 30-90 days             | +15     |
|                               | 90-180 days            | +10     |
|                               | 180-365 days           | +5      |
|                               | > 2 years              | -10     |
| **Release Consistency**       |                        |         |
|                               | > 10 releases          | +10     |
|                               | 5-10 releases          | +5      |
| **Deprecation Status**        |                        |         |
|                               | Deprecated             | -20     |
| **Commit Frequency (30d)**    |                        |         |
|                               | > 1 commit/day         | +15     |
|                               | > 0.1 commit/day       | +10     |
|                               | Any commits            | +5      |
| **Issue Close Rate (90d)**    |                        |         |
|                               | > 80%                  | +10     |
|                               | 50-80%                 | +5      |
| **Archived Repository**       |                        |         |
|                               | Is archived            | -30     |

**Score Range**: 0-100 (clamped)

---

### Community Score (20%)

**Purpose**: Evaluate community size, engagement, and collaboration health.

**⚠️ IDENTIFIED BUG**: Current implementation starts at 0, not 50. Missing GitHub data results in 0 instead of neutral 50.

#### Current Scoring Factors

| Factor                        | Condition              | Points  |
|-------------------------------|------------------------|---------|
| **Contributors**              |                        |         |
|                               | > 100 contributors     | +30     |
|                               | 20-100 contributors    | +25     |
|                               | 5-20 contributors      | +20     |
|                               | 2-5 contributors       | +10     |
| **Stars**                     |                        |         |
|                               | > 10,000 stars         | +30     |
|                               | 1,000-10,000 stars     | +25     |
|                               | 100-1,000 stars        | +15     |
|                               | 10-100 stars           | +5      |
| **Forks**                     |                        |         |
|                               | > 100 forks            | +20     |
|                               | 10-100 forks           | +10     |
| **PR Merge Rate (90d)**       |                        |         |
|                               | > 70%                  | +20     |
|                               | 40-70%                 | +10     |

**Maximum Achievable**: 100 points
**Without GitHub Data**: Returns 50 (neutral) — CORRECT BEHAVIOR

---

### Popularity Score (15%)

**Purpose**: Evaluate adoption level as implicit quality validation.

**⚠️ IDENTIFIED BUG**: Current implementation starts at 0. Packages with no pypistats data get 0 instead of neutral 50.

#### Current Scoring Factors

| Factor                        | Condition              | Points  |
|-------------------------------|------------------------|---------|
| **Monthly Downloads**         |                        |         |
|                               | > 10M downloads        | +50     |
|                               | 1M-10M downloads       | +40     |
|                               | 100K-1M downloads      | +30     |
|                               | 10K-100K downloads     | +20     |
|                               | 1K-10K downloads       | +10     |
|                               | 100-1K downloads       | +5      |
| **Watchers**                  |                        |         |
|                               | > 1,000 watchers       | +30     |
|                               | 100-1,000 watchers     | +20     |
|                               | 10-100 watchers        | +10     |
| **Stars Bonus**               |                        |         |
|                               | > 5,000 stars          | +20     |

**Maximum Achievable**: 100 points

**⚠️ Issue**: Stars are counted in BOTH Community AND Popularity scores (double-counting)

---

### Code Quality Score (unused)

**Purpose**: Evaluate code quality signals.

**⚠️ IDENTIFIED BUG**: This score is calculated but NOT included in the weighted average.

#### Scoring Factors

| Factor                        | Condition              | Points  |
|-------------------------------|------------------------|---------|
| Base score                    |                        | 50      |
| Contributors > 5              |                        | +15     |
| Contributors 2-5              |                        | +10     |
| PR merge rate > 60%           |                        | +15     |
| PR merge rate 30-60%          |                        | +10     |
| Avg issue close < 7 days      |                        | +10     |
| Avg issue close 7-30 days     |                        | +5      |
| Not a fork                    |                        | +10     |

---

## Grade Thresholds

| Grade | Score Range | Interpretation                          |
|-------|-------------|-----------------------------------------|
| A     | 90-100      | Excellent health, minimal risk          |
| B     | 80-89       | Good health, low risk                   |
| C     | 70-79       | Acceptable health, moderate monitoring  |
| D     | 60-69       | Concerning health, investigate          |
| F     | 0-59        | Poor health, high risk, seek alternatives |

---

## Maintenance Status Classification

| Status      | Criteria                                    | Risk Level |
|-------------|---------------------------------------------|------------|
| ACTIVE      | Activity within 90 days                     | Low        |
| STABLE      | Activity within 1 year                      | Low        |
| SLOW        | Activity within 2 years                     | Medium     |
| MINIMAL     | Activity within 3 years                     | High       |
| ABANDONED   | No activity for 3+ years                    | Critical   |
| ARCHIVED    | Repository explicitly archived              | Critical   |
| DEPRECATED  | Package marked deprecated on PyPI           | Critical   |

---

## Identified Issues

### Critical Bugs

1. **Community Score Base = 0**
   - **Impact**: Packages without GitHub data score 0 instead of neutral 50
   - **Severity**: High — artificially lowers overall scores
   - **Fix**: Return 50.0 when `repo is None` (already implemented) but base score starts at 0 when repo exists

2. **Popularity Score Base = 0**
   - **Impact**: Packages with low downloads score near 0
   - **Severity**: High — newer packages unfairly penalized
   - **Fix**: Add base score of 50

3. **Code Quality Score Not Used**
   - **Impact**: Calculated but never included in weighted sum
   - **Severity**: Medium — wasted computation, missing signal
   - **Fix**: Either include in weights or remove calculation

4. **Stars Double-Counted**
   - **Impact**: Star count affects both Community AND Popularity scores
   - **Severity**: Medium — inflates GitHub-heavy packages
   - **Fix**: Use stars in only one component

5. **Grade Thresholds Misaligned**
   - **Impact**: With scoring bugs, most packages cluster at C/D
   - **Severity**: Medium — reduces grade utility
   - **Fix**: After fixing scoring bugs, re-evaluate thresholds

### Data Issues

1. **GitHub Rate Limiting**
   - Unauthenticated: 60 requests/hour
   - Missing data defaults to 0 scores (should be neutral)
   - Fix: Use None vs 0 to distinguish "missing" from "zero"

2. **pypistats.org API**
   - May return 0 for new packages
   - No distinction between "no data" and "zero downloads"

---

## Industry Comparison

### Scoring Approaches

| Tool              | Approach                                    | Key Differentiator              |
|-------------------|---------------------------------------------|----------------------------------|
| **DHM (current)** | Weighted composite (4 components)           | Open vs Fixed vuln distinction   |
| **Snyk Advisor**  | Normalized 0-100 with letter grades         | Supply chain awareness           |
| **Libraries.io**  | SourceRank algorithm (25+ signals)          | Cross-ecosystem comparison       |
| **OpenSSF**       | Pass/fail checks with confidence scores     | Security-focused, binary checks  |
| **deps.dev**      | Multi-faceted cards without single score    | Detailed signal breakdowns       |
| **npms.io**       | Quality/Maintenance/Popularity with Bezier  | Normalized logarithmic scaling   |

### Industry Best Practices

1. **Logarithmic Scaling**: Use log scales for stars, downloads (already done)
2. **Bezier Normalization**: Smooth curves instead of step functions
3. **Supply Chain Analysis**: Check for typosquatting, dependency confusion
4. **License Compliance**: Include license compatibility in scoring
5. **Dependency Graph**: Score transitive dependencies, not just direct

---

## Proposed Improvements

### Phase 1: Bug Fixes (Immediate)

1. **Fix Community Score Base**
   ```python
   def _calculate_community_score(self, repo):
       if not repo:
           return 50.0  # Neutral
       score = 50.0  # START AT 50, NOT 0
       # ... rest of calculation
   ```

2. **Fix Popularity Score Base**
   ```python
   def _calculate_popularity_score(self, pypi, repo):
       score = 50.0  # START AT 50, NOT 0
       # ... rest of calculation
   ```

3. **Remove Star Double-Counting**
   - Keep stars in Community Score (engagement signal)
   - Remove stars bonus from Popularity Score

4. **Decide on Code Quality Score**
   - Option A: Add 5% weight, reduce others proportionally
   - Option B: Remove calculation entirely

### Phase 2: Scoring Refinements (Short-term)

1. **Implement Bezier Normalization**
   - Replace step functions with smooth curves
   - Better differentiation across the score range

2. **Add License Scoring**
   - Identify license from PyPI metadata
   - Warn on restrictive/unclear licenses

3. **Improve Grade Thresholds**
   - After fixing bugs, analyze score distribution
   - Adjust thresholds for meaningful differentiation

### Phase 3: Advanced Features (Medium-term)

1. **Supply Chain Security**
   - Typosquatting detection (Levenshtein distance from popular packages)
   - Maintainer reputation scoring
   - Namespace confusion warnings

2. **Dependency Graph Analysis**
   - Score transitive dependencies
   - Identify "weakest link" in dependency tree
   - Calculate aggregate risk

3. **Trend Analysis**
   - Track score changes over time
   - Alert on declining health
   - Predict maintenance abandonment

---

## Implementation Roadmap

### Immediate (This Week)
- [ ] Fix Community Score base to 50
- [ ] Fix Popularity Score base to 50
- [ ] Remove star double-counting
- [ ] Decide Code Quality Score fate

### Short-term (Next 2 Sprints)
- [ ] Implement Bezier normalization
- [ ] Add license compliance scoring
- [ ] Re-calibrate grade thresholds
- [ ] Add confidence levels to scores

### Medium-term (Next Quarter)
- [ ] Supply chain security checks
- [ ] Dependency graph analysis
- [ ] Historical trend tracking
- [ ] Alternative package suggestions

---

## Appendix A: Vulnerability Severity Mapping

| CVSSv3 Score | DHM RiskLevel | Deduction |
|--------------|---------------|-----------|
| 9.0-10.0     | CRITICAL      | 40        |
| 7.0-8.9      | HIGH          | 25        |
| 4.0-6.9      | MEDIUM        | 10        |
| 0.1-3.9      | LOW           | 5         |
| 0.0 / Info   | INFO          | 1         |

---

## Appendix B: Data Sources

| Data Point              | Source                | Fallback    |
|-------------------------|----------------------|-------------|
| Package metadata        | PyPI JSON API        | None        |
| Download statistics     | pypistats.org        | 0           |
| Repository metrics      | GitHub API           | Neutral (50)|
| Vulnerabilities         | OSV (Open Source Vulnerabilities) | Empty list |

---

## Appendix C: Example Score Calculations

### Example 1: Well-Maintained Popular Package

**Package**: requests (hypothetical current state)
- **Security**: 100 (no open vulns)
- **Maintenance**: 85 (recent release, good commit frequency)
- **Community**: 95 (5000+ stars, 100+ contributors)
- **Popularity**: 100 (10M+ downloads)

**Overall**: (100×0.35) + (85×0.30) + (95×0.20) + (100×0.15) = 35 + 25.5 + 19 + 15 = **94.5 (A)**

### Example 2: Abandoned Package with Fixed Vulnerabilities

**Package**: old-but-patched
- **Security**: 78 (5 fixed critical vulns: 100 - 5×40×0.1 = 80, rounded)
- **Maintenance**: 20 (no release in 3 years)
- **Community**: 50 (no GitHub data)
- **Popularity**: 55 (moderate downloads)

**Overall**: (78×0.35) + (20×0.30) + (50×0.20) + (55×0.15) = 27.3 + 6 + 10 + 8.25 = **51.55 (F)**

### Example 3: New Package with Limited Data

**Package**: brand-new-tool
- **Security**: 100 (no vulns)
- **Maintenance**: 70 (single release)
- **Community**: 50 (new repo, few stars)
- **Popularity**: 50 (low downloads)

**Overall**: (100×0.35) + (70×0.30) + (50×0.20) + (50×0.15) = 35 + 21 + 10 + 7.5 = **73.5 (C)**

---

*Document maintained by DHM development team. Last updated: 27 January 2026.*
