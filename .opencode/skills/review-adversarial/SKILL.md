---
name: review-adversarial
description: 'Adversarial review pattern (Judgment Day): parallel independent reviews from multiple perspectives, conflict detection, evidence-based verdicts, bounded native review with bundles, receipts, and gates. Trigger: When implementing code review, quality gates, or adversarial validation of agent-generated code.'
version: 1.0
metadata:
  phase:
    - quality
  layer:
    - testing
  enforcement: recommended
  depends_on:
    - code-review
    - framework-qa-validation
  consumed_by:
    - agent-qa
  agent_roles:
    - control-agent
  validation_profile: security
  mcp_usage: context7
---

## Purpose

Define the adversarial review pattern for the framework. Modeled after the "Judgment Day" pattern from Gentle-AI, this skill implements parallel independent reviews from multiple perspectives (security, reliability, performance, readability, correctness) with conflict resolution and evidence-based verdicts. Goes beyond traditional code review by running multiple review agents simultaneously and comparing their findings.

## When to use this skill

Activate this skill when:

- Reviewing mission-critical code before production deployment
- Validating agent-generated code that affects security or data integrity
- Running pre-merge quality gates for complex features
- Implementing Judgement Day review phase in SDD workflow
- Detecting conflicting recommendations between review perspectives
- Building evidence chains for compliance/audit requirements

**Do not** activate when:

- Reviewing trivial changes (typos, formatting) — use `code-review`
- Running automated linting (use linter in CI)
- Reviewing documentation changes

## Relation to other skills

| Skill | Relation | Description |
|-------|----------|-------------|
| `code-review` | Predecesora | Standard review patterns that adversarial review extends |
| `framework-qa-validation` | Predecesora | QA gates that adversarial review enforces |
| `security` | Complementaria | Security perspective reviewer focuses on OWASP, auth |
| `performance` | Complementaria | Performance perspective reviewer focuses on latency, memory |

## Adversarial Review Architecture

```
                  ┌─────────────────┐
                  │   Code Change    │
                  └────────┬────────┘
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                  ▼
   ┌──────────┐     ┌──────────┐       ┌──────────┐
   │ Security │     │Reliability│       │Readability│
   │ Reviewer │     │ Reviewer │  ...  │ Reviewer │
   └────┬─────┘     └────┬─────┘       └────┬─────┘
        │                │                 │
        └────────────────┼─────────────────┘
                         ▼
                  ┌────────────┐
                  │  Arbiter   │
                  │ (Conflict  │
                  │ Resolution)│
                  └─────┬──────┘
                        ▼
                 ┌─────────────┐
                 │   Verdict   │
                 │  (Go/No-Go) │
                 └─────────────┘
```

## Reviewer Perspectives

### Security Reviewer

```python
class SecurityReviewer:
    """Reviews code from security perspective only."""
    
    async def review(self, change: CodeChange) -> SecurityFindings:
        findings = []
        
        # OWASP Top 10 checks
        findings.extend(await self.check_injection(change))
        findings.extend(await self.check_broken_auth(change))
        findings.extend(await self.check_sensitive_data_exposure(change))
        findings.extend(await self.check_xxe(change))
        findings.extend(await self.check_broken_access_control(change))
        
        # Stack-specific checks
        findings.extend(await self.check_secrets_in_code(change))
        findings.extend(await self.check_unsafe_deserialization(change))
        
        return SecurityFindings(
            perspective="security",
            findings=findings,
            risk_level=self.calculate_risk(findings)
        )
```

### Reliability Reviewer

```python
class ReliabilityReviewer:
    """Reviews code from reliability and robustness perspective."""
    
    async def review(self, change: CodeChange) -> ReliabilityFindings:
        findings = []
        
        findings.extend(await self.check_error_handling(change))
        findings.extend(await self.check_null_safety(change))
        findings.extend(await self.check_race_conditions(change))
        findings.extend(await self.check_resource_leaks(change))
        findings.extend(await self.check_transaction_boundaries(change))
        findings.extend(await self.check_retry_logic(change))
        
        return ReliabilityFindings(
            perspective="reliability",
            findings=findings,
            robustness_score=self.calculate_robustness(findings)
        )
```

### Performance Reviewer

```python
class PerformanceReviewer:
    """Reviews code from performance perspective."""
    
    async def review(self, change: CodeChange) -> PerformanceFindings:
        findings = []
        
        findings.extend(await self.check_n_plus_one(change))
        findings.extend(await self.check_unnecessary_allocations(change))
        findings.extend(await self.check_blocking_io(change))
        findings.extend(await self.check_missing_indexes(change))
        findings.extend(await self.check_query_complexity(change))
        
        return PerformanceFindings(
            perspective="performance",
            findings=findings,
            complexity_score=self.calculate_complexity(findings)
        )
```

### Readability Reviewer

```python
class ReadabilityReviewer:
    """Reviews code from readability and maintainability perspective."""
    
    async def review(self, change: CodeChange) -> ReadabilityFindings:
        findings = []
        
        findings.extend(await self.check_naming_conventions(change))
        findings.extend(await self.check_function_length(change))
        findings.extend(await self.check_comment_quality(change))
        findings.extend(await self.check_code_duplication(change))
        findings.extend(await self.check_cyclomatic_complexity(change))
        
        return ReadabilityFindings(
            perspective="readability",
            findings=findings,
            clarity_score=self.calculate_clarity(findings)
        )
```

## Conflict Resolution (Arbiter)

