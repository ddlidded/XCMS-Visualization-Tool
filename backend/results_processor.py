"""Process and combine XCMS data with MS2 matching results."""
from typing import List, Dict, Any, Optional
from backend.data_loader import load_xcms_data, get_peak_info
from backend.models import MatchingResult, SpectrumMatch


def process_matching_results(
    xcms_peaks: List[Dict[str, Any]],
    matching_results: List[Dict[str, Any]],
    algorithm: str = "ms2query"
) -> List[Dict[str, Any]]:
    """
    Combine XCMS peak data with MS2 matching results.
    
    Args:
        xcms_peaks: List of XCMS peak dictionaries
        matching_results: List of matching result dictionaries
        algorithm: Algorithm used for matching
        
    Returns:
        List of combined results with metabolite annotations
    """
    processed_results = []
    
    for match_result in matching_results:
        query_index = match_result.get("query_index", -1)
        query_spectrum = match_result.get("query_spectrum", {})
        matches = match_result.get("matches", [])
        best_match = match_result.get("best_match")
        
        # Find corresponding XCMS peak
        feature_name = query_spectrum.get("feature_name", f"Feature_{query_index}")
        xcms_peak = get_peak_info(xcms_peaks, feature_name)
        
        if xcms_peak is None:
            # Try to find by m/z and RT if feature name not found
            precursor_mz = query_spectrum.get("precursor_mz")
            rt = query_spectrum.get("retention_time")
            if precursor_mz and rt:
                xcms_peak = find_peak_by_mz_rt(xcms_peaks, precursor_mz, rt)
        
        # Create combined result
        combined_result = {
            "feature_name": feature_name,
            "xcms_peak": xcms_peak,
            "precursor_mz": query_spectrum.get("precursor_mz"),
            "retention_time": query_spectrum.get("retention_time"),
            "algorithm": algorithm,
            "matches": matches,
            "best_match": best_match,
            "match_count": len(matches),
            "confidence_score": calculate_confidence_score(matches, best_match)
        }
        
        processed_results.append(combined_result)
    
    return processed_results


def find_peak_by_mz_rt(
    peaks: List[Dict[str, Any]],
    mz: float,
    rt: float,
    mz_tolerance: float = 0.01,
    rt_tolerance: float = 30.0
) -> Optional[Dict[str, Any]]:
    """Find XCMS peak by m/z and RT."""
    for peak in peaks:
        peak_mz = peak.get("mz", 0)
        peak_rt = peak.get("rt", 0)
        
        if abs(peak_mz - mz) <= mz_tolerance and abs(peak_rt - rt) <= rt_tolerance:
            return peak
    return None


def calculate_confidence_score(
    matches: List[Dict[str, Any]],
    best_match: Optional[Dict[str, Any]]
) -> float:
    """
    Calculate confidence score based on matching results.
    
    Args:
        matches: List of all matches
        best_match: Best match dictionary
        
    Returns:
        Confidence score between 0 and 1
    """
    if not best_match:
        return 0.0
    
    # Base score from best match
    base_score = best_match.get("score", 0.0)
    
    # Boost if multiple high-quality matches agree
    if len(matches) > 1:
        top_scores = [m.get("score", 0.0) for m in matches[:3]]
        avg_top_score = sum(top_scores) / len(top_scores)
        consistency_boost = min(0.2, (avg_top_score - base_score) * 0.5)
        base_score += consistency_boost
    
    # Penalize if matched peaks are too few
    matched_peaks = best_match.get("matched_peaks", 0)
    total_peaks = best_match.get("total_peaks", 1)
    peak_ratio = matched_peaks / total_peaks if total_peaks > 0 else 0
    base_score *= (0.5 + 0.5 * peak_ratio)
    
    return min(1.0, max(0.0, base_score))


def format_results_for_export(
    processed_results: List[Dict[str, Any]],
    format: str = "json"
) -> Any:
    """
    Format processed results for export.
    
    Args:
        processed_results: List of processed result dictionaries
        format: Export format ("json" or "csv")
        
    Returns:
        Formatted data ready for export
    """
    if format == "json":
        return processed_results
    elif format == "csv":
        # Flatten for CSV export
        csv_rows = []
        for result in processed_results:
            xcms_peak = result.get("xcms_peak", {})
            best_match = result.get("best_match", {})
            metadata = best_match.get("metadata", {})
            
            row = {
                "feature_name": result.get("feature_name", ""),
                "precursor_mz": result.get("precursor_mz", ""),
                "retention_time": result.get("retention_time", ""),
                "xcms_mz": xcms_peak.get("mz", ""),
                "xcms_rt": xcms_peak.get("rt", ""),
                "compound_name": best_match.get("compound_name", ""),
                "match_score": best_match.get("score", ""),
                "algorithm": result.get("algorithm", ""),
                "confidence_score": result.get("confidence_score", ""),
                "matched_peaks": best_match.get("matched_peaks", ""),
                "smiles": metadata.get("smiles", ""),
                "inchi": metadata.get("inchi", ""),
                "inchikey": metadata.get("inchikey", "")
            }
            csv_rows.append(row)
        return csv_rows
    else:
        raise ValueError(f"Unsupported format: {format}")


def generate_summary_statistics(
    processed_results: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Generate summary statistics from processed results.
    
    Args:
        processed_results: List of processed result dictionaries
        
    Returns:
        Dictionary with summary statistics
    """
    total_features = len(processed_results)
    matched_features = sum(1 for r in processed_results if r.get("best_match"))
    high_confidence = sum(1 for r in processed_results if r.get("confidence_score", 0) >= 0.7)
    
    scores = [r.get("confidence_score", 0) for r in processed_results if r.get("confidence_score")]
    avg_score = sum(scores) / len(scores) if scores else 0.0
    
    algorithms = {}
    for result in processed_results:
        algo = result.get("algorithm", "unknown")
        algorithms[algo] = algorithms.get(algo, 0) + 1
    
    return {
        "total_features": total_features,
        "matched_features": matched_features,
        "match_rate": matched_features / total_features if total_features > 0 else 0.0,
        "high_confidence_matches": high_confidence,
        "average_confidence_score": avg_score,
        "algorithms_used": algorithms
    }

