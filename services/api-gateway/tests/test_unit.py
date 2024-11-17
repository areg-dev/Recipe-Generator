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


@pytest.fixture
def request_recipe_prompt():
    return {"recipe": f"""
        Sure! Here's a quick and delicious vegetarian pasta recipe that's nut-free and perfect for serving 4 people, all within 30 minutes.
        ### Quick Italian Spinach and Tomato Pasta
        #### Ingredients:
        - 12 oz (340g) pasta (penne or spaghetti)
        - 2 tablespoons olive oil
        - 4 cloves garlic, minced
        - 1 can (14 oz) diced tomatoes (with their juice)
        - 4 cups fresh spinach (if using frozen, thawed and drained)
        - 1 teaspoon dried oregano
        - 1 teaspoon dried basil
        - Salt and pepper, to taste
        - Grated Parmesan cheese (optional, for serving)
        - Fresh basil leaves, for garnish (optional)
        #### Instructions:
        1. Cook the Pasta:
           - Bring a large pot of salted water to a boil. Add the pasta and cook according to the package directions until al dente. Reserve ½ cup of pasta water, then drain the pasta.
        2. Prepare the Sauce:
           - While the pasta is cooking, heat the olive oil in a large skillet over medium heat. Add the minced garlic and sauté for about 1 minute until fragrant, stirring frequently to avoid burning.
        3. Add Tomatoes and Spinach:
           - Pour in the canned diced tomatoes (with juice) and stir. Bring to a simmer and add the fresh spinach. Cook for about 3-4 minutes until the spinach wilts down.
        4. Season:
           - Stir in the dried oregano and basil. Season with salt and pepper to taste. If the sauce is too thick, add a little of the reserved pasta water to reach your desired consistency.
        5. Combine:
           - Add the drained pasta to the skillet and toss everything together to combine. Cook for another 1-2 minutes to heat through, allowing the pasta to absorb some of the sauce.
        6. Serve:
           - Plate the pasta and sprinkle with grated Parmesan cheese and fresh basil leaves, if desired.
        #### Enjoy!
        This dish is healthy, flavorful, and comes together in under 30 minutes. Perfect for a quick weeknight dinner!
        """}

@pytest.fixture
def request_recipe_validation_prompt():
    return {"recipe": f"""
        Sure! Here's a quick and delicious vegetarian pasta recipe that's nut-free and perfect for serving 4 people, all within 30 minutes.
        ### Quick Italian Spinach and Tomato Pasta
        #### Ingredients:
        - 12 oz (340g) pasta (penne or spaghetti)
        - 2 tablespoons olive oil
        - 4 cloves garlic, minced
        - 1 can (14 oz) diced tomatoes (with their juice)
        - 4 cups fresh spinach (if using frozen, thawed and drained)
        - 1 teaspoon dried oregano
        - 1 teaspoon dried basil
        - Salt and pepper, to taste
        - Grated Parmesan cheese (optional, for serving)
        - Fresh basil leaves, for garnish (optional)
        #### Instructions:
        1. Cook the Pasta:
           - Bring a large pot of salted water to a boil. Add the pasta and cook according to the package directions until al dente. Reserve ½ cup of pasta water, then drain the pasta.
        2. Prepare the Sauce:
           - While the pasta is cooking, heat the olive oil in a large skillet over medium heat. Add the minced garlic and sauté for about 1 minute until fragrant, stirring frequently to avoid burning.
        3. Add Tomatoes and Spinach:
           - Pour in the canned diced tomatoes (with juice) and stir. Bring to a simmer and add the fresh spinach. Cook for about 3-4 minutes until the spinach wilts down.
        4. Season:
           - Stir in the dried oregano and basil. Season with salt and pepper to taste. If the sauce is too thick, add a little of the reserved pasta water to reach your desired consistency.
        5. Combine:
           - Add the drained pasta to the skillet and toss everything together to combine. Cook for another 1-2 minutes to heat through, allowing the pasta to absorb some of the sauce.
        6. Serve:
           - Plate the pasta and sprinkle with grated Parmesan cheese and fresh basil leaves, if desired.
        #### Enjoy!
        This dish is healthy, flavorful, and comes together in under 30 minutes. Perfect for a quick weeknight dinner!
        
            calories: 420,
            protein: 15,
            fat: 12,
            carbohydrates: 63,
            totalWeight: 680
        """}


def test_generate_recipe(request_recipe_data):
    url = "http://127.0.0.1:8080/generate-recipe"
    response = requests.post(url, json=request_recipe_data)

    assert response.status_code == 200
    data = response.json()
    print('\n', data['recipe'])


def test_calculate_nutrition(request_recipe_prompt):
    url = "http://127.0.0.1:8080/calculate-nutrition"

    response = requests.post(url, json=request_recipe_prompt)

    assert response.status_code == 200
    data = response.json()
    print('\n', data['recipe'])


def test_validate_recipt(request_recipe_validation_prompt):
    url = "http://127.0.0.1:8080/validate-recipe"

    response = requests.post(url, json=request_recipe_validation_prompt)

    assert response.status_code == 200
    data = response.json()
    print('\n', data['validated'])
