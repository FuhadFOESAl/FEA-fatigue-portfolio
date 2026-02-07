# FEA Verification Checklist

**Project:** L-Bracket Fatigue Analysis  
**Part Number:** LB-2024-001  
**Analyst:** [Your Name]  
**Date:** [Analysis Date]  
**Software:** CalculiX CCX 2.21 + PrePoMax  
**Status:** ⬜ In Progress / ⬜ Complete

---

## Section 1: Pre-Analysis Checks

### 1.1 Model Geometry
| Check | Status | Notes |
|-------|--------|-------|
| CAD import successful | ⬜ | Verify no lost features |
| Units consistent (mm, N, MPa) | ⬜ | Check CAD export units |
| Critical dimensions match drawing | ⬜ | H=100, L=80, T=6, W=50 |
| Hole diameters correct (10mm) | ⬜ | Verify clearance for M10 |
| No unintended gaps/penetrations | ⬜ | Check CAD for errors |

### 1.2 Material Definition
| Check | Status | Notes |
|-------|--------|-------|
| E = 68.9 GPa entered correctly | ⬜ | Verify in material card |
| ν = 0.33 entered correctly | ⬜ | Verify in material card |
| Density = 2700 kg/m³ | ⬜ | For mass calculation |
| Units consistent | ⬜ | MPa, mm, tonne system |

### 1.3 Property Assignment
| Check | Status | Notes |
|-------|--------|-------|
| Material assigned to all parts | ⬜ | Check color coding |
| Section properties correct | ⬜ | Solid section, uniform |
| Orientation correct | ⬜ | No element distortion |

---

## Section 2: Mesh Verification

### 2.1 Mesh Convergence Study
| Mesh | Element Size (mm) | Element Count | Max Stress (MPa) | Change (%) | Status |
|------|-------------------|---------------|------------------|------------|--------|
| 1 (Coarse) | 10 | ~500 | ___ | - | ⬜ |
| 2 | 6 | ~1,500 | ___ | ___% | ⬜ |
| 3 (Medium) | 4 | ~4,000 | ___ | ___% | ⬜ |
| 4 | 2.5 | ~12,000 | ___ | ___% | ⬜ |
| 5 (Fine) | 1.5 | ~35,000 | ___ | ___% | ⬜ |

**Convergence Criterion:** < 5% stress change between final two meshes  
**Selected Mesh:** Mesh ___ for production runs

### 2.2 Mesh Quality Metrics
| Check | Criterion | Actual | Status |
|-------|-----------|--------|--------|
| Min element quality | > 0.1 (0-1 scale) | ___ | ⬜ |
| Max aspect ratio | < 10:1 | ___ | ⬜ |
| Elements through thickness | ≥ 2 | ___ | ⬜ |
| Jacobian (min) | > 0.6 | ___ | ⬜ |
| Warping angle (max) | < 30° | ___ | ⬜ |

### 2.3 Mesh Refinement
| Location | Refined? | Element Size | Justification |
|----------|----------|--------------|---------------|
| Hole perimeters | ⬜ | ___ mm | Stress concentration |
| Corner region | ⬜ | ___ mm | Stress concentration |
| Load application | ⬜ | ___ mm | Accuracy |
| Constraint areas | ⬜ | ___ mm | Reaction accuracy |

---

## Section 3: Boundary Condition Verification

### 3.1 Constraint Check
| Check | Status | Expected | Actual |
|-------|--------|----------|--------|
| Vertical leg holes constrained | ⬜ | All DOFs | ___ |
| No over-constraint | ⬜ | Free to deform | ___ |
| No rigid body modes | ⬜ | 0 eigenvalues | ___ |

### 3.2 Load Verification
| Load Case | Applied Force (N) | Direction | Distribution | Status |
|-----------|-------------------|-----------|--------------|--------|
| LC1 | 490.5 | -Z | Uniform pressure | ⬜ |
| LC2 | 1471.5 | -Z | Uniform pressure | ⬜ |
| LC3 Mean | 490.5 | -Z | Uniform pressure | ⬜ |
| LC3 Alt | ±196.2 | -Z | Uniform pressure | ⬜ |

---

## Section 4: Equilibrium Verification

### 4.1 Reaction Force Balance (LC2 - Critical Case)

| Direction | Applied Force (N) | Sum Reactions (N) | Difference (N) | Error (%) | Status |
|-----------|-------------------|-------------------|----------------|-----------|--------|
| X | 0 | ___ | ___ | ___% | ⬜ |
| Y | 0 | ___ | ___ | ___% | ⬜ |
| Z | -1471.5 | ___ | ___ | ___% | ⬜ |

**Acceptance Criterion:** |Error| < 0.1%  
**Result:** ⬜ PASS / ⬜ FAIL

### 4.2 Free Body Diagram Check
```
Sketch expected reaction distribution:

    [Equipment Load: 1471.5 N ↓]
         ___________
        /           \
       /   H-leg     \
      /               \
     /    Corner       \
    /___________________\
    |                   |
    |    V-leg          |
    |  ○           ○    |  ← Two bolt holes
    |___________________|
         ↑          ↑
    [Reactions: 735.75 N each]
```

