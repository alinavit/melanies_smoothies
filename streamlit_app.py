# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Write directly to the app
st.title("Customize Your Smoothie! :cup_with_straw:")
st.write(
    """
    Choose the fruits you want in your custom Smoothie!
    """
)

name_of_order = st.text_input("Name of Smoothie")
st.write("The name on your Smoothie will be: ", name_of_order)






#session = get_active_session()


from snowflake.snowpark import Session

@st.cache_resource
def create_snowpark_session():
    config = {
        "account": "hqb23554",
        "user": "alivit",
        "password": "Welcome@2025!",
        "role": "ACCOUNTADMIN",
        "warehouse": "COMPUTE_WH",
        "database": "SMOOTHIES",
        "schema": "PUBLIC"
    }
    return Session.builder.configs(config).create()

# Use the session in your Streamlit app
session = create_snowpark_session()

####################################################


my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()
st.dataframe(pd_df)

#st.write(ingredients_list)
#st.text(ingredients_list)

ingredients_list = st.multiselect("Choose up to 5 ingredients:", my_dataframe, max_selections=5)
time_to_insert = st.button('Submit Order')


if ingredients_list:
    ingredients_string = ''
    
    for i in ingredients_list:
        ingredients_string += i + ' '

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == i, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', i,' is ', search_on, '.')
        
        st.subheader(i + 'Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on )
        st_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)



    my_insert_stmt = """ insert into smoothies.public.orders(NAME_ON_ORDER, ingredients) 
                            values ('"""+ name_of_order + """','""" + ingredients_string +  """')"""


    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
