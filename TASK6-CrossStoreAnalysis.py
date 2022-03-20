import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import altair as alt
from vega_datasets import data

st.title("TASK 6: 跨店分析")
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



st.subheader("1. 每笔订单金额的分析")
# Add a column to store 总金额 for each 订单编号
df_order["总金额"] = df_order["单项数量"] * df_order["单项金额"]
df1 = df_order.groupby(["订单编号", "门店名称"], as_index=False)["总金额"].sum()
df1["log(总金额)"] = np.log(df1["总金额"])
# Create a histogram to show the distribution of 销售额 generally
t = alt.TitleParams("每笔订单金额的总体分布状况", subtitle=["图 1.1 Histogram"])
hist1 = alt.Chart(df1, title=t).mark_bar(
    opacity=0.3,
    binSpacing=0
).encode(
    alt.X('log(总金额):Q', bin=alt.Bin(maxbins=100)),
    alt.Y('count()', stack=None),
    # strokeDash="门店名称:N",
    tooltip = ['总金额']
)
st.altair_chart(hist1.interactive(), use_container_width = True)
st.write("从图1.1的直方图可以看到,每笔订单消费金额总体呈现为右偏的正态分布.")

# Create a line chart to show the distribution of 销售额 by each store
t = alt.TitleParams("各门店每笔订单金额的分布状况对比", subtitle=["图 1.2 Line Chart"])
line1 = alt.Chart(df1, title=t).mark_line().encode(
    alt.X('log(总金额):Q'),
    alt.Y('count()'),
    alt.Color('门店名称:N'),
    # strokeDash="门店名称:N",
    tooltip = ['总金额','门店名称']
)
st.altair_chart(line1.interactive(), use_container_width = True)
st.caption("注:缩放该图以查看每个消费金额所对应的具体数量")
st.write("从图1.2中可以发现,三家门店A,B和C的每个订单消费金额的分布状况基本一致,可以近似看作是右偏的正态分布,其中大部分的订单金额都 \
    集中在1元~16元这个区间,其余的数量不论是高金额(>16元)还是低金额(<1元)都比较少. 虽然三家门店的订单金额整体趋势相同,但是具体的 \
        数量还是有所差别. 例如我们可以看到,对于大多数订单金额所对应的数量,基本符合B > A > C的规律. 结合以上这些特点可知, \
            A,B,C三家门店在顾客的消费特征上并无显著差别,大多数人每笔订单消费的金额都固定在1~16元这个区间,不同之处在于 \
                B的客流要大于A的客流,C的客流最小. 所以在营销策略上三家店可以保持一致,因为主要客户的消费能力都差不多.")

# Create a pyramid plot to show 平均每单购买金额 by male and female
# Add a column to store at which hour the order is completed
df2 = pd.merge(df_CT, df_order[['PID', '交易时间', '门店名称']], how="left", on="PID")
df2["交易小时"] = [int(x[11:13]) for x in df2['交易时间']] 
df2["log(平均每单购买金额)"] = np.log(df2["平均每单购买金额"])
df2["log(距离上次光顾时间)"] = np.log(df2["距离上次光顾时间"])
df2["log(平均每单购买数量)"] = np.log(df2["平均每单购买数量"])
df2.rename({'性别': 'gender', '交易小时': 'hour'}, axis=1, inplace=True)
# Create a slider to select between different hours
slider = alt.binding_range(min=0, max=23, step=1)
select_hour = alt.selection_single(name='hour', fields=['hour'], bind=slider, init={'hour': 0})
# Create the baseplot
base = alt.Chart(df2).add_selection(
    select_hour
).transform_filter(
    select_hour
).properties(
    width=250
)
color_scale = alt.Scale(domain=['male', 'female'], range=['#1f77b4', '#e377c2'])
# Create the left plot
left = base.transform_filter(
    alt.datum.gender == 'female'
).encode(
    y = alt.Y('门店名称:N', axis=None),
    x = alt.X('平均每单购买金额:Q', sort=alt.SortOrder('descending')),
    color=alt.Color('gender:N', scale=color_scale, legend=None)
).mark_bar().properties(title='女性客户')
# Create the middle plot
middle = base.encode(
    y = alt.Y('门店名称:N', axis=None),
    text = alt.Text('门店名称:N'),
).mark_text().properties(width=20)
# Create the right plot
right = base.transform_filter(
    alt.datum.gender == 'male'
).encode(
    y = alt.Y('门店名称:N', axis=None),
    x = alt.X('平均每单购买金额:Q'),
    color = alt.Color('gender:N', scale=color_scale, legend=None)
).mark_bar().properties(title='男性客户')
# Combine them together
p1 = alt.concat(left, middle, right, spacing=5)
st.altair_chart(p1, use_container_width = True)



