"""
Pythia8 Tool
============

Tool for Pythia8 particle physics simulations.
Provides templates and helpers for event generation.
"""

import os
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..config import (
    PYTHIA_WORKSPACE,
    PYTHIA_SCRIPTS_DIR,
    PYTHIA_EVENTS_DIR,
    PYTHIA_RESULTS_DIR,
    PYTHIA_DEFAULT_BEAM,
    PYTHIA_DEFAULT_ENERGY,
    PYTHIA_DEFAULT_NEVENTS,
    PYTHIA_PROCESSES,
    get_timestamp
)


# ============================================================================
# Pythia8 Code Templates
# ============================================================================

PYTHIA_BASIC_TEMPLATE = '''"""
Pythia8 Event Generation Script
Generated: {timestamp}
Process: {process_name}
Energy: {energy} GeV
Events: {nevents}
"""

import pythia8mc

def main():
    # Initialize Pythia
    pythia = pythia8mc.Pythia()
    
    # Beam settings
    pythia.readString("Beams:idA = 2212")  # proton
    pythia.readString("Beams:idB = 2212")  # proton
    pythia.readString("Beams:eCM = {energy}")
    
    # Process settings
{process_settings}
    
    # Initialize
    pythia.init()
    
    # Event loop
    n_events = {nevents}
    for i_event in range(n_events):
        if not pythia.next():
            continue
        
        # Event processing
        event = pythia.event
        multiplicity = event.size()
        
        if i_event < 10:  # Print first 10 events
            print(f"Event {{i_event}}: {{multiplicity}} particles")
    
    # Statistics
    pythia.stat()
    
    print(f"\\nGenerated {{n_events}} events successfully!")

if __name__ == "__main__":
    main()
'''

PYTHIA_HISTOGRAM_TEMPLATE = '''"""
Pythia8 Event Generation with Histogramming
Generated: {timestamp}
Process: {process_name}
"""

import pythia8mc
import numpy as np
import matplotlib.pyplot as plt

def main():
    # Initialize Pythia
    pythia = pythia8mc.Pythia()
    
    # Beam settings
    pythia.readString("Beams:idA = 2212")
    pythia.readString("Beams:idB = 2212")
    pythia.readString("Beams:eCM = {energy}")
    
    # Process settings
{process_settings}
    
    pythia.init()
    
    # Histograms
    pt_values = []
    eta_values = []
    multiplicity_values = []
    
    n_events = {nevents}
    for i_event in range(n_events):
        if not pythia.next():
            continue
        
        event = pythia.event
        n_charged = 0
        
        for i in range(event.size()):
            particle = event[i]
            if particle.isFinal() and particle.isCharged():
                n_charged += 1
                pt_values.append(particle.pT())
                eta_values.append(particle.eta())
        
        multiplicity_values.append(n_charged)
    
    pythia.stat()
    
    # Create histograms
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    
    axes[0].hist(pt_values, bins=50, range=(0, 10))
    axes[0].set_xlabel('pT [GeV]')
    axes[0].set_ylabel('Counts')
    axes[0].set_title('Transverse Momentum')
    
    axes[1].hist(eta_values, bins=50, range=(-5, 5))
    axes[1].set_xlabel('eta')
    axes[1].set_ylabel('Counts')
    axes[1].set_title('Pseudorapidity')
    
    axes[2].hist(multiplicity_values, bins=50)
    axes[2].set_xlabel('N_charged')
    axes[2].set_ylabel('Events')
    axes[2].set_title('Charged Multiplicity')
    
    plt.tight_layout()
    plt.savefig('{output_path}')
    print(f"Saved histogram to {output_path}")
    
    # Print summary
    print(f"\\nSummary:")
    print(f"  Mean pT: {{np.mean(pt_values):.3f}} GeV")
    print(f"  Mean eta: {{np.mean(eta_values):.3f}}")
    print(f"  Mean multiplicity: {{np.mean(multiplicity_values):.1f}}")

if __name__ == "__main__":
    main()
'''

