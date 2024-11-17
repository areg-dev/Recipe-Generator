import json
import re

from typing import List
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from pymongo.errors import ConnectionFailure
from starlette.responses import JSONResponse
from datetime import datetime

from MongoDB import MongoDB
from RabbitMQ import RabbitMQ
from Logger import Logger

Logger.initialize_logger()
MongoDB.initialize_mongo()
MongoDB.initialize_mongo()
app = FastAPI()


class RecipeRequest(BaseModel):
    number_of_persons: int
    dish_type: str
    max_cooking_time: int
    allergies_list: list
    diet_requirements: list
    cuisine_list: list


@app.post("/generate-recipe")
async def generate_recipe(data: RecipeRequest):
    # The channel object (not connection) will create on each request
    # I think could it be better to separate the channel connect/disconnect logic
    try:
        rmq = RabbitMQ(RabbitMQ.QUEUE_RECIPE_GENERATION)
        response = await rmq.request(data.model_dump_json())
        return JSONResponse(content={"recipe": response}, status_code=200)
    except Exception as e:
        Logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


def extract_nutrition(text):
    match = re.search(r'(\{.*\})', text.replace('\n', ''))
    if match:
        json_str = match.group(0)
        try:
            return json.loads(json_str)
        except Exception as e:
            Logger.error(f"Extract Nutrition fail due to: {str(e)}")
    return None


@app.post("/calculate-nutrition")
async def calculate_nutrition(data: dict):
    try:
        rmq = RabbitMQ(RabbitMQ.QUEUE_NUTRITIONAL_CALCULATOR)
        response = await rmq.request(json.dumps(data))
        return JSONResponse(content={"recipe": extract_nutrition(response)}, status_code=200)
    except Exception as e:
        Logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@app.post("/validate-recipe")
async def validate_recipe(data: dict):
    try:
        rmq = RabbitMQ(RabbitMQ.QUEUE_RECIPE_VALIDATION)
        response = await rmq.request(json.dumps(data))
        return JSONResponse(content={"validated": response}, status_code=200)
    except Exception as e:
        Logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@app.post("/make-recipe")
async def validate_recipe(data: RecipeRequest):
    try:
        for i in range(0, 3):  # In case of OpenAI incorrect issue retry 3 times
            rmq = RabbitMQ(RabbitMQ.QUEUE_RECIPE_GENERATION)
            recipe = await rmq.request(data.model_dump_json())
            if not recipe:
                continue

            rmq = RabbitMQ(RabbitMQ.QUEUE_NUTRITIONAL_CALCULATOR)
            nutrition = await rmq.request(json.dumps({"recipe": recipe}))
            if not nutrition:
                continue
            for i in ['{', '}', '`', '\n', '"', 'json']:
                nutrition = str(nutrition).replace(i, '')
            nutrition = nutrition.strip(' ').replace('  ', ' ')
            recipe += '\n' + nutrition

            rmq = RabbitMQ(RabbitMQ.QUEUE_RECIPE_VALIDATION)
            validation = await rmq.request(json.dumps({"recipe": recipe}))
            if 'yes' not in validation.lower():
                continue

            result = {"recipe": recipe, "nutrition": nutrition, "validation": validation}
            MongoDB.RECIPE_COLLECTION.insert_one({"date-time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "recipe": recipe})
            return JSONResponse(content=result,
                                status_code=200)
        #data = {"recipe": "Sure! Here is a delicious vegetarian Italian pasta recipe that serves 4, is nut-free, and can be cooked in under 30 minutes:\n\n### Creamy Spinach and Tomato Fettuccine\n\n#### Ingredients:\n- 12 oz (340g) fettuccine pasta\n- 2 tablespoons olive oil\n- 3 cloves garlic, minced\n- 1 cup cherry tomatoes, halved\n- 5 cups fresh spinach (washed and roughly chopped)\n- 1 cup heavy cream (or a non-dairy cream alternative, if preferred)\n- 1/2 cup grated Parmesan cheese (or a non-dairy alternative)\n- Salt and pepper, to taste\n- 1/2 teaspoon red pepper flakes (optional)\n- Fresh basil leaves, for garnish\n\n#### Instructions:\n\n1. **Cook the Pasta**: \n   - Bring a large pot of salted water to a boil. Add the fettuccine and cook according to package instructions until al dente (usually about 8-10 minutes). Reserve about 1 cup of the pasta water, then drain the pasta and set it aside.\n\n2. **Saut\u00e9 the Garlic and Tomatoes**:\n   - In a large skillet, heat the olive oil over medium heat. Add the minced garlic and saut\u00e9 for about 30 seconds until fragrant (be careful not to burn it).\n   - Add the halved cherry tomatoes to the skillet, cook for about 3-4 minutes until they soften and begin to burst.\n\n3. **Add Spinach**:\n   - Stir in the chopped spinach and cook for another 2-3 minutes until wilted.\n\n4. **Make the Cream Sauce**:\n   - Pour in the heavy cream, stirring to combine. Allow it to simmer for 2-3 minutes to thicken slightly. If the sauce is too thick, add some reserved pasta water until desired consistency is reached.\n   - Stir in the grated Parmesan cheese and mix until melted and creamy. Season with salt, pepper, and red pepper flakes (if using).\n\n5. **Combine the Pasta and Sauce**:\n   - Add the cooked fettuccine to the skillet, tossing well to coat the pasta evenly with the sauce. Adjust seasoning as needed.\n\n6. **Serve**:\n   - Divide the creamy pasta among plates or bowls. Garnish with fresh basil leaves and an extra sprinkle of Parmesan cheese, if desired.\n\n#### Enjoy!\nThis Creamy Spinach and Tomato Fettuccine dish is flavorful, comforting, and perfect for a quick vegetarian meal. Enjoy your meal!\ncalories: 760, protein: 20, fat: 40, carbohydrates: 78, totalWeight: 680"}

        return JSONResponse(content={"recipe": "Not able to generate recipe, please check your input data"},
                            status_code=200)
    except ConnectionFailure as e:
        Logger.error(f"Error connecting to database: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error connecting to database: {str(e)}")
    except Exception as e:
        Logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


class PaginatedResponse(BaseModel):
    current_page: int
    total_pages: int
    page_size: int
    total_records: int
    data: List[str]


@app.get("/recipes", response_model=PaginatedResponse)
async def get_paginated_recipes(
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=100)):
    try:
        skip = (page - 1) * page_size
        total_records = MongoDB.RECIPE_COLLECTION.count_documents({})
        recipes_cursor = MongoDB.RECIPE_COLLECTION.find().skip(skip).limit(page_size)
        recipes = [doc['recipe'] for doc in recipes_cursor]
        print(page, skip)
        total_pages = total_records // page_size + 1
        return JSONResponse(
            status_code=200,
            content={
                "current_page": page,
                "total_pages": total_pages,
                "page_size": page_size,
                "total_records": total_records,
                "data": recipes
            })
    except ConnectionFailure as e:
        Logger.error(f"Error connecting to database: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error connecting to database: {str(e)}")
    except Exception as e:
        Logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
