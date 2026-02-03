import pandas as pd
import streamlit as st
import millify as mf
import matplotlib.pyplot as plt
import plotly.graph_objects as go


df = pd.read_csv('data.csv')


####Data cleaning####

#Order date, ship Date -- > Date
df_cleared = df
df_cleared['Order Date'] = pd.to_datetime(df_cleared['Order Date'], format='%d/%m/%Y %H:%M:%S')
df_cleared['Ship Date'] = pd.to_datetime(df_cleared['Ship Date'], format='%d/%m/%Y')


# year extract
year_values = df_cleared['Order Date'].dt.year
df_cleared.insert(2, 'Year', year_values)


#shipdate + 2 year

df_cleared['Ship Date'] = df_cleared['Ship Date'] + pd.DateOffset(years=2)


#days to ship kiszámítása 
Delivery_time = df_cleared['Ship Date'] - df_cleared['Order Date']
df_cleared.insert(4, 'Days_to_ship', Delivery_time) 

#postal code kitöltés alakítás
df_cleared['Postal Code'].fillna(27217.0, inplace=True)

df_cleared['Postal Code'] = df_cleared['Postal Code'].astype(int)

# Sales kerekítés 2-re és átnevezés Price-ra
df_cleared['Sales'] = df_cleared['Sales'].round(2)

df_cleared.rename(columns={'Sales': 'Price'}, inplace=True)

# Profit kerekítése kettő tizedesre 
df_cleared['Profit'] = df_cleared['Profit'].round(2) 


                                                ####Dashboard layout####

            ###Sidebar

st.sidebar.title('Filters')

if st.sidebar.button("Clear all Filters"):
    st.session_state.selected_year = None
    st.session_state.Quarter = None
    st.session_state.Region = None
    st.session_state.State = None
    st.session_state.City = None
    st.session_state.Ship_Mode = None
    st.session_state.Segment = None
    st.session_state.Category = None
    st.session_state.Subcategory = None
    st.rerun()


        ##évek

min_year = int(df_cleared["Year"].min())
max_year = int(df_cleared["Year"].max())

if st.session_state.get("selected_year") is None:
    st.session_state.selected_year = (min_year, max_year)


selected_year = st.sidebar.slider("Year", min_year, max_year, st.session_state.selected_year, key='selected_year')


        ##negyedévek
df_cleared["Quarter"] = df_cleared["Order Date"].dt.quarter
quarter_labels = ["Q1", "Q2", "Q3", "Q4"]

if st.session_state.get("Quarter") is None:
    st.session_state.Quarter = quarter_labels


selected_quarters = st.sidebar.multiselect("Quarter", quarter_labels, default=st.session_state.Quarter, key='Quarter')

    #érték adása a labelhez
quarter_map = {"Q1": 1, "Q2": 2, "Q3": 3, "Q4": 4}

selected_quarter_numbers = [quarter_map[q] for q in selected_quarters]

    #szűrés
df_filtered = df_cleared[(df_cleared["Year"].between(selected_year[0], selected_year[1])) & (df_cleared["Quarter"].isin(selected_quarter_numbers))]

    #Régió

region_options = list(df_cleared['Region'].unique()) #filterben kivet régiók

if st.session_state.get("Region") is None:
    st.session_state.Region = region_options
else:
    if not set(st.session_state.Region).issubset(region_options):
        st.session_state.Region = region_options

Region = st.sidebar.multiselect('Region', df_cleared['Region'].unique(), default = st.session_state.Region, key='Region')

            #Államok és városok
        #Állam
state_options = list(df_cleared['State'].unique()) #listázod a reset miatt

if st.session_state.get("State") is None:
    st.session_state.State = state_options
else:
    if not set(st.session_state.State).issubset(state_options):
        st.session_state.State = state_options

state = st.sidebar.multiselect('State', df_cleared['State'].unique(), default=st.session_state.State, key='State')

        #Város
       
state_map = df_cleared.groupby('State')['City'].unique().apply(list).to_dict()
    
    #listába gyűjtöm a várost a kiválasztott álllamhoz
