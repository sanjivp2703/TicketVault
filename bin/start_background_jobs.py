#!/usr/bin/env python3
"""
Start background jobs for automated transaction processing
Run this script to start the automated deadline checking and payment processing
"""
import sys
import os
import pathlib

# Add parent directory to path to import insta485
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from insta485.background_jobs import start_background_jobs

if __name__ == "__main__":
    print("🚀 Starting Safe Transaction Background Jobs...")
    print("This will handle:")
    print("  ✅ Automatic deadline checking")
    print("  ✅ Payment release processing") 
    print("  ✅ Email notifications")
    print("  ✅ Transaction state management")
    print()
    print("Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        start_background_jobs()
        
        # Keep the script running
        import time
        while True:
            time.sleep(60)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping background jobs...")
        from insta485.background_jobs import stop_background_jobs
        stop_background_jobs()
        print("✅ Background jobs stopped successfully")
    except Exception as e:
        print(f"❌ Error in background jobs: {e}")
        sys.exit(1)
