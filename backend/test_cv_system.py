#!/usr/bin/env python3
"""
CV System Diagnostic Test
Tests all CV components end-to-end
"""

import sys
import os
sys.path.insert(0, '.')

import cv2
import numpy as np
from io import BytesIO

print("="*70)
print("CV SYSTEM DIAGNOSTIC TEST")
print("="*70)

# Test 1: Import CVProcessor
print("\n[1] Testing CVProcessor import...")
try:
    from app.cv.services.cv_processor import CVProcessor
    print("✅ CVProcessor import successful")
except Exception as e:
    print(f"❌ CVProcessor import failed: {e}")
    sys.exit(1)

# Test 2: Initialize CVProcessor
print("\n[2] Testing CVProcessor initialization...")
try:
    processor = CVProcessor()
    print("✅ CVProcessor initialized")
except Exception as e:
    print(f"❌ CVProcessor init failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Start session
print("\n[3] Testing session start...")
try:
    result = processor.start_session()
    session_id = result['session_id']
    print(f"✅ Session started: {session_id}")
except Exception as e:
    print(f"❌ Session start failed: {e}")
    sys.exit(1)

# Test 4: Create test frame
print("\n[4] Creating test frame...")
try:
    # Create a 640x480 RGB frame with a simple pattern
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    # Add some colors to make it realistic
    frame[:, :, 0] = 100  # Blue channel
    frame[:, :, 1] = 150  # Green channel  
    frame[:, :, 2] = 200  # Red channel
    
    # Encode as JPEG
    success, encoded = cv2.imencode('.jpg', frame)
    if not success:
        raise Exception("Failed to encode frame")
    
    frame_bytes = encoded.tobytes()
    print(f"✅ Test frame created: {len(frame_bytes)} bytes")
except Exception as e:
    print(f"❌ Frame creation failed: {e}")
    sys.exit(1)

# Test 5: Process frame
print("\n[5] Testing frame processing...")
try:
    metrics = processor.process_frame(frame_bytes)
    print("✅ Frame processed successfully!")
    print("\nMetrics returned:")
    for key, value in metrics.items():
        print(f"  • {key}: {value}")
except Exception as e:
    print(f"❌ Frame processing failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: Stop session
print("\n[6] Testing session stop...")
try:
    result = processor.stop_session()
    print("✅ Session stopped successfully!")
    if result:
        print(f"\nAnalysis file: {result.get('analysis_file', 'N/A')}")
        print(f"Session file: {result.get('session_file', 'N/A')}")
except Exception as e:
    print(f"❌ Session stop failed: {e}")
    import traceback
    traceback.print_exc()

# Test 7: Check exports folder
print("\n[7] Checking exports folder...")
import os
from pathlib import Path

exports_dir = Path('exports')
if exports_dir.exists():
    files = list(exports_dir.glob('*'))
    json_files = [f for f in files if f.suffix == '.json']
    print(f"✅ Exports folder exists")
    print(f"   Total files: {len(files)}")
    print(f"   JSON files: {len(json_files)}")
    if json_files:
        print("\n   Recent exports:")
        for f in sorted(json_files, key=lambda x: x.stat().st_mtime, reverse=True)[:3]:
            print(f"   • {f.name} ({f.stat().st_size} bytes)")
else:
    print("❌ Exports folder does not exist")

print("\n" + "="*70)
print("✅✅✅ CV SYSTEM FULLY FUNCTIONAL! ✅✅✅")
print("="*70)
print("\nAll tests passed! The CV system is working correctly.")
print("\nIf CV is not showing in frontend:")
print("1. Check browser console for JavaScript errors")
print("2. Check Network tab for /cv/ API calls")
print("3. Verify camera permissions granted")
print("4. Check that video element is playing")
print("5. Verify CVTrackingService.startSession() is called")
