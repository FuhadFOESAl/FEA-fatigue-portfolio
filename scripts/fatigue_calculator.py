#!/usr/bin/env python3
"""
Fatigue Life Calculator Module
Implements stress-based fatigue analysis with mean stress corrections.

Usage:
    from fatigue_calculator import FatigueAnalyzer
    
    analyzer = FatigueAnalyzer('inputs/material.yaml')
    life = analyzer.calculate_life(Smax=200, Smin=50, method='goodman')
    print(f"Predicted life: {life:.2e} cycles")
"""

import numpy as np
import yaml
from dataclasses import dataclass
from typing import Dict, Optional, Tuple, Literal
from pathlib import Path


@dataclass
class StressCycle:
    """Container for cyclic stress parameters."""
    smax: float      # Maximum stress (MPa)
    smin: float      # Minimum stress (MPa)
    
    @property
    def mean_stress(self) -> float:
        """Mean stress: Sm = (Smax + Smin) / 2"""
        return (self.smax + self.smin) / 2
    
    @property
    def stress_amplitude(self) -> float:
        """Stress amplitude: Sa = (Smax - Smin) / 2"""
        return (self.smax - self.smin) / 2
    
    @property
    def stress_range(self) -> float:
        """Stress range: ΔS = Smax - Smin"""
        return self.smax - self.smin
    
    @property
    def r_ratio(self) -> float:
        """Stress ratio: R = Smin / Smax"""
        if self.smax == 0:
            return -1 if self.smin < 0 else 1
        return self.smin / self.smax


