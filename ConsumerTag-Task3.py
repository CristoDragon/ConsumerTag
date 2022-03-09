import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import altair as alt


st.title("TASK 3: 标签体系应用-用户画像")
st.subheader("Author: Runsheng Xu")

# Read in the data from csv file
CT_data = pd.read_csv("https://raw.githubusercontent.com/CristoDragon/CSE5243/main/ConsumerTag(utf8).csv", encoding="utf8")
# Replcace all empty cells with NaN
df1 = CT_data.replace(r'^\s*$', np.nan, regex=True)
if st.checkbox("查看原始数据ConsumerTag(utf8).csv"):
    st.write(df1)

st.subheader("1. 平均每单购买金额的分布情况分析")
# Create a histogram to show the distribution of "平均每单购买金额"
title1 = alt.TitleParams("用户平均每单购买金额的总体分布状况", subtitle=["图 1.1"])
base = alt.Chart(df1, title=title1)
histogram1 = base.mark_bar().encode(
    x = alt.X('平均每单购买金额:Q', bin=alt.BinParams(maxbins=100), axis=None),
    y = alt.Y('count()', stack = None),
    tooltip = ['平均每单购买金额']
)
rule1 = base.mark_rule(color='red').encode(
    x = 'mean(平均每单购买金额):Q',
    size = alt.value(2)
)
st.altair_chart((histogram1 + rule1).interactive(), use_container_width = True)
st.caption("注: 图1.1中红线标识为'平均每单购买金额'的平均值, 可缩放此图查看细节")
st.write("从图1.1中可以看到,绝大多数便利店客户的平均每单购买金额是大概处于[0,40]元这个范围内的,the distribution is extremely \
    right skewed,这点从中位数小于平均值也可以看出. 基于平均购买金额的此分布特征,我们可以将研究重点放在[0,40]之间的这部分\
        客户,思考如何提高他们每单的购买价格. 由于这部分群体占全部客户的份额很大,所以他们平均购买金额的少量提升也会带来巨大收益.")

# Create a histogram to show the distribution of "平均每单购买金额"
title2 = alt.TitleParams("用户平均每单购买金额的分布状况", subtitle=["图 1.2"])
histogram2 = alt.Chart(df1, title=title2).transform_fold(
    ['平均每单购买金额'],
    as_=['平均每单购买金额/数量', '元/个']
).mark_bar(
    opacity=0.45,
    binSpacing=0
).encode(
    alt.X('平均每单购买金额:Q', bin = alt.Bin(maxbins=100)),
    alt.Y('count()', stack = None),
    alt.Color('性别:N')
    
)
st.altair_chart(histogram2.interactive(), use_container_width = True)
st.write("从图1.2中可以看出,男性和女性的'平均每单购买金额'分布情况基本与客户整体的分布情况一致.")

# Create a histogram to show the distribution of "平均每单购买金额" in log scale
title3 = alt.TitleParams("用户平均每单购买金额的分布状况(log scale)", subtitle=["图 1.3"])
df2 = df1.copy()
df2["log(平均每单购买金额)"] = np.log(df1["平均每单购买金额"])
histogram3 = alt.Chart(df2, title=title3).transform_fold(
    ['log(平均每单购买金额)'],
    as_=['平均每单购买金额/数量', '元/个']
).mark_bar(
    opacity=0.45,
    binSpacing=0
).encode(
    alt.X('log(平均每单购买金额):Q', bin=alt.Bin(maxbins=100)),
    alt.Y('count()', stack=None),
    alt.Color('性别:N')  
)
st.altair_chart(histogram3.interactive(), use_container_width = True)
st.write("由于原始数据的histogram过于skewed,我们对'平均每单购买金额'取对数'以后可以看到基本服从正态分布. 在此图中可以清楚 \
    的看到男性用户在各个购买金额上所对应的数量基本都多余女性用户,可能是由于采集的样本中男性客户总数要多余女性用户. 除此以外 \
        他们的分布状况并无太大区别.")



