import pytest
import requests


@pytest.fixture
def request_recipe_data():
    return {
        "number_of_persons": 4,
        "dish_type": "Pasta",
        "max_cooking_time": 30,
        "allergies_list": ["nuts"],
        "diet_requirements": ["vegetarian"],
        "cuisine_list": ["Italian"]
    }


def test_make_recipe(request_recipe_data):
    url = "http://127.0.0.1:8080/make-recipe"
    response = requests.post(url, json=request_recipe_data)

    assert response.status_code == 200
    data = response.json()
    print('\n', data)


def test_get_recipe_by_page():
    url = "http://127.0.0.1:8080/recipes?page=1&page_size=10"
    response = requests.get(url)

    assert response.status_code == 200
    data = response.json()
    print('\n', data)