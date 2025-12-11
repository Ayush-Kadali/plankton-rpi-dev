# 🚀 Running the AquaLens Integration - Step by Step

## ✅ Everything is Ready!

The integration is **complete and tested**. Here's proof it works:

```
✓ Server started successfully!
✓ Pipeline started: {'status': 'started', 'source': 'aqualens/1.mp4'}
✓ Pipeline is now running!
✓ Integration is working perfectly! 🎉
```

---

## 🎬 Quick Start (3 Commands)

### Option 1: Run the Full Dashboard
```bash
streamlit run app.py
```
Then click on the **"🧬 Community Detection"** tab (the 5th tab at the top).

### Option 2: Run Quick Demo
```bash
python3 demo_aqualens.py
```
This demonstrates the integration working without the full UI.

### Option 3: Run Tests
```bash
python3 test_aqualens_integration.py
```
This verifies all components are working correctly.

---

## 📺 What You'll See in the Dashboard

### Step-by-Step Walkthrough:

#### 1. Launch Dashboard
```bash
$ streamlit run app.py
```

You'll see this in your browser:
```
┌────────────────────────────────────────────────────────────┐
│  🔬 Marine Plankton Detection System                      │
│  Advanced AI-powered monitoring across Indian coastal...   │
└────────────────────────────────────────────────────────────┘

Tabs:
┌──────────────────────────────────────────────────────────┐
│ 🏠 Overview │ 🗺️ Geographic Map │ 📊 Data Analysis │    │
│ 📥 Export Reports │ 🧬 Community Detection ← CLICK HERE! │
└──────────────────────────────────────────────────────────┘
```

#### 2. Click "🧬 Community Detection" Tab

You'll see:
```
🧬 Community Detection Analysis
Real-time plankton community detection using GML and BigCLAM

📖 About Community Detection:
This feature uses advanced graph machine learning (GML) algorithms
to detect overlapping communities in plankton populations...

⚙️ Server Controls
┌────────────────────────────────────────────────────────┐
│  [🚀 Start Server]  [🛑 Stop Server]  [🔄 Refresh]    │
│                                                        │
│  ⚠️ Server Status: Not running                        │
│     Start the server to use this feature              │
└────────────────────────────────────────────────────────┘
```

#### 3. Click "🚀 Start Server"

After clicking, you'll see:
```
⚙️ Server Controls
┌────────────────────────────────────────────────────────┐
│  [🚀 Start Server]  [🛑 Stop Server]  [🔄 Refresh]    │
│                                                        │
│  ✓ Server Status: Running                             │
└────────────────────────────────────────────────────────┘

🎬 Pipeline Controls
┌────────────────────────────────────────────────────────┐
│ Input Source: ⦿ Video File  ○ Camera                  │
│                                                        │
│ Select Video: [aqualens/1.mp4            ▼]           │
│                                                        │
│ Processing Device: [cpu                  ▼]           │
│ Target FPS: ━━━━●━━━━ 6.0                            │
│ Analysis Window: ━━━●━━━━ 3.0 seconds                │
│ ☐ Use HDBSCAN Clustering                              │
│ Number of Communities: ━━━━●━━━━ 6                   │
│                                                        │
│ [▶️ Start Analysis]  [⏹️ Stop Analysis]               │
└────────────────────────────────────────────────────────┘
```

#### 4. Configure and Click "▶️ Start Analysis"

The system will start processing:
```
✓ Pipeline Status: Running
Source: aqualens/1.mp4
Output: aqualens/video_artifacts

📊 Real-Time Analysis
┌────────────────────────┬──────────────────────────┐
│  🎥 Live Stream        │  📈 Summary              │
│                        │                          │
│  ┌──────────────────┐  │  Total Nodes: 42        │
│  │                  │  │  Species Detected: 6     │
│  │  [Video playing  │  │  Communities: 4          │
│  │   with bounding  │  │  Overlapping: Yes        │
│  │   boxes and      │  │                          │
│  │   community      │  │  Species Distribution:   │
│  │   badges]        │  │  • Species_0: 15        │
│  │                  │  │  • Species_1: 12        │
│  └──────────────────┘  │  • Species_2: 8         │
│                        │                          │
│                        │  Community Sizes:        │
│                        │  • Community 0: 18      │
│                        │  • Community 1: 14      │
│                        │                          │
│                        │  [🔄 Refresh Data]       │
└────────────────────────┴──────────────────────────┘
```

---

## 🔧 Integration Points (For Developers)

### Where the Integration Lives:

```
Your Project Structure:
plank-1/
├── app.py ← MODIFIED (added tab + imports)
│   ├── Line 31: Import integration module
│   ├── Line 395: Initialize manager
│   ├── Line 866-1074: New render function
│   └── Line 1085-1106: Added 5th tab
│
├── modules/
│   └── aqualens_integration.py ← NEW (integration bridge)
│       ├── AquaLensManager class
│       ├── start_server()
│       ├── start_pipeline()
│       ├── get_summary()
│       └── get_stream_url()
│
└── aqualens/ ← EXISTING (feature from teammate)
    ├── server.py (FastAPI backend)
    ├── final_final_pipeline.py (processing engine)
    ├── community_pipeline.py (standalone)
    ├── 1.mp4, 2.mp4 (test videos)
    └── ... (other files)
```

### How It Works:

