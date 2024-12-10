import time
import board
import adafruit_bme680
import adafruit_ccs811
import adafruit_sgp30
from collections import deque
import statistics


class Sensors:
    def __init__(self, bme680_addr=0x77):
        # I2C Init
        self.i2c = board.I2C()
        # BME680 Init
        self.bme680 = adafruit_bme680.Adafruit_BME680_I2C(
            self.i2c, address=bme680_addr)
        # Set sea level pressure default
        self.bme680.sea_level_pressure = 1013.25
        # CCS811 Init
        self.ccs811 = adafruit_ccs811.CCS811(self.i2c)
        # SGP30 Init
        self.sgp30 = adafruit_sgp30.Adafruit_SGP30(self.i2c)
        self.sgp30.iaq_init()
        time.sleep(15)

        # Wait until CCS811 is ready
        while not self.ccs811.data_ready:
            time.sleep(0.5)

        # Last minute data collection
        self.tvoc_data = deque(maxlen=60)
        self.eco2_data = deque(maxlen=60)

    def read_all(self):
        # BME680
        temperature = self.bme680.temperature
        humidity = self.bme680.humidity
        pressure = self.bme680.pressure
        altitude = self.bme680.altitude
        gas_resistance = self.bme680.gash

        # CCS811
        eco2_ccs811 = self.ccs811.eco2
        tvoc_ccs811 = self.ccs811.tvoc

        # SGP30
        eco2_sgp30 = self.sgp30.eCO2
        tvoc_sgp30 = self.sgp30.TVOC

        # Averages of eCO2 and TVOC
        average_eco2 = (eco2_ccs811 + eco2_sgp30)/2
        average_tvoc = (tvoc_ccs811 + tvoc_sgp30)/2

        # Median Data of eCO2 and TVOC from last minute
        median_eco2 = statistics.median(self.eco2_data) if len(
            self.eco2_data) > 0 else "N/A"
        median_tvoc = statistics.median(self.tvoc_data) if len(
            self.eco2_data) > 0 else "N/A"

        # Data Output to Main
        return {
            "temperature": temperature,
            "humidity": humidity,
            "pressure": pressure,
            "altitude": altitude,
            "gas_resistance": gas_resistance,
            "eco2_ccs811": eco2_ccs811,
            "tvoc_ccs811": tvoc_ccs811,
            "eco2_sgp30": eco2_sgp30,
            "tvoc_sgp30": tvoc_sgp30,
            "average_eco2": average_eco2,
            "average_tvoc": average_tvoc,
            "median_eco2": median_eco2,
            "median_tvoc": median_tvoc
        }