class FatigueAnalyzer:
    """Fatigue life prediction using stress-based methods."""
    
    def __init__(self, material_yaml: str = 'inputs/material.yaml'):
        """
        Initialize with material properties.
        
        Args:
            material_yaml: Path to material properties YAML file
        """
        self.material = self._load_material(material_yaml)
        self._validate_properties()
    
    def _load_material(self, yaml_path: str) -> Dict:
        """Load material properties from YAML."""
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)
        return data['material']
    
    def _validate_properties(self) -> None:
        """Validate that required fatigue properties exist."""
        required = [
            'strength.ultimate_strength',
            'strength.yield_strength',
            'fatigue.fatigue_strength_coefficient',
            'fatigue.fatigue_strength_exponent',
            'fatigue.endurance_limit_corrected'
        ]
        
        for prop in required:
            keys = prop.split('.')
            value = self.material
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    raise ValueError(f"Missing required material property: {prop}")
    
    @property
    def ultimate_strength(self) -> float:
        """Ultimate tensile strength (MPa)."""
        return self.material['strength']['ultimate_strength']
    
    @property
    def yield_strength(self) -> float:
        """Yield strength (MPa)."""
        return self.material['strength']['yield_strength']
    
    @property
    def fatigue_strength_coefficient(self) -> float:
        """Fatigue strength coefficient σ'f (MPa)."""
        return self.material['fatigue']['fatigue_strength_coefficient']
    
    @property
    def fatigue_strength_exponent(self) -> float:
        """Fatigue strength exponent b (dimensionless)."""
        return self.material['fatigue']['fatigue_strength_exponent']
    
    @property
    def endurance_limit(self) -> float:
        """Corrected endurance limit Se (MPa)."""
        return self.material['fatigue']['endurance_limit_corrected']
    
    def basquin_cycles(self, stress_amplitude: float) -> float:
        """
        Calculate cycles to failure using Basquin equation.
        
        Basquin: σa = σ'f × (2N)^b
        Solving for N: N = 0.5 × (σa/σ'f)^(1/b)
        
        Args:
            stress_amplitude: Fully reversed stress amplitude (MPa)
            
        Returns:
            Predicted cycles to failure
        """
        sigma_f = self.fatigue_strength_coefficient
        b = self.fatigue_strength_exponent
        Se = self.endurance_limit
        
        # Check endurance limit
        if stress_amplitude <= Se:
            return float('inf')  # Infinite life
        
        # Basquin equation
        N = 0.5 * (stress_amplitude / sigma_f) ** (1 / b)
        
        return max(N, 1e3)  # Minimum 1000 cycles
    
    def goodman_equivalent_stress(self, stress_cycle: StressCycle) -> float:
        """
        Calculate equivalent fully reversed stress using Goodman correction.
        
        Goodman: Sa/Se + Sm/Su = 1
        Equivalent stress: Seq = Sa / (1 - Sm/Su)
        
        Args:
            stress_cycle: StressCycle object with Smax, Smin
            
        Returns:
            Equivalent fully reversed stress amplitude (MPa)
        """
        Sa = stress_cycle.stress_amplitude
        Sm = stress_cycle.mean_stress
        Su = self.ultimate_strength
        
        # Goodman mean stress correction
        if Sm >= Su:
            return float('inf')  # Mean stress exceeds ultimate
        
        equivalent_stress = Sa / (1 - Sm / Su)
        
        return equivalent_stress
    
    def gerber_equivalent_stress(self, stress_cycle: StressCycle) -> float:
        """
        Calculate equivalent stress using Gerber parabola (less conservative).
        
        Gerber: Sa/Se + (Sm/Su)^2 = 1
        
        Args:
            stress_cycle: StressCycle object
            
        Returns:
            Equivalent fully reversed stress amplitude (MPa)
        """
        Sa = stress_cycle.stress_amplitude
        Sm = stress_cycle.mean_stress
        Su = self.ultimate_strength
        
        equivalent_stress = Sa / (1 - (Sm / Su) ** 2)
        
        return equivalent_stress
    
    def soderberg_equivalent_stress(self, stress_cycle: StressCycle) -> float:
        """
        Calculate equivalent stress using Soderberg (most conservative).
        
        Soderberg: Sa/Se + Sm/Sy = 1
        
        Args:
            stress_cycle: StressCycle object
            
        Returns:
            Equivalent fully reversed stress amplitude (MPa)
        """
        Sa = stress_cycle.stress_amplitude
        Sm = stress_cycle.mean_stress
        Sy = self.yield_strength
        
        equivalent_stress = Sa / (1 - Sm / Sy)
        
        return equivalent_stress
    
    def calculate_life(self, 
                      smax: float, 
                      smin: float,
                      method: Literal['goodman', 'gerber', 'soderberg'] = 'goodman') -> Dict:
        """
        Calculate fatigue life with mean stress correction.
        
        Args:
            smax: Maximum stress in cycle (MPa)
            smin: Minimum stress in cycle (MPa)
            method: Mean stress correction method
            
        Returns:
            Dictionary with life prediction results
        """
        cycle = StressCycle(smax, smin)
        
        # Select correction method
        if method == 'goodman':
            equivalent_stress = self.goodman_equivalent_stress(cycle)
        elif method == 'gerber':
            equivalent_stress = self.gerber_equivalent_stress(cycle)
        elif method == 'soderberg':
            equivalent_stress = self.soderberg_equivalent_stress(cycle)
        else:
            raise ValueError(f"Unknown method: {method}")
        
        # Calculate life using Basquin
        cycles = self.basquin_cycles(equivalent_stress)
        
        # Calculate safety factor on life
        design_life = 1e6
        fos_life = cycles / design_life if cycles < float('inf') else float('inf')
        
        # Calculate safety factor on stress (Goodman)
        Se = self.endurance_limit
        Su = self.ultimate_strength
        Sa = cycle.stress_amplitude
        Sm = cycle.mean_stress
        
        if Sa > 0:
            fos_stress = 1 / (Sa/Se + Sm/Su)
        else:
            fos_stress = float('inf')
        
        return {
            'smax': smax,
            'smin': smin,
            'mean_stress': Sm,
            'stress_amplitude': Sa,
            'r_ratio': cycle.r_ratio,
            'equivalent_stress': equivalent_stress,
            'method': method,
            'predicted_cycles': cycles,
            'predicted_life_log': np.log10(cycles) if cycles < float('inf') else float('inf'),
            'fos_on_life': fos_life,
            'fos_on_stress': fos_stress,
            'infinite_life': cycles >= 1e7
        }
    
    def miners_rule(self, 
                   load_spectrum: list,
                   method: Literal['goodman', 'gerber', 'soderberg'] = 'goodman') -> Dict:
        """
        Calculate cumulative damage using Miner's linear rule.
        
        Args:
            load_spectrum: List of (smax, smin, cycles) tuples
            method: Mean stress correction method
            
        Returns:
            Dictionary with damage accumulation results
        """
        total_damage = 0
        block_results = []
        
        for smax, smin, n_cycles in load_spectrum:
            life_result = self.calculate_life(smax, smin, method)
            N_f = life_result['predicted_cycles']
            
            if N_f == float('inf'):
                damage = 0
            else:
                damage = n_cycles / N_f
            
            total_damage += damage
            
            block_results.append({
                'smax': smax,
                'smin': smin,
                'n_applied': n_cycles,
                'N_failure': N_f,
                'damage': damage
            })
        
        # Predicted life based on total damage
        if total_damage > 0:
            predicted_blocks = 1 / total_damage
        else:
            predicted_blocks = float('inf')
        
        return {
            'total_damage': total_damage,
            'predicted_blocks': predicted_blocks,
            'failure_predicted': total_damage >= 1.0,
            'block_details': block_results
        }
    
    def generate_sn_data(self, 
                        n_points: int = 50,
                        include_mean_stress: bool = True) -> Dict:
        """
        Generate S-N curve data for plotting.
        
        Args:
            n_points: Number of points to generate
            include_mean_stress: Include mean stress correction curves
            
        Returns:
            Dictionary with S-N curve data
        """
        # Fully reversed (R=-1)
        N = np.logspace(3, 8, n_points)
        S_rev = self.fatigue_strength_coefficient * (2 * N) ** self.fatigue_strength_exponent
        S_rev = np.maximum(S_rev, self.endurance_limit)
        
        data = {
            'cycles': N.tolist(),
            'stress_fully_reversed': S_rev.tolist(),
            'endurance_limit': self.endurance_limit
        }
        
        if include_mean_stress:
            # R=0 (pulsating tension)
            S_r0 = []
            for n in N:
                # Iterative solution for R=0
                # Sa = Sm, Goodman: Sa/Se + Sa/Su = 1 => Sa = 1/(1/Se + 1/Su)
                Sa_equiv = self.fatigue_strength_coefficient * (2 * n) ** self.fatigue_strength_exponent
                Sa_equiv = max(Sa_equiv, self.endurance_limit)
                # For R=0: Sa = Sm, Goodman gives Sa = Seq * (1 - Sa/Su)
                # Solving: Sa = Seq / (1 + Seq/Su)
                Sa = Sa_equiv / (1 + Sa_equiv / self.ultimate_strength)
                S_r0.append(Sa)
            data['stress_r0'] = S_r0
        
        return data


