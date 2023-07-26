import time

def beep_pc():
    try:
        # For Windows
        import winsound
        frequency = 2500  # Set the frequency (in Hz)
        duration = 1000   # Set the duration (in ms)
        winsound.Beep(frequency, duration)
    except ImportError:
        try:
            # For Linux and Mac
            import os
            os.system("echo -e '\a'")
        except:
            print("Beep sound not supported on this platform.")

def beep_android():
    # For Android using Kivy
    try:
        from plyer import notification
        notification.notify(title='Beep', message='', timeout=1)
    except ImportError:
        print("Beep sound not supported on this platform.")

if __name__ == "__main__":
    print("Generating beep sound on PC...")
    beep_pc()
    time.sleep(1)  # Add a delay to distinguish the two beeps

    print("Generating beep sound on Android...")
    beep_android()
