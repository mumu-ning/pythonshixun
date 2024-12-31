import pyecharts.charts
import pypinyin
import streamlit as st
import streamlit_echarts as st_echarts
import requests
from bs4 import BeautifulSoup
import jieba
from pyecharts.charts import Funnel, Bar, WordCloud, Map, Boxplot, Pie, Line, Scatter
import streamlit.components.v1 as components
from pyecharts import options as opts
from pypinyin import pinyin, Style
import re  # 正则表达式库
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import plotly.graph_objects as go

# 全局设置 Matplotlib 中文字体
def set_chinese_font():
    font_path = 'C:\\Windows\\Fonts\\simhei.ttf'  # 根据实际情况调整
    prop = fm.FontProperties(fname=font_path)
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False

set_chinese_font()
# 调用

def remove_stopwords(text):
    stop_words = {'my', 'not', 'couldn', "mustn't", 'and', 'why', "weren't", 'its', 'same', 'hasn', 'again', 'being', "you'd", 'hers', 'don', "wasn't", 'more', "isn't", 'when', 'ma', 'were', 't', 'by', 're', "couldn't", 'we', 'that', "hadn't", 'she', 'down', 's', 'themselves', 'each', 'because', 'having', "you're", 'herself', 'a', 'those', 'them', 'above', 'how', 'only', 'shouldn', 've', 'itself', 'be', 'out', 'up', 'until', 'whom', 'yours', 'did', 'our', 'through', 'below', 'won', "won't", 'nor', 'now', 'off', 'while', "should've", 'wouldn', 'll', 'needn', "mightn't", 'didn', 'hadn', 'an', "wouldn't", 'from', 'in', 'all', 'yourselves', 'both', 'after', 'he', 'few', "you've", 'at', 'these', 'him', "aren't", "haven't", 'his', 'has', 'you', 'myself', 'aren', 'with', 'it', 'will', 'any', "shan't", 'than', 'some', 'haven', 'mustn', "shouldn't", 'theirs', 'been', 'their', 'about', 'on', "you'll", 'm', 'into', 'himself', 'yourself', 'doesn', 'are', 'such', 'your', 'against', 'to', 'mightn', 'doing', 'further', 'over', 'as', 'they', 'during', 'so', 'there', 'between', 'which', 'once', 'me', 'had', 'here', 'under', 'most', 'can', 'but', 'before', 'wasn', "that'll", 'd', 'just', "she's", "it's", 'other', 'have', 'no', 'i', "didn't", 'her', "don't", 'ours', 'very', 'the', 'should', 'too', "needn't", 'if', 'of', 'was', 'isn', 'own', 'what', 'where', 'ourselves', 'or', 'this', 'ain', 'then', 'for', 'weren', 'do', 'who', 'is', "hasn't", "doesn't", 'shan', 'am', 'o', 'y', 'does'}
    words = text.split()
    filtered_words = [word for word in words if word.lower() not in stop_words]
    return ' '.join(filtered_words)

def remove_punctuations(text):
    cleaned_text = re.sub(r'[^\w\s]', '', text)
    return cleaned_text

def crawlingFn(url):
    response = requests.get(url)
    encoding = response.encoding if 'charset' in response.headers.get('content-type', '').lower() else None
    soup = BeautifulSoup(response.content, 'html.parser', from_encoding=encoding)
    text_content = soup.text
    text_content = remove_punctuations(text_content)
    text_content = remove_stopwords(text_content)
    return text_content

def get_word_counts_20():
    input_url = st.text_input("Enter URL:")
    if input_url.strip() == "":
        return {}
    else:
        text = crawlingFn(input_url)
        words = jieba.lcut(text)
        word_counts = {}
        for word in words:
            if len(word) > 1:
                word_counts[word] = word_counts.get(word, 0) + 1
        min_freq = st.slider("设置最低词频阈值", 0, max(word_counts.values()) if word_counts else 0, 0)
        filtered_word_counts = {word: freq for word, freq in word_counts.items() if freq >= min_freq}
        word_counts_20 = dict(sorted(filtered_word_counts.items(), key=lambda x: x[1], reverse=True)[:20])
        return word_counts_20

def page_home_pyecharts():
    word_counts_20 = get_word_counts_20()
    if word_counts_20:
        bar = Bar()
        val = list(map(int, word_counts_20.values()))
        wordList = list(word_counts_20.keys())
        bar.add_xaxis(wordList)
        bar.add_yaxis("关键词", val)
        bar.set_global_opts(xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45)))
        st_echarts.st_pyecharts(bar)

def page_home_matplotlib():
    word_counts_20 = get_word_counts_20()
    if word_counts_20:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(word_counts_20.keys(), word_counts_20.values())
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig)

