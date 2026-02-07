#!/usr/bin/env python3
"""
Plotting Module for FEA Results
Generates publication-quality plots for mesh convergence, stress contours, and sensitivity studies.

Usage:
    from generate_plots import MeshConvergencePlot, SensitivityPlot
    MeshConvergencePlot.create('results/mesh_study/convergence_data.csv')
"""

import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import seaborn as sns

# Set publication-quality defaults
mpl.rcParams['font.size'] = 11
mpl.rcParams['axes.labelsize'] = 12
mpl.rcParams['axes.titlesize'] = 14
mpl.rcParams['xtick.labelsize'] = 10
mpl.rcParams['ytick.labelsize'] = 10
mpl.rcParams['legend.fontsize'] = 10
mpl.rcParams['figure.dpi'] = 150
mpl.rcParams['savefig.dpi'] = 150
mpl.rcParams['savefig.bbox'] = 'tight'


class MeshConvergencePlot:
    """Generate mesh convergence study plots."""
    
    @staticmethod
    def create(convergence_csv: str, output_path: str = 'results/figures/mesh_convergence.png'):
        """
        Create mesh convergence plot from CSV data.
        
        Expected CSV format:
        mesh_id,element_size_mm,element_count,max_stress_mpa,max_disp_mm,solve_time_s
        1,10.0,500,145.2,1.85,2.1
        2,6.0,1500,158.3,1.92,4.5
        ...
        """
        data = pd.read_csv(convergence_csv)
        
        fig, axes = plt.subplots(1, 3, figsize=(14, 4))
        
        # Plot 1: Stress convergence
        ax1 = axes[0]
        ax1.plot(data['element_count'], data['max_stress_mpa'], 
                'bo-', linewidth=2, markersize=8, label='Max Stress')
        
        # Calculate percent change
        stress_change = data['max_stress_mpa'].pct_change() * 100
        for i, (ec, sc, change) in enumerate(zip(data['element_count'][1:], 
                                                  data['max_stress_mpa'][1:],
                                                  stress_change[1:])):
            ax1.annotate(f'{change:+.1f}%', 
                        xy=(ec, sc), 
                        xytext=(10, 10), 
                        textcoords='offset points',
                        fontsize=8,
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.3))
        
        ax1.set_xlabel('Element Count')
        ax1.set_ylabel('Max von Mises Stress (MPa)')
        ax1.set_title('Stress Convergence')
        ax1.grid(True, alpha=0.3)
        ax1.set_xscale('log')
        
        # Plot 2: Displacement convergence
        ax2 = axes[1]
        ax2.plot(data['element_count'], data['max_disp_mm'], 
                'go-', linewidth=2, markersize=8, label='Max Displacement')
        ax2.set_xlabel('Element Count')
        ax2.set_ylabel('Max Displacement (mm)')
        ax2.set_title('Displacement Convergence')
        ax2.grid(True, alpha=0.3)
        ax2.set_xscale('log')
        
        # Plot 3: Solve time vs accuracy trade-off
        ax3 = axes[2]
        scatter = ax3.scatter(data['solve_time_s'], data['max_stress_mpa'],
                            c=data['element_count'], cmap='viridis',
                            s=100, edgecolors='black', linewidth=1)
        
        # Add mesh labels
        for i, row in data.iterrows():
            ax3.annotate(f"Mesh {row['mesh_id']}",
                        xy=(row['solve_time_s'], row['max_stress_mpa']),
                        xytext=(5, 5), textcoords='offset points',
                        fontsize=8)
        
        ax3.set_xlabel('Solve Time (s)')
        ax3.set_ylabel('Max von Mises Stress (MPa)')
        ax3.set_title('Accuracy vs Computational Cost')
        ax3.grid(True, alpha=0.3)
        cbar = plt.colorbar(scatter, ax=ax3)
        cbar.set_label('Element Count')
        
        plt.tight_layout()
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path)
        print(f"Mesh convergence plot saved to: {output_path}")
        plt.close()
        
        return fig
    
    @staticmethod
    def create_element_size_plot(convergence_csv: str, 
                                  output_path: str = 'results/figures/element_size_convergence.png'):
        """Alternative plot showing convergence vs element size (h-refinement)."""
        data = pd.read_csv(convergence_csv)
        
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # Primary axis: Stress
        ax.plot(data['element_size_mm'], data['max_stress_mpa'], 
               'bo-', linewidth=2, markersize=10, label='Max Stress')
        ax.set_xlabel('Element Size (mm)', fontsize=12)
        ax.set_ylabel('Max von Mises Stress (MPa)', color='b', fontsize=12)
        ax.tick_params(axis='y', labelcolor='b')
        ax.grid(True, alpha=0.3)
        
        # Secondary axis: Displacement
        ax2 = ax.twinx()
        ax2.plot(data['element_size_mm'], data['max_disp_mm'], 
                'rs--', linewidth=2, markersize=8, label='Max Displacement')
        ax2.set_ylabel('Max Displacement (mm)', color='r', fontsize=12)
        ax2.tick_params(axis='y', labelcolor='r')
        
        # Convergence threshold line (5%)
        final_stress = data['max_stress_mpa'].iloc[-1]
        threshold = final_stress * 0.05
        ax.axhline(y=final_stress, color='g', linestyle='--', alpha=0.5, 
                  label=f'Converged: {final_stress:.1f} MPa')
        ax.fill_between(data['element_size_mm'], 
                       final_stress - threshold, 
                       final_stress + threshold,
                       alpha=0.1, color='green', label='±5% band')
        
        ax.set_title('Mesh Convergence Study: h-Refinement', fontsize=14)
        
        # Combine legends
        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
        
        plt.tight_layout()
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path)
        print(f"Element size convergence plot saved to: {output_path}")
        plt.close()
        
        return fig


