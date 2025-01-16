from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import requests

#Load Enviremon Variables
load_dotenv()

app = Flask(__name__)

#Allow CORS
CORS(app)

#Gloabal Variables
API_KEY = os.getenv("API_KEY")
STOCK_ENDPOINT = "https://www.alphavantage.co/query"


@app.route('/api/stock', methods=['GET'])
def get_stock_data():
     #Assigning the value of the URI Parameter stock 
    stock_name = request.args.get('stock')
    
    if not stock_name:
        return jsonify({"error": "Stock symbol is required"}), 400

    #API Call Params
    stock_params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": stock_name,
        "apikey": API_KEY
    }
    #GET request to the external API Service
    response = requests.get(STOCK_ENDPOINT, params=stock_params)

    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch data from API"}), 500

    data = response.json().get("Time Series (Daily)")
    
    if not data:
        return jsonify({"error": "Stock data not available"}), 404

    #Looking for the opening and closing prices
    res_list = [value for (key, value) in data.items()]
    yesterday_closing = float(res_list[0]["4. close"])
    yesterday_opening = float(res_list[0]["1. open"])

    #Calculating the variation 
    variation_percentage = round(((yesterday_closing - yesterday_opening) / yesterday_opening) * 100, 2)

    return jsonify({
        "stock": stock_name,
        "yesterday_opening": yesterday_opening,
        "yesterday_closing": yesterday_closing,
        "variation_percentage": variation_percentage
    })

if __name__ == '__main__':
    app.run(debug=True)
