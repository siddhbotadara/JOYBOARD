#dda.py
import os
import joblib
import numpy as np
import settings

MODEL_FILE = os.path.join(os.path.dirname(__file__), "dda_model_Joyboard.pkl")

class DynamicDifficulty:
    def __init__(self):
        self.last_prediction_string = "NO DATA"
        self.previous_factor = 1.0
        self.current_factor = 1.0
        self.min_factor = 0.5
        self.max_factor = 2.0

        self.SCALE_FACTOR = 20.0 
        self.model = self._load_model()

    def _load_model(self): 
        if os.path.exists(MODEL_FILE):
            try:
                print("")
                return joblib.load(MODEL_FILE)
            except Exception as e:
                pass
        print("")
        return None

    def update(self, level_num, time_taken, health_ratio):
        
        if self.model is not None:
            try:
                features = np.array([[level_num, time_taken, health_ratio]])
                # The model now predicts the 'performance_delta'
                predicted_delta = float(self.model.predict(features)[0]) 
                
                # Use the predicted delta to adjust the factor:
                # Positive delta (player did better) -> factor > 1.0 (harder)
                # Negative delta (player struggled) -> factor < 1.0 (easier)
                factor = 1.0 + (predicted_delta / self.SCALE_FACTOR)
                
                self.current_factor = max(self.min_factor, min(self.max_factor, factor))

                self.last_prediction_string = (
                    "Difficulty Increased (Excellent Performance)" if predicted_delta > 0
                    else "Difficulty Decreased (Struggling)" if predicted_delta < 0
                    else "Difficulty Maintained (Steady Performance)"
                )

            except Exception as e:
                self._rule_adjust(time_taken, health_ratio)
        else:
            self._rule_adjust(time_taken, health_ratio)

        self._apply_to_settings()

    def _rule_adjust(self, time_taken, health_ratio):
        adjustment = 0.0
        if time_taken < 40 and health_ratio > 0.8:
            adjustment = +0.15
            self.last_prediction_string = "Difficulty Increased (Excellent Performance)"
        elif time_taken > 110 or health_ratio < 0.35:
            adjustment = -0.15
            self.last_prediction_string = "Difficulty Decreased (Struggling)"
        else:
            self.last_prediction_string = "Difficulty Maintained (Steady Performance)"
        self.current_factor = max(self.min_factor, min(self.max_factor, self.current_factor + adjustment))
    

    def _apply_to_settings(self):
        try:
            if not hasattr(self, "_base_values_saved"):
                self._base_LAVA = settings.LAVA_DAMAGE_AMOUNT
                self._base_ENEMY_BULLET = settings.ENEMY_BULLET_DAMAGE
                self._base_BASE_ENEMY_HEALTH = getattr(settings, "BASE_ENEMY_HEALTH", 1)
                self._base_values_saved = True

            settings.LAVA_DAMAGE_AMOUNT = max(1, int(round(self._base_LAVA * self.current_factor)))
            settings.ENEMY_BULLET_DAMAGE = max(1, int(round(self._base_ENEMY_BULLET * self.current_factor)))
            settings._DDA_ENEMY_HEALTH_MULTIPLIER = self.current_factor

        except Exception as e:
            pass

    def get_prediction_string(self):
        # Compare previous vs current factor
        if self.current_factor > self.previous_factor + 0.1:
            result = "Difficulty Increased (You're Crushing!)"
        elif self.current_factor < self.previous_factor - 0.1:
            result = "Difficulty Decreased (Take it Easy)"
        else:
            result = "Difficulty Maintained (Balanced Play)"

        # Update previous factor for next comparison
        self.previous_factor = self.current_factor

        return result