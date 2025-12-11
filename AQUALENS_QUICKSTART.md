# AquaLens Community Detection - Quick Start Guide

## What's Been Added?

The AquaLens community detection feature has been successfully integrated into your Marine Plankton Detection System! This feature adds powerful real-time community analysis using Graph Machine Learning (GML) algorithms.

### New Features:
- ✅ **New Tab**: "🧬 Community Detection" in the main dashboard
- ✅ **Integration Module**: `modules/aqualens_integration.py` - manages the AquaLens server
- ✅ **FastAPI Server**: Runs in the background to process video streams
- ✅ **Real-time Analysis**: Live video stream with overlaid detection results
- ✅ **Community Detection**: Identifies overlapping communities using BigCLAM algorithm
- ✅ **Species Clustering**: Automatic species classification using deep learning

## Installation

### Step 1: Install Dependencies

The AquaLens feature requires additional Python packages. Install them with:

```bash
pip install -r requirements_aqualens.txt
```

This will install:
- FastAPI & Uvicorn (web server)
- PyTorch & TorchVision (deep learning)
- scikit-learn (clustering algorithms)
- opencv-python (video processing) - if not already installed
- And optional packages like HDBSCAN and scikit-image

### Step 2: Verify Installation

Run the test script to verify everything is working:

```bash
python3 test_aqualens_integration.py
```

You should see all tests pass. If any fail, check the error messages and install missing dependencies.

## Usage

### Quick Start (3 steps):

1. **Launch the Dashboard**
   ```bash
   streamlit run app.py
   ```

2. **Navigate to Community Detection Tab**
   - Click on the "🧬 Community Detection" tab at the top

3. **Start Analyzing**
   - Click "🚀 Start Server" to initialize the AquaLens server
   - Select a video file or camera as input
   - Configure analysis parameters (or use defaults)
   - Click "▶️ Start Analysis" to begin
   - Watch the real-time stream and results!

### Detailed Workflow:

#### 1. Server Control
```
Server Status → Not Running
↓
Click "🚀 Start Server"
↓
Server Status → Running ✓
```

#### 2. Pipeline Configuration
Choose your input:
- **Video File**: Select from dropdown (detects .mp4, .avi, .mov files)
- **Camera**: Enter camera index (0 for default webcam)

Adjust parameters:
- **Processing Device**: CPU (default) or CUDA (if you have GPU)
- **Target FPS**: 6 FPS (recommended) - lower = faster, higher = more accurate
- **Analysis Window**: 3 seconds (recommended) - time window for community detection
- **Use HDBSCAN**: Off (default) - advanced clustering, slower but more accurate
- **Number of Communities**: 6 (default) - expected number of species/communities

#### 3. Start Analysis
```
Click "▶️ Start Analysis"
↓
Pipeline processes video in background
↓
Live stream appears with bounding boxes
Community badges show on organisms
Real-time stats update continuously
```

#### 4. View Results
The interface displays:
- **Live Video Stream**: Annotated with detections and community labels
- **Total Nodes**: Count of detected organisms
- **Species Detected**: Number of distinct species found
- **Communities**: Number of communities identified
- **Overlapping Communities**: Yes/No indicator
- **Species Distribution**: Top 5 species with counts
- **Community Sizes**: Top 5 communities with member counts

#### 5. Stop Analysis
```
Click "⏹️ Stop Analysis" to stop pipeline
Click "🛑 Stop Server" to shut down server completely
```

## Example Videos

The system detected these test videos:
- `aqualens/1.mp4` - Sample plankton video 1
- `aqualens/2.mp4` - Sample plankton video 2
- `Real_Time_Vids/*.mov` - Additional test videos

Try starting with one of these to see the feature in action!

## What Does It Do?

### Community Detection Algorithm
1. **Detect Organisms**: Segments video frames to find plankton
2. **Extract Features**: Uses MobileNetV3 neural network to create embeddings
3. **Cluster Species**: Groups similar organisms into species
4. **Build Graph**: Creates connections based on spatial proximity and species similarity
5. **Find Communities**: Uses BigCLAM to identify overlapping communities
6. **Track Over Time**: Maintains tracking across frames
7. **Display Results**: Shows annotated video with real-time statistics

