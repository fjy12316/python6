import streamlit as st
import requests
from bs4 import BeautifulSoup
import jieba
from collections import Counter
import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import WordCloud, Line, Bar, Pie, Scatter, Radar
from streamlit_echarts import st_pyecharts
import matplotlib.pyplot as plt
from matplotlib import font_manager
import seaborn as sns
import os
import re

# 页面配置
st.set_page_config(page_title="文本分析", page_icon="", layout="wide")

# 隐藏 Streamlit 默认菜单和 "Deploy" 按钮
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    <[表情]yle>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# 设置中文字体路径
try:
    custom_font_path = "C:/Windows/Fonts/simsun.ttc"
    custom_font = font_manager.FontProperties(fname=custom_font_path)
    plt.rcParams['font.sans-serif'] = custom_font_path #设置全局字体
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
except Exception as e:
    st.error(f"字体加载失败，请检查字体路径是否正确。错误详情: {e}")
    st.stop()

# 自动打开浏览器运行
if "RUN_FROM_STREAMLIT" not in os.environ:
    os.environ["RUN_FROM_STREAMLIT"] = "true"
    os.system(f"streamlit run {__file__}")
    st.stop()

st.title("文本分析")

# Streamlit 输入框
url = st.text_input("请输入URL:", placeholder="")

if url:
    # 获取网页内容
    try:
        response = requests.get(url)
        response.encoding = "utf-8"
        response.raise_for_status()  # 检查请求是否成功
        soup = BeautifulSoup(response.text, "html.parser")
        body = soup.body
        text = body.get_text(strip=True)  # 提取纯文本
    except Exception as e:
        st.error(f" 获取文本失败: {e}")
        st.stop()

    # 使用 jieba 进行中文分词
    cleaned_text = re.sub(r'<.*?>', '', text)
    cleaned_text = re.sub(r'[^\w]', '', cleaned_text)
    words = jieba.cut(text)
    word_list = [word for word in words if len(word) > 1 and not word.isdigit()]  # 去除单个字符
    word_freq = Counter(word_list)  # 统计词频

    # 提取前20个高频词
    most_common_words = word_freq.most_common(20)
    word_df = pd.DataFrame(most_common_words, columns=["词汇", "频次"])
    word_df = word_df.sort_values(by="频次", ascending=True)  # 按照频次升序排序

    # 生成词云图
    wordcloud = WordCloud()
    wordcloud.add(
        "",
        [list(z) for z in zip(word_df["词汇"], word_df["频次"])],
        word_size_range=[20, 100]
    )
    wordcloud.set_global_opts(title_opts=opts.TitleOpts(title="词云图", title_textstyle_opts=opts.TextStyleOpts(font_family="SimHei")))

    # Streamlit显示词频前20名
    st.subheader("词频排名前20的词汇")
    st.dataframe(word_df)#表格显示

    # Streamlit Sidebar 图形筛选
    chart_type = st.sidebar.selectbox(
        "选择图形类型", ["词云图", "柱状图", "折线图", "饼图", "散点图", "热力图", "雷达图"]
    )

    if chart_type == "词云图":
        st_pyecharts(wordcloud)

    elif chart_type == "柱状图":
        bar_chart = Bar()
        bar_chart.add_xaxis(word_df["词汇"].tolist())
        bar_chart.add_yaxis("频次", word_df["频次"].tolist())
        bar_chart.set_global_opts(title_opts=opts.TitleOpts(title="词频柱状图"))
        st_pyecharts(bar_chart)

    elif chart_type == "折线图":
        line_chart = Line()
        line_chart.add_xaxis(word_df["词汇"].tolist())
        line_chart.add_yaxis("频次", word_df["频次"].tolist())
        line_chart.set_global_opts(title_opts=opts.TitleOpts(title="词频折线图"))
        st_pyecharts(line_chart)

    elif chart_type == "饼图":
        pie_chart = Pie()
        pie_chart.add("", [list(z) for z in zip(word_df["词汇"], word_df["频次"])]).set_global_opts(
            title_opts=opts.TitleOpts(title="词频饼图")
        )
        st_pyecharts(pie_chart)

    elif chart_type == "散点图":
        scatter_chart = Scatter()
        scatter_chart.add_xaxis(word_df["词汇"].tolist())
        scatter_chart.add_yaxis("频次", word_df["频次"].tolist())
        scatter_chart.set_global_opts(title_opts=opts.TitleOpts(title="词频散点图"))
        st_pyecharts(scatter_chart)

    elif chart_type == "热力图":
        sns.set(font='SimHei')
        heat_data = pd.DataFrame(word_df["频次"].values).T
        fig, ax = plt.subplots(figsize=(10, 1))
        sns.heatmap(heat_data, annot=True, cmap="YlGnBu", cbar=False, xticklabels=word_df["词汇"].tolist(), ax=ax)
        ax.set_title("词频热力图")
        st.pyplot(fig)

    elif chart_type == "雷达图":
        radar_chart = Radar()
        radar_chart.add_schema(
            schema=[opts.RadarIndicatorItem(name=row["词汇"], max_=word_df["频次"].max()) for _, row in word_df.iterrows()]
        )
        radar_chart.add("词频", [word_df["频次"].tolist()])
        radar_chart.set_global_opts(title_opts=opts.TitleOpts(title="词频雷达图"))
        st_pyecharts(radar_chart)