PYTHIA_ANALYSIS_TEMPLATE = '''"""
Pythia8 Analysis Script
Generated: {timestamp}
Analysis: {analysis_name}
"""

import pythia8mc
import json
import numpy as np

def analyze_events(pythia, n_events):
    """Analyze generated events and collect statistics."""
    
    results = {{
        'n_events': n_events,
        'pt_mean': 0,
        'pt_std': 0,
        'eta_mean': 0,
        'multiplicity_mean': 0,
        'cross_section': 0,
        'particles': {{}}
    }}
    
    pt_all = []
    eta_all = []
    mult_all = []
    particle_counts = {{}}
    
    for i_event in range(n_events):
        if not pythia.next():
            continue
        
        event = pythia.event
        n_final = 0
        
        for i in range(event.size()):
            p = event[i]
            if p.isFinal():
                n_final += 1
                pt_all.append(p.pT())
                eta_all.append(p.eta())
                
                pid = abs(p.id())
                name = p.name()
                particle_counts[name] = particle_counts.get(name, 0) + 1
        
        mult_all.append(n_final)
    
    # Compute statistics
    results['pt_mean'] = float(np.mean(pt_all)) if pt_all else 0.0
    results['pt_std'] = float(np.std(pt_all)) if pt_all else 0.0
    results['eta_mean'] = float(np.mean(eta_all)) if eta_all else 0.0
    results['multiplicity_mean'] = float(np.mean(mult_all)) if mult_all else 0.0
    
    # Cross section (with error handling for version compatibility)
    try:
        info = pythia.info
        results['cross_section'] = info.sigmaGen()
        results['cross_section_error'] = info.sigmaErr()
    except AttributeError:
        results['cross_section'] = 0.0
        results['cross_section_error'] = 0.0
    
    # Top 10 particles
    sorted_particles = sorted(particle_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    results['particles'] = dict(sorted_particles)
    
    return results

def main():
    pythia = pythia8mc.Pythia()
    
    # Configuration
    pythia.readString("Beams:idA = 2212")
    pythia.readString("Beams:idB = 2212")
    pythia.readString("Beams:eCM = {energy}")
    
{process_settings}
    
    pythia.init()
    
    # Run analysis
    results = analyze_events(pythia, {nevents})
    
    pythia.stat()
    
    # Save results
    output_file = "{output_path}"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\\nResults saved to {{output_file}}")
    print(f"\\nAnalysis Summary:")
    print(f"  Events: {{results['n_events']}}")
    print(f"  Cross section: {{results['cross_section']:.6e}} mb")
    print(f"  Mean pT: {{results['pt_mean']:.3f}} GeV")
    print(f"  Mean multiplicity: {{results['multiplicity_mean']:.1f}}")

if __name__ == "__main__":
    main()
'''