```
┌─ User Action in Streamlit ─┐
│ Click "Start Server"        │
└──────────┬──────────────────┘
           │
           ▼
┌─ Integration Module ────────┐
│ AquaLensManager             │
│   .start_server()           │  ← Spawns server process
└──────────┬──────────────────┘
           │
           ▼
┌─ FastAPI Server ────────────┐
│ aqualens/server.py          │  ← Running on localhost:8000
│   POST /start               │
│   GET /stream.mjpg          │
│   GET /summary              │
└──────────┬──────────────────┘
           │
           ▼
┌─ Pipeline Engine ───────────┐
│ final_final_pipeline.py     │  ← Background thread
│   • Captures video frames   │
│   • Detects organisms       │
│   • Extracts embeddings     │
│   • Clusters species        │
│   • Builds graph            │
│   • Finds communities       │
│   • Annotates video         │
│   • Streams output          │
└─────────────────────────────┘
```

---

## 🎯 What the Feature Does

### Real-Time Processing Pipeline:

1. **Video Input** → Reads from file or camera
2. **Segmentation** → Detects plankton organisms
3. **Embedding** → Extracts features using MobileNetV3
4. **Tracking** → Follows organisms across frames
5. **Clustering** → Groups into species (HDBSCAN/K-Means)
6. **Graph Building** → Creates spatial + species graph
7. **Community Detection** → Runs BigCLAM algorithm
8. **Visualization** → Annotates and streams video

### Output:

- **Live Video Stream**: MJPEG with bounding boxes and labels
- **Species Counts**: How many of each species detected
- **Community Info**: Which organisms form communities
- **Overlap Detection**: Identifies organisms in multiple communities
- **Real-time Stats**: Updated continuously as video processes

---

## 📊 Sample Output

When you run the demo or use the dashboard, you'll see:

```python
{
  "timestamp": "2025-12-11T13:04:52Z",
  "total_nodes": 42,
  "species_counts": {
    "Species_0": 15,
    "Species_1": 12,
    "Species_2": 8,
    "Species_3": 5,
    "Species_4": 2
  },
  "communities": [
    {"community_id": 0, "count": 18},
    {"community_id": 1, "count": 14},
    {"community_id": 2, "count": 10},
    {"community_id": 3, "count": 6}
  ],
  "overlapping": true
}
```

---

## 🧪 Verification Commands

### Check Integration:
```bash
# Run full test suite
python3 test_aqualens_integration.py

# Expected output:
Dependencies............................ ✓ PASS
Module Import........................... ✓ PASS
Manager Creation........................ ✓ PASS
Video Files............................. ✓ PASS
Server Lifecycle........................ ✓ PASS
------------------------------------------------------------
Total: 5/5 tests passed
```

### Quick Demo:
```bash
# Run demonstration
python3 demo_aqualens.py

# Expected output:
✓ Manager created: http://localhost:8000
✓ Server started successfully!
✓ Pipeline started: {'status': 'started', 'source': 'aqualens/1.mp4'}
Pipeline is now running!
Integration is working perfectly! 🎉
```

### Access Endpoints Directly:
```bash
# Start the server (in background)
cd aqualens && python3 server.py &

# Wait for server to start
sleep 3

# Check status
curl http://localhost:8000/status

# Start pipeline
curl -X POST http://localhost:8000/start \
  -H "Content-Type: application/json" \
  -d '{"video": "1.mp4", "device": "cpu"}'

# Get summary
curl http://localhost:8000/summary

# View stream in browser
open http://localhost:8000/stream.mjpg
```

---

## 📁 Files You Can Use

### Test Videos (already in your project):
```
aqualens/1.mp4
aqualens/2.mp4
Real_Time_Vids/first try.mov
Real_Time_Vids/v4 try 2.mov
Real_Time_Vids/3rd try.mov
... and 5 more!
```

### Documentation Files:
```
INTEGRATION_SUMMARY.md        ← Technical overview (this file)
AQUALENS_INTEGRATION.md       ← Detailed technical docs
AQUALENS_QUICKSTART.md        ← User-friendly guide
RUN_INTEGRATION.md            ← Step-by-step instructions
```

### Test/Demo Scripts:
```
test_aqualens_integration.py  ← Comprehensive test suite
demo_aqualens.py              ← Quick demonstration
```

---

## 🎉 You're All Set!

The integration is **complete, tested, and ready to use**!

### To start using it now:

```bash
# Option 1: Full dashboard with UI
streamlit run app.py

# Option 2: Quick demonstration
python3 demo_aqualens.py

# Option 3: Run tests
python3 test_aqualens_integration.py
```

### What to expect:
- ✅ Server starts in 2-3 seconds
- ✅ Pipeline processes video in real-time
- ✅ Live stream shows annotated organisms
- ✅ Statistics update automatically
- ✅ Clean shutdown when done

---

## 🆘 Need Help?

1. **Read the docs**: `AQUALENS_QUICKSTART.md`
2. **Run tests**: `python3 test_aqualens_integration.py`
3. **Check logs**: Look at terminal output when server runs
4. **Common issues**:
   - Port 8000 in use? → Stop other services
   - Missing deps? → `pip3 install -r requirements_aqualens.txt`
   - Python < 3.9? → Upgrade Python

---

**Ready to see community detection in action? → `streamlit run app.py` 🚀**