class StressContourPlot:
    """Generate stress contour plots from FEA results."""
    
    @staticmethod
    def create_path_plot(results_csv: str, 
                        path_points: List[Tuple[float, float, float]],
                        output_path: str = 'results/figures/stress_path.png',
                        title: str = 'Stress Distribution Along Path'):
        """
        Plot stress variation along a defined path.
        
        Args:
            results_csv: Path to FEA results CSV
            path_points: List of (x, y, z) coordinates defining the path
            output_path: Where to save the plot
            title: Plot title
        """
        from read_fea_results import FEAResults
        
        results = FEAResults(results_csv)
        
        # Extract stress along path
        path_data = []
        for i, (x, y, z) in enumerate(path_points):
            stress = results.get_stress_at_point(x, y, z)
            if stress:
                path_data.append({
                    'position': i,
                    'distance': i * 5,  # Assuming 5mm spacing
                    'von_mises': stress.von_mises,
                    's1': stress.max_principal,
                    's_hydro': stress.hydrostatic
                })
        
        df = pd.DataFrame(path_data)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.plot(df['distance'], df['von_mises'], 'b-', linewidth=2, 
               label='von Mises', marker='o')
        ax.plot(df['distance'], df['s1'], 'r--', linewidth=2, 
               label='Max Principal', marker='s')
        
        # Add yield strength line
        ax.axhline(y=276, color='g', linestyle=':', linewidth=2, 
                  label='Yield Strength (276 MPa)', alpha=0.7)
        
        ax.set_xlabel('Distance Along Path (mm)', fontsize=12)
        ax.set_ylabel('Stress (MPa)', fontsize=12)
        ax.set_title(title, fontsize=14)
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path)
        print(f"Stress path plot saved to: {output_path}")
        plt.close()
        
        return fig


