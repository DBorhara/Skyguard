from gps3 import gps3


class GPS:
    def __init__(self):
        self.gps_socket = gps3.GPSDSocket()
        self.data_stream = gps3.DataStream()
        self.gps_socket.connect()
        self.gps_socket.watch()

    def read_gps(self):
        gps_lat = None
        gps_lon = None
        gps_alt = None
        gps_fix = False

        try:
            for new_data in self.gps_socket:
                if new_data:
                    self.data_stream.unpack(new_data)
                    if self.data_stream.TPV['lat'] != 'n/a' and self.data_stream.TPV['lon'] != 'n/a':
                        gps_lat = self.data_stream.TPV['lat']
                        gps_lon = self.data_stream.TPV['lon']
                        gps_alt = self.data_stream.TPV['alt']
                        gps_fix = True
                    break
        except Exception as e:
            print("GPS read error:", e)

        return gps_fix, gps_lat, gps_lon, gps_alt