available_city = []
for c in state:
    available_city.extend(state_map[c])


if st.session_state.get("City") is None:
    st.session_state.City = available_city
else:
    if not set(st.session_state.City).issubset(available_city):
        st.session_state.City = available_city


city = st.sidebar.multiselect('City', available_city, default=st.session_state.City, key='City')

     # összekötés ha az egyik üres legyen a másik is
if len(city) == 0:
    ste = []
else: ste = [st for st, ctys in state_map.items() if any(cty in ctys for cty in city)] 
        
        #ship mode
ship_options = list(df_cleared['Ship Mode'].unique())

if st.session_state.get("Ship_Mode") is None:
    st.session_state.Ship_Mode = ship_options
else:
    if not set(st.session_state.Ship_Mode).issubset(ship_options):
        st.session_state.Ship_Mode = ship_options
      
Ship_Mode = st.sidebar.multiselect('Ship Mode', df_cleared['Ship Mode'].unique(), default = st.session_state.Ship_Mode, key='Ship_Mode')

        #Segment
segment_options = list(df_cleared['Segment'].unique())

if st.session_state.get("Segment") is None:
    st.session_state.Segment = segment_options
else:
    if not set(st.session_state.Segment).issubset(segment_options):
        st.session_state.Segment = segment_options


Segment = st.sidebar.multiselect('Segment', df_cleared['Segment'].unique(), default = st.session_state.Segment, key = 'Segment')


        ##szórakozás a sub és a category filterrel hogy automatikusan kiszűrje a sub-ot is ha a categoryt veszek ki
    #listázom a subot, és rákötöm category szerint kulcsra 

    ##category filter reset

category_options = list(df_cleared['Category'].unique())

if st.session_state.get("Category") is None:
    st.session_state.Category = category_options
else:
    if not set(st.session_state.Category).issubset(category_options):
        st.session_state.Category = category_options

    
category_map = df_cleared.groupby("Category")["Sub-Category"].unique().apply(list).to_dict()

    #multiselect
category = st.sidebar.multiselect('Category', df_cleared['Category'].unique(), default=st.session_state.Category, key='Category')

    # listázom  az összes subcategory-t a kiválasztott kategóriákhoz
available_sub = []
for sub in category:
    available_sub.extend(category_map[sub])

    #sub filterem + clear all
if st.session_state.get("Subcategory") is None:
    st.session_state.Subcategory = available_sub
else:
    if not set(st.session_state.Subcategory).issubset(available_sub):
        st.session_state.Subcategory = available_sub

    #multiselect
Subcategory = st.sidebar.multiselect('Subcategory', available_sub, default = st.session_state.Subcategory, key='Subcategory' )

    # összekötés ha az egyik üres legyen a másik is
if len(Subcategory) == 0:
    category = []
else: category = [cat for cat, subs in category_map.items() if any(sub in subs for sub in Subcategory)]

### FILTER 

df_filtered = df_cleared[
    (df_cleared["Year"].between(selected_year[0], selected_year[1]))
    & (df_cleared["Quarter"].isin(selected_quarter_numbers))
    & (df_cleared["Region"].isin(Region))
    & (df_cleared["State"].isin(state))
    & (df_cleared["City"].isin(city))
    & (df_cleared["Ship Mode"].isin(Ship_Mode))
    & (df_cleared["Segment"].isin(Segment))
    & (df_cleared["Category"].isin(category))
    & (df_cleared["Sub-Category"].isin(Subcategory))]







                                ######DASHBOARD

#teljes oldal szélesség
st.set_page_config(layout="wide")

st.markdown(
    """
    <h1 style='text-align: center;'>
        Superstore 
        <span style='color:#B22234;'>U</span>
        <span style='color:#FFFFFF;'>S</span>
        <span style='color:#3C3B6E;'>A</span>
    </h1>
    """,
    unsafe_allow_html=True)

total_sales = df_filtered.groupby('Order ID')['Price'].sum().sum()
total_profit = df_filtered.groupby('Order ID')['Profit'].sum().sum()
number_of_orders = df_filtered['Order ID'].nunique() #==nun unique