class SensitivityPlot:
    """Generate sensitivity study visualizations."""
    
    @staticmethod
    def create_tornado(sensitivity_csv: str,
                      output_path: str = 'results/figures/sensitivity_tornado.png',
                      baseline_stress: float = 180.0):
        """
        Create tornado diagram for sensitivity analysis.
        
        Expected CSV format:
        parameter,level,value,percent_change_from_baseline
        thickness,4mm,220.5,22.5
        thickness,6mm,180.0,0.0
        thickness,8mm,152.3,-15.4
        fillet_radius,0mm,210.2,16.8
        ...
        """
        data = pd.read_csv(sensitivity_csv)
        
        # Calculate sensitivity indices (% change per unit change)
        parameters = data['parameter'].unique()
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # Plot 1: Tornado diagram
        ax1 = axes[0]
        
        y_pos = 0
        colors = ['#d62728', '#2ca02c', '#1f77b4']
        
        for i, param in enumerate(parameters):
            param_data = data[data['parameter'] == param]
            min_change = param_data['percent_change_from_baseline'].min()
            max_change = param_data['percent_change_from_baseline'].max()
            
            # Draw bar from min to max
            ax1.barh(y_pos, max_change - min_change, left=min_change, 
                    height=0.6, color=colors[i % len(colors)], 
                    alpha=0.7, edgecolor='black', linewidth=1)
            
            # Add parameter label
            ax1.text(min_change - 2, y_pos, param, 
                    ha='right', va='center', fontsize=10, fontweight='bold')
            
            # Add value labels
            ax1.text(min_change, y_pos, f'{min_change:+.1f}%', 
                    ha='right', va='center', fontsize=9)
            ax1.text(max_change, y_pos, f'{max_change:+.1f}%', 
                    ha='left', va='center', fontsize=9)
            
            y_pos += 1
        
        ax1.axvline(x=0, color='black', linewidth=1)
        ax1.set_xlabel('Percent Change in Max Stress (%)', fontsize=12)
        ax1.set_title('Sensitivity Analysis: Tornado Diagram', fontsize=14)
        ax1.set_yticks([])
        ax1.grid(True, alpha=0.3, axis='x')
        ax1.set_xlim(-30, 30)
        
        # Plot 2: Parameter response curves
        ax2 = axes[1]
        
        for i, param in enumerate(parameters):
            param_data = data[data['parameter'] == param].sort_values('level')
            
            # Extract numeric values from level strings
            try:
                x_vals = [float(str(l).replace('mm', '').replace('GPa', '')) 
                         for l in param_data['level']]
                ax2.plot(x_vals, param_data['value'], 
                        marker='o', linewidth=2, label=param, markersize=8)
            except ValueError:
                # Non-numeric levels (e.g., material names)
                x_vals = range(len(param_data))
                ax2.plot(x_vals, param_data['value'], 
                        marker='o', linewidth=2, label=param, markersize=8)
                ax2.set_xticks(x_vals)
                ax2.set_xticklabels(param_data['level'], rotation=45)
        
        ax2.axhline(y=baseline_stress, color='r', linestyle='--', 
                   label=f'Baseline ({baseline_stress} MPa)')
        ax2.set_xlabel('Parameter Value', fontsize=12)
        ax2.set_ylabel('Max von Mises Stress (MPa)', fontsize=12)
        ax2.set_title('Parameter Response Curves', fontsize=14)
        ax2.legend(loc='best')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path)
        print(f"Sensitivity plot saved to: {output_path}")
        plt.close()
        
        return fig


