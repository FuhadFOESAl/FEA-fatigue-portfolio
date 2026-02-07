# Quick Start Guide

Get up and running with the FEA Fatigue Portfolio in 5 minutes.

---

## 1. Clone and Setup (2 minutes)

```bash
# Clone the repository
git clone https://github.com/yourusername/fea-fatigue-portfolio.git
cd fea-fatigue-portfolio

# Install Python dependencies
pip install -r requirements.txt
```

---

## 2. Generate Plots (1 minute)

```bash
# Generate all analysis plots
python scripts/generate_plots.py
```

**Output:**
- `results/figures/mesh_convergence.png`
- `results/figures/element_size_convergence.png`
- `results/figures/sn_curve.png`
- `results/figures/goodman_diagram.png`

---

## 3. Run Fatigue Calculator (1 minute)

```bash
# Run fatigue life calculations with examples
python scripts/fatigue_calculator.py
```

**Output:** Console output showing:
- Material properties
- Life predictions for different load cases
- Goodman vs Gerber vs Soderberg comparison
- Miner's rule damage accumulation

---

## 4. Generate Report (1 minute)

```bash
# Generate Markdown and HTML reports
python scripts/generate_report.py
```

**Output:**
- `reports/analysis_report.md`
- `reports/analysis_report.html`

Open `reports/analysis_report.html` in your browser to view the complete analysis report.

---

## What's Next?

### Option A: Run with Your Own FEA Data

1. Export FEA results as CSV from your solver (CalculiX, ANSYS, ABAQUS, etc.)
2. Place in `results/static/` and `results/fatigue/`
3. Generate summary JSON files (see below)
4. Re-run `generate_report.py`

### Option B: Complete Full Workflow with Free Tools

1. **CAD:** Create L-bracket in FreeCAD → Export as `cad/lbracket_v1.step`
2. **Mesh:** Import into PrePoMax → Create 5 mesh densities → Export `.inp` files
3. **Solve:** Run CalculiX CCX → Export `.frd` results
4. **Post-process:** Convert `.frd` to CSV using `ccx2paraview` or custom script
5. **Analyze:** Use provided Python scripts for fatigue and reporting

### Option C: Use Commercial Solver (Export Workflow)

1. **CAD:** Export STEP from SolidWorks/Creo/CATIA
2. **Pre-process:** Import into ANSYS/ABAQUS
3. **Export:** Write input deck in CalculiX-compatible format
4. **Solve:** Run with CalculiX OR solve in commercial solver
5. **Export results:** CSV format with node coordinates and stress components
6. **Post-process:** Use provided Python scripts

---

## File Format Reference

### FEA Results CSV Format

```csv
node_id,x,y,z,sxx,syy,szz,sxy,syz,sxz,ux,uy,uz
1,0.0,0.0,0.0,120.5,45.2,12.3,8.5,2.1,3.4,0.01,0.002,0.15
2,1.0,0.0,0.0,115.3,42.1,11.8,7.9,1.9,3.1,0.009,0.0018,0.142
...
```

**Required columns:**
- `node_id`: Node identifier
- `x, y, z`: Coordinates (mm)
- `sxx, syy, szz`: Normal stress components (MPa)
- `sxy, syz, sxz`: Shear stress components (MPa)
- `ux, uy, uz`: Displacements (mm) - optional but recommended

### Summary JSON Format

```json
{
  "load_case": "LC2_Max_Acceleration",
  "max_von_mises": 185.2,
  "max_displacement": 1.97,
  "fos_yield": 1.49,
  "fos_yield_pass": true
}
```

---

## Common Issues

### Issue: `ModuleNotFoundError: No module named 'yaml'`

**Solution:**
```bash
pip install pyyaml
```

### Issue: Plots not generating

**Solution:** Check that data files exist:
```bash
ls results/mesh_study/convergence_data.csv
ls results/static/lc2_summary.json
```

### Issue: Report shows "TBD" for all values

**Solution:** The report generator looks for JSON summary files. Create them from your FEA results:

```python
from scripts.read_fea_results import FEAResults
import json

results = FEAResults('your_results.csv')
stats = results.get_summary_stats()

# Add required fields
stats['fos_yield'] = 276 / stats['max_von_mises']
stats['fos_yield_pass'] = stats['fos_yield'] > 1.25

with open('results/static/lc2_summary.json', 'w') as f:
    json.dump(stats, f, indent=2)
```

---

## Directory Structure After Setup

```
fea-fatigue-portfolio/
├── README.md                    # Main documentation
├── QUICKSTART.md               # This file
├── requirements.txt            # Python dependencies
├── docs/                       # Documentation
│   ├── IMPLEMENTATION_PLAN.md
│   ├── requirements.md
│   ├── assumptions.md
│   ├── verification_checklist.md
│   └── RESUME_BULLETS.md
├── inputs/                     # Input files
│   ├── material.yaml
│   └── loadcases.yaml
├── scripts/                    # Python automation
│   ├── read_fea_results.py
│   ├── generate_plots.py
│   ├── fatigue_calculator.py
│   └── generate_report.py
├── results/                    # Analysis results
│   ├── mesh_study/
│   │   └── convergence_data.csv
│   ├── static/
│   │   ├── lc1_summary.json
│   │   └── lc2_summary.json
│   ├── fatigue/
│   │   └── fatigue_summary.json
│   ├── sensitivity/
│   │   └── sensitivity_summary.json
│   └── figures/               # Generated plots (after running)
└── reports/                   # Generated reports (after running)
    ├── analysis_report.md
    └── analysis_report.html
```

---

## Getting Help

1. **Check the README:** Detailed documentation in `README.md`
2. **Review the code:** All scripts are documented with docstrings
3. **Run examples:** `python scripts/fatigue_calculator.py` shows example usage
4. **Open an issue:** GitHub Issues for bugs or questions

---

## Next Steps for Portfolio Development

### Week 1: Foundation
- [ ] Create CAD model in FreeCAD
- [ ] Export STEP file
- [ ] Document geometry in `docs/requirements.md`

### Week 2: Mesh & Static
- [ ] Create 5 mesh densities in PrePoMax
- [ ] Run static analysis for LC1, LC2
- [ ] Complete mesh convergence study
- [ ] Fill out verification checklist

### Week 3: Fatigue & Sensitivity
- [ ] Extract stress data for LC3
- [ ] Run fatigue calculations
- [ ] Perform sensitivity study
- [ ] Generate all plots

### Week 4: Design Iteration & Polish
- [ ] Create V2 design with fillet and rib
- [ ] Re-run full analysis
- [ ] Quantify improvements
- [ ] Generate final report
- [ ] Push to GitHub

---

**Ready to start?** Run `python scripts/generate_plots.py` now!
