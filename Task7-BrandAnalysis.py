import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import altair as alt

st.title("TASK 7: 品牌分析")
st.subheader("Author: Runsheng Xu")

# Read in the data from csv file
CT_data = pd.read_csv("https://raw.githubusercontent.com/CristoDragon/CSE5243/main/ConsumerTag(utf8).csv", encoding="utf8")
order_data = pd.read_csv("https://raw.githubusercontent.com/CristoDragon/CSE5243/main/order(utf8).csv", encoding="utf8")
person_data = pd.read_csv("https://raw.githubusercontent.com/CristoDragon/CSE5243/main/person.csv", encoding="gbk")
# Replcace all empty cells with NaN
df_CT = CT_data.replace(r'^\s*$', np.nan, regex=True)
df_order = order_data.replace(r'^\s*$', np.nan, regex=True)
df_person = person_data.replace(r'^\s*$', np.nan, regex=True)
if st.checkbox("查看原始数据: ConsumerTag(utf8).csv"):
    st.write(df_CT)
if st.checkbox("查看原始数据: order(utf8).csv"):
    st.write(df_order)
if st.checkbox("查看原始数据: person.csv"):
    st.write(df_person)



st.subheader("1. 整体分析")
# Count the number of items sold by each brand
count = df_order['品牌'].value_counts()
# Pick the top 10 excluding 其他品牌
list_count = count[1:11].tolist()
list_index = count[1:11].index[0:10].tolist()
# Create a dictionary to store the top 10 brand and their items sold
dic_count = {"品牌":list_index, "品牌销售数量":list_count}
df_count = pd.DataFrame.from_dict(dic_count)
# Join df_count with df_order so that we know 品牌销售数量 associated with each brand
df1 = pd.merge(df_order, df_count, how="left", on="品牌")
# Drop all the rows with at least 1 NA values(to pick top 10 brands with our counts)
df1 = df1.dropna()
# Create a readial chart to show how much proportionis the brand 康师傅
t = alt.TitleParams("康师傅在Top10品牌中的占比", subtitle=["图 1.1 Radial Chart"])
base = alt.Chart(df1, title=t).encode(
    theta = alt.Theta("count(品牌):Q", stack=True),
    radius = alt.Radius("count(品牌)", scale=alt.Scale(type="linear", zero=True, rangeMin=20)),
    color = "品牌:N",
    tooltip = ['品牌','count(品牌)']
)
c1 = base.mark_arc(innerRadius=20, stroke="#fff")
c2 = base.mark_text(radiusOffset=10).encode(text="品牌:N")
st.altair_chart((c1 + c2), use_container_width = True)
st.write("从图1.1中可以看到康师傅的销量在所有品牌中位列第二,仅次于七匹狼. 但是想要更全面的分析康师傅的品牌状况,需要对其 \
    下级分类详细分析,以便和同类型竞品进行比较.")


# Create a barchart to show 
# Calculate how much money sold by each of top 10 brand
df1["单项金额"] = df1["单项数量"] * df1["单项金额"]
df2 = df1.groupby(["品牌"], as_index=False)["单项金额"].sum()
df2.rename({'单项金额': '品牌销售额'}, axis=1, inplace=True)
df2["log(品牌销售额)"] = np.log(df2["品牌销售额"])
t = alt.TitleParams("销量top10品牌的销售额", subtitle=["图 1.2 Top K Items"])
barchart1 = alt.Chart(df2, title=t).mark_bar().encode(
    x = alt.X('品牌:N', sort='-y', axis=alt.Axis(labelAngle=45)),
    y = alt.Y('品牌销售额:Q'),
    color = alt.Color('log(品牌销售额):Q'),
    tooltip = ['品牌','品牌销售额']
)
st.altair_chart(barchart1, use_container_width = True)
st.write("从图1.2可以看出康师傅的销售额位列第三,结合其总体销量位列第二可推断其商品利润率有待提升.")


