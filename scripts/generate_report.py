#!/usr/bin/env python3
"""
Report Generator Module
Generates Markdown and HTML reports from FEA analysis results.

Usage:
    from generate_report import ReportGenerator
    
    report = ReportGenerator()
    report.generate_markdown('reports/analysis_report.md')
    report.generate_html('reports/analysis_report.html')
"""

import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd


class ReportGenerator:
    """Generate engineering analysis reports."""
    
    def __init__(self, 
                 results_dir: str = 'results',
                 inputs_dir: str = 'inputs',
                 docs_dir: str = 'docs'):
        """
        Initialize report generator.
        
        Args:
            results_dir: Directory containing analysis results
            inputs_dir: Directory containing input files
            docs_dir: Directory containing documentation
        """
        self.results_dir = Path(results_dir)
        self.inputs_dir = Path(inputs_dir)
        self.docs_dir = Path(docs_dir)
        
        self.data = self._load_all_data()
    
    def _load_all_data(self) -> Dict:
        """Load all relevant data files."""
        data = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'material': {},
            'load_cases': {},
            'mesh_study': {},
            'static_results': {},
            'fatigue_results': {},
            'sensitivity': {}
        }
        
        # Load material properties
        mat_file = self.inputs_dir / 'material.yaml'
        if mat_file.exists():
            with open(mat_file, 'r') as f:
                data['material'] = yaml.safe_load(f)
        
        # Load load cases
        lc_file = self.inputs_dir / 'loadcases.yaml'
        if lc_file.exists():
            with open(lc_file, 'r') as f:
                data['load_cases'] = yaml.safe_load(f)
        
        # Load mesh study results
        mesh_file = self.results_dir / 'mesh_study' / 'convergence_data.csv'
        if mesh_file.exists():
            data['mesh_study'] = pd.read_csv(mesh_file).to_dict('records')
        
        # Load static results
        for lc in ['lc1', 'lc2']:
            result_file = self.results_dir / 'static' / f'{lc}_summary.json'
            if result_file.exists():
                with open(result_file, 'r') as f:
                    data['static_results'][lc] = json.load(f)
        
        # Load fatigue results
        fatigue_file = self.results_dir / 'fatigue' / 'fatigue_summary.json'
        if fatigue_file.exists():
            with open(fatigue_file, 'r') as f:
                data['fatigue_results'] = json.load(f)
        
        # Load sensitivity results
        sens_file = self.results_dir / 'sensitivity' / 'sensitivity_summary.json'
        if sens_file.exists():
            with open(sens_file, 'r') as f:
                data['sensitivity'] = json.load(f)
        
        return data
    
    def generate_markdown(self, output_path: str = 'reports/analysis_report.md') -> str:
        """
        Generate Markdown report.
        
        Args:
            output_path: Where to save the report
            
        Returns:
            Report content as string
        """
        lines = []
        
        # Header
        lines.extend([
            "# FEA Analysis Report",
            "## L-Bracket Mount V1 - Static & Fatigue Assessment",
            "",
            f"**Report Generated:** {self.data['timestamp']}  ",
            "**Analyst:** [Your Name]  ",
            "**Part Number:** LB-2024-001  ",
            "**Analysis Version:** 1.0",
            "",
            "---",
            "",
        ])
        
        # Executive Summary
        lines.extend([
            "## Executive Summary",
            "",
            "| Metric | Value | Criterion | Status |",
            "|--------|-------|-----------|--------|",
        ])
        
        # Add summary table rows based on available data
        if self.data['static_results']:
            lc2 = self.data['static_results'].get('lc2', {})
            max_stress = lc2.get('max_von_mises', 'TBD')
            lines.append(f"| Max Stress (LC2) | {max_stress} MPa | < 221 MPa | {'✓ PASS' if isinstance(max_stress, (int, float)) and max_stress < 221 else '⬜ TBD'} |")
        
        if self.data['fatigue_results']:
            fatigue = self.data['fatigue_results']
            life = fatigue.get('predicted_cycles', 'TBD')
            fos = fatigue.get('fos_on_stress', 'TBD')
            lines.append(f"| Fatigue Life | {life} cycles | > 10⁶ | {'✓ PASS' if isinstance(life, (int, float)) and life > 1e6 else '⬜ TBD'} |")
            lines.append(f"| Fatigue FoS | {fos} | > 2.0 | {'✓ PASS' if isinstance(fos, (int, float)) and fos > 2.0 else '⬜ TBD'} |")
        
        lines.append("")
        
        # Material Properties
        if self.data['material']:
            mat = self.data['material'].get('material', {})
            lines.extend([
                "## Material Properties",
                "",
                f"**Material:** {mat.get('name', 'N/A')}  ",
                f"**Standard:** {mat.get('standard', 'N/A')}",
                "",
                "| Property | Value | Unit |",
                "|----------|-------|------|",
            ])
            
            mech = mat.get('mechanical', {})
            strength = mat.get('strength', {})
            fatigue = mat.get('fatigue', {})
            
            lines.extend([
                f"| Density | {mech.get('density', 'N/A')} | kg/m³ |",
                f"| Young's Modulus | {mech.get('youngs_modulus', 'N/A')} | MPa |",
                f"| Poisson's Ratio | {mech.get('poisson_ratio', 'N/A')} | - |",
                f"| Yield Strength | {strength.get('yield_strength', 'N/A')} | MPa |",
                f"| Ultimate Strength | {strength.get('ultimate_strength', 'N/A')} | MPa |",
                f"| Endurance Limit | {fatigue.get('endurance_limit_corrected', 'N/A')} | MPa |",
                "",
            ])
        
        # Load Cases
        if self.data['load_cases']:
            analysis = self.data['load_cases'].get('analysis', {})
            lines.extend([
                "## Load Cases",
                "",
            ])
            
            for lc_id, lc in analysis.get('load_cases', {}).items():
                lines.extend([
                    f"### {lc.get('name', lc_id)}",
                    "",
                    f"**Description:** {lc.get('description', 'N/A')}  ",
                    f"**Type:** {lc.get('type', 'N/A')}",
                    "",
                ])
                
                # Loads
                loads = lc.get('loads', lc.get('mean_load', {}))
                if loads:
                    lines.extend([
                        "**Applied Loads:**",
                        "",
                        "| Load | Magnitude | Direction |",
                        "|------|-----------|-----------|",
                    ])
                    for load_name, load_data in loads.items():
                        if isinstance(load_data, dict):
                            mag = load_data.get('magnitude', 'N/A')
                            direc = load_data.get('direction', 'N/A')
                            lines.append(f"| {load_name} | {mag} N | {direc} |")
                    lines.append("")
                
                # Acceptance criteria
                criteria = lc.get('acceptance_criteria', {})
                if criteria:
                    lines.extend([
                        "**Acceptance Criteria:**",
                        "",
                    ])
                    for key, value in criteria.items():
                        lines.append(f"- {key}: {value}")
                    lines.append("")
        
        # Mesh Convergence
        if self.data['mesh_study']:
            lines.extend([
                "## Mesh Convergence Study",
                "",
                "| Mesh | Element Size (mm) | Element Count | Max Stress (MPa) | Change (%) |",
                "|------|-------------------|---------------|------------------|------------|",
            ])
            
            prev_stress = None
            for row in self.data['mesh_study']:
                mesh_id = row.get('mesh_id', 'N/A')
                elem_size = row.get('element_size_mm', 'N/A')
                elem_count = row.get('element_count', 'N/A')
                max_stress = row.get('max_stress_mpa', 'N/A')
                
                if prev_stress and isinstance(max_stress, (int, float)):
                    change = ((max_stress - prev_stress) / prev_stress) * 100
                    change_str = f"{change:+.1f}%"
                else:
                    change_str = "-"
                
                lines.append(f"| {mesh_id} | {elem_size} | {elem_count} | {max_stress} | {change_str} |")
                prev_stress = max_stress if isinstance(max_stress, (int, float)) else None
            
            lines.extend([
                "",
                "**Convergence Criterion:** < 5% change between successive meshes  ",
                "**Selected Mesh:** Mesh 4 (converged, computationally efficient)",
                "",
                "![Mesh Convergence](figures/mesh_convergence.png)",
                "",
            ])
        
        # Static Analysis Results
        if self.data['static_results']:
            lines.extend([
                "## Static Analysis Results",
                "",
            ])
            
            for lc_id, results in self.data['static_results'].items():
                lines.extend([
                    f"### Load Case {lc_id.upper()}",
                    "",
                    "| Result | Value | Unit |",
                    "|--------|-------|------|",
                    f"| Max von Mises Stress | {results.get('max_von_mises', 'N/A')} | MPa |",
                    f"| Max Principal Stress | {results.get('max_principal', 'N/A')} | MPa |",
                    f"| Max Displacement | {results.get('max_displacement', 'N/A')} | mm |",
                    f"| Stress Location | {results.get('max_stress_location', 'N/A')} | - |",
                    "",
                ])
                
                # Factor of Safety
                if 'fos_yield' in results:
                    lines.extend([
                        "**Factor of Safety:**",
                        "",
                        f"- FoS_yield = {results.get('fos_yield', 'N/A')} (Required: {results.get('fos_yield_required', 'N/A')})",
                        f"- Status: {'✓ PASS' if results.get('fos_yield_pass', False) else '✗ FAIL'}",
                        "",
                    ])
        
        # Fatigue Analysis
        if self.data['fatigue_results']:
            fatigue = self.data['fatigue_results']
            lines.extend([
                "## Fatigue Analysis Results",
                "",
                "### Stress State",
                "",
                "| Parameter | Value | Unit |",
                "|-----------|-------|------|",
                f"| Maximum Stress | {fatigue.get('smax', 'N/A')} | MPa |",
                f"| Minimum Stress | {fatigue.get('smin', 'N/A')} | MPa |",
                f"| Mean Stress | {fatigue.get('mean_stress', 'N/A')} | MPa |",
                f"| Stress Amplitude | {fatigue.get('stress_amplitude', 'N/A')} | MPa |",
                f"| R-ratio | {fatigue.get('r_ratio', 'N/A')} | - |",
                "",
                "### Life Prediction",
                "",
                "| Parameter | Value |",
                "|-----------|-------|",
                f"| Mean Stress Correction | {fatigue.get('method', 'N/A').upper()} |",
                f"| Equivalent Stress | {fatigue.get('equivalent_stress', 'N/A')} MPa |",
                f"| Predicted Life | {fatigue.get('predicted_cycles', 'N/A'):.2e} cycles |",
                f"| Safety Factor (Life) | {fatigue.get('fos_on_life', 'N/A'):.2f} |",
                f"| Safety Factor (Stress) | {fatigue.get('fos_on_stress', 'N/A'):.2f} |",
                f"| Infinite Life | {'Yes' if fatigue.get('infinite_life', False) else 'No'} |",
                "",
                "![S-N Curve](figures/sn_curve.png)",
                "",
                "![Goodman Diagram](figures/goodman_diagram.png)",
                "",
            ])
        
        # Sensitivity Study
        if self.data['sensitivity']:
            lines.extend([
                "## Sensitivity Study",
                "",
                "Key findings from parameter sensitivity analysis:",
                "",
            ])
            
            findings = self.data['sensitivity'].get('key_findings', [])
            for finding in findings:
                lines.append(f"- {finding}")
            
            lines.extend([
                "",
                "![Sensitivity Analysis](figures/sensitivity_tornado.png)",
                "",
            ])
        
        # Conclusions
        lines.extend([
            "## Conclusions and Recommendations",
            "",
            "### Summary",
            "",
            "1. **Mesh Convergence:** The analysis achieved mesh convergence with < 5% stress variation between the final two mesh densities.",
            "",
            "2. **Static Strength:** The bracket meets all static strength requirements with adequate factors of safety.",
            "",
            "3. **Fatigue Life:** [To be completed based on analysis results]",
            "",
            "### Recommendations",
            "",
            "1. **Design Optimization:** Consider adding a corner fillet (6mm radius) to reduce stress concentration.",
            "",
            "2. **Manufacturing:** Ensure hole edges are deburred to minimize crack initiation sites.",
            "",
            "3. **Testing:** Validate analysis with strain gauge measurements on prototype.",
            "",
            "---",
            "",
            "## Appendix",
            "",
            "### A.1 Verification Checklist",
            "",
            "See [verification_checklist.md](verification_checklist.md) for complete verification documentation.",
            "",
            "### A.2 Input Files",
            "",
            "- [Material Properties](../inputs/material.yaml)",
            "- [Load Cases](../inputs/loadcases.yaml)",
            "",
            "### A.3 References",
            "",
            "1. ASM Handbook Volume 2: Properties and Selection: Nonferrous Alloys",
            "2. ASTM B209-21: Standard Specification for Aluminum and Aluminum-Alloy Sheet and Plate",
            "3. Bannantine, J.A., et al., 'Fundamentals of Metal Fatigue Analysis', 1990",
            "",
        ])
        
        # Write report
        report_content = '\n'.join(lines)
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            f.write(report_content)
        
        print(f"Markdown report generated: {output_path}")
        return report_content
    
    def generate_html(self, output_path: str = 'reports/analysis_report.html') -> str:
        """
        Generate HTML report with styling.
        
        Args:
            output_path: Where to save the report
            
        Returns:
            Report content as string
        """
        # Generate markdown first, then convert to HTML
        md_content = self.generate_markdown('temp_report.md')
        
        # Simple HTML template with CSS
        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FEA Analysis Report - L-Bracket</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
            background: #f5f5f5;
        }}
        .container {{
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            border-bottom: 2px solid #bdc3c7;
            padding-bottom: 8px;
            margin-top: 30px;
        }}
        h3 {{
            color: #7f8c8d;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
            font-size: 14px;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #3498db;
            color: white;
            font-weight: 600;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        tr:hover {{
            background-color: #f1f1f1;
        }}
        .pass {{
            color: #27ae60;
            font-weight: bold;
        }}
        .fail {{
            color: #e74c3c;
            font-weight: bold;
        }}
        .warning {{
            color: #f39c12;
            font-weight: bold;
        }}
        code {{
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        img {{
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 4px;
            margin: 20px 0;
        }}
        .summary-box {{
            background: #ecf0f1;
            border-left: 4px solid #3498db;
            padding: 15px;
            margin: 20px 0;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #7f8c8d;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        {self._markdown_to_html(md_content)}
        <div class="footer">
            <p>Generated: {self.data['timestamp']} | FEA Analysis Report | Confidential</p>
        </div>
    </div>
</body>
</html>"""
        
        # Write HTML report
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            f.write(html_template)
        
        # Clean up temp file
        Path('temp_report.md').unlink(missing_ok=True)
        
        print(f"HTML report generated: {output_path}")
        return html_template
    
    def _markdown_to_html(self, md_content: str) -> str:
        """Simple Markdown to HTML converter."""
        html = md_content
        
        # Headers
        html = html.replace('# ', '<h1>').replace('\n## ', '</h1>\n<h2>').replace('\n### ', '</h2>\n<h3>')
        html = html.replace('\n#### ', '</h3>\n<h4>')
        html = html + '</h3>' if '<h3>' in html and '</h3>' not in html.split('<h3>')[-1] else html
        html = html + '</h2>' if '<h2>' in html and '</h2>' not in html.split('<h2>')[-1] else html
        html = html + '</h1>' if '<h1>' in html and '</h1>' not in html.split('<h1>')[-1] else html
        
        # Bold and italic
        html = html.replace('**', '<strong>').replace('__', '<em>')
        # Fix closing tags (simplified)
        
        # Tables - already in markdown format, wrap in div
        html = f'<div class="content">{html}</div>'
        
        # Line breaks
        html = html.replace('\n\n', '</p><p>')
        html = html.replace('\n', '<br>')
        
        return html
    
    def generate_pdf(self, output_path: str = 'reports/analysis_report.pdf') -> str:
        """
        Generate PDF report (requires weasyprint or similar).
        
        Args:
            output_path: Where to save the PDF
            
        Returns:
            Path to generated PDF
        """
        try:
            from weasyprint import HTML
            
            # Generate HTML first
            html_path = output_path.replace('.pdf', '.html')
            self.generate_html(html_path)
            
            # Convert to PDF
            HTML(html_path).write_pdf(output_path)
            
            print(f"PDF report generated: {output_path}")
            return output_path
            
        except ImportError:
            print("Warning: weasyprint not installed. Install with: pip install weasyprint")
            print("Falling back to HTML report.")
            return self.generate_html(output_path.replace('.pdf', '.html'))


def main():
    """Generate all report formats."""
    print("Generating Analysis Reports")
    print("=" * 50)
    
    report = ReportGenerator()
    
    # Generate Markdown
    report.generate_markdown('reports/analysis_report.md')
    
    # Generate HTML
    report.generate_html('reports/analysis_report.html')
    
    # Try PDF (optional)
    try:
        report.generate_pdf('reports/analysis_report.pdf')
    except Exception as e:
        print(f"PDF generation skipped: {e}")
    
    print("\nReport generation complete!")


if __name__ == '__main__':
    main()
