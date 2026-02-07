#!/usr/bin/env python3
"""
FEA Results Reader Module
Reads exported CSV results from CalculiX/Code_Aster and extracts key metrics.

Usage:
    from read_fea_results import FEAResults
    results = FEAResults('results/static/lc2_results.csv')
    print(f"Max stress: {results.max_von_mises} MPa")
"""

import pandas as pd
import numpy as np
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import yaml


@dataclass
class StressState:
    """Container for stress tensor components."""
    sxx: float
    syy: float
    szz: float
    sxy: float
    syz: float
    sxz: float
    
    @property
    def von_mises(self) -> float:
        """Calculate von Mises equivalent stress."""
        return np.sqrt(0.5 * (
            (self.sxx - self.syy)**2 +
            (self.syy - self.szz)**2 +
            (self.szz - self.sxx)**2 +
            6 * (self.sxy**2 + self.syz**2 + self.sxz**2)
        ))
    
    @property
    def principal_stresses(self) -> Tuple[float, float, float]:
        """Calculate principal stresses (eigenvalues of stress tensor)."""
        stress_tensor = np.array([
            [self.sxx, self.sxy, self.sxz],
            [self.sxy, self.syy, self.syz],
            [self.sxz, self.syz, self.szz]
        ])
        eigenvalues = np.linalg.eigvalsh(stress_tensor)
        return tuple(sorted(eigenvalues, reverse=True))
    
    @property
    def max_principal(self) -> float:
        """Maximum principal stress (σ1)."""
        return self.principal_stresses[0]
    
    @property
    def hydrostatic(self) -> float:
        """Hydrostatic (mean) stress."""
        return (self.sxx + self.syy + self.szz) / 3