# Create a radial chart to show the 一级分类,二级分类,三级分类 of all items with 康师傅 brand
df1 = df_order[df_order["品牌"] == "康师傅"].copy()
df2 = pd.melt(df1, id_vars=['商品编号'], value_vars=['一级分类', '二级分类', '三级分类'], var_name='分类级别', value_name='商品类型')
# Create the selectbox to choose from 一级分类,二级分类,三级分类
option = st.selectbox("请选择分类方式", pd.Series(['一级分类', '二级分类', '三级分类']))
# Filter the data according to the selected 
filter_data = df2[df2['分类级别'] == option]
t = alt.TitleParams("康师傅各级分类销量占比", subtitle=["图 1.3 Radial Chart"])
base = alt.Chart(filter_data, title=t).encode(
    theta = alt.Theta("count(商品类型):Q", stack=True),
    radius = alt.Radius("count(商品类型)", scale=alt.Scale(type="linear", zero=True, rangeMin=20)),
    color = "商品类型:N",
    tooltip = ['商品类型','count(商品类型)']
)
c1 = base.mark_arc(innerRadius=20, stroke="#fff")
c2 = base.mark_text(radiusOffset=10).encode(text="商品类型:N")
st.altair_chart((c1 + c2), use_container_width = True)
st.write("从图1.3选择一级分类后可以看到,康师傅在售的所有商品都可以分为两类:饮料和方便素食,其中饮料占据了约三分之二的销量份额. \
    选择二级分类后可以看到,以茶饮料为首的饮料类二级产品占据了过半份额,方便速食即为即食类主食. 进一步查看三级分类可以看到 \
        即食类主食实际上是即食面类,茶饮料也主要由各种即饮茶类所构成. 至此我们便对康师傅所销售的产品分布有了大致了解.")



st.subheader("2. 顾客画像")
# Create a donut chart to show the sex composition of customers buying 康师傅
# Join df1 and df_person to know the sex information of customers buying 康师傅
df2 = pd.merge(df1, df_person, how="left", on="PID")
# Calculate the percentage of male and female in all customers buying 康师傅
count = df2['性别'].value_counts()
# Create lists to store the percentage results
list_percentage = []
for i in range(0, count.size):
    list_percentage.append(((count[i] / count.sum()) * 100).round(2).astype(str) + '%')
list_index = count.index[:].tolist()
# Create a dictionary to store the 性别 and their percentage
dic_percentage = {"性别":list_index, "性别占比":list_percentage}
df_percentage = pd.DataFrame.from_dict(dic_percentage)
# Join df2 with df_percentage so that we know 性别占比 associated with male and female
df3 = pd.merge(df2, df_percentage, how="left", on="性别")
t = alt.TitleParams("康师傅品牌顾客的性别分布", subtitle=["图 2.1 Donut Chart"])
donut1 = alt.Chart(df3, title=t).mark_arc(innerRadius=100).encode(
    theta = alt.Theta("count(性别):Q"),
    color = alt.Color("性别:N"),
    tooltip = ['性别','性别占比']
)
st.altair_chart(donut1, use_container_width = True)
st.caption("注: 移动鼠标指针以查看具体比例")
st.write("从图2.1可以看到男性顾客占比为66.3%,女性为33.7%,说明康师傅的产品整体来看以男性购买者居多")





# Create a donut chart to show the age composition of customers buying 康师傅
# Calculate the percentage of 年代 in all customers buying 康师傅
df2 = pd.merge(df1, df_CT, how="left", on="PID")
count = df2['年代'].value_counts()
# Create lists to store the percentage results
list_percentage = []
for i in range(0, count.size):
    list_percentage.append(((count[i] / count.sum()) * 100).round(2).astype(str) + '%')
list_index = count.index[:].tolist()
# Create a dictionary to store the 年代 and their percentage
dic_percentage = {"年代":list_index, "年代占比":list_percentage}
df_percentage = pd.DataFrame.from_dict(dic_percentage)
# Join df2 with df_percentage so that we know 年代占比 associated with each 年代
df3 = pd.merge(df2, df_percentage, how="left", on="年代")
t = alt.TitleParams("康师傅品牌顾客的年龄层分布", subtitle=["图 2.2 Donut Chart"])
donut1 = alt.Chart(df3, title=t).mark_arc(innerRadius=100).encode(
    theta = alt.Theta("count(年代):Q"),
    color = alt.Color("年代:N"),
    tooltip = ['年代','年代占比']
)
st.altair_chart(donut1, use_container_width = True)
st.caption("注: 移动鼠标指针以查看具体比例")
st.write("从图2.2可以看到")


