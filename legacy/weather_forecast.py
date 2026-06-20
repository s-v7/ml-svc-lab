import requests
from flask import Flask, render_template, request, jsonify
import logging
from datetime import datetime, timezone
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt

app = Flask(__name__)

def new_weather_forecast(city):
    # HGBrasil API 
    url = f'https://api.hgbrasil.com/weather?key=SUA-CHAVE&city_name={city}'

    response = requests.get(url)

    if response.status_code == 200:
    	data_new = response.json()

    print(f'Temp: {data_new["results"]["temp"]}')
    print(f'Date: {data_new["results"]["date"]}')
    print(f'Time: {data_new["results"]["time"]}')
    print(f'Description: {data_new["results"]["description"]}')
    print(f'Wind_speedy: {data_new["results"]["wind_speedy"]}\n')

    # Input data
    data = data_new["results"]["forecast"]

    # Converting data into a pandas DataFrame
    df = pd.DataFrame(data)

    file_path = 'clima_tempo.csv'

    with open(file_path, 'a', newline='') as file:
    	# Writing to a CSV file
    	df.to_csv(file, index=False, header=not file.tell())

    print(f'[!!]New data was added to the CSV file successfully!\n')
    
    # Reading a CSV file
    #pd.read_csv("clima_tempo.csv")

    # Writing Data Df
    print(df)
    print(f'\nDescribe: {df.describe()}')

    # Selecting the relevant columns for input (features) and output (target)
    features = df[['max', 'min', 'cloudiness', 'rain', 'rain_probability']]
    target = df['condition']

    # Check the total amount of data
    total_samples = len(df)

    # Make sure you have enough data to split
    if total_samples >= 2:

        # Split data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)

        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # Creating the neural network model
        model = MLPClassifier(hidden_layer_sizes=(100, 50), max_iter=500, random_state=42)

        # Training the model
        model.fit(X_train_scaled, y_train)

        # Making predictions on the test set
        predictions_proba = model.predict_proba(X_test_scaled)  # Odds for each class
        predictions = model.predict(X_test_scaled)  # Predicted classes

        # Adding the probability of rain at the output for the user
        for pred, proba in zip(predictions, predictions_proba):
          index_rain = model.classes_.tolist().index('rain')
          probability_of_rain = proba[index_rain] * 100
          print(f'\nCondition: {pred}, Probability of Rain: {probability_of_rain:.2f}%')

        # Identifying days with probability of rain
        days_with_rain = [day['date'] for day, pred, proba in zip(data, predictions, predictions_proba) if pred == 'rain' and proba[model.classes_.tolist().index('rain')] > 0.5]
        print(f'\nDays with probability of rain: {days_with_rain}\n')

        # Create a bar chart
        plt.figure(figsize=(10, 6))

        # Bar for the amount of rain
        plt.bar(df["date"], df["rain"], color='blue', label='Rain (mm)')

        # Line for percentage of clouds
        plt.plot(df["date"], df["cloudiness"], color='gray', marker='o', label='Clouds (%)')

        # Line for the probability of rain
        plt.plot(df["date"], df["rain_probability"], color='green', marker='o', linestyle='dashed', label='Prob. Rain (%)')

        # Aesthetic adjustments
        plt.title(f'Meteorological Data: {data_new["results"]["city"]} - Date: {data_new["results"]["date"]} - Time: {data_new["results"]["time"]}')
        plt.xlabel('Data')
        plt.ylabel('Values')
        plt.legend()
        plt.grid(True)

        # View the chart
        plt.show()
    else:
        print("There is not enough data to split.")

def get_information_cep(cep):
    # ViaCEP API URL with the desired zip code
    url = f'https://viacep.com.br/ws/{cep}/json/'

    # Make a GET request to the API
    response = requests.get(url)

    # Check if the request was successful (code 200)
    if response.status_code == 200:
        # Convert the response to JSON format
        data_cep = response.json()

        # Display the information obtained
        print(f'\nCEP: {data_cep["cep"]}')
        print(f'Public place: {data_cep["logradouro"]}')
        print(f'Complement: {data_cep["complemento"]}')
        print(f'Neighborhood: {data_cep["bairro"]}')
        print(f'City: {data_cep["localidade"]}')
        print(f'UF: {data_cep["uf"]}')
    else:
        print(f'Request error. Status code: {response.status_code}')

    if 'localidade' in data_cep:
        city = data_cep['localidade']

    new_weather_forecast(city)

#if __name__ == '__main__':
	#app.run(debug=True)

# Example of use

zip_code = input("Enter zip code: ")
get_information_cep(zip_code)
