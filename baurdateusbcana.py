import sys
import serial
import time

def configure_can_adapter(port):
    """
    Configures the Waveshare USB-CAN-A adapter with a custom baud rate.
    """
    # --- Bit Timing Calculation for 666666 bps @ 24MHz clock ---
    # These values are calculated for an SJA1000-compatible controller.
    # Bitrate = Clock / (Prescaler * (1 + TSEG1 + TSEG2))
    # 666666 ≈ 24,000,000 / (3 * (1 + 9 + 2))
    #
    # BTR0 Register (SJW + BRP):
    #   BRP (Baud Rate Prescaler) = 3 - 1 = 2
    #   SJW (Sync Jump Width) = 1 - 1 = 0
    #   BTR0 = (SJW << 6) | BRP = (0 << 6) | 2 = 0x02
    #
    # BTR1 Register (SAM + TSEG2 + TSEG1):
    #   TSEG1 = 9 - 1 = 8
    #   TSEG2 = 2 - 1 = 1
    #   SAM (Sample points) = 0 (sample once)
    #   BTR1 = (SAM << 7) | (TSEG2 << 4) | TSEG1 = (0<<7)|(1<<4)|8 = 0x18
    #
    btr0 = "02"
    btr1 = "18"
    
    # The command format is "sBTR0BTR1\r"
    custom_baud_rate_command = f"s{btr0}{btr1}\r".encode('ascii')
    open_command = b"O\r"
    close_command = b"C\r"

    try:
        # The device's serial interface usually runs at a high speed.
        # 2000000 is the default for this model.
        ser = serial.Serial(port, 2000000, timeout=0.1)
        print(f"Successfully opened serial port {port}")

        # 1. Send Close command to ensure a known state
        print("Sending 'Close' command...")
        ser.write(close_command)
        time.sleep(0.1)
        response = ser.read_all()
        if response:
            print(f"Response: {response}")

        # 2. Send custom baud rate command
        print(f"Sending custom baud rate command: {custom_baud_rate_command.strip().decode()}")
        ser.write(custom_baud_rate_command)
        time.sleep(0.1)
        response = ser.read_all()
        if response:
            print(f"Response: {response}")
        else:
            print("No response to baud rate command (this is often normal).")

        # 3. Send Open command to activate the CAN channel
        print("Sending 'Open' command...")
        ser.write(open_command)
        time.sleep(0.1)
        response = ser.read_all()
        if response:
            print(f"Response: {response}")

        ser.close()
        print("\nConfiguration sent successfully.")
        print(f"Device on {port} is now configured for 666666 bps.")
        print("You can now use your CAN application that communicates over this serial port.")

    except serial.SerialException as e:
        print(f"Error: Could not open or write to serial port {port}.")
        print(f"Details: {e}")
        print("Please check the port name and ensure you have the correct permissions (e.g., run with sudo or add your user to the 'dialout' group).")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 configure_waveshare_can.py /dev/ttyUSB<number>")
        print("Example: python3 configure_waveshare_can.py /dev/ttyUSB0")
        sys.exit(1)
    
    serial_port = sys.argv[1]
    configure_can_adapter(serial_port)
