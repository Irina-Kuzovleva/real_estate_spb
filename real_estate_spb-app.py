#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
#import numpy as np
import pickle
import xgboost as xgb



# In[ ]:


st.write("""
# Калькулятор стоимости квартиры

Данный калькулятор помогает рассчитать примерную рыночную стоимость квартиры в г. Санкт-Петербург (по состоянию на 2018г).

""")

st.sidebar.header('Параметры квартиры')


# In[ ]:


#Собираем данные и создаем таблицу

def user_input_features():

    cityCenters_nearest = st.sidebar.slider('Расстояние до центра города, км', 0.0,25.0,14.9)
    total_area = st.sidebar.slider('Общая площадь квартиры, м2', 13.0,120.0,33.8)
    living_area = st.sidebar.slider('Жилая площадь квартиры, м2', 14.0,90.0,17.6)
    kitchen_area = st.sidebar.slider('Площадь кухни, м2', 5.0,45.0,7.5)
    rooms = st.sidebar.slider('Кол-во комнат', 0, 10, 1)
    ceiling_height = st.sidebar.slider('Высота потолков, м', 2.0,4.0,2.56)
    balcony = st.sidebar.slider('Кол-во балконов', 0, 5, 1)
    floor = st.sidebar.slider('Этаж квартиры', 1, 35, 6) 
    floors_total = st.sidebar.slider('Всего этажей в доме', 1,35,9)
    is_apartment = st.sidebar.selectbox('Является ли апартаментами',('Нет','Да'))
    studio = st.sidebar.selectbox('Является ли студией',('Нет','Да'))
    open_plan = st.sidebar.selectbox('Со свободной планировкой',('Нет','Да'))
      
    
    data = {'total_area': total_area,
            'rooms': rooms,
            'ceiling_height': ceiling_height,
            'floors_total': floors_total,
            'living_area': living_area,
            'floor': floor,
            'is_apartment': is_apartment,
            'studio': studio,
            'open_plan': open_plan,
            'kitchen_area': kitchen_area,
            'balcony': balcony,
            'cityCenters_nearest': cityCenters_nearest
           }
    
    features = pd.DataFrame(data, index=[0])
    return features
    
input_df = user_input_features()


# In[ ]:


#Обработаем переменные и создадим дополнительные
def apartment(is_apartment):
    
    if is_apartment == 'Да':
        return True
    else:
        return False

    
def studio(studio):
    
    if studio == 'Да':
        return True
    else:
        return False
    
def plan(open_plan):
    
    if open_plan == 'Да':
        return True
    else:
        return False
    
def categorize_floors(row):
    floors_total = row['floors_total']
    floor = row['floor']
    
    if (floor == 1):
        return 'первый'
    if (floor == floors_total):
        return 'последний'
    
    return 'другой'
    
    
input_df['is_apartment'] = input_df.apply(lambda row: apartment(row['is_apartment']), axis=1)
input_df['studio'] = input_df.apply(lambda row: studio(row['studio']), axis=1)
input_df['open_plan'] = input_df.apply(lambda row: plan(row['open_plan']), axis=1)

input_df['cityCenters_nearest'] = input_df['cityCenters_nearest'] * 1000

input_df['floor_category'] = input_df.apply(categorize_floors, axis=1)


# In[ ]:


#Финальная версия тестовой выборки
real_estate_spb_raw = pd.read_csv('https://raw.githubusercontent.com/Irina-Kuzovleva/real_estate_spb/master/real_estate_spb_cleaned.csv')
df = pd.concat([input_df,real_estate_spb_raw],axis=0)
df = df[:1]


# In[ ]:


#Загружаем модель и делаем предсказания
load_real_estate_spb = pickle.load(open('real_estate_spb.pkl', 'rb'))

prediction = load_real_estate_spb.predict(df)
prediction_final = round(prediction[0])
prediction_final = '{0:,}'.format(prediction_final).replace(',', ' ')

#prediction = str(prediction)[::-1]
#prediction = ' '.join(prediction[i:i+3] for i in range(0, len(prediction), 3))[::-1]

prediction_m2 = prediction[0] / df['total_area'][0]
prediction_m2_final = round(prediction_m2)
prediction_m2_final = '{0:,}'.format(prediction_m2_final).replace(',', ' ')

#st.markdown("""
#<style>
#.big-font {
#    font-size:100px !important;
#}
#</style>
#""", unsafe_allow_html=True)

#st.subheader('Рыночная цена квартиры')
#st.write(prediction_final)

st.subheader('Рыночная цена квартиры')
st.write(prediction_final)

st.subheader('Цена за м2')
st.write(prediction_m2_final)

