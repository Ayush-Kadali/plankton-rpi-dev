# AquaLens Community Detection Integration

## Overview

The AquaLens feature has been integrated into the Marine Plankton Detection System as an additional analysis capability. This integration provides real-time community detection using Graph Machine Learning (GML) and BigCLAM algorithms to identify overlapping communities in plankton populations.

## What is AquaLens?

AquaLens is a sophisticated video processing pipeline that:
- **Detects plankton** in real-time video streams
- **Extracts embeddings** using MobileNetV3 neural networks
- **Clusters species** using HDBSCAN or MiniBatchKMeans
- **Builds spatial graphs** based on proximity and species similarity
- **Identifies communities** using BigCLAM (overlapping community detection)
- **Tracks organisms** across frames using centroid tracking

## Features

### 1. **Real-time Video Processing**
- Process video files or live camera feeds
- Configurable frame rate and processing windows
- Adaptive segmentation with strand detection

### 2. **Community Detection**
- BigCLAM algorithm for overlapping community detection
- Spatial and species-based graph construction
- Real-time community membership scoring

### 3. **Species Classification**
- Deep learning-based embedding extraction
- Automatic clustering into species groups
- Soft assignment with probability distributions

### 4. **Live Visualization**
- MJPEG stream with HUD overlay
- Bounding boxes with species labels
- Community badges on detected organisms
- Real-time statistics display

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Dashboard                       │
│                        (app.py)                              │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              AquaLens Integration Module                     │
│          (modules/aqualens_integration.py)                   │
│                                                              │
│  • AquaLensManager: Controls server lifecycle                │
│  • API Client: Communicates with FastAPI server             │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  FastAPI Server                              │
│                (aqualens/server.py)                          │
│                                                              │
│  Endpoints:                                                  │
│  • POST /start  - Start pipeline                            │
│  • POST /stop   - Stop pipeline                             │
│  • GET /status  - Get pipeline status                       │
│  • GET /frame.jpg - Latest frame                            │
│  • GET /stream.mjpg - MJPEG stream                          │
│  • GET /summary - Analysis summary                          │
│  • GET /table   - Data tables                               │
│  • GET /raw_nodes - Raw node data                           │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                Pipeline Engine                               │
│         (aqualens/final_final_pipeline.py)                   │
│                                                              │
│  Components:                                                 │
│  • Video Capture & Frame Processing                         │
│  • Segmentation (with Frangi filter for strands)            │
│  • Centroid Tracker (multi-object tracking)                 │
│  • Embedder (MobileNetV3 backbone)                          │
│  • Clusterer (HDBSCAN / MiniBatchKMeans)                    │
│  • Graph Builder (spatial + species similarity)             │
│  • BigCLAM (community detection)                            │
│  • HUD Renderer (annotated video output)                    │
│  • GlobalState (thread-safe state management)               │
└─────────────────────────────────────────────────────────────┘
```

## How to Use

### 1. **Access the Feature**
- Open the Streamlit dashboard: `streamlit run app.py`
- Navigate to the **"🧬 Community Detection"** tab

### 2. **Start the Server**
- Click **"🚀 Start Server"** button
- Wait for the server to initialize (2-3 seconds)
- Server runs on `http://localhost:8000`

### 3. **Configure Pipeline**
Select your input source:
- **Video File**: Choose from available videos in the project
- **Camera**: Specify camera index (0 for default webcam)

Configure processing parameters:
- **Processing Device**: CPU or CUDA (GPU)
- **Target FPS**: Processing frame rate (1-30 FPS)
- **Analysis Window**: Time window for community detection (1-10 seconds)
- **Use HDBSCAN**: Enable advanced clustering (requires more CPU)
- **Number of Communities**: Expected community count (2-12)

### 4. **Start Analysis**
- Click **"▶️ Start Analysis"**
- The pipeline will begin processing the video
- Live stream appears in the interface
- Real-time statistics update automatically

### 5. **View Results**
The interface displays:
- **Live Stream**: Annotated video with bounding boxes and community badges
- **Total Nodes**: Number of detected organisms
- **Species Detected**: Number of distinct species found
- **Communities**: Number of communities identified
- **Overlapping Communities**: Whether organisms belong to multiple communities
- **Species Distribution**: Top 5 species with counts
- **Community Sizes**: Top 5 communities with member counts

### 6. **Stop Analysis**
- Click **"⏹️ Stop Analysis"** to stop the pipeline
- Click **"🛑 Stop Server"** to shut down the server

## Technical Details

### Community Detection Algorithm (BigCLAM)

BigCLAM (Cluster Affiliation Model for Big Networks) is used to detect overlapping communities:

1. **Graph Construction**:
   - Nodes: Detected plankton organisms
   - Edges: Based on spatial proximity and species similarity
   - Weight: `W = spatial_affinity + α * species_similarity`

