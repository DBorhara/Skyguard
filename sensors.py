import time
import board
import adafruit_bme680
import adafruit_ccs811
import adafruit_sgp30


class Sensors:
    def __init__(self, bme680_addr=0x77):
        self.i2c = board.I2C()
        self.bme680 = adafruit_bme680.Adafruit_BME680_I2C(
            self.i2c, address=bme680_addr)
        self.bme680.sea_level_pressure = 1013.25

        self.ccs811 = adafruit_ccs811.CCS811(self.i2c)
        self.sgp30 = adafruit_sgp30.Adafruit_SGP30(self.i2c)
        self.sgp30.iaq_init()
        time.sleep(15)

        # Wait until CCS811 is ready
        while not self.ccs811.data_ready:
            time.sleep(0.5)

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

        return {
            "temperature": temperature,
            "humidity": humidity,
            "pressure": pressure,
            "altitude": altitude,
            "gas_resistance": gas_resistance,
            "eco2_ccs811": eco2_ccs811,
            "tvoc_ccs811": tvoc_ccs811,
            "eco2_sgp30": eco2_sgp30,
            "tvoc_sgp30": tvoc_sgp30
        }
