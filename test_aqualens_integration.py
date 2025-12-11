#!/usr/bin/env python3
"""
Test script for AquaLens integration
Verifies that the integration module works correctly
"""

import sys
import time
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

def test_import():
    """Test that all modules can be imported"""
    print("Testing imports...")
    try:
        from modules import aqualens_integration
        print("✓ Successfully imported aqualens_integration module")
        return True
    except Exception as e:
        print(f"✗ Failed to import: {e}")
        return False


def test_manager_creation():
    """Test that AquaLensManager can be created"""
    print("\nTesting manager creation...")
    try:
        from modules.aqualens_integration import AquaLensManager
        manager = AquaLensManager()
        print(f"✓ Created AquaLensManager: {manager.base_url}")
        return manager
    except Exception as e:
        print(f"✗ Failed to create manager: {e}")
        return None


def test_server_lifecycle(manager):
    """Test starting and stopping the server"""
    print("\nTesting server lifecycle...")

    # Check initial state
    print("Checking initial server state...")
    if manager.is_server_running():
        print("⚠ Server already running, stopping it first...")
        manager.stop_server()
        time.sleep(2)

    # Start server
    print("Starting server...")
    if manager.start_server():
        print("✓ Server started successfully")

        # Verify it's running
        time.sleep(1)
        if manager.is_server_running():
            print("✓ Server is responsive")

            # Get status
            status = manager.get_status()
            print(f"✓ Server status: {status}")

            # Stop server
            print("\nStopping server...")
            if manager.stop_server():
                print("✓ Server stopped successfully")
                time.sleep(1)

                # Verify it's stopped
                if not manager.is_server_running():
                    print("✓ Server is no longer running")
                    return True
                else:
                    print("✗ Server still running after stop")
                    return False
            else:
                print("✗ Failed to stop server")
                return False
        else:
            print("✗ Server not responsive")
            manager.stop_server()
            return False
    else:
        print("✗ Failed to start server")
        return False


def test_video_availability():
    """Check if test videos are available"""
    print("\nChecking for test videos...")
    video_files = []

    for ext in ['*.mp4', '*.avi', '*.mov']:
        video_files.extend(Path('.').glob(ext))
        video_files.extend(Path('aqualens').glob(ext))
        video_files.extend(Path('Real_Time_Vids').glob(ext))

    if video_files:
        print(f"✓ Found {len(video_files)} video files:")
        for vf in video_files[:5]:  # Show first 5
            print(f"  - {vf}")
        if len(video_files) > 5:
            print(f"  ... and {len(video_files) - 5} more")
        return True
    else:
        print("⚠ No video files found - you'll need to provide a video to test the pipeline")
        return False


def test_dependencies():
    """Check if all required dependencies are installed"""
    print("\nChecking dependencies...")
    required = [
        ('fastapi', 'FastAPI'),
        ('uvicorn', 'Uvicorn'),
        ('requests', 'Requests'),
        ('torch', 'PyTorch'),
        ('torchvision', 'TorchVision'),
        ('sklearn', 'scikit-learn'),
        ('cv2', 'OpenCV'),
        ('pandas', 'Pandas'),
        ('numpy', 'NumPy'),
    ]

    optional = [
        ('hdbscan', 'HDBSCAN'),
        ('skimage', 'scikit-image'),
    ]

    all_required = True
    for module_name, display_name in required:
        try:
            __import__(module_name)
            print(f"✓ {display_name}")
        except ImportError:
            print(f"✗ {display_name} - REQUIRED")
            all_required = False

    print("\nOptional dependencies:")
    for module_name, display_name in optional:
        try:
            __import__(module_name)
            print(f"✓ {display_name}")
        except ImportError:
            print(f"⚠ {display_name} - optional but recommended")

    return all_required


def main():
    """Run all tests"""
    print("=" * 60)
    print("AquaLens Integration Test Suite")
    print("=" * 60)

    results = []

    # Test dependencies
    results.append(("Dependencies", test_dependencies()))

    # Test imports
    results.append(("Module Import", test_import()))

    # Test manager creation
    manager = test_manager_creation()
    results.append(("Manager Creation", manager is not None))

    # Test video availability
    results.append(("Video Files", test_video_availability()))

    # Test server lifecycle (only if manager was created)
    if manager:
        results.append(("Server Lifecycle", test_server_lifecycle(manager)))
    else:
        results.append(("Server Lifecycle", False))

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:.<40} {status}")

    print("-" * 60)
    print(f"Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ All tests passed! The integration is ready to use.")
        print("\nNext steps:")
        print("1. Run: streamlit run app.py")
        print("2. Navigate to the '🧬 Community Detection' tab")
        print("3. Start the server and configure your pipeline")
        return 0
    else:
        print("\n⚠ Some tests failed. Please check the output above.")
        print("\nIf dependencies are missing, install them with:")
        print("  pip install -r requirements_aqualens.txt")
        return 1


if __name__ == "__main__":
    sys.exit(main())