class FatiguePlot:
    """Generate fatigue analysis plots."""
    
    @staticmethod
    def create_sn_curve(material_yaml: str,
                       output_path: str = 'results/figures/sn_curve.png',
                       stress_points: Optional[List[Tuple[float, float]]] = None):
        """
        Create S-N curve plot with Goodman diagram.
        
        Args:
            material_yaml: Path to material properties YAML
            output_path: Where to save plot
            stress_points: List of (stress_amplitude, cycles) points to overlay
        """
        import yaml
        
        with open(material_yaml, 'r') as f:
            mat = yaml.safe_load(f)['material']['fatigue']
        
        sigma_f_prime = mat['fatigue_strength_coefficient']
        b = mat['fatigue_strength_exponent']
        Se = mat['endurance_limit_corrected']
        
        # Generate S-N curve
        N = np.logspace(3, 8, 1000)  # 10^3 to 10^8 cycles
        S = sigma_f_prime * (2 * N) ** b  # Basquin equation
        
        # Apply endurance limit plateau
        S = np.maximum(S, Se)
        
        fig, ax = plt.subplots(figsize=(10, 7))
        
        # Plot S-N curve
        ax.loglog(N, S, 'b-', linewidth=2.5, label='S-N Curve (Basquin)')
        ax.axhline(y=Se, color='r', linestyle='--', linewidth=2, 
                  label=f'Endurance Limit = {Se} MPa')
        
        # Plot design life point
        design_life = 1e6
        design_stress = sigma_f_prime * (2 * design_life) ** b
        ax.scatter([design_life], [design_stress], color='green', s=150, 
                  zorder=5, marker='*', label=f'Design Point: {design_stress:.1f} MPa @ 10⁶ cycles')
        
        # Overlay actual analysis points if provided
        if stress_points:
            sa_vals, n_vals = zip(*stress_points)
            ax.scatter(n_vals, sa_vals, color='purple', s=100, 
                      marker='o', zorder=5, label='Analysis Results',
                      edgecolors='black', linewidth=1.5)
        
        # Add life regions
        ax.axvline(x=1e3, color='gray', linestyle=':', alpha=0.5)
        ax.axvline(x=1e6, color='gray', linestyle=':', alpha=0.5)
        ax.text(5e3, 300, 'Low Cycle\nFatigue', fontsize=9, ha='center')
        ax.text(5e4, 300, 'High Cycle\nFatigue', fontsize=9, ha='center')
        ax.text(5e7, 300, 'Infinite\nLife', fontsize=9, ha='center')
        
        ax.set_xlabel('Cycles to Failure (N)', fontsize=12)
        ax.set_ylabel('Stress Amplitude (MPa)', fontsize=12)
        ax.set_title('S-N Curve: Aluminum 6061-T6', fontsize=14)
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3, which='both')
        ax.set_xlim(1e3, 1e8)
        ax.set_ylim(50, 500)
        
        plt.tight_layout()
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path)
        print(f"S-N curve plot saved to: {output_path}")
        plt.close()
        
        return fig
    
    @staticmethod
    def create_goodman_diagram(material_yaml: str,
                               output_path: str = 'results/figures/goodman_diagram.png',
                               operating_points: Optional[List[Tuple[float, float]]] = None):
        """
        Create Goodman mean stress correction diagram.
        
        Args:
            material_yaml: Path to material properties
            output_path: Where to save plot
            operating_points: List of (mean_stress, stress_amplitude) points
        """
        import yaml
        
        with open(material_yaml, 'r') as f:
            mat_data = yaml.safe_load(f)['material']
        
        Su = mat_data['strength']['ultimate_strength']
        Se = mat_data['fatigue']['endurance_limit_corrected']
        
        fig, ax = plt.subplots(figsize=(9, 9))
        
        # Goodman line: Sa/Se + Sm/Su = 1
        Sm = np.linspace(0, Su, 100)
        Sa = Se * (1 - Sm / Su)
        
        # Plot Goodman line
        ax.plot(Sm, Sa, 'b-', linewidth=2.5, label='Goodman Line (FoS=1)')
        
        # Plot safety factor lines
        for fos in [2, 3]:
            Sa_fos = (Se / fos) * (1 - Sm / Su)
            ax.plot(Sm, Sa_fos, '--', linewidth=1.5, alpha=0.7, 
                   label=f'FoS = {fos}')
        
        # Plot yield limit (Langer line)
        Sy = mat_data['strength']['yield_strength']
        Sa_yield = Sy - Sm
        ax.plot(Sm, Sa_yield, 'r:', linewidth=2, label='Yield Limit')
        
        # Fill safe region
        ax.fill_between(Sm, 0, np.minimum(Sa, Sa_yield), alpha=0.2, 
                       color='green', label='Safe Region')
        
        # Plot operating points
        if operating_points:
            for i, (sm, sa) in enumerate(operating_points):
                ax.scatter([sm], [sa], color='purple', s=150, zorder=5,
                          marker='o', edgecolors='black', linewidth=2)
                
                # Calculate FoS for this point
                fos = 1 / (sa/Se + sm/Su)
                ax.annotate(f'LC{i+1}\nFoS={fos:.2f}', 
                           xy=(sm, sa), xytext=(10, 10),
                           textcoords='offset points',
                           bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        ax.set_xlabel('Mean Stress (MPa)', fontsize=12)
        ax.set_ylabel('Stress Amplitude (MPa)', fontsize=12)
        ax.set_title('Goodman Mean Stress Correction Diagram', fontsize=14)
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, Su * 1.1)
        ax.set_ylim(0, Se * 1.5)
        
        plt.tight_layout()
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path)
        print(f"Goodman diagram saved to: {output_path}")
        plt.close()
        
        return fig


def create_all_plots(results_dir: str = 'results'):
    """Generate all standard plots for the analysis."""
    print("Generating all analysis plots...")
    print("=" * 50)
    
    results_path = Path(results_dir)
    
    # Mesh convergence
    mesh_csv = results_path / 'mesh_study' / 'convergence_data.csv'
    if mesh_csv.exists():
        MeshConvergencePlot.create(str(mesh_csv))
        MeshConvergencePlot.create_element_size_plot(str(mesh_csv))
    else:
        print(f"Warning: {mesh_csv} not found, skipping mesh plots")
    
    # Sensitivity
    sens_csv = results_path / 'sensitivity' / 'sensitivity_data.csv'
    if sens_csv.exists():
        SensitivityPlot.create_tornado(str(sens_csv))
    else:
        print(f"Warning: {sens_csv} not found, skipping sensitivity plots")
    
    # Fatigue
    mat_yaml = 'inputs/material.yaml'
    if Path(mat_yaml).exists():
        FatiguePlot.create_sn_curve(mat_yaml)
        FatiguePlot.create_goodman_diagram(mat_yaml)
    else:
        print(f"Warning: {mat_yaml} not found, skipping fatigue plots")
    
    print("\nPlot generation complete!")


if __name__ == '__main__':
    create_all_plots()
