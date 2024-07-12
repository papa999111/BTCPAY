import unittest
import requests_mock
from flask import json
from app import app, create_invoice, BTCPAY_SERVER_URL, API_KEY, handle_subscription
import threading
import time

class TestPaymentProcessing(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @requests_mock.Mocker()
    def test_create_invoice(self, mock):
        mock.post(f'{BTCPAY_SERVER_URL}/invoices', json={
            "id": "test_invoice_id",
            "url": "https://your-btcpay-server.com/invoice/test_invoice_id",
            "status": "new"
        })

        response = create_invoice(100, 'test@example.com')
        self.assertEqual(response['id'], 'test_invoice_id')
        self.assertEqual(response['url'], 'https://your-btcpay-server.com/invoice/test_invoice_id')

    @requests_mock.Mocker()
    def test_create_payment_endpoint(self, mock):
        mock.post(f'{BTCPAY_SERVER_URL}/invoices', json={
            "id": "test_invoice_id",
            "url": "https://your-btcpay-server.com/invoice/test_invoice_id",
            "status": "new"
        })

        response = self.app.post('/create', data=json.dumps({
            'amount': 100,
            'email': 'test@example.com'
        }), content_type='application/json')

        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['id'], 'test_invoice_id')
        self.assertEqual(data['url'], 'https://your-btcpay-server.com/invoice/test_invoice_id')

    @requests_mock.Mocker()
    def test_btcpay_webhook(self, mock):
        mock.get(f'{BTCPAY_SERVER_URL}/invoices/test_invoice_id', json={
            "id": "test_invoice_id",
            "price": 100,
            "buyerEmail": "test@example.com",
            "status": "paid"
        })

        data = {
            'event': {
                'name': 'invoice_paid'
            },
            'invoice': {
                'id': 'test_invoice_id'
            }
        }

        response = self.app.post('/webhook', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    @requests_mock.Mocker()
    def test_handle_subscription(self, mock):
        mock.get(f'{BTCPAY_SERVER_URL}/invoices/test_invoice_id', json={
            "id": "test_invoice_id",
            "price": 20,
            "buyerEmail": "test@example.com"
        })

        def run_subscription():
            handle_subscription('test_invoice_id')

        subscription_thread = threading.Thread(target=run_subscription)
        subscription_thread.start()
        subscription_thread.join(timeout=1)  # Wait 1 second for the thread to start

        self.assertTrue(subscription_thread.is_alive(), "Subscription thread did not start correctly.")

if __name__ == '__main__':
    unittest.main()
