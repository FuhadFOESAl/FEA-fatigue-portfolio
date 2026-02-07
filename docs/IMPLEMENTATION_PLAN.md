# FEA Proof + Fatigue Notebook — Implementation Plan

## Part Selection: L-Bracket with Mounting Holes

**Why this part?** L-brackets are universally understood by hiring managers, demonstrate multiple stress concentrations (holes + corner), allow for clear design improvements (fillets, ribs), and are computationally lightweight for mesh convergence studies.

**Use Case:** Structural bracket supporting a 50 kg equipment box on a vibrating vehicle chassis (automotive/industrial application). Must survive 10^6 load cycles with 99% reliability.

---

## Day-by-Day Implementation Schedule

### Day 1: Project Setup & Requirements
- [ ] Create GitHub repo with folder structure
- [ ] Write `docs/requirements.md` with load cases
- [ ] Write `docs/assumptions.md` with material data
- [ ] Create `inputs/loadcases.yaml` and `inputs/material.yaml`
- [ ] Export CAD: `cad/lbracket_v1.step` (initial design)

### Day 2: Mesh Convergence Study
- [ ] Create 5 mesh densities (coarse to fine)
- [ ] Run static analysis for each mesh
- [ ] Record: max von Mises stress, max displacement, element count, solve time
- [ ] Plot convergence curves
- [ ] Determine mesh-independent result threshold

### Day 3: Verification & Static Proof
- [ ] Perform equilibrium check (sum reactions = applied load)
- [ ] Perform free-body diagram verification
- [ ] Calculate FoS_yield for all load cases
- [ ] Check deflection against requirements
- [ ] Document stress singularity handling at holes

### Day 4: Fatigue Analysis
- [ ] Extract stress components from FEA
- [ ] Calculate mean and alternating stress (Sa, Sm)
- [ ] Apply Goodman mean-stress correction
- [ ] Estimate cycles to failure using Basquin equation
- [ ] Calculate fatigue safety factor

### Day 5: Sensitivity Study
- [ ] Parameter 1: Thickness (4mm, 6mm, 8mm)
- [ ] Parameter 2: Fillet radius (0mm, 3mm, 6mm, 10mm)
- [ ] Parameter 3: Material (Al 6061-T6, Al 7075-T6, Steel 4130)
- [ ] Generate tornado diagram

### Day 6: Design Iteration
- [ ] Create improved design: `cad/lbracket_v2.step`
- [ ] Add corner fillet and reinforcing rib
- [ ] Re-run full analysis (mesh, static, fatigue)
- [ ] Quantify improvement: % stress reduction, % life increase

### Day 7: Reporting & Polish
- [ ] Generate all plots and CSV exports
- [ ] Run `scripts/generate_report.py`
- [ ] Write final README with results summary
- [ ] Complete verification checklist
- [ ] Push to GitHub

---

## Key Metrics to Track

| Metric | Target | How Measured |
|--------|--------|--------------|
| Max von Mises Stress | < 0.8 × Sy | FEA post-processing |
| Max Deflection | < 2.0 mm | FEA displacement |
| Fatigue Life | > 10^6 cycles | Goodman + Basquin |
| FoS_yield | > 1.5 | Calculated |
| FoS_fatigue | > 2.0 | Calculated |
| Mesh Convergence | < 5% change | Successive mesh comparison |
| Equilibrium Error | < 0.1% | Sum reactions vs applied |

---

## File Size Management for GitHub

- CAD files: Use STEP (text-based, diffable)
- Results: Export CSV only (no binary .frd files)
- Plots: PNG at 150 DPI (not raw data)
- Mesh files: Include coarse + final only, intermediate meshes in `.gitignore`
- Target repo size: < 50 MB
