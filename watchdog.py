import subprocess
import time

while True:
    process = subprocess.Popen(["streamlit", "run", "app.py"])
    process.wait()
    print("App crashed. Restarting in 3 seconds...")
    time.sleep(3)