def example_usage():
    """Demonstrate fatigue calculator usage."""
    print("Fatigue Life Calculator - Example Usage")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = FatigueAnalyzer('inputs/material.yaml')
    
    print(f"\nMaterial: {analyzer.material['name']}")
    print(f"Ultimate Strength: {analyzer.ultimate_strength} MPa")
    print(f"Endurance Limit: {analyzer.endurance_limit} MPa")
    print(f"Fatigue Coefficient: {analyzer.fatigue_strength_coefficient} MPa")
    print(f"Fatigue Exponent: {analyzer.fatigue_strength_exponent}")
    
    # Example 1: Fully reversed loading (R=-1)
    print("\n" + "-" * 60)
    print("Example 1: Fully Reversed Loading (R=-1)")
    print("-" * 60)
    
    result = analyzer.calculate_life(smax=150, smin=-150, method='goodman')
    print(f"Smax = {result['smax']} MPa, Smin = -150 MPa")
    print(f"Mean Stress = {result['mean_stress']} MPa")
    print(f"Stress Amplitude = {result['stress_amplitude']} MPa")
    print(f"Predicted Life = {result['predicted_cycles']:.2e} cycles")
    print(f"Safety Factor on Life = {result['fos_on_life']:.2f}")
    
    # Example 2: Pulsating tension (R=0)
    print("\n" + "-" * 60)
    print("Example 2: Pulsating Tension (R=0)")
    print("-" * 60)
    
    result = analyzer.calculate_life(smax=120, smin=0, method='goodman')
    print(f"Smax = {result['smax']} MPa, Smin = 0 MPa")
    print(f"Mean Stress = {result['mean_stress']} MPa")
    print(f"Stress Amplitude = {result['stress_amplitude']} MPa")
    print(f"Equivalent Stress (Goodman) = {result['equivalent_stress']:.1f} MPa")
    print(f"Predicted Life = {result['predicted_cycles']:.2e} cycles")
    print(f"Safety Factor on Stress = {result['fos_on_stress']:.2f}")
    
    # Example 3: Mean stress with vibration (R=0.43)
    print("\n" + "-" * 60)
    print("Example 3: Combined Static + Vibration (R=0.43)")
    print("-" * 60)
    
    result = analyzer.calculate_life(smax=100, smin=30, method='goodman')
    print(f"Smax = {result['smax']} MPa, Smin = {result['smin']} MPa")
    print(f"Mean Stress = {result['mean_stress']} MPa")
    print(f"Stress Amplitude = {result['stress_amplitude']} MPa")
    print(f"R-ratio = {result['r_ratio']:.2f}")
    print(f"Predicted Life = {result['predicted_cycles']:.2e} cycles")
    
    # Example 4: Miner's rule with load spectrum
    print("\n" + "-" * 60)
    print("Example 4: Miner's Rule - Load Spectrum")
    print("-" * 60)
    
    # Define load spectrum: (smax, smin, cycles)
    spectrum = [
        (80, 40, 900000),    # 90% at low stress
        (100, 30, 100000),   # 10% at high stress
    ]
    
    miners_result = analyzer.miners_rule(spectrum, method='goodman')
    print("Load Spectrum:")
    for block in miners_result['block_details']:
        print(f"  Smax={block['smax']}, Smin={block['smin']}, "
              f"n={block['n_applied']:.0e}, N={block['N_failure']:.2e}, "
              f"D={block['damage']:.4f}")
    
    print(f"\nTotal Damage = {miners_result['total_damage']:.4f}")
    print(f"Predicted Blocks to Failure = {miners_result['predicted_blocks']:.2f}")
    print(f"Failure Predicted: {miners_result['failure_predicted']}")
    
    # Example 5: Compare mean stress correction methods
    print("\n" + "-" * 60)
    print("Example 5: Mean Stress Correction Comparison")
    print("-" * 60)
    
    smax, smin = 120, 40
    for method in ['goodman', 'gerber', 'soderberg']:
        result = analyzer.calculate_life(smax, smin, method=method)
        print(f"{method.capitalize():12s}: Life = {result['predicted_cycles']:.2e} cycles, "
              f"FoS = {result['fos_on_stress']:.2f}")
    
    print("\n" + "=" * 60)
    print("Analysis complete!")


if __name__ == '__main__':
    example_usage()
