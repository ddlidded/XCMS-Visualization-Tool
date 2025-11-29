# XCMS Processing Guide

## Overview

The tool now includes built-in XCMS processing capabilities, allowing you to process raw mzXML files directly into XCMS peak tables without needing to run XCMS separately.

## Requirements

### Option 1: R with XCMS Package (Recommended)

1. **Install R**: Download and install R from https://www.r-project.org/

2. **Install XCMS and CAMERA packages**:
   ```r
   install.packages("xcms")
   install.packages("CAMERA")
   ```

3. **Verify Installation**:
   ```r
   library(xcms)
   library(CAMERA)
   ```

4. **Verify R is in PATH**: The tool uses `Rscript` command, so ensure R is accessible from command line.

### Option 2: pyOpenMS (Alternative)

Install pyOpenMS for Python-based processing (limited XCMS compatibility):

```bash
pip install pyopenms
```

Note: pyOpenMS has a different API and may not provide full XCMS feature parity.

## Usage

### Via Web Interface

1. **Upload mzXML Files**: Upload your raw mzXML files in the upload section
2. **Enable XCMS Processing**: Check the "Process mzXML files with XCMS" checkbox
3. **Configure Parameters**: Adjust XCMS parameters as needed:
   - **PPM**: Mass accuracy in parts per million (default: 10)
   - **Peakwidth**: Min and max peak width in seconds (default: 5-30)
   - **SN Threshold**: Signal-to-noise threshold (default: 6)
   - **m/z Diff**: Minimum difference in m/z for peak detection (default: 0.01)
   - **Bandwidth**: Bandwidth for peak grouping (default: 5)
4. **Run Processing**: Click "Run XCMS Processing"
5. **Wait for Completion**: Processing may take several minutes depending on file size
6. **Use Results**: The generated peak table will be automatically used for subsequent matching

### Via API

#### Check Availability

```bash
curl http://localhost:8000/api/xcms/check
```

#### Process Files

```bash
curl -X POST http://localhost:8000/api/xcms/process \
  -H "Content-Type: application/json" \
  -d '{
    "mzxml_files": ["mzxml_file1.mzXML", "mzxml_file2.mzXML"],
    "config": {
      "ppm": 10,
      "peakwidth_min": 5,
      "peakwidth_max": 30,
      "snthresh": 6,
      "mzdiff": 0.01,
      "bw": 5
    }
  }'
```

#### Process with YAML Parameters

```bash
curl -X POST http://localhost:8000/api/xcms/process-from-yaml \
  -H "Content-Type: application/json" \
  -d '{
    "mzxml_files": ["file1.mzXML", "file2.mzXML"],
    "yaml_file": "params.yaml"
  }'
```

## XCMS Parameters

### Peak Detection Parameters

- **ppm**: Mass accuracy in parts per million (1-50, default: 10)
- **peakwidth_min**: Minimum peak width in seconds (1-100, default: 5)
- **peakwidth_max**: Maximum peak width in seconds (1-200, default: 30)
- **snthresh**: Signal-to-noise threshold (1-20, default: 6)
- **mzdiff**: Minimum difference in m/z for peak detection (0.001-1.0, default: 0.01)
- **prefilter_min**: Minimum number of peaks (1-100, default: 3)
- **prefilter_max**: Maximum intensity threshold (10-10000, default: 100)

### Peak Grouping Parameters

- **bw**: Bandwidth for peak grouping (1-50, default: 5)
- **mzwid**: m/z width for grouping (0.001-0.1, default: 0.006)
- **minfrac**: Minimum fraction of samples (0.0-1.0, default: 0.5)
- **minsamp**: Minimum number of samples (0+, default: 0)

### Methods

- **peak_detection_method**: "centWave" (default) or "matchedFilter"
- **peak_grouping_method**: "density" (default) or "nearest"
- **rt_correction_method**: "obiwarp" (default) or "loess"

## Output Files

XCMS processing generates:

1. **PeakTable_verbose.csv**: Complete peak table with all features and intensities
2. **sample.info.csv**: Sample metadata and grouping information

These files are saved in `results/xcms_output_{job_id}/` directory.

## Troubleshooting

### R Not Found

**Error**: `Rscript: command not found`

**Solution**: 
- Ensure R is installed and in your system PATH
- On Windows, add R to PATH or use full path to Rscript
- Verify with: `Rscript --version`

### XCMS Package Not Installed

**Error**: `Error loading XCMS library`

**Solution**:
```r
install.packages("xcms")
install.packages("CAMERA")
```

### Processing Timeout

**Error**: Processing takes too long or times out

**Solution**:
- Large files may take 30+ minutes
- Consider processing fewer files at once
- Check available system memory
- Increase timeout in `backend/xcms_processor.py` if needed

### Memory Issues

**Error**: Out of memory during processing

**Solution**:
- Process files in smaller batches
- Increase system RAM if possible
- Close other applications
- Use fewer samples per batch

## Integration with Workflow

After XCMS processing:

1. The generated peak table is automatically available
2. You can proceed directly to MS2 extraction and matching
3. No need to manually upload the XCMS results CSV
4. The workflow continues seamlessly

## Performance Tips

1. **Batch Processing**: Process multiple files together for better alignment
2. **Parameter Tuning**: Adjust parameters based on your instrument and data
3. **Quality Control**: Review generated peak tables before matching
4. **Resource Management**: XCMS processing is CPU and memory intensive

## Example Workflow

1. Upload 5 mzXML files from your experiment
2. Enable XCMS processing
3. Use default parameters (or adjust based on your data)
4. Run XCMS processing (wait 10-30 minutes)
5. Upload spectral library
6. Configure matching parameters
7. Run spectral matching
8. View and export results

This eliminates the need for separate XCMS processing steps!