###key 

col1, col2, col3 = st.columns(3)

with col1:
    st.metric('Total Sales', f'${mf.millify(total_sales, precision=2)}')
with col2:
    st.metric('Total Profit', f'${mf.millify(total_profit, precision=2)}')
with col3:
    st.metric('Total Orders', number_of_orders)


        ###10 product by sale 
col4, col5 = st.columns(2)

with col4:
    df_filtered['Revenue'] = df_filtered['Quantity'] * df_filtered['Price'] * df_filtered['Discount']
    top_sales = df_filtered.groupby('Product Name')['Revenue'].sum().sort_values(ascending=False).head(10)

    st.metric('Top Product by Sales', top_sales.index[0])

    fig, ax = plt.subplots(figsize=[10,6])
    bars = ax.barh(top_sales.index, top_sales, color='steelblue')
    ax.set_xlabel("Total Sales")
    ax.set_ylabel("Product Name")
    ax.set_title("Top 10 Products by Sales")
    ax.invert_yaxis() #megfordítom a sorrendet hogy a legnagyobb legyen felül
    ax.bar_label(bars, fmt="%.0f")
    #ax.bar_label(bars, labels=top_sales.index)
    st.pyplot(fig)

        ### 10 products by profit

with col5:
    top_profit_product = df_filtered.groupby('Product Name')['Profit'].sum().sort_values(ascending=False).head(10)

    st.metric('Top Product by Profit', top_profit_product.index[0])


    fig, ax = plt.subplots(figsize=[8.5,6])
    bars =ax.barh(top_profit_product.index, top_profit_product, color='green')
    ax.set_xlabel('Profit')
    ax.set_ylabel('Product Name')
    ax.set_title("Top 10 Product by Profit")
    ax.invert_yaxis()
    ax.bar_label(bars, fmt="%.0f")
    st.pyplot(fig)

            ### AVG Shipping 

col6 , col7 = st.columns(2)

with col6: 
    min_days = df_filtered["Days_to_ship"].min().days
    max_days = df_filtered["Days_to_ship"].max().days
    avg_days = df_filtered["Days_to_ship"].dt.days.mean()

    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = avg_days,
        title = {"text": "Average Days to Ship"},
        gauge = {
            "axis": {"range": [min_days, max_days]},
            "bar": {"color": "#D60000"},
            "steps": [
                {"range": [min_days, avg_days], "color": "#20317A"},
                {"range": [avg_days, max_days], "color": "#20317A"}]}))
    fig.update_layout(
    width=700, #streamlites 700
    height=500, #steamlites 500
    margin=dict(l=20, r=20, t=40, b=20))

    st.plotly_chart(fig, use_container_width=False)


        
            ### Sales trends

with col7:
    sales_by_state = df_filtered.groupby('Region')['Price'].sum()
    fig, ax = plt.subplots(figsize=(2, 6))
    values = sales_by_state.values
    labels = sales_by_state.index


    wedges, texts, autotexts = ax.pie(
        values,
        labels=None,                 
        autopct='%1.1f%%',           
        pctdistance=0.7,             
        startangle=90,
        textprops={'fontsize': 8}
    )


    ax.legend(
        wedges,
        labels,
        title="Reigon",
        loc="center left",
        bbox_to_anchor=(1, 0.5),
        fontsize=8
    )

    ax.set_title("Sales by Region", fontsize=8)

    st.pyplot(fig)
    



Sales_trends = df_filtered.groupby(['Category', 'Year'])['Revenue'].sum().reset_index()


pivot = Sales_trends.pivot(index='Year', columns='Category', values='Revenue')

fig, ax = plt.subplots(figsize=(7,4))
pivot.plot(kind='bar', ax=ax)

ax.set_xlabel('Year')
ax.set_ylabel('Revenue')
ax.set_title('Sales Trends by Category')
ax.legend(title='Category', fontsize=8 , title_fontsize=10, loc='upper center')

st.pyplot(fig)