import time
import board
import busio
import adafruit_bme680
import adafruit_ccs811
import adafruit_sgp30
from gps3 import gps3
import smbus

# ===========================================================================
# LCD Constants (from lcd_i2c.py)
# ===========================================================================
I2C_ADDR = 0x27  # <<----- Add your LCD I2C address here
LCD_WIDTH = 16    # Maximum characters per line

LCD_CHR = 1  # Mode - Sending data
LCD_CMD = 0  # Mode - Sending command

LCD_LINE_1 = 0x80  # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0  # LCD RAM address for the 2nd line

LCD_BACKLIGHT = 0x08  # On
# LCD_BACKLIGHT = 0x00  # Off

ENABLE = 0b00000100  # Enable bit

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

# Set up I2C bus
bus = smbus.SMBus(1)  # Rev 2 Pi uses bus 1


def lcd_init():
    # Initialize display
    lcd_byte(0x33, LCD_CMD)  # 110011 Initialize
    lcd_byte(0x32, LCD_CMD)  # 110010 Initialize
    lcd_byte(0x06, LCD_CMD)  # Cursor move direction
    lcd_byte(0x0C, LCD_CMD)  # Turn cursor off
    lcd_byte(0x28, LCD_CMD)  # 2 line display (5x8 font)
    lcd_byte(0x01, LCD_CMD)  # Clear display
    time.sleep(E_DELAY)


def lcd_byte(bits, mode):
    # Send byte to data pins
    # bits = the data
    # mode = 1 for data, 0 for command
    bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
    bits_low = mode | ((bits << 4) & 0xF0) | LCD_BACKLIGHT

    # High bits
    bus.write_byte(I2C_ADDR, bits_high)
    lcd_toggle_enable(bits_high)

    # Low bits
    bus.write_byte(I2C_ADDR, bits_low)
    lcd_toggle_enable(bits_low)


def lcd_toggle_enable(bits):
    # Toggle enable pin
    time.sleep(E_DELAY)
    bus.write_byte(I2C_ADDR, (bits | ENABLE))
    time.sleep(E_PULSE)
    bus.write_byte(I2C_ADDR, (bits & ~ENABLE))
    time.sleep(E_DELAY)


def lcd_string(message, line):
    # Send string to display
    message = message.ljust(LCD_WIDTH, " ")
    lcd_byte(line, LCD_CMD)
    for i in range(LCD_WIDTH):
        lcd_byte(ord(message[i]), LCD_CHR)


# ===========================================================================
# Initialize I2C for sensors
i2c = board.I2C()  # SDA=GPIO2, SCL=GPIO3

# Initialize sensors (I2C)
bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c, address=0x77)
ccs811 = adafruit_ccs811.CCS811(i2c)
sgp30 = adafruit_sgp30.Adafruit_SGP30(i2c)

bme680.sea_level_pressure = 1013.25
sgp30.iaq_init()
time.sleep(15)

while not ccs811.data_ready:
    time.sleep(0.5)

# Setup GPS via gpsd and gps3
gps_socket = gps3.GPSDSocket()
data_stream = gps3.DataStream()
gps_socket.connect()
gps_socket.watch()

# Initialize the LCD
lcd_init()

# ===========================================================================
# Main loop
while True:
    # Read sensors
    temperature = bme680.temperature
    humidity = bme680.humidity
    pressure = bme680.pressure
    altitude = bme680.altitude
    gas_resistance = bme680.gas

    eco2_ccs811 = ccs811.eco2
    tvoc_ccs811 = ccs811.tvoc

    eco2_sgp30 = sgp30.eCO2
    tvoc_sgp30 = sgp30.TVOC

    # GPS data
    gps_lat = None
    gps_lon = None
    gps_alt = None
    gps_fix = False

    try:
        for new_data in gps_socket:
            if new_data:
                data_stream.unpack(new_data)
                if data_stream.TPV['lat'] != 'n/a' and data_stream.TPV['lon'] != 'n/a':
                    gps_lat = data_stream.TPV['lat']
                    gps_lon = data_stream.TPV['lon']
                    gps_alt = data_stream.TPV['alt']
                    gps_fix = True
                break
    except Exception as e:
        print("GPS read error:", e)

    # Print data to terminal (optional)
    print("\nEnvironmental + GPS Data:")
    print(f"T: {temperature:.2f}C  H: {humidity:.2f}%")
    print(f"P: {pressure:.2f}hPa  Alt: {altitude:.2f}m")
    print(f"Gas: {gas_resistance}Ω")
    print(f"CCS811 eCO2: {eco2_ccs811} ppm, TVOC: {tvoc_ccs811} ppb")
    print(f"SGP30 eCO2: {eco2_sgp30} ppm, TVOC: {tvoc_sgp30} ppb")

    if gps_fix:
        print(f"GPS Fix: Lat: {gps_lat}, Lon: {gps_lon}, Alt: {gps_alt} m")
    else:
        print("GPS: No Fix")

    # Update LCD lines
    line1 = f"T:{temperature:.1f}C H:{humidity:.1f}%"
    if gps_fix and gps_lat is not None and gps_lon is not None:
        # Truncate or format for 16 chars
        lat_str = f"{gps_lat:.2f}"
        lon_str = f"{gps_lon:.2f}"
        line2 = f"{lat_str},{lon_str}"
    else:
        line2 = "GPS:No Fix"

    # Write to LCD
    lcd_string(line1, LCD_LINE_1)
    lcd_string(line2, LCD_LINE_2)

    time.sleep(5)