### Output
The system generates:
- **Visual Output**: Annotated video stream with bounding boxes and labels
- **Community Memberships**: Each organism assigned to one or more communities
- **Species Counts**: How many of each species detected
- **Community Statistics**: Size and overlap information
- **Raw Data**: Available via API endpoints for further analysis

## Troubleshooting

### "Server won't start"
- **Port in use**: Another service may be using port 8000
  - Solution: Stop other services or change port in `modules/aqualens_integration.py`
- **Missing dependencies**: Run `pip install -r requirements_aqualens.txt`
- **Python version**: Requires Python 3.8+

### "Pipeline fails to start"
- **Invalid video path**: Make sure the video file exists
- **Camera not found**: Try different camera indices (0, 1, 2...)
- **Memory error**: Reduce FPS target or use smaller video

### "No detections appearing"
- **Video quality**: Ensure video shows visible plankton
- **Wrong input**: Verify you selected the correct video/camera
- **Threshold too high**: Detections may be filtered out (requires code adjustment)

### "Server Status shows 'Not Running' after starting"
- Wait 2-3 seconds for server to initialize
- Check terminal for error messages
- Try clicking "🔄 Refresh Status"

## Performance Tips

### For Faster Processing:
- Set FPS to 3-6 (default is good)
- Keep HDBSCAN disabled (use MiniBatchKMeans)
- Reduce number of communities to 4-6
- Use CPU unless you have a good GPU

### For Better Accuracy:
- Increase FPS to 10-15 (slower)
- Enable HDBSCAN clustering
- Increase analysis window to 5-10 seconds
- Increase number of communities to 8-12

## Files Added/Modified

### New Files:
```
modules/aqualens_integration.py          # Integration module
requirements_aqualens.txt                # AquaLens dependencies
AQUALENS_INTEGRATION.md                  # Detailed technical documentation
AQUALENS_QUICKSTART.md                   # This file
test_aqualens_integration.py             # Integration test script
```

### Modified Files:
```
app.py                                   # Added Community Detection tab
```

### Existing (Unchanged):
```
aqualens/                                # Original AquaLens feature directory
├── server.py                            # FastAPI server
├── final_final_pipeline.py              # Pipeline engine
├── community_pipeline.py                # Standalone community detection
├── 1.mp4, 2.mp4                        # Sample videos
└── ...
```

## API Access

If you want to access the AquaLens server directly (for custom integrations):

```python
import requests

# Start pipeline
requests.post("http://localhost:8000/start", json={
    "video": "aqualens/1.mp4",
    "device": "cpu",
    "fps_target": 6.0
})

# Get status
status = requests.get("http://localhost:8000/status").json()

# Get summary
summary = requests.get("http://localhost:8000/summary").json()

# Get latest frame
frame_jpeg = requests.get("http://localhost:8000/frame.jpg").content

# Stop pipeline
requests.post("http://localhost:8000/stop")
```

See `AQUALENS_INTEGRATION.md` for full API documentation.

## Next Steps

### Recommended Workflow:
1. ✅ Install dependencies: `pip install -r requirements_aqualens.txt`
2. ✅ Run test: `python3 test_aqualens_integration.py`
3. ✅ Launch dashboard: `streamlit run app.py`
4. ✅ Navigate to "🧬 Community Detection" tab
5. ✅ Start server and try with sample video `aqualens/1.mp4`
6. ✅ Experiment with different parameters
7. ✅ Try with your own videos or live camera!

### Advanced Usage:
- Read `AQUALENS_INTEGRATION.md` for technical details
- Customize parameters in `aqualens/final_final_pipeline.py`
- Export community data via API endpoints
- Integrate with database module for persistent storage

## Support

For issues or questions:
1. Check this guide's troubleshooting section
2. Review `AQUALENS_INTEGRATION.md` for technical details
3. Run `python3 test_aqualens_integration.py` to diagnose issues
4. Check terminal output for error messages
5. Verify all dependencies are installed

## Summary

You now have a fully integrated community detection system! This feature:
- ✅ Works as an **additional** feature alongside your existing plankton detection
- ✅ Doesn't replace or modify any existing functionality
- ✅ Provides real-time video analysis with community detection
- ✅ Can process both video files and live camera feeds
- ✅ Uses state-of-the-art GML algorithms (BigCLAM)
- ✅ Includes a user-friendly web interface

**Ready to start?** → `streamlit run app.py` → "🧬 Community Detection" tab

Enjoy exploring plankton communities! 🧬🔬