```python
from enum import Enum
from dataclasses import dataclass

class Verdict(Enum):
    APPROVED = "approved"          # All reviewers agree: go ahead
    CONDITIONAL = "conditional"    # Minor issues: fix and auto-approve
    CONFLICTED = "conflicted"      # Reviewers disagree: human decision needed
    REJECTED = "rejected"          # Critical issues: must fix

@dataclass
class ReviewVerdict:
    verdict: Verdict
    consensus: dict[str, list[Finding]]  # Perspective -> agreed findings
    conflicts: list[Conflict]            # Disagreements between reviewers
    evidence: list[Evidence]             # Evidence chain for audit
    recommendation: str                  # Human-readable recommendation

class ReviewArbiter:
    async def arbitrate(self, *perspectives: ReviewFindings) -> ReviewVerdict:
        # 1. Find consensus (issues all reviewers agree on)
        consensus = self.find_consensus(*perspectives)
        
        # 2. Find conflicts (reviewers disagree)
        conflicts = self.find_conflicts(*perspectives)
        
        # 3. Build evidence chain
        evidence = self.build_evidence_chain(*perspectives)
        
        # 4. Determine verdict
        has_critical = any(f.severity == Severity.CRITICAL 
                          for persp in perspectives 
                          for f in persp.findings)
        
        if has_critical:
            return ReviewVerdict(Verdict.REJECTED, consensus, 
                                conflicts, evidence,
                                "Critical issues found — fix before proceeding")
        
        if conflicts:
            return ReviewVerdict(Verdict.CONFLICTED, consensus,
                                conflicts, evidence,
                                "Reviewers disagree — human review required")
        
        has_minor = any(f.severity == Severity.MINOR
                       for persp in perspectives
                       for f in persp.findings)
        
        if has_minor:
            return ReviewVerdict(Verdict.CONDITIONAL, consensus,
                                conflicts, evidence,
                                "Minor issues — fix and auto-approve")
        
        return ReviewVerdict(Verdict.APPROVED, consensus,
                            conflicts, evidence,
                            "All reviewers approve")

class Conflict:
    perspective_a: str
    perspective_b: str
    issue: str
    position_a: str
    position_b: str
    recommended_resolution: str  # What the arbiter suggests
```

## Bounded Native Review

```python
@dataclass
class ReviewBundle:
    """Groups implementation work for review."""
    id: str
    changes: list[CodeChange]
    receipts: list[Receipt]  # Content-bound proofs
    gates: list[Gate]        # Lifecycle checkpoints
    
    def is_complete(self) -> bool:
        return all(gate.passed for gate in self.gates)

@dataclass
class Receipt:
    """Content-bound proof that freezes a review candidate."""
    id: str
    bundle_id: str
    content_hash: str  # SHA-256 of reviewed content
    reviewer_identity: str
    timestamp: datetime
    signature: str  # Cryptographic signature of the review

    def verify(self, content: str) -> bool:
        """Verify the reviewed content hasn't changed."""
        current_hash = hashlib.sha256(content.encode()).hexdigest()
        return current_hash == self.content_hash

@dataclass
class Gate:
    """Lifecycle checkpoint for review progression."""
    id: str
    name: str
    passed: bool = False
    required_perspectives: list[str] = None  # Which reviewers must pass
    dependencies: list[str] = None  # Other gates that must complete first
    
    def can_proceed(self, completed_gates: set[str]) -> bool:
        if self.dependencies:
            return all(dep in completed_gates for dep in self.dependencies)
        return True
```

## Evidence Chain for Audit

```python
@dataclass
class EvidenceChain:
    """Immutable chain of review evidence for compliance."""
    entries: list[Evidence]
    chain_hash: str  # Hash of previous entry + current entry
    
    def add_entry(self, entry: Evidence) -> 'EvidenceChain':
        prev_hash = self.entries[-1].chain_hash if self.entries else ""
        entry.chain_hash = hashlib.sha256(
            f"{prev_hash}{entry.content_hash}{entry.timestamp.isoformat()}"
            .encode()
        ).hexdigest()
        self.entries.append(entry)
        return self
    
    def verify_integrity(self) -> bool:
        """Verify the chain hasn't been tampered with."""
        for i in range(1, len(self.entries)):
            expected = hashlib.sha256(
                f"{self.entries[i-1].chain_hash}"
                f"{self.entries[i].content_hash}"
                f"{self.entries[i].timestamp.isoformat()}"
                .encode()
            ).hexdigest()
            if expected != self.entries[i].chain_hash:
                return False
        return True

@dataclass
class Evidence:
    reviewer: str
    perspective: str
    content_hash: str
    timestamp: datetime
    chain_hash: str = ""
    findings: list[Finding]
    risk_level: RiskLevel
```

## Decision table

| Situation | Wrong response | Expected response |
|-----------|---------------|-------------------|
| Security reviewer finds injection | Log it as minor | Critical — reject, must fix |
| Two reviewers disagree | Pick one arbitrarily | Flag as conflict, escalate to human |
| Bundle incomplete | Skip remaining gates | Block until all gates pass |
| Evidence chain broken | Ignore | Halt — possible tampering |
| All reviewers approve | Just merge | Verify evidence chain, then approve |

## Verification checklist

- [ ] At least 3 perspectives configured (security, reliability, readability)
- [ ] Conflict resolution logic implemented
- [ ] Evidence chain verifiable
- [ ] Receipts cryptographically bound to content
- [ ] Gates have clear dependencies and pass conditions
- [ ] Risk levels properly assigned (CRITICAL > HIGH > MEDIUM > MINOR)
- [ ] Arbiter produces actionable verdict with evidence
