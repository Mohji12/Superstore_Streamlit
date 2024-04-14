import pandas as pd 
import streamlit as st 
import plotly.express as px 
import os
import warnings 
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Super Market", page_icon=":bar_chart",layout='wide')
st.title(" :bar_chart: Super Market EDA")

st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)

f1 =st.file_uploader(":file_folder: Upload a File",type=(["csv","txt","xlsx","xls"]))
if f1 is not None:
    filename = f1.name
    st.write(filename)
    df = pd.read_csv(filename, encoding="ISO-8859-1")
else:
    os.chdir(r"D:\StreamDash")
    df = pd.read_csv("Sample - Superstore.csv",encoding="ISO-8859-1")

col1,col2 = st.columns((2))

df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
df['Order Date'] = df['Order Date'].dt.strftime("%m/%d/%Y")

StartDate = pd.to_datetime(df['Order Date']).min()
EndDate = pd.to_datetime(df['Order Date']).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", StartDate))

with col2:
    
    date2 = pd.to_datetime(st.date_input("End Date", EndDate))


st.sidebar.header("Choose Your Filter")

# For region
region = st.sidebar.multiselect("Pick Your Region", df['Region'].unique())

if not region:
    df2 = df.copy()
else:
    df2 = df[df["Region"].isin(region)]

# Create for State
state = st.sidebar.multiselect("Pick the State",df2["State"].unique())

if not state:
    df3 = df2.copy()
else:
    df3 = df2[df2["State"].isin(state)]

# Create for City

city = st.sidebar.multiselect("Pick The City",df3['City'].unique())




# filter data based on Region, State and City

if not region and not state and not city:
    filter_df = df
elif not state and not city:
    filter_df = df[df['Region'].isin(region)]
elif not region and not city:
    filter_df = df[df['State'].isin(state)]
elif state and city:
    filter_df = df3[df["State"].isin(state) & df3["City"].isin(city)]
elif region and city:
    filter_df = df3[df["Region"].isin(region) & df3["City"].isin(city)]
elif region and state:
    filter_df = df3[df["State"].isin(region) & df3["State"].isin(state)]
elif city:
    filter_df = df3[df3["City"].isin(city)]
else:
    filter_df = df3[df3["Region"].isin(region) & df3["State"].isin(state) & df3['City'].isin(city)]


category_df = filter_df.groupby(by = ["Category"], as_index = False)["Sales"].sum()
region_df = filter_df.groupby(by = ["Region"], as_index = False)["Sales"].sum()

with col1:
    st.subheader("Category Wise Sales")
    fig = px.bar(category_df, x = 'Category', y = 'Sales', text= ['${:,.2f}'.format(x) for x in category_df["Sales"]])
    st.plotly_chart(fig,use_container_width=True, height = 200)

with col2:
    st.subheader("Region Wise Sales")
    fig = px.pie(region_df, values="Sales", names= "Region", hole = 0.5)
    fig.update_traces(text = filter_df["Region"], textposition = "outside")
    st.plotly_chart(fig, use_container_width= True)


Ship = filter_df.groupby(by = ["Ship Mode"], as_index = False)["Sales"].sum()

cl1,cl2,cl3 = st.columns((3))

with cl1:
    with st.expander("Category_ViewData"):

        st.write(category_df.style.background_gradient(cmap="Blues"))
        csv = category_df.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name="Category.csv", mime="text/csv",
                       help = "Click here to download the data")

with cl2:
    with st.expander("Region_ViewData"):
        region = filter_df.groupby(by = "Region", as_index = False)["Sales"].sum()
        st.write(region.style.background_gradient(cmap="Oranges"))
        st.download_button("Download Data" ,data = csv, file_name="Region.csv",mime="text/csv",
                           help="Click to download the data")
        
with cl3:
    with st.expander("Ship_Sales_Data"):
        st.write(Ship.style.background_gradient(cmap="Greens"))
        csv = Ship.to_csv(index = False).encode('utf-8')
        st.download_button('Download Data', data = csv, file_name="Ship.csv",mime="text\cssv",
                           help='Click to download the data')

filter_df['Order Date'] = pd.to_datetime(filter_df['Order Date'])



filter_df['month_year'] = filter_df['Order Date'].dt.to_period("M")


linechart = pd.DataFrame(filter_df.groupby(filter_df['month_year'].dt.strftime("%Y : %b"))['Sales'].sum()).reset_index()
fig2 = px.line(linechart, x = 'month_year', y ="Sales", labels={"Sales":"Amount"},height=500,width=1000,template="gridon")
st.plotly_chart(fig2,use_container_width=True)

with st.expander("View Data for the Time Series"):
    st.write(linechart.T.style.background_gradient(cmap='Greens'))

# Tree plot based on region,Category and Sub-Category
#st.plotly_chart(fig3,use_container_width=True)

chart1,chart2 = st.columns((2))
with chart1:
    st.subheader('Segment Wise Sales')
    fig = px.pie(filter_df,values = 'Sales',names = "Segment",template = "plotly_dark")
    fig.update_traces(text = filter_df['Segment'],textposition = "inside")
    st.plotly_chart(fig,use_container_width=True)
with chart2:
    st.subheader('Category Wise Sales')
    fig = px.pie(filter_df,values = 'Sales',names = "Category",template = "plotly_dark")
    fig.update_traces(text = filter_df['Category'],textposition = "inside")
    st.plotly_chart(fig,use_container_width=True)

import plotly.figure_factory as ff

st.subheader(":point_right: Month wise sub-category sales summary")

with st.expander('Summary_Table'):
    df_sample = df[0:5][["Region",'State','City','Category','Sales','Profit','Quantity']]
    fig = ff.create_table(df_sample,colorscale="Cividis")
    st.plotly_chart(fig,use_container_width=True)

    st.markdown('Month Wise sub-Category tables')
    filter_df['Month'] = filter_df['Order Date'].dt.month_name()
    sub_category_year = pd.pivot_table(data=filter_df,values="Sales",index=['Sub-Category'],columns="Month")
    st.write(sub_category_year.style.background_gradient(cmap="plasma"))

data1 = px.scatter(filter_df, x = "Sales",y = "Profit", size = "Quantity")
data1['layout'].update(title="Relationship between Sales and Profit Using Scatter Plot",titlefont = dict(size=20),xaxis = dict(title="sales",titlefont = dict(size=20)),
                       yaxis = dict(title="Profit",titlefont = dict(size=20)))
st.plotly_chart(data1,use_container_width=True)
