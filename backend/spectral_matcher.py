"""Traditional spectral matching algorithms."""
from typing import List, Dict, Any, Optional
from matchms import Spectrum
from matchms.similarity import (
    CosineGreedy,
    ModifiedCosine,
    DotProduct
)
import numpy as np


def match_with_traditional(
    query_spectra: List[Spectrum],
    library_spectra: List[Spectrum],
    algorithm: str = "cosine",
    mz_tolerance: float = 0.01,
    min_score: float = 0.0,
    top_n: int = 10
) -> List[Dict[str, Any]]:
    """
    Match query spectra against library using traditional algorithms.
    
    Args:
        query_spectra: List of matchms Spectrum objects to match
        library_spectra: List of library matchms Spectrum objects
        algorithm: Matching algorithm ("dot_product", "cosine", "modified_cosine")
        mz_tolerance: m/z tolerance for matching (Da)
        min_score: Minimum score threshold
        top_n: Number of top matches to return per query
        
    Returns:
        List of matching results dictionaries
    """
    # Initialize similarity function
    if algorithm == "dot_product":
        similarity_fn = DotProduct(tolerance=mz_tolerance)
    elif algorithm == "cosine":
        similarity_fn = CosineGreedy(tolerance=mz_tolerance)
    elif algorithm == "modified_cosine":
        similarity_fn = ModifiedCosine(tolerance=mz_tolerance)
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")
    
    results = []
    
    for i, query_spectrum in enumerate(query_spectra):
        matches = []
        
        for lib_spectrum in library_spectra:
            try:
                # Calculate similarity score
                score = similarity_fn.pair(query_spectrum, lib_spectrum)
                
                if score is None or score[0] < min_score:
                    continue
                
                similarity_score = float(score[0])
                
                # Count matched peaks
                matched_peaks = count_matched_peaks(
                    query_spectrum,
                    lib_spectrum,
                    mz_tolerance
                )
                
                match_dict = {
                    "library_id": lib_spectrum.get("spectrum_id", f"lib_{i}"),
                    "compound_name": lib_spectrum.get("compound_name") or \
                                   lib_spectrum.get("name", "Unknown"),
                    "score": similarity_score,
                    "algorithm": algorithm,
                    "matched_peaks": matched_peaks,
                    "total_peaks": len(query_spectrum.peaks.mz),
                    "metadata": {
                        "precursor_mz": lib_spectrum.get("precursor_mz"),
                        "retention_time": lib_spectrum.get("retention_time"),
                        "smiles": lib_spectrum.get("smiles"),
                        "inchi": lib_spectrum.get("inchi"),
                        "inchikey": lib_spectrum.get("inchikey")
                    }
                }
                matches.append(match_dict)
                
            except Exception as e:
                print(f"Error matching spectrum {i} against library: {str(e)}")
                continue
        
        # Sort by score and take top N
        matches.sort(key=lambda x: x["score"], reverse=True)
        top_matches = matches[:top_n]
        
        results.append({
            "query_index": i,
            "query_spectrum": {
                "precursor_mz": query_spectrum.get("precursor_mz"),
                "retention_time": query_spectrum.get("retention_time")
            },
            "matches": top_matches,
            "best_match": top_matches[0] if top_matches else None
        })
    
    return results


def count_matched_peaks(
    spectrum1: Spectrum,
    spectrum2: Spectrum,
    mz_tolerance: float
) -> int:
    """
    Count the number of matched peaks between two spectra.
    
    Args:
        spectrum1: First spectrum
        spectrum2: Second spectrum
        mz_tolerance: m/z tolerance for matching
        
    Returns:
        Number of matched peaks
    """
    mz1 = spectrum1.peaks.mz
    mz2 = spectrum2.peaks.mz
    
    matched = 0
    used_indices = set()
    
    for mz_val in mz1:
        for j, mz_val2 in enumerate(mz2):
            if j in used_indices:
                continue
            if abs(mz_val - mz_val2) <= mz_tolerance:
                matched += 1
                used_indices.add(j)
                break
    
    return matched


def calculate_dot_product(
    spectrum1: Spectrum,
    spectrum2: Spectrum,
    mz_tolerance: float = 0.01
) -> float:
    """Calculate dot product similarity between two spectra."""
    similarity_fn = DotProduct(tolerance=mz_tolerance)
    score = similarity_fn.pair(spectrum1, spectrum2)
    return float(score[0]) if score else 0.0


def calculate_cosine_similarity(
    spectrum1: Spectrum,
    spectrum2: Spectrum,
    mz_tolerance: float = 0.01
) -> float:
    """Calculate cosine similarity between two spectra."""
    similarity_fn = CosineGreedy(tolerance=mz_tolerance)
    score = similarity_fn.pair(spectrum1, spectrum2)
    return float(score[0]) if score else 0.0


def calculate_modified_cosine(
    spectrum1: Spectrum,
    spectrum2: Spectrum,
    mz_tolerance: float = 0.01
) -> float:
    """Calculate modified cosine similarity between two spectra."""
    similarity_fn = ModifiedCosine(tolerance=mz_tolerance)
    score = similarity_fn.pair(spectrum1, spectrum2)
    return float(score[0]) if score else 0.0

