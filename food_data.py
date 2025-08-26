# Basic food categories for quick identification
BASIC_FOODS = [
    'apple', 'banana', 'orange', 'grape', 'strawberry', 'blueberry', 'raspberry',
    'chicken', 'beef', 'pork', 'fish', 'salmon', 'tuna', 'shrimp',
    'rice', 'pasta', 'bread', 'potato', 'sweet potato', 'quinoa',
    'broccoli', 'spinach', 'kale', 'carrot', 'tomato', 'onion', 'garlic',
    'milk', 'cheese', 'yogurt', 'egg', 'butter', 'olive oil', 'coconut oil',
    'almond', 'walnut', 'peanut', 'cashew', 'sunflower seed', 'chia seed',
    'oatmeal', 'cereal', 'granola', 'honey', 'maple syrup', 'sugar',
    'salt', 'pepper', 'basil', 'oregano', 'thyme', 'rosemary'
]

# Common foods database with nutritional information
COMMON_FOODS_DB = {
    'apple': {
        'name': 'Apple',
        'brand': 'Generic',
        'calories': 95,
        'protein': 0.5,
        'carbs': 25,
        'fat': 0.3,
        'fiber': 4.4,
        'sugar': 19,
        'sodium': 2
    },
    'banana': {
        'name': 'Banana',
        'brand': 'Generic',
        'calories': 105,
        'protein': 1.3,
        'carbs': 27,
        'fat': 0.4,
        'fiber': 3.1,
        'sugar': 14,
        'sodium': 1
    },
    'chicken breast': {
        'name': 'Chicken Breast',
        'brand': 'Generic',
        'calories': 165,
        'protein': 31,
        'carbs': 0,
        'fat': 3.6,
        'fiber': 0,
        'sugar': 0,
        'sodium': 74
    },
    'salmon': {
        'name': 'Salmon',
        'brand': 'Generic',
        'calories': 208,
        'protein': 25,
        'carbs': 0,
        'fat': 12,
        'fiber': 0,
        'sugar': 0,
        'sodium': 59
    },
    'brown rice': {
        'name': 'Brown Rice',
        'brand': 'Generic',
        'calories': 216,
        'protein': 4.5,
        'carbs': 45,
        'fat': 1.8,
        'fiber': 3.5,
        'sugar': 0.4,
        'sodium': 10
    },
    'quinoa': {
        'name': 'Quinoa',
        'brand': 'Generic',
        'calories': 222,
        'protein': 8.1,
        'carbs': 39,
        'fat': 3.6,
        'fiber': 5.2,
        'sugar': 1.6,
        'sodium': 13
    },
    'broccoli': {
        'name': 'Broccoli',
        'brand': 'Generic',
        'calories': 55,
        'protein': 3.7,
        'carbs': 11,
        'fat': 0.6,
        'fiber': 5.2,
        'sugar': 2.6,
        'sodium': 33
    },
    'spinach': {
        'name': 'Spinach',
        'brand': 'Generic',
        'calories': 23,
        'protein': 2.9,
        'carbs': 3.6,
        'fat': 0.4,
        'fiber': 2.2,
        'sugar': 0.4,
        'sodium': 79
    },
    'sweet potato': {
        'name': 'Sweet Potato',
        'brand': 'Generic',
        'calories': 103,
        'protein': 2,
        'carbs': 24,
        'fat': 0.2,
        'fiber': 3.8,
        'sugar': 7,
        'sodium': 41
    },
    'greek yogurt': {
        'name': 'Greek Yogurt',
        'brand': 'Generic',
        'calories': 59,
        'protein': 10,
        'carbs': 3.6,
        'fat': 0.4,
        'fiber': 0,
        'sugar': 3.2,
        'sodium': 36
    },
    'egg': {
        'name': 'Egg',
        'brand': 'Generic',
        'calories': 70,
        'protein': 6,
        'carbs': 0.6,
        'fat': 5,
        'fiber': 0,
        'sugar': 0.4,
        'sodium': 70
    },
    'almonds': {
        'name': 'Almonds',
        'brand': 'Generic',
        'calories': 164,
        'protein': 6,
        'carbs': 6,
        'fat': 14,
        'fiber': 3.5,
        'sugar': 1.2,
        'sodium': 0
    },
    'oatmeal': {
        'name': 'Oatmeal',
        'brand': 'Generic',
        'calories': 150,
        'protein': 5,
        'carbs': 27,
        'fat': 3,
        'fiber': 4,
        'sugar': 1,
        'sodium': 115
    },
    'avocado': {
        'name': 'Avocado',
        'brand': 'Generic',
        'calories': 160,
        'protein': 2,
        'carbs': 9,
        'fat': 15,
        'fiber': 7,
        'sugar': 0.7,
        'sodium': 7
    },
    'tomato': {
        'name': 'Tomato',
        'brand': 'Generic',
        'calories': 22,
        'protein': 1.1,
        'carbs': 4.8,
        'fat': 0.2,
        'fiber': 1.2,
        'sugar': 3.2,
        'sodium': 5
    },
    'carrot': {
        'name': 'Carrot',
        'brand': 'Generic',
        'calories': 41,
        'protein': 0.9,
        'carbs': 10,
        'fat': 0.2,
        'fiber': 2.8,
        'sugar': 4.7,
        'sodium': 69
    },
    'milk': {
        'name': 'Milk',
        'brand': 'Generic',
        'calories': 103,
        'protein': 8,
        'carbs': 12,
        'fat': 2.4,
        'fiber': 0,
        'sugar': 12,
        'sodium': 107
    },
    'cheese': {
        'name': 'Cheese',
        'brand': 'Generic',
        'calories': 113,
        'protein': 7,
        'carbs': 0.4,
        'fat': 9,
        'fiber': 0,
        'sugar': 0.1,
        'sodium': 176
    },
    'olive oil': {
        'name': 'Olive Oil',
        'brand': 'Generic',
        'calories': 119,
        'protein': 0,
        'carbs': 0,
        'fat': 14,
        'fiber': 0,
        'sugar': 0,
        'sodium': 0
    },
    'honey': {
        'name': 'Honey',
        'brand': 'Generic',
        'calories': 64,
        'protein': 0.1,
        'carbs': 17,
        'fat': 0,
        'fiber': 0,
        'sugar': 17,
        'sodium': 1
    },
    'bread': {
        'name': 'Bread',
        'brand': 'Generic',
        'calories': 79,
        'protein': 3.1,
        'carbs': 15,
        'fat': 1,
        'fiber': 1.9,
        'sugar': 1.4,
        'sodium': 149
    }
}
