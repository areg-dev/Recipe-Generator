import pytest
import requests


@pytest.fixture
def request_data():
    return {
        "number_of_persons": 4,
        "dish_type": "Pasta",
        "max_cooking_time": 30,
        "allergies_list": ["nuts"],
        "diet_requirements": ["vegetarian"],
        "cuisine_list": ["Italian"]
    }


def test_generate_recipe(request_data):
    url = "http://127.0.0.1:8080/generate-recipe"
    response = requests.post(url, json=request_data)

    assert response.status_code == 200
    data = response.json()
    print('\n', data['message'])
