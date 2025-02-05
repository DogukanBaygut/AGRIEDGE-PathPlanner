class IrrigationPredictor:
    def __init__(self):
        # Sulama için eşik değerleri
        self.thresholds = {
            'soil_moisture': 40,  # %40'ın altında sulama gerekli
            'temperature': 30,    # 30°C üstünde sulama önceliği artar
            'humidity': 50,       # %50'nin altında sulama önceliği artar
        }
    
    def predict_irrigation_time(self, current_data):
        """Sulama zamanını tahmin et"""
        score = 0
        reasons = []
        
        # Toprak nemi kontrolü
        if current_data['soil_moisture'] < self.thresholds['soil_moisture']:
            score += 3
            reasons.append("Düşük toprak nemi")
            
        # Sıcaklık kontrolü
        if current_data['temperature'] > self.thresholds['temperature']:
            score += 2
            reasons.append("Yüksek sıcaklık")
            
        # Nem kontrolü
        if current_data['humidity'] < self.thresholds['humidity']:
            score += 1
            reasons.append("Düşük nem")
            
        # Sulama önerisi oluştur
        urgency = "Düşük"
        if score >= 4:
            urgency = "Yüksek"
        elif score >= 2:
            urgency = "Orta"
            
        return {
            'need_irrigation': score >= 2,
            'urgency': urgency,
            'score': score,
            'reasons': reasons
        } 