class PythiaTool:
    """
    Tool for generating Pythia8 simulation scripts.
    
    Provides templates and helpers for particle physics simulations.
    """
    
    name = "pythia_tool"
    description = """Generate Pythia8 simulation scripts for particle physics.
    Available processes: qcd, minbias, higgs, top, w, z, dijet.
    Returns Python code ready for execution."""
    
    def __init__(self, workspace: str = PYTHIA_WORKSPACE):
        self.workspace = workspace
        self.scripts_dir = PYTHIA_SCRIPTS_DIR
        self.events_dir = PYTHIA_EVENTS_DIR
        self.results_dir = PYTHIA_RESULTS_DIR
        
        # Ensure directories exist
        for d in [self.scripts_dir, self.events_dir, self.results_dir]:
            os.makedirs(d, exist_ok=True)
    
    def get_process_settings(self, process_type: str) -> str:
        """Get Pythia settings for a process type."""
        settings = PYTHIA_PROCESSES.get(process_type, PYTHIA_PROCESSES['minbias'])
        lines = settings.split('\n')
        formatted = '\n'.join(f'    pythia.readString("{line}")' for line in lines if line.strip())
        return formatted
    
    def generate_basic_script(self, 
                              process_type: str = 'minbias',
                              energy: int = PYTHIA_DEFAULT_ENERGY,
                              nevents: int = PYTHIA_DEFAULT_NEVENTS,
                              script_name: str = None) -> Dict[str, Any]:
        """
        Generate a basic Pythia8 event generation script.
        
        Args:
            process_type: Type of process (qcd, minbias, higgs, etc.)
            energy: Center of mass energy in GeV
            nevents: Number of events to generate
            script_name: Optional script name
            
        Returns:
            Dict with script code and path
        """
        timestamp = datetime.now().isoformat()
        
        if script_name is None:
            script_name = f"pythia_{process_type}_{get_timestamp()}.py"
        
        if not script_name.endswith('.py'):
            script_name += '.py'
        
        process_settings = self.get_process_settings(process_type)
        
        code = PYTHIA_BASIC_TEMPLATE.format(
            timestamp=timestamp,
            process_name=process_type,
            energy=energy,
            nevents=nevents,
            process_settings=process_settings
        )
        
        script_path = os.path.join(self.scripts_dir, script_name)
        
        return {
            'success': True,
            'code': code,
            'script_path': script_path,
            'script_name': script_name,
            'process_type': process_type,
            'energy': energy,
            'nevents': nevents
        }
    
    def generate_histogram_script(self,
                                  process_type: str = 'minbias',
                                  energy: int = PYTHIA_DEFAULT_ENERGY,
                                  nevents: int = PYTHIA_DEFAULT_NEVENTS,
                                  script_name: str = None,
                                  output_name: str = None) -> Dict[str, Any]:
        """
        Generate a Pythia8 script with histogramming.
        
        Args:
            process_type: Type of process
            energy: Center of mass energy in GeV
            nevents: Number of events
            script_name: Optional script name
            output_name: Output histogram filename
            
        Returns:
            Dict with script code and paths
        """
        timestamp = datetime.now().isoformat()
        ts = get_timestamp()
        
        if script_name is None:
            script_name = f"pythia_hist_{process_type}_{ts}.py"
        
        if output_name is None:
            output_name = f"histogram_{process_type}_{ts}.png"
        
        output_path = os.path.join(self.results_dir, output_name)
        process_settings = self.get_process_settings(process_type)
        
        code = PYTHIA_HISTOGRAM_TEMPLATE.format(
            timestamp=timestamp,
            process_name=process_type,
            energy=energy,
            nevents=nevents,
            process_settings=process_settings,
            output_path=output_path
        )
        
        script_path = os.path.join(self.scripts_dir, script_name)
        
        return {
            'success': True,
            'code': code,
            'script_path': script_path,
            'output_path': output_path,
            'process_type': process_type
        }
    
    def generate_analysis_script(self,
                                 process_type: str = 'minbias',
                                 analysis_name: str = 'default',
                                 energy: int = PYTHIA_DEFAULT_ENERGY,
                                 nevents: int = PYTHIA_DEFAULT_NEVENTS,
                                 script_name: str = None,
                                 output_name: str = None) -> Dict[str, Any]:
        """
        Generate a Pythia8 analysis script.
        
        Args:
            process_type: Type of process
            analysis_name: Name for the analysis
            energy: Center of mass energy
            nevents: Number of events
            script_name: Optional script name
            output_name: Output JSON filename
            
        Returns:
            Dict with script code and paths
        """
        timestamp = datetime.now().isoformat()
        ts = get_timestamp()
        
        if script_name is None:
            script_name = f"analysis_{analysis_name}_{ts}.py"
        
        if output_name is None:
            output_name = f"results_{analysis_name}_{ts}.json"
        
        output_path = os.path.join(self.results_dir, output_name)
        process_settings = self.get_process_settings(process_type)
        
        code = PYTHIA_ANALYSIS_TEMPLATE.format(
            timestamp=timestamp,
            analysis_name=analysis_name,
            energy=energy,
            nevents=nevents,
            process_settings=process_settings,
            output_path=output_path
        )
        
        script_path = os.path.join(self.scripts_dir, script_name)
        
        return {
            'success': True,
            'code': code,
            'script_path': script_path,
            'output_path': output_path,
            'analysis_name': analysis_name
        }
    
    def run(self, action: str, **kwargs) -> Dict[str, Any]:
        """
        Main entry point for the tool.
        
        Args:
            action: Action to perform (basic, histogram, analysis, list_processes)
            **kwargs: Additional arguments for the action
            
        Returns:
            Dict with results
        """
        if action == 'basic':
            return self.generate_basic_script(**kwargs)
        elif action == 'histogram':
            return self.generate_histogram_script(**kwargs)
        elif action == 'analysis':
            return self.generate_analysis_script(**kwargs)
        elif action == 'list_processes':
            return {
                'success': True,
                'processes': list(PYTHIA_PROCESSES.keys()),
                'descriptions': {
                    'qcd': 'Hard QCD processes',
                    'minbias': 'Minimum bias / soft QCD',
                    'higgs': 'Higgs production via gluon fusion',
                    'top': 'Top quark pair production',
                    'w': 'W boson production',
                    'z': 'Z boson production',
                    'dijet': 'Dijet production'
                }
            }
        else:
            return {
                'success': False,
                'error': f"Unknown action: {action}. Use: basic, histogram, analysis, list_processes"
            }
    
    def get_pythia_api_docs(self) -> str:
        """Return a summary of Pythia8 Python API."""
        return '''
Pythia8 Python API Summary (PyPI: pythia8mc, version 8.316)
============================================================

IMPORTANT: The module is 'pythia8mc' (not 'pythia8').
Install: pip install pythia8mc

BASIC USAGE (TESTED AND WORKING):
---------------------------------
import pythia8mc
import os

# Create output directory
os.makedirs("./output", exist_ok=True)

# Initialize Pythia
pythia = pythia8mc.Pythia()

# Beam settings (REQUIRED)
pythia.readString("Beams:idA = 2212")  # proton
pythia.readString("Beams:idB = 2212")  # proton
pythia.readString("Beams:eCM = 5020")  # 5.02 TeV

# Process - USE ONLY ONE OF THESE:
pythia.readString("SoftQCD:all = on")  # Minimum bias (RECOMMENDED)
# OR: pythia.readString("HardQCD:all = on")  # Hard QCD

# Initialize (MUST call after all readString)
pythia.init()

# Event loop
for i in range(1000):
    if not pythia.next():
        continue
    event = pythia.event
    for j in range(event.size()):
        p = event[j]
        if p.isFinal() and p.isCharged():
            print(f"pT={p.pT():.2f}, eta={p.eta():.2f}")

# Print statistics
pythia.stat()

PARTICLE METHODS (SAFE TO USE):
-------------------------------
p = event[i]
p.id()        # PDG ID (int)
p.name()      # Particle name (string)
p.pT()        # Transverse momentum (float)
p.eta()       # Pseudorapidity (float)
p.phi()       # Azimuthal angle (float)
p.e()         # Energy (float)
p.m()         # Mass (float)
p.px(), p.py(), p.pz()  # Momentum components
p.isFinal()   # Is final state particle (bool)
p.isCharged() # Is electrically charged (bool)

VALID PROCESS SETTINGS (USE ONLY THESE):
----------------------------------------
"SoftQCD:all = on"        # Minimum bias - safe, general purpose
"HardQCD:all = on"        # Hard QCD jets
"HardQCD:gg2gg = on"      # Gluon-gluon scattering
"HardQCD:gg2qqbar = on"   # Gluon to quark pair
"Top:gg2ttbar = on"       # Top pair production
"WeakSingleBoson:ffbar2W = on"  # W production
"WeakSingleBoson:ffbar2gmZ = on"  # Z production
"HiggsSM:gg2H = on"       # Higgs via gluon fusion

THINGS TO AVOID (WILL CAUSE ERRORS):
------------------------------------
- "HardQCD:off" - INVALID, just don't enable it
- "SoftQCD:off" - INVALID, just don't enable it
- pythia.info in some versions - use try/except
- Accessing events before init()

COMPLETE WORKING EXAMPLE:
-------------------------
import pythia8mc
import numpy as np
import json
import os

os.makedirs("./output", exist_ok=True)

pythia = pythia8mc.Pythia()
pythia.readString("Beams:idA = 2212")
pythia.readString("Beams:idB = 2212")
pythia.readString("Beams:eCM = 5020")
pythia.readString("SoftQCD:all = on")
pythia.init()

pt_vals = []
eta_vals = []
for i in range(1000):
    if not pythia.next(): continue
    for j in range(pythia.event.size()):
        p = pythia.event[j]
        if p.isFinal() and p.isCharged():
            pt_vals.append(p.pT())
            eta_vals.append(p.eta())

pythia.stat()

results = {"mean_pt": float(np.mean(pt_vals)), "mean_eta": float(np.mean(eta_vals)), "n_particles": len(pt_vals)}
with open("./output/results.json", "w") as f:
    json.dump(results, f, indent=2)
print("Done! Results saved to ./output/results.json")
'''


# Tool function for agent registration
def create_pythia_tool(workspace: str = PYTHIA_WORKSPACE) -> Dict[str, Any]:
    """Create a Pythia tool instance for agent registration."""
    tool = PythiaTool(workspace)
    return {
        'name': tool.name,
        'description': tool.description,
        'function': tool.run,
        'instance': tool
    }

