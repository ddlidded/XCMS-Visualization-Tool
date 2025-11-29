"""Pydantic models for API requests and responses."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class MatchingAlgorithm(str, Enum):
    """Available spectral matching algorithms."""
    MS2QUERY = "ms2query"
    DOT_PRODUCT = "dot_product"
    COSINE = "cosine"
    MODIFIED_COSINE = "modified_cosine"


class MatchingConfig(BaseModel):
    """Configuration for spectral matching."""
    algorithm: MatchingAlgorithm = Field(default=MatchingAlgorithm.MS2QUERY)
    mz_tolerance: float = Field(default=0.01, ge=0.001, le=1.0)
    rt_tolerance: float = Field(default=30.0, ge=1.0, le=300.0)
    min_score: float = Field(default=0.0, ge=0.0, le=1.0)
    top_n: int = Field(default=10, ge=1, le=100)


class MS2ExtractionConfig(BaseModel):
    """Configuration for MS2 spectrum extraction."""
    mz_tolerance: float = Field(default=0.01, ge=0.001, le=1.0)
    rt_tolerance: float = Field(default=30.0, ge=1.0, le=300.0)
    min_intensity: float = Field(default=100.0, ge=0.0)


class XCMSProcessingConfig(BaseModel):
    """Configuration for XCMS processing."""
    ppm: float = Field(default=10.0, ge=1.0, le=50.0)
    peakwidth_min: float = Field(default=5.0, ge=1.0, le=100.0)
    peakwidth_max: float = Field(default=30.0, ge=1.0, le=200.0)
    snthresh: float = Field(default=6.0, ge=1.0, le=20.0)
    mzdiff: float = Field(default=0.01, ge=0.001, le=1.0)
    quant_method: str = Field(default="into")
    minfrac: float = Field(default=0.5, ge=0.0, le=1.0)
    minsamp: int = Field(default=0, ge=0)
    bw: float = Field(default=5.0, ge=1.0, le=50.0)
    mzwid: float = Field(default=0.006, ge=0.001, le=0.1)
    peak_detection_method: str = Field(default="centWave")
    peak_grouping_method: str = Field(default="density")
    rt_correction_method: str = Field(default="obiwarp")
    prefilter_min: int = Field(default=3, ge=1, le=100)
    prefilter_max: float = Field(default=100.0, ge=10.0, le=10000.0)


class PeakInfo(BaseModel):
    """Information about an XCMS peak."""
    name: str
    mz: float
    mzmin: float
    mzmax: float
    rt: float
    rtmin: float
    rtmax: float
    npeaks: int
    intensities: Dict[str, float]


class SpectrumMatch(BaseModel):
    """Result of spectral matching."""
    library_id: str
    compound_name: Optional[str] = None
    score: float
    algorithm: str
    matched_peaks: int
    total_peaks: int
    metadata: Dict[str, Any] = {}


class MatchingResult(BaseModel):
    """Complete matching result for a feature."""
    feature_name: str
    mz: float
    rt: float
    matches: List[SpectrumMatch]
    best_match: Optional[SpectrumMatch] = None


class ProcessingStatus(BaseModel):
    """Status of a processing job."""
    job_id: str
    status: str  # "pending", "processing", "completed", "error"
    progress: float = 0.0
    message: Optional[str] = None


class XCMSProcessingResult(BaseModel):
    """Result of XCMS processing."""
    success: bool
    peak_table: Optional[str] = None
    sample_info: Optional[str] = None
    output_dir: Optional[str] = None
    message: str
    error: Optional[str] = None
