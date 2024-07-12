from flask import Flask, request, jsonify
import time
import threading
import requests

app = Flask(__name__)

BTCPAY_SERVER_URL = 'https://your-btcpay-server.com'
API_KEY = 'IiLlG7WbbEkbWvCP7Mvr7ZIibIMkY0vdD77nPV1yvoQ'
STORE_ID = '6XaMmbVni3QAcZvHeC2u82kBgFKJTPBZ9dqEGZcCMCd5'

def create_invoice(amount, buyer_email):
    invoice_data = {
        "price": amount,
        "currency": "USD",
        "buyerEmail": buyer_email,
        "notificationURL": "https://your-server.com/webhook",
        "extendedNotifications": True
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {API_KEY}'
    }
    response = requests.post(f'{BTCPAY_SERVER_URL}/invoices', json=invoice_data, headers=headers)
    return response.json()

@app.route('/webhook', methods=['POST'])
def btcpay_webhook():
    data = request.json
    if data['event']['name'] == 'invoice_paid':
        invoice_id = data['invoice']['id']
        threading.Thread(target=handle_subscription, args=(invoice_id,)).start()
    return '', 200

def handle_subscription(invoice_id):
    invoice = get_invoice(invoice_id)
    amount = invoice['price']
    email = invoice['buyerEmail']

    time.sleep(10 * 24 * 60 * 60)  # Wait 10 days

    if amount == 20:
        hourly_rate = 800
    elif amount in [200, 799]:
        hourly_rate = 3000

    while True:
        create_invoice(hourly_rate, email)
        time.sleep(3600)  # Every hour

def get_invoice(invoice_id):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {API_KEY}'
    }
    response = requests.get(f'{BTCPAY_SERVER_URL}/invoices/{invoice_id}', headers=headers)
    return response.json()

@app.route('/create', methods=['POST'])
def create_payment():
    data = request.json
    amount = data['amount']
    email = data['email']
    invoice = create_invoice(amount, email)
    return jsonify(invoice)

if __name__ == '__main__':
    app.run(port=4242)
