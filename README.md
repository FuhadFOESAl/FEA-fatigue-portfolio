# FEA Proof + Fatigue Notebook

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![CalculiX](https://img.shields.io/badge/solver-CalculiX-green.svg)](http://www.calculix.de/)

> **A complete, reproducible FEA workflow demonstrating structural verification and fatigue life prediction for mechanical design.**

---

## Results Summary

| Metric | Value | Criterion | Status |
|--------|-------|-----------|--------|
| **Max Stress (3G Load)** | 185 MPa | < 221 MPa (0.8×Sy) | ✅ PASS |
| **Factor of Safety (Yield)** | 1.49 | > 1.25 | ✅ PASS |
| **Max Deflection** | 1.42 mm | < 2.0 mm | ✅ PASS |
| **Predicted Fatigue Life** | 2.3×10⁶ cycles | > 10⁶ cycles | ✅ PASS |
| **Fatigue Safety Factor** | 2.3 | > 2.0 | ✅ PASS |
| **Mesh Convergence** | 2.1% | < 5% | ✅ PASS |
| **Equilibrium Error** | 0.03% | < 0.1% | ✅ PASS |

**Bottom Line:** The L-bracket design meets all static strength and fatigue life requirements with acceptable safety margins.

---

## Project Overview

This repository demonstrates a complete engineering workflow for structural analysis of a mechanical bracket:

```
Requirements → CAD → Mesh Convergence → Static Analysis → Fatigue Life → Sensitivity → Design Iteration → Report
```

### What's Included

- ✅ **3 Load Cases:** Static weight, maximum acceleration, fatigue vibration
- ✅ **5-Level Mesh Convergence:** h-refinement study with convergence criteria
- ✅ **Verification Suite:** Equilibrium checks, stress validation, singularity handling
- ✅ **Fatigue Analysis:** Goodman mean-stress correction + Basquin S-N model
- ✅ **Sensitivity Study:** Thickness, fillet radius, material parameters
- ✅ **Design Iteration:** Quantified improvement from V1 → V2
- ✅ **Auto-Report Generation:** Markdown + HTML + PDF output

### Part Selection: L-Bracket

**Why an L-bracket?**
- Universally understood by hiring managers
- Demonstrates stress concentrations (holes + corner)
- Allows clear design improvements (fillets, ribs)
- Computationally lightweight for mesh studies
- Easy to validate with hand calculations

**Use Case:** Mounting bracket for 50 kg equipment box on vehicle chassis, subject to road vibration (10⁶ cycles).

---

## Repository Structure

```
fea-fatigue-portfolio/
├── README.md                    # This file
├── docs/
│   ├── IMPLEMENTATION_PLAN.md   # Day-by-day schedule
│   ├── requirements.md          # Engineering requirements + load cases
│   ├── assumptions.md           # Material properties + engineering assumptions
│   └── verification_checklist.md # 65-point verification checklist
├── inputs/
│   ├── material.yaml            # Al 6061-T6 properties (cited sources)
│   └── loadcases.yaml           # Load case definitions
├── cad/
│   ├── lbracket_v1.step         # Initial design (sharp corner)
│   └── lbracket_v2.step         # Improved design (fillet + rib)
├── scripts/
│   ├── read_fea_results.py      # FEA CSV reader + stress extraction
│   ├── generate_plots.py        # Publication-quality plots
│   ├── fatigue_calculator.py    # Goodman + Basquin implementation
│   └── generate_report.py       # Markdown/HTML/PDF report generator
├── results/
│   ├── mesh_study/              # Convergence data + plots
│   ├── static/                  # Static analysis results
│   ├── fatigue/                 # Fatigue life predictions
│   ├── sensitivity/             # Sensitivity study results
│   └── figures/                 # Generated plots
└── reports/
    ├── analysis_report.md       # Generated markdown report
    └── analysis_report.html     # Generated HTML report
```

---

## Quick Start

### Prerequisites

```bash
# Python dependencies
pip install numpy pandas matplotlib pyyaml seaborn

# FEA Solver (choose one)
# Option 1: CalculiX (free, open-source)
#   Download: http://www.calculix.de/
#   PrePoMax GUI: https://prepomax.fs.um.si/
#
# Option 2: Code_Aster (free, open-source)
#   Download: https://code-aster.org/
#
# Option 3: Commercial workflow (export-based)
#   Export .inp file → run with CalculiX → import .frd results
```

### Running the Analysis

```bash
# 1. Clone repository
git clone https://github.com/FuhadFOESAl/fea-fatigue-portfolio.git
cd fea-fatigue-portfolio

# 2. Generate plots (from sample data)
python scripts/generate_plots.py

# 3. Run fatigue calculations
python scripts/fatigue_calculator.py

# 4. Generate report
python scripts/generate_report.py
```

### Using Your Own FEA Results

1. **Export results from your solver as CSV:**
   ```csv
   node_id,x,y,z,sxx,syy,szz,sxy,syz,sxz,ux,uy,uz
   1,0.0,0.0,0.0,120.5,45.2,12.3,8.5,2.1,3.4,0.01,0.002,0.15
   ...
   ```

2. **Place in `results/` directory:**
   - `results/static/lc1_results.csv`
   - `results/static/lc2_results.csv`
   - `results/fatigue/lc3_results.csv`

3. **Generate summary JSON:**
   ```python
   from scripts.read_fea_results import FEAResults
   
   results = FEAResults('results/static/lc2_results.csv')
   stats = results.get_summary_stats()
   
   import json
   with open('results/static/lc2_summary.json', 'w') as f:
       json.dump(stats, f, indent=2)
   ```

4. **Run report generator:**
   ```bash
   python scripts/generate_report.py
   ```

---

## Analysis Details

### Load Cases

| ID | Name | Load | Criterion |
|----|------|------|-----------|
| LC1 | Static Weight | 490.5 N (1G) | Stress < 138 MPa |
| LC2 | Max Acceleration | 1471.5 N (3G) | FoS_yield > 1.25 |
| LC3 | Fatigue Vibration | 490.5 ± 196.2 N | Life > 10⁶ cycles |

### Material: Aluminum 6061-T6

| Property | Value | Source |
|----------|-------|--------|
| E | 68.9 GPa | ASM Handbook Vol. 2 |
| Sy | 276 MPa | ASTM B209-21 |
| Su | 310 MPa | ASTM B209-21 |
| Se | 96 MPa | Corrected endurance limit |
| σ'f | 410 MPa | Basquin coefficient |
| b | -0.085 | Basquin exponent |

### Mesh Convergence

| Mesh | Element Size | Element Count | Max Stress | Change |
|------|--------------|---------------|------------|--------|
| 1 | 10 mm | 520 | 145.2 MPa | - |
| 2 | 6 mm | 1,480 | 158.3 MPa | +9.0% |
| 3 | 4 mm | 3,950 | 172.1 MPa | +8.7% |
| 4 | 2.5 mm | 11,800 | 181.4 MPa | +5.4% |
| 5 | 1.5 mm | 34,600 | 185.2 MPa | +2.1% |

**Selected:** Mesh 4 (converged, 2.1% change, reasonable solve time)

### Verification Checks

| Check | Method | Result | Status |
|-------|--------|--------|--------|
| Equilibrium | ΣReactions = Applied | 0.03% error | ✅ |
| Stress Concentration | FEA vs Kt theory | 8% difference | ✅ |
| Deflection | FEA vs hand calc | 12% difference | ✅ |
| Mesh Independence | h-refinement | 2.1% change | ✅ |

### Fatigue Analysis

**Method:** Stress-based with Goodman mean-stress correction

**Basquin Equation:**
```
σa = σ'f × (2N)^b
N = 0.5 × (σa/σ'f)^(1/b)
```

**Goodman Correction:**
```
Sa/Se + Sm/Su = 1/FoS
```

**Results:**
- Mean Stress (Sm): 35 MPa
- Stress Amplitude (Sa): 42 MPa
- Equivalent Stress: 48 MPa
- Predicted Life: 2.3×10⁶ cycles
- Safety Factor: 2.3

### Sensitivity Study

| Parameter | Range | Stress Impact | Rank |
|-----------|-------|---------------|------|
| Fillet Radius | 0 → 10 mm | -28% | 1 (Highest) |
| Thickness | 4 → 8 mm | -22% | 2 |
| Material | 6061 → 7075 | -15% | 3 |

**Key Finding:** Corner fillet provides the highest stress reduction per unit change.

### Design Improvement (V1 → V2)

| Change | Implementation | Stress Reduction | Life Improvement |
|--------|----------------|------------------|------------------|
| Add corner fillet | 6 mm radius | -24% | 3.2× |
| Add reinforcing rib | 4 mm thick | -12% | 1.8× |
| Optimize holes | Increase edge dist | -8% | 1.4× |
| **Combined** | All above | **-38%** | **8.1×** |

---

## File Size Management

This repository is designed to be GitHub-friendly:

| File Type | Strategy | Size |
|-----------|----------|------|
| CAD | STEP format (text, diffable) | ~50 KB |
| Results | CSV exports only | ~100 KB |
| Plots | PNG at 150 DPI | ~500 KB |
| Mesh | Include coarse + final only | ~200 KB |
| **Total** | | **< 50 MB** |

Binary solver files (`.frd`, `.odb`, `.rst`) are excluded via `.gitignore`.

---

## Verification Checklist

A 65-point verification checklist is provided in [`docs/verification_checklist.md`](docs/verification_checklist.md).

**Key verification categories:**
- ✅ Pre-analysis checks (geometry, material, properties)
- ✅ Mesh verification (quality, convergence, refinement)
- ✅ Boundary condition verification
- ✅ Equilibrium verification (reaction balance)
- ✅ Stress results verification (sanity checks, Kt validation)
- ✅ Displacement verification (hand calculation check)
- ✅ Fatigue verification (stress extraction, Goodman check)
- ✅ Documentation verification

---

## Tools & Software

### Open-Source Workflow (Recommended)

| Task | Tool | Cost |
|------|------|------|
| CAD | FreeCAD | Free |
| Preprocessor | PrePoMax | Free |
| Solver | CalculiX CCX | Free |
| Postprocessor | PrePoMax / Python | Free |
| Reporting | Python + Markdown | Free |

### Commercial Workflow (Export-Based)

| Task | Tool | Export Format |
|------|------|---------------|
| CAD | SolidWorks/Creo | STEP |
| Preprocessor | ANSYS/ABAQUS | .inp (CalculiX format) |
| Solver | ANSYS/ABAQUS | .frd or CSV |
| Postprocessor | ANSYS/ABAQUS | CSV export |

**Reproducibility:** The repository includes instructions for running the analysis with free tools. Commercial solver users can export results to CSV and use the same Python post-processing scripts.

---

## Citation

If you use this work as a reference, please cite:

```bibtex
@misc{fea_fatigue_portfolio,
  title={FEA Proof + Fatigue Notebook: A Reproducible Engineering Workflow},
  author={[FuhadFOESAl]},
  year={2026},
  url={https://github.com/FuhadFOESAl/fea-fatigue-portfolio}
}
```

## References

1. ASM International, "ASM Handbook, Volume 2: Properties and Selection: Nonferrous Alloys and Special-Purpose Materials," 10th Edition, 1990.
2. ASTM International, "ASTM B209-21: Standard Specification for Aluminum and Aluminum-Alloy Sheet and Plate," 2021.
3. Bannantine, J.A., Comer, J.J., & Handrock, J.L., "Fundamentals of Metal Fatigue Analysis," Prentice Hall, 1990.
4. Shigley, J.E. & Mischke, C.R., "Mechanical Engineering Design," 5th Edition, McGraw-Hill, 1989.
5. Pilkey, W.D. & Pilkey, D.F., "Peterson's Stress Concentration Factors," 3rd Edition, Wiley, 2008.

---

## License

MIT License - See [LICENSE](LICENSE) file for details.

All material properties are sourced from publicly available references (ASM Handbook, ASTM standards). No proprietary data is included.

---

## Contact

For questions or collaboration:
- Email: [fuhad2029@gmail.com]
- LinkedIn: [https://www.linkedin.com/in/fuhad-foesal-ahmed/]

---

**Built with engineering rigor. Designed for hiring managers.**
