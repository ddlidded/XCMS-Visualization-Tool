# XCMS Metabolite MS2 Spectral Matching Tool

A modern web-based application for processing XCMS results, extracting MS2 spectra from mzXML files, and performing advanced spectral matching using MS2Query and traditional algorithms against user-provided spectral libraries.

## Features

- **Multi-format Support**: Upload spectral libraries in MSP, MGF, JSON, or mzML formats
- **MS2Query Integration**: ML-assisted spectral matching for exact matches and analog searches
- **Traditional Algorithms**: Fallback matching using dot product, cosine, and modified cosine similarity
- **Automatic MS2 Extraction**: Extract MS2 spectra from mzXML files and match to XCMS features
- **Interactive Visualization**: View spectra and compare query vs library matches
- **Export Results**: Download matching results as CSV or JSON
- **Modern UI**: Built with Tailwind CSS and Flowbite for a responsive, professional interface

## Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Backend Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd XCMS-Visualization-Tool
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) Install MS2Query models:
```bash
# MS2Query will download pre-trained models on first use
# Or you can train your own models using your spectral library
```

### Frontend Setup

The frontend uses CDN resources (Tailwind CSS, Flowbite, Chart.js), so no build step is required. Simply open `frontend/index.html` in a web browser or serve it through a web server.

## Usage

### Starting the Backend Server

1. Navigate to the project directory:
```bash
cd XCMS-Visualization-Tool
```

2. Start the FastAPI server:
```bash
python -m uvicorn backend.main:app --reload
```

The API will be available at `http://localhost:8000`

### Accessing the Web Interface

1. Open `frontend/index.html` in a web browser, or
2. Serve the frontend directory using a simple HTTP server:
```bash
cd frontend
python -m http.server 8080
```

Then navigate to `http://localhost:8080`

### Workflow

1. **Upload Files**:
   - Upload your XCMS results CSV file (PeakTable)
   - Upload one or more mzXML files containing MS2 spectra
   - Upload a spectral library file (MSP, MGF, JSON, or mzML format)

2. **Configure Matching**:
   - Select matching algorithm (MS2Query recommended for best results)
   - Set m/z and RT tolerances
   - Configure minimum score threshold and number of results

3. **Run Matching**:
   - Click "Run Matching" to start the process
   - Monitor progress in the status indicator

4. **View Results**:
   - Browse matched metabolites in the results table
   - View individual spectra by clicking "Spectrum"
   - Export results as CSV or JSON

## API Endpoints

### File Upload
- `POST /api/upload/xcms` - Upload XCMS results CSV
- `POST /api/upload/mzxml` - Upload mzXML file
- `POST /api/upload/library` - Upload spectral library

### Data Processing
- `GET /api/xcms/peaks?xcms_file=<filename>` - Get XCMS peak data
- `POST /api/extract/ms2` - Extract MS2 spectra from mzXML
- `POST /api/match/spectra` - Perform spectral matching

### WebSocket
- `WS /ws/progress` - Real-time progress updates

## Spectral Library Formats

### MSP (NIST Format)
Standard NIST mass spectral library format with compound information and MS2 peaks.

### MGF (Mascot Generic Format)
Common format for MS/MS data with precursor information and fragment ions.

### JSON
Custom JSON format with structure:
```json
{
  "mz": [100.0, 150.0, 200.0],
  "intensities": [1000, 500, 200],
  "metadata": {
    "compound_name": "Example",
    "precursor_mz": 300.0,
    "retention_time": 600.0
  }
}
```

### mzML
Standard mass spectrometry data format (mzML 1.1).

## MS2Query Integration

MS2Query provides machine learning-assisted spectral matching:

- **Exact Matches**: Identify compounds with exact spectral matches
- **Analog Search**: Find structurally similar compounds
- **Confidence Scores**: ML-based confidence scoring

To use MS2Query:
1. Ensure `ms2query` is installed: `pip install ms2query`
2. Pre-trained models will be downloaded automatically on first use
3. Or train custom models using your own spectral library

For more information, see: https://github.com/iomega/ms2query

## Workflow Inspiration

This tool is inspired by the [OpenMS uMetaFlow](https://pubmed.ncbi.nlm.nih.gov/37173725/) workflow, which provides a comprehensive pipeline for untargeted metabolomics analysis including:
- Data pre-processing
- Spectral matching
- Molecular formula prediction
- Structural annotation

## Configuration

### Backend Configuration

Edit `backend/config.py` to customize:
- File upload size limits
- Default matching parameters
- Allowed file extensions

### Frontend Configuration

Edit `frontend/js/api.js` to change the API base URL:
```javascript
const API_BASE_URL = 'http://localhost:8000';
```

## Troubleshooting

### MS2Query Not Available
If you see warnings about MS2Query not being available:
```bash
pip install ms2query
```

### File Upload Errors
- Check file size limits in `backend/config.py`
- Ensure file formats are supported
- Verify file paths and permissions

### Matching Errors
- Verify spectral library format is correct
- Check that MS2 spectra were successfully extracted
- Review m/z and RT tolerance settings

## Development

### Project Structure
```
.
├── backend/          # FastAPI backend
│   ├── main.py      # FastAPI application
│   ├── data_loader.py
│   ├── ms2_extractor.py
│   ├── library_parser.py
│   ├── ms2query_matcher.py
│   ├── spectral_matcher.py
│   └── results_processor.py
├── frontend/         # HTML/JavaScript frontend
│   ├── index.html
│   ├── css/
│   └── js/
└── requirements.txt
```

### Adding New Matching Algorithms

1. Implement algorithm in `backend/spectral_matcher.py`
2. Add option to `MatchingAlgorithm` enum in `backend/models.py`
3. Update frontend dropdown in `frontend/index.html`

## License

[Add your license here]

## Citation

If you use this tool in your research, please cite:
- MS2Query: [citation]
- OpenMS uMetaFlow: [citation]
- XCMS: [citation]

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Support

For issues and questions:
- Open an issue on GitHub
- Check the documentation
- Review the API documentation at `http://localhost:8000/docs` when the server is running