st.subheader("2. 平均每单购买金额的分析")
# Create an interval selection over an x-axis encoding
brush = alt.selection_interval(encodings=['x'])
# Determine opacity based on brush
opacity = alt.condition(brush, alt.value(0.9), alt.value(0.1))
# Create a histogram to over view number of orders per store
t = alt.TitleParams("平均每单购买金额与进店次数的关系", subtitle=["图 2.1 Interactive Chart"])
overview = alt.Chart(df2, title=t).mark_bar().encode(
    x = alt.X('门店名称:N', axis=alt.Axis(title=None, labelAngle=0)), # no title, no label angle)
    y = alt.Y('count()', title=None), # counts, no axis title
    color = alt.Color('门店名称:N'),
    opacity=opacity
).add_selection(
    brush      # add interval brush selection to the chart
).properties(
    width=600, # set the chart width to 600 pixels
    height=60  # set the chart height to 60 pixels
)
# Create a scatterplot to show the relationship between 购买数量&购买金额
detail = alt.Chart(df2).mark_circle().encode(
    x = alt.X('进店次数:N'),
    y = alt.Y('log(平均每单购买金额):Q'),
    # set opacity based on brush selection
    color = alt.Color('门店名称:N'),
    opacity=opacity,
    tooltip = ['进店次数', '平均每单购买金额']
).properties(width=600) # set chart width to match the first chart
# Vertically concatenate (vconcat) charts using the '&' operator
st.write(overview & detail.interactive())
st.caption("注:在直方图上拖动鼠标以查看不同门店在散点图上的状况")
st.write("从图2.1可以看到,总体上来说随着进店次数的增加,用户平均每单购买金额的期望值一直保持在log scale=2(也就是7.5元) \
    附近,而购买金额的方差却在不断减少. 通过在直方图上拖动鼠标查看A,B,C三家店的情况,发现他们都基本符合此特征. 这说明 \
        用户到店次数的多和少似乎与其每笔订单购买金额的大小并无线性相关,但是随着到店次数的增多,每单购买金额的确在向着7.5元 \
            附近收敛. 也就是说到店次数多的顾客其每次购物的金额比到店次数少的顾客更加稳定(向着7.5元收敛),更小可能出现 \
                购物金额很高或很低的情况. 可以进一步研究到店次数多的用户购买频次高的商品top3有哪些,这些商品的平均价格 \
                    正好是7.5元吗等问题,从而获知如何增强用户的忠诚度.")



st.subheader("3. 用户年龄的分析")
# Create a radial chart to show the 年代 composition of all customers in each store
t = alt.TitleParams("所有用户年龄占比分析(总体)", subtitle=["图 3.1 Radial Chart"])
base = alt.Chart(df2, title=t).encode(
    theta = alt.Theta("count(年代):Q", stack=True),
    radius = alt.Radius("count(年代)", scale=alt.Scale(type="linear", zero=True, rangeMin=20)),
    color = "年代:N",
    tooltip = ['年代','count(年代)']
)
c1 = base.mark_arc(innerRadius=20, stroke="#fff")
c2 = base.mark_text(radiusOffset=10).encode(text="年代:N")
st.altair_chart((c1 + c2), use_container_width = True)
st.write("从图3.1可以看出,70后,80后,90后和00后的客户占据了三家门店总体人群的绝大部分,其中90后的占比更是超过了总数的三分之一 \
    ,80后占比位居第二. 这说明仅从年龄段来看,年轻群体是三家便利店的主流客户,中老年客户的占比较低. 因此在选择广告营销策略时 \
        可以着重调查年轻群体的喜好,以达到增加主流群体消费额和用户忠诚度等目标.")

option = st.selectbox("请选择门店", pd.Series(['A', 'B', 'C']))
filter_data = df2[df2['门店名称'] == option]
# Create a radial chart to show the 年代 composition of all customers in each store
t = alt.TitleParams("用户年龄占比分析(某一门店))", subtitle=["图 3.2 Radial Chart"])
base = alt.Chart(filter_data, title=t).encode(
    theta = alt.Theta("count(年代):Q", stack=True),
    radius = alt.Radius("count(年代)", scale=alt.Scale(type="linear", zero=True, rangeMin=20)),
    color = "年代:N",
    tooltip = ['年代','count(年代)']
)
c1 = base.mark_arc(innerRadius=20, stroke="#fff")
c2 = base.mark_text(radiusOffset=10).encode(text="年代:N")
st.altair_chart((c1 + c2), use_container_width = True)
st.write("通过选择不同的门店查看性别比例的饼图可以看到,A,B,C三家门店的共同点在于90后的占比都很高,从三分之一到一半不等, \
    80后的占比也都稳定在总数的五分之一左右. 但是00后作为最年轻的群体,在B店所占比例要明显高于A,C两店所占比例,推断可能的 \
        原因是B店附近有相当数量的中小学,作为B店稳定的00后客户来源. 年龄老于70后的用户在三家门店占比均很低,可以不去考虑.")