| Check | Expected | Actual | Status |
|-------|----------|--------|--------|
| Total reaction = applied | 1471.5 N | ___ N | ⬜ |
| Symmetric distribution | ~50/50 | ___% / ___% | ⬜ |
| Moment equilibrium | ΣM = 0 | ΣM = ___ | ⬜ |

---

## Section 5: Stress Results Verification

### 5.1 Stress Sanity Checks
| Check | Criterion | Actual | Status |
|-------|-----------|--------|--------|
| Max stress location | Corner or hole | ___ | ⬜ |
| Max stress < Sy | 276 MPa | ___ MPa | ⬜ |
| Stress at constraint | < 2× global max | ___ MPa | ⬜ |
| No negative pressures | All ≥ 0 | ___ | ⬜ |

### 5.2 Stress Concentration Validation
| Location | FEA Stress (MPa) | Nominal Stress (MPa) | Kt (FEA) | Kt (Theory) | Error | Status |
|----------|------------------|----------------------|----------|-------------|-------|--------|
| Hole edge | ___ | ___ | ___ | 3.0 | ___% | ⬜ |
| Corner | ___ | ___ | ___ | ~4.5* | ___% | ⬜ |

*Sharp corner theoretical Kt → ∞, use engineering judgment

### 5.3 Principal Stress Check
| Check | σ1 (MPa) | σ2 (MPa) | σ3 (MPa) | τmax (MPa) | Status |
|-------|----------|----------|----------|------------|--------|
| At max location | ___ | ___ | ___ | ___ | ⬜ |
| σ1 ≥ σ2 ≥ σ3 | ⬜ Verify ordering | | | | |

---

## Section 6: Displacement Verification

### 6.1 Deflection Check
| Check | Expected | Actual | Status |
|-------|----------|--------|--------|
| Max deflection location | Free end | ___ | ⬜ |
| Deflection direction | -Z | ___ | ⬜ |
| Max deflection < limit | 2.0 mm | ___ mm | ⬜ |
| Deflection pattern reasonable | Smooth curve | ⬜ Visual | |

### 6.2 Hand Calculation Check (Cantilever Approximation)
```
δ = FL³ / (3EI)

Where:
F = 1471.5 N
L = 80 mm (effective cantilever)
E = 68900 MPa
I = (50 × 6³) / 12 = 900 mm⁴

δ_hand = 1471.5 × 80³ / (3 × 68900 × 900)
δ_hand = ___ mm
```

| Method | Deflection (mm) | Status |
|--------|-----------------|--------|
| Hand calc | ___ | - |
| FEA | ___ | - |
| Difference | ___% | ⬜ < 20% |

---

## Section 7: Fatigue Verification

### 7.1 Stress Extraction Check
| Parameter | Symbol | Value | Unit | Status |
|-----------|--------|-------|------|--------|
| Max principal stress | σ_max | ___ | MPa | ⬜ |
| Min principal stress | σ_min | ___ | MPa | ⬜ |
| Alternating stress | Sa | ___ | MPa | ⬜ |
| Mean stress | Sm | ___ | MPa | ⬜ |
| Stress ratio | R | ___ | - | ⬜ |

### 7.2 Goodman Diagram Check
```
Sa/Se + Sm/Su ≤ 1/FoS

Sa = ___ MPa
Sm = ___ MPa
Se = 96 MPa
Su = 310 MPa

LHS = ___/96 + ___/310 = ___
FoS_fatigue = 1/LHS = ___
```

| Check | Criterion | Actual | Status |
|-------|-----------|--------|--------|
| Goodman sum | < 0.5 (for FoS=2) | ___ | ⬜ |
| FoS_fatigue | > 2.0 | ___ | ⬜ |

### 7.3 Life Estimate Check
```
N = (Sa / σ'f)^(1/b)

σ'f = 410 MPa
b = -0.085
Sa = ___ MPa

N = ___ cycles
```

| Check | Criterion | Actual | Status |
|-------|-----------|--------|--------|
| Predicted life | > 10^6 cycles | ___ | ⬜ |
| Life safety factor | > 2× design life | ___ | ⬜ |

---

## Section 8: Documentation Check

| Item | Status | Location |
|------|--------|----------|
| Analysis report generated | ⬜ | reports/ |
| All plots saved | ⬜ | results/figures/ |
| CSV data exported | ⬜ | results/data/ |
| README updated | ⬜ | README.md |
| Input files archived | ⬜ | inputs/ |

---

## Section 9: Sign-Off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Analyst | | | |
| Reviewer | | | |
| Approver | | | |

---

## Summary

| Category | Checks Passed | Total Checks | Percentage |
|----------|---------------|--------------|------------|
| Pre-Analysis | ___ | 10 | ___% |
| Mesh | ___ | 12 | ___% |
| BCs & Loads | ___ | 8 | ___% |
| Equilibrium | ___ | 6 | ___% |
| Stress | ___ | 10 | ___% |
| Displacement | ___ | 6 | ___% |
| Fatigue | ___ | 8 | ___% |
| Documentation | ___ | 5 | ___% |
| **TOTAL** | **___** | **65** | **___%** |

**Overall Status:** ⬜ APPROVED / ⬜ APPROVED WITH COMMENTS / ⬜ REQUIRES REVISION

**Comments:**
```
[Enter any deviations, assumptions, or concerns here]
```
