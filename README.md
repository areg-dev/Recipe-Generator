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

#### Output Example
```text
Sure! Here's a quick and delicious vegetarian pasta recipe that's nut-free and inspired by Italian cuisine. This recipe serves 4 and can be prepared in under 30 minutes.
```