st.subheader("2. 用户偏好品牌的分布情况分析")
# Create a barplot
df3 = df1.copy()
df3["偏好品牌top1_Count"] = [1] * df1.shape[0]
df3["偏好品牌top2_Count"] = [1] * df1.shape[0]
df3["偏好品牌top3_Count"] = [1] * df1.shape[0]
df4 = df3[["偏好品牌top1", "偏好品牌top1_Count"]].groupby("偏好品牌top1", as_index=False).count().rename(columns={'偏好品牌top1_Count':'top1_Count'})
df4.sort_values(by=["top1_Count"], ascending=False, inplace=True)
df5 = df3[["偏好品牌top2", "偏好品牌top2_Count"]].groupby("偏好品牌top2", as_index=False).count().rename(columns={'偏好品牌top2_Count':'top2_Count'})
df5.sort_values(by=["top2_Count"], ascending=False, inplace=True)
df6 = df3[["偏好品牌top3", "偏好品牌top3_Count"]].groupby("偏好品牌top3", as_index=False).count().rename(columns={'偏好品牌top3_Count':'top3_Count'})
df6.sort_values(by=["top3_Count"], ascending=False, inplace=True)

title4 = alt.TitleParams("用户偏好品牌top1的分布状况(前10名)", subtitle=["图 2.1"])
barchart1 = alt.Chart(df4.iloc[0:10,:], title=title4).mark_bar(opacity=0.5, color="blue").encode(
    x = alt.X('top1_Count:Q', title='Count'),
    y = alt.Y("偏好品牌top1:N", title='偏好品牌top1', sort='-x'),
    tooltip = ['偏好品牌top1','top1_Count']
)
title5 = alt.TitleParams("用户偏好品牌top2的分布状况(前10名)", subtitle=["图 2.2"])
barchart2 = alt.Chart(df5.iloc[0:10,:], title=title5).mark_bar(opacity=0.5, color="red").encode(
    x = alt.X('top2_Count:Q', title='Count'),
    y = alt.Y("偏好品牌top2:N", title='偏好品牌top2', sort='-x'),
    tooltip = ['偏好品牌top2','top2_Count']
)
title6 = alt.TitleParams("用户偏好品牌top3的分布状况(前10名)", subtitle=["图 2.3"])
barchart3 = alt.Chart(df6.iloc[0:10,:], title=title6).mark_bar(opacity=0.5, color="grey").encode(
    x = alt.X('top3_Count:Q', title='Count'),
    y = alt.Y("偏好品牌top3:N", title='偏好品牌top3', sort='-x'),
    tooltip = ['偏好品牌top3','top3_Count']
)
st.altair_chart(barchart1.interactive(), use_container_width = True)
st.altair_chart(barchart2.interactive(), use_container_width = True)
st.altair_chart(barchart3.interactive(), use_container_width = True)
st.write("从图2.1,图2.2和图2.3可以看出,七匹狼,康师傅,可口可乐,农夫山泉,怡宝,伊利等均出现在三个图中,说明顾客偏好品牌的top1,top2 \
    和top3中重合的品牌站绝大多数(前10名). 在这些品牌中我们可以看到,主营业务为饮料或瓶装水的企业占据了至少一半的份额,侧面 \
        说明顾客在便利店最频繁购买的商品里面饮品是主体. 可以在未来的研究中将重点放在饮料相关的产品上,提升产品质量,增加产品\
        丰富度等,进而提升客流.")


# Create a readial chart
title4 = alt.TitleParams("用户偏好品牌top1的分布状况(前7名)", subtitle=["图 2.4"])
radial1 = alt.Chart(df4.iloc[0:7,:], title=title4).encode(
    theta = alt.Theta("top1_Count:Q", stack = True),
    radius = alt.Radius("top1_Count:Q", scale = alt.Scale(type="linear", zero=True, rangeMin=20)),
    color="偏好品牌top1:N",
    tooltip = ['偏好品牌top1','top1_Count']
)
c1 = radial1.mark_arc(innerRadius=20, stroke="#fff")
c2 = radial1.mark_text(radiusOffset=10).encode(text="偏好品牌top1:N")
st.altair_chart(c1 + c2, use_container_width = True)

