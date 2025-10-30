#!/usr/bin/env python3
"""
Watchdog: Monitors training and auto-restarts if it crashes.
Runs continuously in background.
"""

import subprocess
import time
import os
from datetime import datetime

LOG_FILE = "/home/watchdog.log"

def log(message):
    """Log with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = f"[{timestamp}] {message}"
    print(msg)
    with open(LOG_FILE, "a") as f:
        f.write(msg + "\n")

def is_training_running(config_name):
    """Check if training process is running"""
    try:
        result = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return config_name in result.stdout
    except:
        return False

def get_log_size(log_file):
    """Get log file size"""
    try:
        return os.path.getsize(log_file)
    except:
        return 0

def restart_training(script_path, log_path):
    """Restart training"""
    log(f"🔄 Restarting training: {script_path}")
    try:
        subprocess.Popen(
            [script_path],
            stdout=open(log_path, "a"),
            stderr=subprocess.STDOUT
        )
        time.sleep(5)
        log("✅ Training restarted")
        return True
    except Exception as e:
        log(f"❌ Failed to restart: {e}")
        return False

def main():
    log("🐕 Watchdog started - monitoring 3B training")
    
    config_3b = "llama32_3b_paraphrase_config.yaml"
    script_3b = "/home/run_llama32_3b_paraphrase_training.sh"
    log_3b = "/home/llama32_3b_paraphrase_training.log"
    
    last_log_size = get_log_size(log_3b)
    no_progress_count = 0
    
    while True:
        time.sleep(300)  # Check every 5 minutes
        
        # Check if process is running
        if not is_training_running(config_3b):
            log("⚠️  Training process not found!")
            
            # Check if completed
            if os.path.exists("/home/models/llama32_3b_paraphrase_lora/adapter_model.safetensors"):
                log("✅ Training completed successfully!")
                break
            else:
                log("❌ Training crashed or stopped - restarting...")
                restart_training(script_3b, log_3b)
                last_log_size = get_log_size(log_3b)
                no_progress_count = 0
                continue
        
        # Check if log is growing (training is progressing)
        current_log_size = get_log_size(log_3b)
        
        if current_log_size <= last_log_size:
            no_progress_count += 1
            log(f"⚠️  No progress detected ({no_progress_count}/3)")
            
            if no_progress_count >= 3:  # 15 minutes of no progress
                log("❌ Training appears stuck - will restart")
                # Kill old process
                subprocess.run(["pkill", "-f", config_3b])
                time.sleep(5)
                restart_training(script_3b, log_3b)
                no_progress_count = 0
        else:
            if no_progress_count > 0:
                log(f"✅ Training progressing ({current_log_size - last_log_size} bytes added)")
            no_progress_count = 0
        
        last_log_size = current_log_size
    
    log("🐕 Watchdog finished - 3B training complete")

if __name__ == "__main__":
    main()

