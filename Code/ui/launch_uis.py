"""
Launch script for dual Streamlit UIs
Starts both Admin Monitor and End User interfaces
"""

import subprocess
import sys
import time
import webbrowser
from pathlib import Path
import signal
import os


def print_banner():
    """Print startup banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║           LangGraph Dual UI System Launcher                 ║
    ║                                                              ║
    ║  Starting two Streamlit interfaces:                         ║
    ║  • Admin Monitor UI (Port 8501)                             ║
    ║  • End User UI (Port 8502)                                  ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def check_streamlit():
    """Check if Streamlit is installed"""
    try:
        import streamlit
        print("✅ Streamlit is installed")
        return True
    except ImportError:
        print("❌ Streamlit is not installed")
        print("Install it with: pip install streamlit")
        return False


def check_files():
    """Check if required UI files exist"""
    current_dir = Path(__file__).parent
    required_files = [
        "admin_monitor_ui.py",
        "user_interface_ui.py",
        "workflow_state_manager.py"
    ]
    
    missing_files = []
    for file in required_files:
        file_path = current_dir / file
        if file_path.exists():
            print(f"✅ Found {file}")
        else:
            print(f"❌ Missing {file}")
            missing_files.append(file)
    
    if missing_files:
        print("\n⚠️  Please create the missing files before running.")
        return False
    
    return True


def launch_streamlit(script_name, port):
    """Launch a Streamlit app on specified port"""
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        script_name,
        "--server.port", str(port),
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false"
    ]
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        return process
    except Exception as e:
        print(f"❌ Error launching {script_name}: {e}")
        return None


def open_browsers(admin_port=8501, user_port=8502):
    """Open browser tabs for both UIs"""
    print("\n🌐 Opening browser tabs...")
    time.sleep(3)  # Wait for Streamlit to start
    
    try:
        webbrowser.open(f"http://localhost:{admin_port}")
        time.sleep(1)
        webbrowser.open(f"http://localhost:{user_port}")
        print("✅ Browser tabs opened")
    except Exception as e:
        print(f"⚠️  Could not open browsers: {e}")
        print(f"   Please manually open:")
        print(f"   - Admin Monitor: http://localhost:{admin_port}")
        print(f"   - End User UI: http://localhost:{user_port}")


def main():
    """Main launcher function"""
    print_banner()
    
    # Pre-flight checks
    print("\n📋 Running pre-flight checks...\n")
    
    if not check_streamlit():
        sys.exit(1)
    
    if not check_files():
        sys.exit(1)
    
    print("\n✅ All checks passed!\n")
    
    # Launch UIs
    print("🚀 Launching UIs...\n")
    
    admin_process = launch_streamlit("admin_monitor_ui.py", 8501)
    if not admin_process:
        print("❌ Failed to launch Admin Monitor UI")
        sys.exit(1)
    
    print("✅ Admin Monitor UI starting on port 8501")
    time.sleep(2)
    
    user_process = launch_streamlit("user_interface_ui.py", 8502)
    if not user_process:
        print("❌ Failed to launch End User UI")
        admin_process.terminate()
        sys.exit(1)
    
    print("✅ End User UI starting on port 8502")
    
    # Open browsers
    open_browsers(8501, 8502)
    
    print("\n" + "="*60)
    print("✅ Both UIs are running!")
    print("="*60)
    print("\n📍 Access URLs:")
    print("   • Admin Monitor: http://localhost:8501")
    print("   • End User UI:   http://localhost:8502")
    print("\n💡 Tips:")
    print("   • Open both URLs in separate browser tabs")
    print("   • Use Admin Monitor to track workflow execution")
    print("   • Use End User UI to input data and view results")
    print("\n⚠️  Press Ctrl+C to stop both services")
    print("="*60 + "\n")
    
    # Keep processes running
    try:
        # Monitor processes
        while True:
            # Check if processes are still running
            admin_status = admin_process.poll()
            user_status = user_process.poll()
            
            if admin_status is not None:
                print(f"\n⚠️  Admin Monitor UI stopped (exit code: {admin_status})")
                break
            
            if user_status is not None:
                print(f"\n⚠️  End User UI stopped (exit code: {user_status})")
                break
            
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down UIs...")
    
    finally:
        # Clean shutdown
        print("   Stopping Admin Monitor UI...")
        admin_process.terminate()
        
        print("   Stopping End User UI...")
        user_process.terminate()
        
        # Wait for processes to terminate
        try:
            admin_process.wait(timeout=5)
            user_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            print("   Force killing processes...")
            admin_process.kill()
            user_process.kill()
        
        print("\n✅ All services stopped")
        print("="*60)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
