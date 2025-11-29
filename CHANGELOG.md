# Changelog

## [1.0.0] - Initial Release

### Added
- FastAPI backend with RESTful API endpoints
- Frontend with Tailwind CSS and Flowbite components
- MS2Query integration for ML-assisted spectral matching
- Traditional matching algorithms (dot product, cosine, modified cosine)
- Multi-format library support (MSP, MGF, JSON, mzML)
- MS2 spectrum extraction from mzXML files
- Interactive spectrum visualization with Chart.js
- Results export (CSV/JSON)
- WebSocket support for progress updates
- Comprehensive error handling
- API health check endpoint

### Features
- File upload for XCMS results, mzXML files, and spectral libraries
- Configurable matching parameters
- Real-time status updates
- Responsive web interface
- Export functionality for results

### Technical Details
- Backend: Python 3.9+, FastAPI, matchms, MS2Query
- Frontend: HTML5, JavaScript, Tailwind CSS, Flowbite, Chart.js
- Data formats: CSV, mzXML, MSP, MGF, JSON, mzML

