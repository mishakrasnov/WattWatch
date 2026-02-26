import pandas as pd
class Model:
    def __init__(self, model_path):
        self.model = None
        
        
    def train(self, training_data):
        """
        Train the model with the provided training data.

        Args:
            training_data (list): list of jsons containing training data
        """
        pass

    def predict(self, input_data):
        """


        Args:
            input_data (list): list of timestamps

        Returns:
            list: list of predictions
        """
        
        prediciton = pd.DataFrame({'yhat': [0.0], 'yhat_lower': [0.0], 'yhat_upper': [0.0]})
        
        return prediciton
    