from datetime import datetime, timedelta
import random
import numpy as np

class WeatherDataGenerator:
    def __init__(self):
        self.base_values = {
            'temperature': {'min': 15, 'max': 35},
            'humidity': {'min': 30, 'max': 90},
            'soil_moisture': {'min': 20, 'max': 80}
        }
    
    def generate_historical_data(self, days=30):
        """Simüle edilmiş geçmiş veri oluştur"""
        data = []
        base_date = datetime.now() - timedelta(days=days)
        
        for day in range(days):
            current_date = base_date + timedelta(days=day)
            # Her gün için 24 saatlik veri
            for hour in range(24):
                time = current_date + timedelta(hours=hour)
                
                # Gerçekçi veri simülasyonu
                temperature = random.uniform(
                    self.base_values['temperature']['min'], 
                    self.base_values['temperature']['max']
                )
                humidity = random.uniform(
                    self.base_values['humidity']['min'], 
                    self.base_values['humidity']['max']
                )
                soil_moisture = random.uniform(
                    self.base_values['soil_moisture']['min'], 
                    self.base_values['soil_moisture']['max']
                )
                
                # Gün içi değişimleri simüle et
                temperature += 5 * np.sin(hour * np.pi / 12)  # Gündüz daha sıcak
                humidity -= 10 * np.sin(hour * np.pi / 12)   # Gündüz daha kuru
                
                data.append({
                    'timestamp': time,
                    'temperature': temperature,
                    'humidity': humidity,
                    'soil_moisture': soil_moisture,
                })
        
        return data

    def generate_current_data(self):
        """Anlık veri oluştur"""
        return {
            'soil_moisture': random.uniform(
                self.base_values['soil_moisture']['min'], 
                self.base_values['soil_moisture']['max']
            ),
            'temperature': random.uniform(
                self.base_values['temperature']['min'], 
                self.base_values['temperature']['max']
            ),
            'humidity': random.uniform(
                self.base_values['humidity']['min'], 
                self.base_values['humidity']['max']
            )
        } 