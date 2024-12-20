import time
from lcd import LCD
from sensors import Sensors
from gps import GPS


def main():
    # Init LCD
    lcd = LCD()

    # Init Sensors
    sensors = Sensors()

    # Init GPS
    gps = GPS()

    while True:
        # Get sensor data
        data = sensors.read_all()

        # Get GPS data
        gps_fix, gps_lat, gps_lon, gps_alt = gps.read_gps()

        # Print to terminal (Debugging Purposes, Can Comment Out)
        print("\nEnvironmental + GPS Data:")
        print(f"T: {data['temperature']:.2f}C  H: {data['humidity']:.2f}%")
        print(f"P: {data['pressure']:.2f}hPa  Alt: {data['altitude']:.2f}m")
        print(f"Gas: {data['gas_resistance']}Ω")
        print(f"CCS811 eCO2: {data['eco2_ccs811']} ppm, TVOC: {
              data['tvoc_ccs811']} ppb")
        print(f"SGP30 eCO2: {data['eco2_sgp30']} ppm, TVOC: {
              data['tvoc_sgp30']} ppb")

        # Print GPS else print average + median tvoc, eco2
        if gps_fix:
            print(f"GPS Fix: Lat: {gps_lat}, Lon: {gps_lon}, Alt: {gps_alt} m")
        else:
            print(f"TVOC: Average TVOC:{
                  data['average_tvoc']} Median TVOC:{data['median_tvoc']}")
            print(f"eCO2: Average eCO2:{
                  data['average_eco2']} Median eCO2:{data['median_eco2']}")

        # Format LCD lines
        # Sesnor Outputs - Change data here to get different sensor outputs
        line1 = f"T:{data['temperature']:.1f}C H:{data['humidity']:.1f}%"
        # GPS Latitude and Longitutde
        if gps_fix and gps_lat is not None and gps_lon is not None:
            lat_str = f"{gps_lat:.2f}"
            lon_str = f"{gps_lon:.2f}"
            line2 = f"{lat_str},{lon_str}"
        else:
            avg_tvoc_string = f"{data['average_tvoc']:.2f}"
            avg_eco2_string = f"{data['average_eco2']:.2f}"
            median_tvoc_string = f"{data['median_tvoc']:.2f}"
            median_eco2_string = f"{data['median_eco2']:.2f}"
            line2 = f"TVOC:A:{avg_tvoc_string}, M:{median_tvoc_string}, eCO2:A:{
                avg_eco2_string}, M:{median_eco2_string}"

        # Display data on LCD
        lcd.display_data(line1, line2)

        time.sleep(5)


if __name__ == "__main__":
    main()