title5 = alt.TitleParams("用户偏好品牌top2的分布状况(前7名)", subtitle=["图 2.5"])
radial1 = alt.Chart(df5.iloc[0:7,:], title=title4).encode(
    theta = alt.Theta("top2_Count:Q", stack = True),
    radius = alt.Radius("top2_Count:Q", scale = alt.Scale(type="linear", zero=True, rangeMin=20)),
    color="偏好品牌top2:N",
    tooltip = ['偏好品牌top2','top2_Count']
)
c1 = radial1.mark_arc(innerRadius=20, stroke="#fff")
c2 = radial1.mark_text(radiusOffset=10).encode(text="偏好品牌top3:N")
st.altair_chart(c1 + c2, use_container_width = True)

title6 = alt.TitleParams("用户偏好品牌top3的分布状况(前7名)", subtitle=["图 2.6"])
radial1 = alt.Chart(df6.iloc[0:7,:], title=title4).encode(
    theta = alt.Theta("top3_Count:Q", stack = True),
    radius = alt.Radius("top3_Count:Q", scale = alt.Scale(type="linear", zero=True, rangeMin=20)),
    color="偏好品牌top3:N",
    tooltip = ['偏好品牌top3','top3_Count']
)
c1 = radial1.mark_arc(innerRadius=20, stroke="#fff")
c2 = radial1.mark_text(radiusOffset=10).encode(text="偏好品牌top3:N")
st.altair_chart(c1 + c2, use_container_width = True)




st.subheader("3. 用户年龄层与平均每单购买金额的交叉分析")
# Create a boxplot to reveal the difference in distribution of '平均每单购买金额' in each '年代'
t1 = alt.TitleParams("用户平均每单购买金额的Boxplot over '年代'", subtitle=["图 3.1"])
boxplot1 = alt.Chart(df1, title=t1).mark_boxplot(extent=0.5).encode(
    x = alt.X('年代:N'),
    y = alt.Y('平均每单购买金额:Q'),
    color = alt.Color('年代'),
    tooltip = ["年代","平均每单购买金额"]
)
st.altair_chart(boxplot1.interactive(), use_container_width = True)

t2 = alt.TitleParams("用户平均每单购买金额的Boxplot over '年代'(log scale)", subtitle=["图 3.2"])
boxplot2 = alt.Chart(df2, title=t2).mark_boxplot(extent=0.5).encode(
    x = alt.X('年代:N'),
    y = alt.Y('log(平均每单购买金额):Q'),
    color = alt.Color('年代'),
    tooltip = ["年代","log(平均每单购买金额)"]
)
st.altair_chart(boxplot2.interactive(), use_container_width = True)
st.write("从图3.2可以看出一些各个年龄段的顾客其平均每单购买金额的分布特征. 总体而言,各个年龄段平均每单购买金额的期望值相差不是很大 \
    ,而且从图中也看不出明显的线性相关. 但是各个年龄段其购买金额的第一四分位数和第三四分位数的差值却有明显区别, 例如10后和40后的这个差值 \
        要明显小于其他年龄段,可以进一步研究有哪些商品(例如top3)是10后和40后频繁购买的,你们这些商品在此年龄段具有主导地位. 90后的这个 \
            插值要明显高于其他年龄段,有可能说明90后群体的购买种类丰富,消费能力和消费意愿也存在很大差别,造成了这个variation. \
                如果仔细观察箱型图中平均值的水平线,可以看到60后的平均购买金额要高于其他年龄段,可能是由于60后以退休人群为主, \
                    消费习惯比较传统(意味着更多在便利店的购买量而不是网购)同时又有一定的消费能力.")