class FEAResults:
    """Class to handle FEA result files."""
    
    def __init__(self, csv_path: str):
        """
        Initialize with path to CSV results file.
        
        Expected CSV format (from CalculiX/Code_Aster export):
        node_id, x, y, z, sxx, syy, szz, sxy, syz, sxz, ux, uy, uz
        """
        self.file_path = Path(csv_path)
        self.data = None
        self._load_data()
        
    def _load_data(self) -> None:
        """Load CSV data into pandas DataFrame."""
        if not self.file_path.exists():
            raise FileNotFoundError(f"Results file not found: {self.file_path}")
        
        self.data = pd.read_csv(self.file_path)
        
        # Validate expected columns
        required_cols = ['node_id', 'x', 'y', 'z', 'sxx', 'syy', 'szz']
        missing = [c for c in required_cols if c not in self.data.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
    
    @property
    def node_count(self) -> int:
        """Number of nodes in result file."""
        return len(self.data)
    
    @property
    def max_von_mises(self) -> float:
        """Maximum von Mises stress in model."""
        vm_stresses = self.data.apply(
            lambda row: StressState(
                row['sxx'], row['syy'], row['szz'],
                row.get('sxy', 0), row.get('syz', 0), row.get('sxz', 0)
            ).von_mises,
            axis=1
        )
        return vm_stresses.max()
    
    @property
    def max_von_mises_location(self) -> Tuple[float, float, float]:
        """Coordinates of maximum von Mises stress location."""
        self.data['von_mises'] = self.data.apply(
            lambda row: StressState(
                row['sxx'], row['syy'], row['szz'],
                row.get('sxy', 0), row.get('syz', 0), row.get('sxz', 0)
            ).von_mises,
            axis=1
        )
        max_row = self.data.loc[self.data['von_mises'].idxmax()]
        return (max_row['x'], max_row['y'], max_row['z'])
    
    @property
    def max_displacement(self) -> float:
        """Maximum total displacement magnitude."""
        if 'ux' not in self.data.columns:
            return 0.0
        disp_mag = np.sqrt(
            self.data['ux']**2 + 
            self.data['uy']**2 + 
            self.data['uz']**2
        )
        return disp_mag.max()
    
    @property
    def max_displacement_location(self) -> Tuple[float, float, float]:
        """Coordinates of maximum displacement location."""
        if 'ux' not in self.data.columns:
            return (0, 0, 0)
        disp_mag = np.sqrt(
            self.data['ux']**2 + 
            self.data['uy']**2 + 
            self.data['uz']**2
        )
        max_idx = disp_mag.idxmax()
        row = self.data.loc[max_idx]
        return (row['x'], row['y'], row['z'])
    
    def get_stress_at_point(self, x: float, y: float, z: float, 
                           tolerance: float = 1.0) -> Optional[StressState]:
        """
        Get stress state at specific coordinates (nearest node).
        
        Args:
            x, y, z: Coordinates to query
            tolerance: Search radius
            
        Returns:
            StressState object or None if no node within tolerance
        """
        distances = np.sqrt(
            (self.data['x'] - x)**2 +
            (self.data['y'] - y)**2 +
            (self.data['z'] - z)**2
        )
        
        if distances.min() > tolerance:
            return None
            
        nearest = self.data.loc[distances.idxmin()]
        return StressState(
            nearest['sxx'], nearest['syy'], nearest['szz'],
            nearest.get('sxy', 0),
            nearest.get('syz', 0),
            nearest.get('sxz', 0)
        )
    
    def get_reaction_forces(self, constraint_nodes: List[int]) -> Dict[str, float]:
        """
        Calculate reaction forces at constrained nodes.
        
        Note: This requires reaction force data in the CSV.
        If not available, use solver output directly.
        
        Args:
            constraint_nodes: List of node IDs at constraints
            
        Returns:
            Dictionary with reaction force components
        """
        # This is a placeholder - actual implementation depends on
        # how reaction forces are exported from your solver
        return {'rx': 0, 'ry': 0, 'rz': 0, 'total': 0}
    
    def extract_critical_path(self, start_point: Tuple[float, float, float],
                             end_point: Tuple[float, float, float],
                             num_points: int = 20) -> pd.DataFrame:
        """
        Extract stress values along a path between two points.
        
        Args:
            start_point: (x, y, z) start coordinates
            end_point: (x, y, z) end coordinates
            num_points: Number of interpolation points
            
        Returns:
            DataFrame with path coordinates and stresses
        """
        path_data = []
        for i in range(num_points):
            t = i / (num_points - 1)
            x = start_point[0] + t * (end_point[0] - start_point[0])
            y = start_point[1] + t * (end_point[1] - start_point[1])
            z = start_point[2] + t * (end_point[2] - start_point[2])
            
            stress = self.get_stress_at_point(x, y, z)
            if stress:
                path_data.append({
                    'position': t,
                    'x': x, 'y': y, 'z': z,
                    'sxx': stress.sxx, 'syy': stress.syy, 'szz': stress.szz,
                    'von_mises': stress.von_mises,
                    's1': stress.max_principal
                })
        
        return pd.DataFrame(path_data)
    
    def get_summary_stats(self) -> Dict:
        """Get summary statistics for the results."""
        self.data['von_mises'] = self.data.apply(
            lambda row: StressState(
                row['sxx'], row['syy'], row['szz'],
                row.get('sxy', 0), row.get('syz', 0), row.get('sxz', 0)
            ).von_mises,
            axis=1
        )
        
        stats = {
            'node_count': self.node_count,
            'max_von_mises': self.max_von_mises,
            'max_von_mises_location': self.max_von_mises_location,
            'mean_von_mises': self.data['von_mises'].mean(),
            'std_von_mises': self.data['von_mises'].std(),
            'max_displacement': self.max_displacement,
            'max_displacement_location': self.max_displacement_location,
        }
        
        # Add principal stress stats
        principal_stats = self.data.apply(
            lambda row: StressState(
                row['sxx'], row['syy'], row['szz'],
                row.get('sxy', 0), row.get('syz', 0), row.get('sxz', 0)
            ).principal_stresses,
            axis=1, result_type='expand'
        )
        principal_stats.columns = ['s1', 's2', 's3']
        
        stats['max_principal'] = principal_stats['s1'].max()
        stats['min_principal'] = principal_stats['s3'].min()
        
        return stats


def load_material_properties(yaml_path: str = 'inputs/material.yaml') -> Dict:
    """Load material properties from YAML file."""
    with open(yaml_path, 'r') as f:
        return yaml.safe_load(f)


def load_load_cases(yaml_path: str = 'inputs/loadcases.yaml') -> Dict:
    """Load load case definitions from YAML file."""
    with open(yaml_path, 'r') as f:
        return yaml.safe_load(f)


if __name__ == '__main__':
    # Example usage
    print("FEA Results Reader - Example Usage")
    print("=" * 50)
    
    # Load material and load case data
    material = load_material_properties()
    load_cases = load_load_cases()
    
    print(f"\nMaterial: {material['material']['name']}")
    print(f"Yield Strength: {material['material']['strength']['yield_strength']} MPa")
    
    print(f"\nLoad Cases Defined:")
    for lc_id, lc_data in load_cases['analysis']['load_cases'].items():
        print(f"  - {lc_id}: {lc_data['name']}")
    
    # Example: Load results (if file exists)
    results_path = 'results/static/lc2_von_mises.csv'
    if Path(results_path).exists():
        results = FEAResults(results_path)
        stats = results.get_summary_stats()
        print(f"\nResults Summary:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
    else:
        print(f"\nNote: Results file '{results_path}' not found.")
        print("Run FEA analysis and export CSV to use this module.")
