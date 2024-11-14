# Recipe Generator

Recipe Generator is a microservice-based application that generates, validates, and stores recipes on demand. It uses multiple services to handle the business logic, recipe generation, nutritional calculation, and validation, all orchestrated via RabbitMQ for communication.

## Services Overview

- **api-gateway**: Business logic API built with FastAPI.
- **recipe-generation**: Generates recipes using OpenAI API.
- **nutritional-calculation**: Calculates nutritional information for recipes.
- **recipe-validation**: Validates recipes using OpenAI API.
- **RabbitMQ**: Messaging system used for service communication.


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

2. Navigate to the root of the `recipe-generator` directory:
    ```bash
    cd recipe-generator
    ```

3. Build the Docker images:
    ```bash
    docker-compose build
    ```

4. Start the services:
    ```bash
    docker-compose up
    ```

## Run Tests

To run the tests for the `api-gateway` service:

1. Navigate to the test directory:
    ```bash
    cd services/api-gateway/tests
    ```

2. Run the tests using pytest:
    ```bash
    pytest -s test_api_gateway.py
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
Sure! Here's a quick and delicious vegetarian pasta recipe that's nut-free and inspired by Italian cuisine. This recipe serves 4 and can be prepared in under 30 minutes.
```

```text
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
This dish is healthy, flavorful, and comes together in under 30 minutes. Perfect for a quick weeknight dinner!```
```
