# listen_unity.py
import time
import win32file

PIPE_NAME = r"\\.\pipe\UnityAIAgentLog"

print("=== Unity Log Listener ===")

while True:
    try:
        handle = win32file.CreateFile(
            PIPE_NAME,
            win32file.GENERIC_READ,
            0, None,
            win32file.OPEN_EXISTING,
            0, None
        )

        print("[Connected] Listening Unity Logs...")

        while True:
            result, data = win32file.ReadFile(handle, 4096)
            text = data.decode("utf-8", errors="replace").strip()
            if text:
                print("[Unity]", text)

    except Exception as e:
        print("[Waiting for Unity Log Pipe...]")
        time.sleep(1)