2. **Community Detection**:
   - Each node has a K-dimensional latent vector F
   - Probability of edge (i,j): `P(i,j) = 1 - exp(-F_i · F_j)`
   - Optimized using gradient descent with negative sampling

3. **Membership Scores**:
   - Each node gets a score for each community
   - Threshold at 0.3 for binary membership
   - Supports overlapping communities (nodes in multiple communities)

### Clustering Methods

**HDBSCAN** (Hierarchical Density-Based Spatial Clustering):
- Better for irregular cluster shapes
- Automatically determines number of clusters
- Handles noise points (-1 label)
- More computationally intensive

**MiniBatchKMeans**:
- Faster for large datasets
- Fixed number of clusters (K_init parameter)
- Soft assignment via distance to centroids
- More suitable for streaming data

### Embedding Extraction

- **Backbone**: MobileNetV3-Small (pretrained on ImageNet)
- **Features**: Global average pooling of final conv layer
- **Augmentation**: Shape features (area, aspect ratio, solidity, major/minor axis, perimeter)
- **Combined**: Concatenated embedding (576-dim CNN + 5-dim shape = 581-dim)

## File Structure

```
plank-1/
├── app.py                          # Main Streamlit dashboard (updated)
├── modules/
│   └── aqualens_integration.py     # Integration module (new)
├── aqualens/                       # AquaLens feature directory
│   ├── server.py                   # FastAPI server
│   ├── final_final_pipeline.py     # Pipeline engine
│   ├── community_pipeline.py       # Standalone community detection
│   ├── 1.mp4, 2.mp4               # Sample videos
│   ├── video_artifacts/            # Output directory (created at runtime)
│   └── ...
└── AQUALENS_INTEGRATION.md         # This file
```

## Dependencies

The AquaLens feature requires the following Python packages (in addition to existing project dependencies):

```
fastapi
uvicorn
requests
torch
torchvision
scikit-learn
opencv-python
pandas
numpy
pillow
```

Optional (for enhanced features):
```
hdbscan          # For advanced clustering
scikit-image     # For Frangi filter (strand detection)
```

## API Endpoints

When the server is running, you can interact with these endpoints:

- **GET** `/` - Web interface with preview
- **GET** `/status` - Pipeline status
- **POST** `/start` - Start pipeline with JSON config
- **POST** `/stop` - Stop running pipeline
- **GET** `/frame.jpg` - Latest processed frame (JPEG)
- **GET** `/stream.mjpg` - MJPEG stream
- **GET** `/summary` - Analysis summary (JSON)
- **GET** `/table` - Data tables (JSON)
- **GET** `/raw_nodes` - Raw detection data (JSON)

## Troubleshooting

### Server won't start
- **Check port 8000**: Make sure no other service is using port 8000
- **Check dependencies**: Ensure all required packages are installed
- **Check Python version**: Requires Python 3.8+

### Pipeline fails to start
- **Invalid video path**: Verify the video file exists and is readable
- **Camera not found**: Check camera index (try 0, 1, 2)
- **Memory issues**: Reduce FPS target or window size
- **CUDA errors**: Switch to CPU device if GPU is unavailable

### No detections appearing
- **Video quality**: Ensure video has visible plankton
- **Segmentation threshold**: May need adjustment for your microscopy setup
- **Min/max area**: Default 20-50000 pixels, adjust in pipeline code if needed

### Poor clustering results
- **Not enough data**: Wait for more frames to accumulate (initial_cluster_min=40)
- **Wrong K value**: Adjust K_init to match expected species count
- **Try HDBSCAN**: Enable HDBSCAN for automatic cluster detection

## Performance Optimization

### For faster processing:
- Lower FPS target (3-6 FPS recommended)
- Disable HDBSCAN (use MiniBatchKMeans)
- Reduce number of communities (K_init)
- Use CPU for small videos, GPU for high-resolution streams

### For better accuracy:
- Higher FPS target (but slower)
- Enable HDBSCAN clustering
- Longer analysis windows (5-10 seconds)
- More communities (K_init = 8-12)

## Future Enhancements

Potential improvements to the integration:
- [ ] Save analysis results to database
- [ ] Export community detection data to CSV
- [ ] Historical analysis and comparison
- [ ] Integration with geographic mapping
- [ ] Custom species classifier training
- [ ] Multi-camera support
- [ ] Batch video processing
- [ ] Advanced visualization options

## Credits

- **AquaLens Pipeline**: Original implementation by the AquaLens team
- **Integration**: Added to Marine Plankton Detection System
- **BigCLAM Algorithm**: Based on "Overlapping Community Detection at Scale" (Yang & Leskovec, 2013)

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify server logs in terminal
3. Check browser console for errors
4. Review aqualens/video_artifacts/ for output files
