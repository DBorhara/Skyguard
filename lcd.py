import time
import smbus

# Constants
I2C_ADDR = 0x23
LCD_W = 16
LCD_CHR = 1
LCD_CMD = 0
LCD_L1 = 0x80
LCD_L2 = 0xC0
LCD_BACKLIGHT = 0x08
ENABLE = 0b00000100
E_PULSE = 0.0005
E_DELAY = 0.0005


class LCD:
    def __init__(self, address=I2C_ADDR):
        self.address = address
        self.bus = smbus.SMBus(1)
        self.lcd_init()

    # Init Display
    def lcd_init(self):
        self.lcd_byte(0x33, LCD_CMD)  # Initialize
        self.lcd_byte(0x32, LCD_CMD)  # Initialize
        self.lcd_byte(0x06, LCD_CMD)  # Cursor move direction
        self.lcd_byte(0x0C, LCD_CMD)  # Turn cursor off
        self.lcd_byte(0x28, LCD_CMD)  # 2 line display
        self.lcd_byte(0x01, LCD_CMD)  # Clear display
        time.sleep(E_DELAY)

    def lcd_byte(self, bits, mode):
        bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
        bits_low = mode | ((bits << 4) & 0xF0) | LCD_BACKLIGHT

        # High bits
        self.bus.write_byte(self.address, bits_high)
        self.lcd_toggle_enable(bits_high)

        # Low bits
        self.bus.write_byte(self.address, bits_low)
        self.lcd_toggle_enable(bits_low)

    def lcd_toggle_enable(self, bits):
        time.sleep(E_DELAY)
        self.bus.write_byte(self.address, (bits | ENABLE))
        time.sleep(E_PULSE)
        self.bus.write_byte(self.address, (bits | ~ENABLE))
        time.sleep(E_DELAY)

    def lcd_string(self, message, line):
        message = message.ljust(LCD_W, " ")
        self.lcd_byte(line, LCD_CMD)
        for i in range(LCD_W):
            self.lcd_byte(ord(message[i]), LCD_CHR)

    def display_data(self, line1, line2):
        self.lcd_string(line1, LCD_L1)
        self.lcd_string(line2, LCD_L2)
