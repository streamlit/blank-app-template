import streamlit as st

st.title("Recipe Ingredients Analysis")
st.write(
    "Diego Ferrer, Seungwoo An, Jackson Muncy."
)

st.header("Chapter 1: Seungwoo An")
st.write("This chapter provides an overview of the project and objectives.")

code = """
# Step 1: Install necessary libraries
!pip install datasets pandas matplotlib seaborn

# Step 2: Import required libraries
from datasets import load_dataset
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Step 3: Load the dataset from Hugging Face
dataset = load_dataset("AkashPS11/recipes_data_food.com", split="train")

# Step 4: Convert the dataset to a pandas DataFrame for easier manipulation
df = dataset.to_pandas()

# Display the column names to check the structure
print("Column Names in Dataset:")
print(df.columns)

# Step 5: Check for the column that contains calorie data
# Update the names for ingredients and calories
ingredients_column = 'RecipeIngredientParts'
calories_column = 'Calories'

# Drop rows with missing calorie data
df = df.dropna(subset=[calories_column])

# Display ingredients and calories columns to verify
print(f"\nIngredients and {calories_column} Columns:")
print(df[[ingredients_column, calories_column]].head())

# Step 6: Feature Engineering on Ingredients
# Calculate the number of ingredients as a simple feature
df['ingredient_count'] = df[ingredients_column].apply(lambda x: len(x))

# Step 7: Correlation Analysis
# Calculate correlation between ingredient count and calories
correlation = df[['ingredient_count', calories_column]].corr()
print("Correlation Matrix:")
print(correlation)

# Step 8: Visualization
# Create a scatter plot to visualize the relationship
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x='ingredient_count', y=calories_column)
plt.title("Ingredient Count vs. Calories")
plt.xlabel("Number of Ingredients")
plt.ylabel("Calories")
plt.show()

# Create a heatmap for correlation
plt.figure(figsize=(6, 4))
sns.heatmap(correlation, annot=True, cmap="coolwarm", fmt=".2f")
plt.title("Correlation Heatmap")
plt.show()



"""

st.code(code, language='python')  # Use 'language' for syntax highlighting

st.write("Here's a scatterplot and a heatmap that could result from the analysis.")
st.image("SA1.png", caption="Scatterplot", use_column_width=True)
st.image("SA2.png", caption="Heatmap", use_column_width=True)


code = """

# Step 1: Install the necessary library (if not already installed)
!pip install datasets matplotlib

# Step 2: Import libraries
from datasets import load_dataset
import matplotlib.pyplot as plt

# Step 3: Load the dataset
dataset = load_dataset("Shengtao/recipe", split="train")

# Step 4: Convert dataset to a DataFrame for easier manipulation (if needed)
import pandas as pd
df = pd.DataFrame(dataset)

# Step 5: Sort the DataFrame by the 'calories' column in descending order and select the top 10
top_10_highest_calories = df.nlargest(10, 'calories')[['title', 'calories']]

# Step 6: Plot the bar graph
plt.figure(figsize=(10, 6))
plt.bar(top_10_highest_calories['title'], top_10_highest_calories['calories'], color='salmon')
plt.xticks(rotation=45, ha="right")
plt.xlabel("title")
plt.ylabel("Calories")
plt.title("Top 10 Foods with Highest Calories")
plt.tight_layout()
plt.show()
"""

st.code(code, language='python')  # Use 'language' for syntax highlighting
st.image("SA3.png", caption="Bar Chart", use_column_width=True)


code = """
# Step 1: Extract ingredients for the top 10 foods
top_10_ingredients = df.nlargest(10, 'calories')['ingredients']

# Step 2: Clean the ingredients by splitting by semicolon and removing extra spaces
all_ingredients = []
for ingredients_list in top_10_ingredients:
    ingredients = [ingredient.strip().lower() for ingredient in ingredients_list.split(';')]
    all_ingredients.extend(ingredients)

# Step 3: Count the frequency of each ingredient
from collections import Counter
ingredient_counts = Counter(all_ingredients)

# Step 4: Prepare the data for plotting
ingredient_data = ingredient_counts.most_common(10)

# Step 5: Create the bar chart for the top 10 most common ingredients
ingredients, counts = zip(*ingredient_data)

plt.figure(figsize=(10, 6))
plt.bar(ingredients, counts, color='lightcoral')
plt.xticks(rotation=45, ha="right")
plt.xlabel("Ingredients")
plt.ylabel("Frequency")
plt.title("Top 10 Most Common Ingredients in High-Calorie Foods")
plt.tight_layout()
plt.show()
"""
st.code(code, language='python')  # Use 'language' for syntax highlighting
st.image("SA4.png", caption="Bar Chart", use_column_width=True)
