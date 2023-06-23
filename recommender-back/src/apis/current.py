from fmiopendata.wfs import download_stored_query
from apis.poi import PointOfInterest
import copy


class Current:
    def __init__(self):
        self.weather = None
        self.get_current_weather()

    def get_current_weather(self):
        '''
        Retrieves the current weather data for various stations.

        Returns:
            dict: A dictionary containing the current weather data for each station.
        '''

        obs = download_stored_query('fmi::observations::weather::multipointcoverage',
                                    args=['bbox=24.5,60,25.5,60.5', 'timeseries=True'])
        data = {}
        for station, metadata in obs.location_metadata.items():
            weatherdata = {
                'Air temperature': str(obs.data[station]['t2m']['values'][-1]) + ' °C',
                'Wind speed': str(obs.data[station]['ws_10min']['values'][-1]) + ' m/s',
                'Precipitation': str(obs.data[station]['ri_10min']['values'][-1]) + ' %',
                'Cloud amount': str(obs.data[station]['n_man']['values'][-1]) + ' %',
                'Humidity': str(obs.data[station]['rh']['values'][-1]) + ' %'
            }
            for value in list(weatherdata):
                if 'nan' in str(weatherdata[value]):
                    weatherdata.pop(value)
            if weatherdata:
                weatherdata['Latitude'] = metadata['latitude']
                weatherdata['Longitude'] = metadata['longitude']
                data[station] = weatherdata
        self.weather = data

    def find_nearest_stations_weather_data(self, poi: PointOfInterest):
        '''
        Finds the nearest weather station to a given point of interest (POI) and adds its weather data to the POI.

        Args:
            poi (PointOfInterest): The POI for which weather data needs to be added.

        Returns:
            PointOfInterest: The modified POI with weather information.

        '''
        lat = poi.latitude
        lon = poi.longitude
        smallest, nearest = float('inf'), ''
        for station in self.weather:
            dist = abs(self.weather[station]['Latitude'] - lat)\
                + abs(self.weather[station]['Longitude'] - lon)
            if dist < smallest:
                smallest, nearest = dist, station
            weather = copy.deepcopy(self.weather[nearest])
            del weather['Latitude']
            del weather['Longitude']
            poi.weather['Current'] = weather
        return poi
