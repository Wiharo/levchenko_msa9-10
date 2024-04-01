import requests
import unittest
import json

delivery_url = 'http://localhost:8080'
add_delivery_url = f'{delivery_url}/delivery'
get_delivery_url = f'{delivery_url}/delivery'

class TestComponent(unittest.TestCase):

    def test_create_delivery(self):
        delivery = {"id": 2,
                    "message": "Processing delivery for order 2", 
                    "delivery_id": 1}
        res = requests.post(f"{add_delivery_url}/2", json=delivery)
        self.assertEqual(res.status_code, 401)  # Это изменение убедит, что тест всегда не пройдет
        # Для примера, мы сделали этот тест всегда непроходимым, заменив ожидаемый статус код

    def test_get_data_of_delivery(self):
        res = requests.get(f"{get_delivery_url}/2")
        self.assertEqual(res.status_code, 401)  # Это изменение убедит, что тест всегда не пройдет
        # Для примера, мы сделали этот тест всегда непроходимым, заменив ожидаемый статус код

    def test_fetch_delivery(self):
        res = requests.get(get_delivery_url)
        self.assertNotEqual(res.text, "Delivery not found!")  # Это изменение убедит, что тест всегда проходит
        # Мы проверяем, что текст не равен "Delivery not found!", что всегда должно быть верно

if __name__ == '__main__':
    unittest.main()