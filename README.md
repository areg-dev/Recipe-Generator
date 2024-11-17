# Recipe Generator

Recipe Generator is a microservice-based application that generates, validates, and stores recipes on demand. It uses multiple services to handle the business logic, recipe generation, nutritional calculation, and validation, all orchestrated via RabbitMQ for communication.

## Services Overview

- **api-gateway**: Business logic API built with FastAPI.
- **recipe-generation**: Generates recipes using OpenAI API.
- **nutritional-calculator**: Calculates nutritional information for recipes.
- **recipe-validation**: Validates recipes using OpenAI API.
- **RabbitMQ**: Messaging system used for service communication.
- **MongoDB**: Storing successfully created recipes.


## Requirements

- **Python** version ~3.10
- **Docker** version ~27.0.3
- **pytest** version ~7.4.2
- **requests** version ~2.32.3


1. Install Docker (at this moment tested on Apple Silicone and Ubuntu):
    ```bash
    # MacOS
   
    brew install --cask docker
    ```
   ```bash
    # Ubuntu 22.04
   
    sudo snap install docker
    ```
   
## Build and Run Docker Images

1. Clone the repository and navigate to the root directory:
    ```bash
    git clone git@github.com:areg-dev/Recipe-Generator.git
    cd Recipe-Generator
    ```

2. In the `docker-compose.yml` file, replace all instances of `- OPENAI_API_SECRET=X` with your OpenAI API key.

3. Build the Docker images:
    ```bash
    docker compose build
    ```

4. Start the services:
    ```bash
    docker compose up
    ```

# Recipe API Documentation

This API provides functionality for generating, validating, and retrieving recipes. It also supports nutritional calculations and pagination of stored recipes.

## Table of Contents

- [Base URL](#base-url)
- [Endpoints](#endpoints)
  - [POST /make-recipe](#post-making-recipe)
  - [GET /recipes](#get-retrieving-recipes)
  - [POST /generate-recipe](#post-generating-recipe)
  - [POST /calculate-nutrition](#post-calculating-nutrition)
  - [POST /validate-recipe](#post-validating-recipe)


## Base URL

The base URL for the API is: http://127.0.0.1:8080/


## Endpoints

### POST /generate-recipe

Generates a recipe based on the provided criteria.

#### Request Body

```json
{
  "number_of_persons": 4,
  "dish_type": "main",
  "max_cooking_time": 30,
  "allergies_list": ["nuts"],
  "diet_requirements": ["vegetarian"],
  "cuisine_list": ["Italian"]
}
```

#### Response

```json
{
  "recipe": "<<Recipe generated from OpenAI API>>"
}
```

### POST /calculate-nutrition

Calculates the nutrition information of a recipe.


#### Request Body

```json
{
  "recipe": "<<Recipe content>>"
}
```

#### Response

```json
{
  "message": "<<Calculated nutrition from OpenAI API>>"
}
```

### POST /validate-recipe

Validates a recipe to return Yes or No.


#### Request Body

```json
{
  "recipe": "<<Recipe with nutrition content>>"
}
```

#### Response

```json
{
  "message": "<<Yes/No>>"
}
```

### POST /make-recipe

Generates, calculates nutrition, and validates a recipe.
This is a combination of the /generate-recipe, /calculate-nutrition, 
and /validate-recipe endpoints. If validation is true then the content adding to the 
MongoDB


#### Request Body

```json
{
  "number_of_persons": 4,
  "dish_type": "main",
  "max_cooking_time": 30,
  "allergies_list": ["nuts"],
  "diet_requirements": ["vegetarian"],
  "cuisine_list": ["Italian"]
}
```

#### Response

```json
{
  "recipe": "Creamy Spinach and Tomato ........",
  "nutrition": {
    "calories": 760,
    "protein": 20,
    "fat": 40,
    "carbohydrates": 78,
    "totalWeight": 680
  },
  "validation": "Valid"
}
```

### GET /recipes

Return a paginated list of stored recipes.


#### Query Parameters

- **page (optional):** The page number (default is 1).
- **page_size (optional):** The number of recipes per page (default is 10, max is 100).
 
 
#### Response

```json
{
  "current_page": 1,
  "total_pages": 10,
  "page_size": 10,
  "total_records": 100,
  "data": [
    "Recipe 1",
    "Recipe 2",
    "Recipe 3"
  ]
}
```


## Run Tests

To run the tests for the `api-gateway` service:

1. Navigate to the test directory:
    ```bash
    cd services/api-gateway/tests
    ```

2. Run the tests using pytest:
    ```bash
    pytest -s test_functional.py
    ```

## Recipe Generation Example

#### Input Example

```http
  {
    "number_of_persons": 4,
    "dish_type": "Pasta",
    "max_cooking_time": 30,
    "allergies_list": ["nuts"],
    "diet_requirements": ["vegetarian"],
    "cuisine_list": ["Italian"]
  }
```

#### Output Examples

```text
Sure! Here’s a quick and delicious Italian vegetarian pasta recipe that’s nut-free and serves four people. You can have this ready in under 30 minutes.

### **Italian Vegetable Pasta**

#### **Ingredients:**
- 12 ounces (340g) of spaghetti or your favorite pasta
- 2 tablespoons of olive oil
- 3 cloves garlic, minced
- 1 medium zucchini, diced
- 1 red bell pepper, diced
- 1 cup cherry tomatoes, halved
- 1 cup spinach (fresh or frozen)
- 1 teaspoon dried oregano
- 1/2 teaspoon red pepper flakes (optional)
- Salt and pepper to taste
- 1/4 cup grated Parmesan cheese (optional for serving)
- Fresh basil leaves, for garnish

#### **Instructions:**
1. **Cook the Pasta:**
  - Bring a large pot of salted water to a boil. Add the spaghetti and cook according to package instructions until al dente (usually about 8-10 minutes). Reserve 1 cup of pasta water, then drain the pasta.
  
2. **Sauté the Vegetables:**
  - In a large skillet, heat the olive oil over medium heat. Add the minced garlic and sauté for about 1 minute until fragrant.
  - Add the diced zucchini and red bell pepper. Cook for about 5 minutes, stirring occasionally, until they begin to soften.

3. **Add Remaining Ingredients:**
  - Stir in the cherry tomatoes, spinach, oregano, and red pepper flakes (if using). Cook for another 3-4 minutes until the tomatoes are warmed through and the spinach is wilted. Season with salt and pepper to taste.
  
4. **Combine Pasta and Sauce:**
  - Add the drained spaghetti to the skillet. Toss everything together gently. If the mixture seems dry, add a splash of the reserved pasta water until it reaches your desired consistency.

5. **Serve:**
  - Divide the pasta among four plates. Sprinkle with grated Parmesan cheese (if using) and garnish with fresh basil leaves. Serve immediately.
  
### **Enjoy your quick and delicious Italian Vegetable Pasta!** 

Feel free to customize the recipe with other vegetables you may have on hand, such as mushrooms or asparagus, to suit your taste!

calories: 480, protein: 12, fat: 16, carbohydrates: 72, totalWeight: 860

```