def page_home_plotly():
    word_counts_20 = get_word_counts_20()
    if word_counts_20:
        fig = go.Figure(data=[go.Bar(x=list(word_counts_20.keys()), y=list(word_counts_20.values()))])
        fig.update_layout(title="条形图", xaxis_title="关键词", yaxis_title="频次")
        st.plotly_chart(fig)

def page_ciyun_pyecharts():
    word_counts = get_word_counts_20()
    if word_counts:
        wordcloud = WordCloud()
        wordcloud.add("", list(word_counts.items()), word_size_range=[20, 100])
        wordcloud.set_global_opts(title_opts=opts.TitleOpts(title="WordCloud Chart"))
        st_echarts.st_pyecharts(wordcloud)

def page_ciyun_matplotlib():
    word_counts = get_word_counts_20()
    if word_counts:
        # Matplotlib does not have a direct word cloud implementation, so we skip this for matplotlib.
        st.write("Matplotlib 不支持词云图，请选择其他库。")

def page_ciyun_plotly():
    word_counts = get_word_counts_20()
    if word_counts:
        # Plotly does not have a direct word cloud implementation, so we skip this for plotly.
        st.write("Plotly 不支持词云图，请选择其他库。")

def page_pie_pyecharts():
    word_counts_20 = get_word_counts_20()
    if word_counts_20:
        word_list = [(x,y) for x,y in word_counts_20.items()]
        pie = Pie()
        pie.add("", word_list, radius=["40%", "55%"])
        pie.set_global_opts(title_opts=opts.TitleOpts(title=""))
        st_echarts.st_pyecharts(pie)

def page_pie_matplotlib():
    word_counts_20 = get_word_counts_20()
    if word_counts_20:
        labels = word_counts_20.keys()
        sizes = word_counts_20.values()
        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        st.pyplot(fig)

def page_pie_plotly():
    word_counts_20 = get_word_counts_20()
    if word_counts_20:
        fig = go.Figure(data=[go.Pie(labels=list(word_counts_20.keys()), values=list(word_counts_20.values()))])
        st.plotly_chart(fig)

def page_broken_pyecharts():
    word_counts_20 = get_word_counts_20()
    if word_counts_20:
        line = Line()
        line.add_xaxis(list(word_counts_20.keys()))
        line.add_yaxis("关键词", list(word_counts_20.values()))
        line.set_global_opts(xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45)))
        st_echarts.st_pyecharts(line)

def page_broken_matplotlib():
    word_counts_20 = get_word_counts_20()
    if word_counts_20:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(word_counts_20.keys(), word_counts_20.values(), marker='o')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig)

def page_broken_plotly():
    word_counts_20 = get_word_counts_20()
    if word_counts_20:
        fig = go.Figure(data=[go.Scatter(x=list(word_counts_20.keys()), y=list(word_counts_20.values()), mode='lines+markers')])
        fig.update_layout(title="折线图", xaxis_title="关键词", yaxis_title="频次")
        st.plotly_chart(fig)

def page_point_pyecharts():
    word_counts_20 = get_word_counts_20()
    if word_counts_20:
        scatter = Scatter()
        scatter.add_xaxis(list(word_counts_20.keys()))
        scatter.add_yaxis("关键词", list(word_counts_20.values()))
        scatter.set_global_opts(xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45)))
        st_echarts.st_pyecharts(scatter)

def page_point_matplotlib():
    word_counts_20 = get_word_counts_20()
    if word_counts_20:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(word_counts_20.keys(), word_counts_20.values())
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig)

def page_point_plotly():
    word_counts_20 = get_word_counts_20()
    if word_counts_20:
        fig = go.Figure(data=[go.Scatter(x=list(word_counts_20.keys()), y=list(word_counts_20.values()), mode='markers')])
        fig.update_layout(title="散点图", xaxis_title="关键词", yaxis_title="频次")
        st.plotly_chart(fig)


def page_box_pyecharts():
    word_counts_20 = get_word_counts_20()
    if word_counts_20:
        box_plot = Boxplot()

        # Prepare data for the box plot
        keys = list(word_counts_20.keys())
        values = list(word_counts_20.values())

        # Create a list of lists where each sublist represents the data points for a single keyword
        # For demonstration purposes, we create artificial data points around the actual frequency.
        # In practice, you might want to use real data or skip this step if your data is already in the correct format.
        data = [[v - 1, v - 0.5, v, v + 0.5, v + 1] for v in values]

        # Add x-axis and y-axis data
        box_plot.add_xaxis(keys)
        box_plot.add_yaxis("关键词词频", box_plot.prepare_data(data))

        # Set global options to improve layout and readability
        box_plot.set_global_opts(
            title_opts=opts.TitleOpts(title="关键词词频箱型图"),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45)),  # Rotate labels for better readability
            yaxis_opts=opts.AxisOpts(name="频次")
        )

        # Render the chart using Streamlit
        st_echarts.st_pyecharts(box_plot, height='600px', width='100%')

