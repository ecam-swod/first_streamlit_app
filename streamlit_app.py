import streamlit
import pandas as pd
import requests
import snowflake.connector
from urllib.error import URLError

def get_fruityvice_data(fruit_choice):
    fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + fruit_choice)
    # Convert json data into a table
    fruityvice_normalized = pd.json_normalize(fruityvice_response.json())
    return fruityvice_normalized

def get_fruit_load_list(my_cnx):
    with my_cnx.cursor() as my_cur:
        my_cur.execute("select * from fruit_load_list")
        return my_cur.fetchall()
    
def insert_row_snowflake(new_fruit, my_cnx):
    with my_cnx.cursor() as my_cur:
        my_cur.execute(f"insert into fruit_load_list values ('{new_fruit}')")

streamlit.title("My Parents New Healthy Diner")

streamlit.header('Breakfast Menu')

streamlit.text('🥣 Omega 3 & Blueberry Oatmeal')
streamlit.text('🥗 Kale, Spinach & Rocket Smoothie')
streamlit.text('🐔 Hard-Boiled Free-Range Egg')
streamlit.text('🥑🍞 Avocado Toast')

streamlit.header('🍌🥭 Build Your Own Fruit Smoothie 🥝🍇')

my_fruit_list = pd.read_csv(
  "https://uni-lab-files.s3.us-west-2.amazonaws.com/dabw/fruit_macros.txt"
).set_index('Fruit')
# Let's put a pick list here so they can pick the fruit they want to include 
fruits_selected = streamlit.multiselect(
    "Pick some fruits:", 
    list(my_fruit_list.index),
    ['Avocado', 'Strawberries'],
)
fruits_to_show = my_fruit_list.loc[fruits_selected]

# Display the table on the page.
streamlit.dataframe(fruits_to_show)

streamlit.header("Fruityvice Fruit Advice!")

try:
    fruit_choice = streamlit.text_input('What fruit would you like information about?','Kiwi')
    if not fruit_choice:
        streamlit.error("Please select a fruit to get information.")
    else:
        fruityvice_normalized = get_fruityvice_data(fruit_choice)
        streamlit.dataframe(fruityvice_normalized)
except URLError as e:
    streamlit.error()
    


if streamlit.button("Get fruit load list"):
    my_cnx = snowflake.connector.connect(**streamlit.secrets["snowflake"])
    my_data_rows = get_fruit_load_list(my_cnx)
    streamlit.header("The fruit load list contains:")
    streamlit.dataframe(my_data_rows)
    

fruit_choice_2 = streamlit.text_input('What fruit would you like to add?','Jackfruit')
streamlit.write('Thanks for entering ', fruit_choice_2)

if streamlit.button("Add fruit"):
    my_cnx = snowflake.connector.connect(**streamlit.secrets["snowflake"])
    insert_row_snowflake(fruit_choice_2, my_cnx)
