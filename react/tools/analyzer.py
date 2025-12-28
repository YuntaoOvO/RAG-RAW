"""
Analyzer Tool
=============

Tool for analyzing results from Pythia simulations and literature reviews.
"""

import os
import re
import json
from typing import Dict, Any, List, Optional
from collections import Counter

from ..config import (
    BASE_DIR,
    OUTPUT_DIR,
    PYTHIA_RESULTS_DIR,
    PYTHIA_FIGURES_DIR,
    TIMESTAMP
)


class AnalyzerTool:
    """
    Tool for analyzing simulation results and extracting information.
    
    Features:
    - Parse Pythia output files
    - Extract future work items from literature reviews
    - Statistical analysis of results
    """
    
    name = "analyzer"
    description = """Analyze results from simulations and documents.
    Can extract future work items from LaTeX files,
    parse simulation outputs, and compute statistics."""
    
    def __init__(self, output_dir: str = OUTPUT_DIR, 
                 results_dir: str = PYTHIA_RESULTS_DIR,
                 figures_dir: str = PYTHIA_FIGURES_DIR):
        self.output_dir = output_dir
        self.results_dir = results_dir
        self.figures_dir = figures_dir
    
    def run(self, action: str, **kwargs) -> Dict[str, Any]:
        """
        Main entry point for the analyzer.
        
        Args:
            action: Action to perform
            **kwargs: Additional arguments
            
        Returns:
            Analysis results
        """
        if action == 'extract_future_work':
            return self.extract_future_work(**kwargs)
        elif action == 'parse_simulation_results':
            return self.parse_simulation_results(**kwargs)
        elif action == 'summarize_literature':
            return self.summarize_literature_review(**kwargs)
        elif action == 'analyze_statistics':
            return self.analyze_statistics(**kwargs)
        elif action == 'list_figures':
            return self.list_available_figures(**kwargs)
        elif action == 'validate_figures':
            return self.validate_figure_references(**kwargs)
        else:
            return {
                'success': False,
                'error': f"Unknown action: {action}"
            }
    
    def extract_future_work(self, tex_file: str = None, 
                           content: str = None) -> Dict[str, Any]:
        """
        Extract future work items from a LaTeX literature review.
        
        Args:
            tex_file: Path to the tex file
            content: LaTeX content string (alternative to file)
            
        Returns:
            Dict with extracted future work items
        """
        # Load content
        if content is None:
            if tex_file is None:
                # Try default file
                tex_file = os.path.join(self.output_dir, f"final_review_{TIMESTAMP}.tex")
            
            if not os.path.exists(tex_file):
                return {
                    'success': False,
                    'error': f"File not found: {tex_file}"
                }
            
            with open(tex_file, 'r', encoding='utf-8') as f:
                content = f.read()
        
        future_work_items = []
        
        # Pattern 1: Look for "Future Work" or "Future Directions" section
        future_section_patterns = [
            r'\\section\{[^}]*[Ff]uture[^}]*\}(.*?)(?=\\section|\\end\{document\}|$)',
            r'\\subsection\{[^}]*[Ff]uture[^}]*\}(.*?)(?=\\section|\\subsection|\\end\{document\}|$)',
            r'Future [Ww]ork[:\s]+(.*?)(?=\\section|\\subsection|\n\n\n|$)',
            r'Future [Dd]irections[:\s]+(.*?)(?=\\section|\\subsection|\n\n\n|$)',
        ]
        
        future_sections = []
        for pattern in future_section_patterns:
            matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
            future_sections.extend(matches)
        
        # Pattern 2: Look for enumerated items
        item_patterns = [
            r'\\item\s+(.+?)(?=\\item|\\end\{|$)',
            r'\d+\.\s+(.+?)(?=\d+\.|$)',
            r'•\s+(.+?)(?=•|$)',
            r'-\s+(.+?)(?=-\s|$)',
        ]
        
        for section in future_sections:
            for pattern in item_patterns:
                items = re.findall(pattern, section, re.DOTALL)
                for item in items:
                    cleaned = self._clean_latex(item)
                    if cleaned and len(cleaned) > 20:  # Filter out too short items
                        future_work_items.append(cleaned)
        
        # Pattern 3: Look for sentences with future-oriented keywords
        future_keywords = [
            'should be investigated',
            'future work',
            'remains to be',
            'further study',
            'open question',
            'unexplored',
            'could be extended',
            'promising direction',
            'needs further',
            'would be interesting'
        ]
        
        sentences = re.split(r'[.!?]\s+', content)
        for sentence in sentences:
            for keyword in future_keywords:
                if keyword.lower() in sentence.lower():
                    cleaned = self._clean_latex(sentence)
                    if cleaned and len(cleaned) > 30 and cleaned not in future_work_items:
                        future_work_items.append(cleaned)
                    break
        
        # Remove duplicates while preserving order
        seen = set()
        unique_items = []
        for item in future_work_items:
            normalized = item.lower().strip()[:50]  # Compare first 50 chars
            if normalized not in seen:
                seen.add(normalized)
                unique_items.append(item)
        
        # Categorize items
        categories = self._categorize_future_work(unique_items)
        
        return {
            'success': True,
            'future_work_items': unique_items,
            'count': len(unique_items),
            'categories': categories,
            'source_file': tex_file
        }
    
    def _clean_latex(self, text: str) -> str:
        """Remove LaTeX commands from text."""
        # Remove common LaTeX commands
        text = re.sub(r'\\cite\{[^}]*\}', '', text)
        text = re.sub(r'\\ref\{[^}]*\}', '', text)
        text = re.sub(r'\\label\{[^}]*\}', '', text)
        text = re.sub(r'\\textbf\{([^}]*)\}', r'\1', text)
        text = re.sub(r'\\textit\{([^}]*)\}', r'\1', text)
        text = re.sub(r'\\emph\{([^}]*)\}', r'\1', text)
        text = re.sub(r'\\\w+\{[^}]*\}', '', text)
        text = re.sub(r'\\\w+', '', text)
        text = re.sub(r'[{}]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _categorize_future_work(self, items: List[str]) -> Dict[str, List[str]]:
        """Categorize future work items by topic."""
        categories = {
            'simulation': [],
            'theoretical': [],
            'experimental': [],
            'methodology': [],
            'other': []
        }
        
        simulation_keywords = ['simulation', 'pythia', 'monte carlo', 'numerical', 'compute']
        theoretical_keywords = ['theory', 'theoretical', 'analytical', 'derive', 'equation']
        experimental_keywords = ['experiment', 'data', 'measurement', 'detector', 'collider']
        methodology_keywords = ['method', 'algorithm', 'technique', 'approach', 'framework']
        
        for item in items:
            item_lower = item.lower()
            categorized = False
            
            if any(kw in item_lower for kw in simulation_keywords):
                categories['simulation'].append(item)
                categorized = True
            if any(kw in item_lower for kw in theoretical_keywords):
                categories['theoretical'].append(item)
                categorized = True
            if any(kw in item_lower for kw in experimental_keywords):
                categories['experimental'].append(item)
                categorized = True
            if any(kw in item_lower for kw in methodology_keywords):
                categories['methodology'].append(item)
                categorized = True
            
            if not categorized:
                categories['other'].append(item)
        
        return {k: v for k, v in categories.items() if v}  # Remove empty categories
    
    def parse_simulation_results(self, results_file: str = None,
                                 content: str = None) -> Dict[str, Any]:
        """
        Parse Pythia simulation results from JSON file.
        
        Args:
            results_file: Path to the results JSON file
            content: JSON content string
            
        Returns:
            Parsed and analyzed results
        """
        if content is None:
            if results_file is None:
                return {
                    'success': False,
                    'error': "No results file or content provided"
                }
            
            if not os.path.exists(results_file):
                return {
                    'success': False,
                    'error': f"File not found: {results_file}"
                }
            
            with open(results_file, 'r', encoding='utf-8') as f:
                content = f.read()
        
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            return {
                'success': False,
                'error': f"Invalid JSON: {str(e)}"
            }
        
        # Analyze the results
        analysis = {
            'success': True,
            'raw_data': data,
            'summary': {},
            'interpretation': []
        }
        
        # Extract key metrics
        if 'n_events' in data:
            analysis['summary']['events'] = data['n_events']
        
        if 'cross_section' in data:
            analysis['summary']['cross_section_mb'] = data['cross_section']
            analysis['interpretation'].append(
                f"Cross section: {data['cross_section']:.6e} mb"
            )
        
        if 'pt_mean' in data:
            analysis['summary']['mean_pt_gev'] = data['pt_mean']
            analysis['interpretation'].append(
                f"Mean transverse momentum: {data['pt_mean']:.3f} GeV"
            )
        
        if 'multiplicity_mean' in data:
            analysis['summary']['mean_multiplicity'] = data['multiplicity_mean']
            analysis['interpretation'].append(
                f"Mean particle multiplicity: {data['multiplicity_mean']:.1f}"
            )
        
        if 'particles' in data:
            analysis['summary']['top_particles'] = data['particles']
            top_particles = list(data['particles'].keys())[:5]
            analysis['interpretation'].append(
                f"Most common particles: {', '.join(top_particles)}"
            )
        
        # Extract generated figures if present
        if 'generated_figures' in data:
            figures = data['generated_figures']
            valid_figures = []
            for fig in figures:
                fig_path = fig.get('path', '')
                if os.path.exists(fig_path):
                    valid_figures.append(fig)
                else:
                    analysis['interpretation'].append(
                        f"Warning: Figure not found: {fig_path}"
                    )
            analysis['summary']['generated_figures'] = valid_figures
            analysis['summary']['figure_count'] = len(valid_figures)
        else:
            analysis['summary']['generated_figures'] = []
            analysis['summary']['figure_count'] = 0
        
        return analysis
    
    def summarize_literature_review(self, tex_file: str = None) -> Dict[str, Any]:
        """
        Summarize a literature review document.
        
        Args:
            tex_file: Path to the tex file
            
        Returns:
            Summary of the document
        """
        if tex_file is None:
            tex_file = os.path.join(self.output_dir, f"final_review_{TIMESTAMP}.tex")
        
        if not os.path.exists(tex_file):
            return {
                'success': False,
                'error': f"File not found: {tex_file}"
            }
        
        with open(tex_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract sections
        sections = re.findall(r'\\section\{([^}]+)\}', content)
        
        # Count citations
        citations = re.findall(r'\\cite\{([^}]+)\}', content)
        all_refs = []
        for cite in citations:
            all_refs.extend(cite.split(','))
        unique_refs = list(set(ref.strip() for ref in all_refs))
        
        # Word count (approximate)
        clean_text = self._clean_latex(content)
        word_count = len(clean_text.split())
        
        # Extract key terms
        terms = self._extract_key_terms(clean_text)
        
        return {
            'success': True,
            'file': tex_file,
            'sections': sections,
            'section_count': len(sections),
            'citations': unique_refs,
            'citation_count': len(unique_refs),
            'word_count': word_count,
            'key_terms': terms[:20]
        }
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms from text."""
        # Simple frequency-based extraction
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        
        # Remove common words
        stopwords = {
            'this', 'that', 'with', 'from', 'have', 'been', 'were', 'will',
            'would', 'could', 'should', 'their', 'there', 'these', 'those',
            'which', 'about', 'also', 'into', 'more', 'some', 'such', 'than',
            'they', 'what', 'when', 'where', 'while', 'each', 'other', 'both',
            'between', 'under', 'after', 'before', 'through', 'during'
        }
        
        filtered = [w for w in words if w not in stopwords]
        counts = Counter(filtered)
        
        return [term for term, count in counts.most_common(30)]
    
    def list_available_figures(self, directory: str = None) -> Dict[str, Any]:
        """
        List all available figures in the figures directory.
        
        Args:
            directory: Optional directory to scan (defaults to PYTHIA_FIGURES_DIR)
            
        Returns:
            Dict with list of available figures
        """
        if directory is None:
            directory = self.figures_dir
        
        if not os.path.exists(directory):
            return {
                'success': True,
                'figures': [],
                'count': 0,
                'directory': directory,
                'message': 'Figures directory does not exist yet'
            }
        
        figures = []
        valid_extensions = ['.pdf', '.png', '.jpg', '.jpeg', '.eps', '.svg']
        
        for filename in os.listdir(directory):
            ext = os.path.splitext(filename)[1].lower()
            if ext in valid_extensions:
                filepath = os.path.join(directory, filename)
                stat = os.stat(filepath)
                figures.append({
                    'path': filepath,
                    'filename': filename,
                    'extension': ext,
                    'size_bytes': stat.st_size,
                    'modified': stat.st_mtime
                })
        
        # Sort by modification time (newest first)
        figures.sort(key=lambda x: x['modified'], reverse=True)
        
        return {
            'success': True,
            'figures': figures,
            'count': len(figures),
            'directory': directory
        }
    
    def validate_figure_references(self, tex_content: str = None, 
                                   tex_file: str = None) -> Dict[str, Any]:
        """
        Check if figures referenced in LaTeX content actually exist.
        
        Args:
            tex_content: LaTeX content string
            tex_file: Path to LaTeX file (alternative to content)
            
        Returns:
            Dict with validation results
        """
        if tex_content is None:
            if tex_file is None:
                return {
                    'success': False,
                    'error': 'No content or file provided'
                }
            if not os.path.exists(tex_file):
                return {
                    'success': False,
                    'error': f'File not found: {tex_file}'
                }
            with open(tex_file, 'r', encoding='utf-8') as f:
                tex_content = f.read()
        
        # Find all \includegraphics references
        pattern = r'\\includegraphics(?:\[.*?\])?\{([^}]+)\}'
        references = re.findall(pattern, tex_content)
        
        valid_refs = []
        invalid_refs = []
        
        for ref in references:
            # Check if it's an absolute path
            if os.path.isabs(ref):
                if os.path.exists(ref):
                    valid_refs.append(ref)
                else:
                    # Try adding common extensions
                    found = False
                    for ext in ['.pdf', '.png', '.jpg', '.eps']:
                        if os.path.exists(ref + ext):
                            valid_refs.append(ref + ext)
                            found = True
                            break
                    if not found:
                        invalid_refs.append(ref)
            else:
                # Relative path - check in figures directory
                full_path = os.path.join(self.figures_dir, ref)
                if os.path.exists(full_path):
                    valid_refs.append(full_path)
                else:
                    # Try adding common extensions
                    found = False
                    for ext in ['.pdf', '.png', '.jpg', '.eps']:
                        if os.path.exists(full_path + ext):
                            valid_refs.append(full_path + ext)
                            found = True
                            break
                    if not found:
                        invalid_refs.append(ref)
        
        return {
            'success': True,
            'total_references': len(references),
            'valid_count': len(valid_refs),
            'invalid_count': len(invalid_refs),
            'valid_figures': valid_refs,
            'invalid_figures': invalid_refs,
            'all_valid': len(invalid_refs) == 0
        }

    def analyze_statistics(self, data: List[float]) -> Dict[str, Any]:
        """
        Compute basic statistics for numerical data.
        
        Args:
            data: List of numerical values
            
        Returns:
            Statistical summary
        """
        if not data:
            return {
                'success': False,
                'error': "Empty data list"
            }
        
        try:
            import numpy as np
            arr = np.array(data)
            
            return {
                'success': True,
                'count': len(arr),
                'mean': float(np.mean(arr)),
                'std': float(np.std(arr)),
                'min': float(np.min(arr)),
                'max': float(np.max(arr)),
                'median': float(np.median(arr)),
                'percentiles': {
                    '25%': float(np.percentile(arr, 25)),
                    '50%': float(np.percentile(arr, 50)),
                    '75%': float(np.percentile(arr, 75))
                }
            }
        except ImportError:
            # Fallback without numpy
            sorted_data = sorted(data)
            n = len(sorted_data)
            mean = sum(data) / n
            variance = sum((x - mean) ** 2 for x in data) / n
            
            return {
                'success': True,
                'count': n,
                'mean': mean,
                'std': variance ** 0.5,
                'min': min(data),
                'max': max(data),
                'median': sorted_data[n // 2]
            }


# Tool function for agent registration
def create_analyzer_tool(output_dir: str = OUTPUT_DIR) -> Dict[str, Any]:
    """Create an analyzer tool instance for agent registration."""
    tool = AnalyzerTool(output_dir)
    return {
        'name': tool.name,
        'description': tool.description,
        'function': tool.run,
        'instance': tool
    }