# def page_box_matplotlib():
#     word_counts_20 = get_word_counts_20()
#     if word_counts_20:
#         data = list(word_counts_20.values())
#         fig, ax = plt.subplots(figsize=(10, 6))
#         ax.boxplot(data)
#         plt.xticks(range(1, len(word_counts_20)+1), word_counts_20.keys(), rotation=45, ha='right')
#         plt.tight_layout()
#         st.pyplot(fig)


def page_box_plotly():
    word_counts_20 = get_word_counts_20()
    if word_counts_20:
        fig = go.Figure()

        # Prepare data for the box plot
        keys = list(word_counts_20.keys())
        values = list(word_counts_20.values())

        # Create a list of lists where each sublist represents the data points for a single keyword
        # For demonstration purposes, we create artificial data points around the actual frequency.
        # In practice, you might want to use real data or skip this step if your data is already in the correct format.
        data_points_list = [[v - 1, v - 0.5, v, v + 0.5, v + 1] for v in values]

        # Add traces for each keyword with its corresponding data points
        for keyword, data_points in zip(keys, data_points_list):
            fig.add_trace(go.Box(y=data_points, name=keyword, boxpoints=False))

        # Update layout to improve readability and aesthetics
        fig.update_layout(
            title="关键词词频箱型图",
            xaxis_title="关键词",
            yaxis_title="频次",
            boxmode='group',  # 确保多个箱形图并排显示
            showlegend=False,  # 如果不需要图例，可以隐藏
            xaxis=dict(tickangle=45)  # 旋转x轴标签以提高可读性
        )

        # Display the chart using Streamlit
        st.plotly_chart(fig)

def page_funnel_pyecharts():
    word_counts_20 = get_word_counts_20()
    if word_counts_20:
        funnel = (
            Funnel()
            .add(series_name="", data_pair=list(word_counts_20.items()), gap=-2)
            .set_colors(["#FFD700", "#FFA500", "#FF4500", "#FF6347", "#FF8C00"])
            .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
        )
        st_echarts.st_pyecharts(funnel)

def page_funnel_matplotlib():
    word_counts_20 = get_word_counts_20()
    if word_counts_20:
        # Matplotlib does not have a direct funnel chart implementation, so we skip this for matplotlib.
        st.write("Matplotlib 不支持漏斗图，请选择其他库。")

def page_funnel_plotly():
    word_counts_20 = get_word_counts_20()
    if word_counts_20:
        # Plotly does not have a direct funnel chart implementation, so we skip this for plotly.
        st.write("Plotly 不支持漏斗图，请选择其他库。")

def main():
    st.title('欢迎使用网页词频可视化工具! 👋')

    library = st.sidebar.selectbox('选择绘图库', ['pyecharts', 'matplotlib', 'plotly'])
    page = st.sidebar.selectbox('导航栏', ['条形图', '词云', '饼状图', '折线图', '散点图', '箱型图', '漏斗图'])

    if page == '条形图':
        if library == 'pyecharts':
            page_home_pyecharts()
        elif library == 'matplotlib':
            page_home_matplotlib()
        elif library == 'plotly':
            page_home_plotly()
    elif page == '词云':
        if library == 'pyecharts':
            page_ciyun_pyecharts()
        elif library == 'matplotlib':
            page_ciyun_matplotlib()
        elif library == 'plotly':
            page_ciyun_plotly()
    elif page == '饼状图':
        if library == 'pyecharts':
            page_pie_pyecharts()
        elif library == 'matplotlib':
            page_pie_matplotlib()
        elif library == 'plotly':
            page_pie_plotly()
    elif page == '折线图':
        if library == 'pyecharts':
            page_broken_pyecharts()
        elif library == 'matplotlib':
            page_broken_matplotlib()
        elif library == 'plotly':
            page_broken_plotly()
    elif page == '散点图':
        if library == 'pyecharts':
            page_point_pyecharts ()
        elif library == 'matplotlib':
            page_point_matplotlib()
        elif library == 'plotly':
            page_point_plotly()
    elif page == '箱型图':
        if library == 'pyecharts':
            page_box_pyecharts()
        elif library == 'matplotlib':
            st.write("Matplotlib不支持箱型图，请选择其他库。")
        elif library == 'plotly':
            page_box_plotly()

    elif page == '漏斗图':
        if library == 'pyecharts':
            page_funnel_pyecharts ()
        elif library == 'matplotlib'or 'plotly':
            st.write("Matplotlib 和 Plotly 不支持漏斗图，请选择其他库。")


if __name__ == '__main__':
    main()