# Engineering Requirements Document
## L-Bracket FEA Analysis Project

**Document Version:** 1.0  
**Date:** 2024-01-15  
**Part Name:** L-Bracket Mount V1  
**Part Number:** LB-2024-001  
**Analyst:** [Your Name]  
**Review Status:** Draft

---

## 1. Design Intent

Mounting bracket for 50 kg equipment box on vehicle chassis. Bracket must:
- Support static weight under 3G vertical acceleration
- Withstand road vibration fatigue (10^6 cycles)
- Allow single-person installation (two-bolt pattern)
- Fit within 150mm × 100mm × 80mm envelope

---

## 2. Geometry Definition

### 2.1 Overall Dimensions
| Parameter | Value | Tolerance |
|-----------|-------|-----------|
| Vertical leg height (H) | 100 mm | ±0.5 mm |
| Horizontal leg length (L) | 80 mm | ±0.5 mm |
| Thickness (T) | 6 mm | ±0.25 mm |
| Width (W) | 50 mm | ±0.5 mm |
| Mounting hole diameter | 10 mm | +0.1/-0 mm |
| Hole center-to-edge distance | 15 mm | ±0.25 mm |
| Corner fillet radius | 0 mm (sharp) V1 / 6 mm V2 | ±0.5 mm |

### 2.2 Critical Features
- Two M10 clearance holes on vertical leg (chassis mount)
- Two M10 clearance holes on horizontal leg (equipment mount)
- 90° corner (stress concentration point)

---

## 3. Material Specification

**Primary Material:** Aluminum 6061-T6  
**Justification:** Good strength-to-weight, excellent fatigue resistance, corrosion resistant, readily available

| Property | Value | Source |
|----------|-------|--------|
| Density (ρ) | 2700 kg/m³ | ASM Handbook Vol. 2 |
| Young's Modulus (E) | 68.9 GPa | ASM Handbook Vol. 2 |
| Poisson's Ratio (ν) | 0.33 | ASM Handbook Vol. 2 |
| Yield Strength (Sy) | 276 MPa | ASTM B209 |
| Ultimate Tensile (Su) | 310 MPa | ASTM B209 |
| Fatigue Strength Coefficient (σ'f) | 410 MPa | Approx. 1.32×Su |
| Fatigue Strength Exponent (b) | -0.085 | Typical for Al alloys |
| Endurance Limit (Se) | 96 MPa | ~0.31×Su (R=-1, 10^7 cycles) |

**Note:** Material properties are from publicly available sources (ASM Handbook, ASTM standards). Not proprietary.

---

## 4. Load Cases

### 4.1 Load Case 1: Static Weight (LC1)
**Description:** Equipment at rest, 1G gravity

| Parameter | Value |
|-----------|-------|
| Applied mass | 50 kg |
| Gravity | 9.81 m/s² |
| Total force | 490.5 N |
| Distribution | Uniform pressure on horizontal leg |
| Direction | -Z (downward) |

**Boundary Conditions:**
- Vertical leg holes: Fixed (all DOFs constrained)
- Contact: Bonded (conservative assumption)

**Acceptance Criteria:**
- Max stress < 0.5 × Sy = 138 MPa (generous margin for fatigue)
- Max deflection < 1.0 mm

---

### 4.2 Load Case 2: Maximum Vertical Acceleration (LC2)
**Description:** Vehicle hits pothole, 3G vertical shock

| Parameter | Value |
|-----------|-------|
| Dynamic load factor | 3.0 |
| Applied force | 1471.5 N |
| Distribution | Uniform pressure on horizontal leg |
| Direction | -Z (downward) |

**Boundary Conditions:**
- Same as LC1

**Acceptance Criteria:**
- Max stress < 0.8 × Sy = 221 MPa (static proof)
- FoS_yield > 1.25
- No permanent deformation

---

### 4.3 Load Case 3: Combined Static + Vibration Fatigue (LC3)
**Description:** Road vibration with mean load, 10^6 cycles design life

| Parameter | Value |
|-----------|-------|
| Mean load (from LC1) | 490.5 N |
| Alternating load amplitude | ±196.2 N (±0.4G vibration) |
| Max cyclic load | 686.7 N |
| Min cyclic load | 294.3 N |
| Load ratio (R) | 0.43 |
| Design cycles | 1,000,000 |
| Required reliability | 99% |

**Duty Cycle:**
- 90% of life at 0.2G amplitude (low stress)
- 10% of life at 0.4G amplitude (high stress)
- Equivalent damage calculation per Miner's rule

**Boundary Conditions:**
- Same as LC1

**Acceptance Criteria:**
- Predicted life > 2 × 10^6 cycles (2× safety factor on life)
- FoS_fatigue > 2.0
- Crack initiation life > 10^6 cycles

---

## 5. Design Constraints

| Constraint | Requirement |
|------------|-------------|
| Mass | < 0.5 kg |
| Max thickness | 10 mm (machining limit) |
| Min hole spacing | 30 mm (wrench clearance) |
| Surface finish | Ra 3.2 μm (as-machined) |
| Operating temp | -40°C to +85°C |

---

## 6. Analysis Requirements

### 6.1 Mesh Requirements
- Minimum 2 elements through thickness
- Hex-dominant mesh preferred
- Local refinement at holes and corner
- 5 mesh densities for convergence study

### 6.2 Solver Requirements
- Static structural analysis
- Linear elastic material (valid since stress < Sy)
- Large displacement effects: OFF (small deflections expected)

### 6.3 Post-Processing Requirements
- von Mises stress contour plots
- Principal stress vectors at critical locations
- Displacement magnitude plots
- Reaction force verification

---

## 7. Success Criteria Summary

| Check | Criterion | Status |
|-------|-----------|--------|
| Mesh convergence | < 5% stress change, final 2 meshes | ⬜ TBD |
| Equilibrium | |ΣReactions - Applied| / |Applied| < 0.1% | ⬜ TBD |
| Static proof LC2 | FoS_yield > 1.25 | ⬜ TBD |
| Deflection LC2 | δ_max < 2.0 mm | ⬜ TBD |
| Fatigue life LC3 | N_pred > 10^6 cycles | ⬜ TBD |
| Fatigue safety | FoS_fatigue > 2.0 | ⬜ TBD |

---

## 8. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2024-01-15 | [Name] | Initial release |
