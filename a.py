import re
import requests
from bs4 import BeautifulSoup
import jieba
from collections import Counter
import streamlit as st
from pyecharts.charts import WordCloud
from pyecharts.charts import Bar,Line,Pie,Scatter
import streamlit.components.v1 as components
from pyecharts import options as opts



# 步骤 1：抓取网页内容
def fetch_url_content(url):
    try:
        # 设置请求头，模拟浏览器访问
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }

        # 发送HTTP请求
        response = requests.get(url, headers=headers, timeout=10)

        # 检查请求是否成功
        if response.status_code == 200:
            print("成功抓取网页！")
        else:
            print(f"网页抓取失败，状态码: {response.status_code}")
            return ""

        # 手动设置正确的编码
        response.encoding = response.apparent_encoding

        # 解析HTML页面
        soup = BeautifulSoup(response.text, 'html.parser')

        # 试图抓取更多的内容
        paragraphs = soup.find_all(['p', 'div', 'span'])
        text = ' '.join([p.get_text(strip=True) for p in paragraphs])

        # 如果没有抓取到任何内容
        if not text:
            print("没有抓取到有效的文本内容")
            return ""

        # 模拟延迟
        #time.sleep(random.uniform(1, 3))  # 添加1到3秒的随机延迟

        return text

    except requests.exceptions.Timeout:
        print("请求超时，尝试重新连接...")
        return fetch_url_content(url)  # 尝试重新抓取
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")
        return ""
    except Exception as e:
        print(f"发生错误: {e}")
        return ""

# 步骤 2：去除HTML标签
def remove_html_tags(text):
    clean_text = re.sub(r'<[^>]+>', '', text)
    return clean_text

# 步骤 3：去除标点符号
def remove_punctuation(text):
    clean_text = re.sub(r'[^\w\s]', '', text)
    return clean_text

# 步骤 4：分词
def segment_text(text):
    words = jieba.cut(text)
    # 将分词结果中的词语以空格分隔
    words_str = ' '.join(list(words))
    return words_str

# 步骤 5：统计词频
def get_word_frequency(segmented_text):
    # 将分词结果的字符串再次分割为列表
    words = segmented_text.split()
    word_count = Counter(words)
    return word_count

# 筛选词频
def filter_word_frequency(word_count, min_freq, max_freq):
    return Counter({word: freq for word, freq in word_count.items() if min_freq <= freq <= max_freq})

# 步骤 6：生成 pyecharts 词云
def generate_wordcloud(word_count):
    # 按词频排序，取前20个词
    sorted_word_count = dict(sorted(word_count.items(), key=lambda item: item[1], reverse=True)[:20])

    # 生成词云
    wc = WordCloud()
    wc.add("词云", list(sorted_word_count.items()), word_size_range=[20, 50])  # 调整词云大小范围
    wc.set_global_opts(title_opts=opts.TitleOpts(title="词云图"))

    return wc


def generate_bar_chart(word_counts):
    bar = Bar()
    words, counts = zip(*word_counts.items())
    bar.add_xaxis(list(words))
    bar.add_yaxis("词频", list(counts))
    bar.set_global_opts(
        title_opts=opts.TitleOpts(title="词频柱状图"),
        xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45))
    )
    return bar

def generate_bar_chart_horizontal(word_counts):
    bar = Bar()
    words, counts = zip(*word_counts.items())
    bar.add_yaxis("词频", list(counts))
    bar.add_xaxis(list(words))
    bar.set_global_opts(
        title_opts=opts.TitleOpts(title="词频条形图"),
        yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45))
    )
    return bar

def generate_area_chart(word_counts):
    line = Line()
    words, counts = zip(*word_counts.items())
    line.add_xaxis(list(words))
    line.add_yaxis(
        "词频", list(counts),
        is_smooth=True,
        label_opts=opts.LabelOpts(is_show=False),
        areastyle_opts=opts.AreaStyleOpts(opacity=0.4)  # 这里使用 areastyle_opts 而不是 area_style
    )
    line.set_global_opts(
        title_opts=opts.TitleOpts(title="词频面积图"),
        xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45))
    )
    return line


def generate_line_chart(word_counts):
    line = Line()
    words, counts = zip(*word_counts.items())
    line.add_xaxis(list(words))
    line.add_yaxis("词频", list(counts))
    line.set_global_opts(
        title_opts=opts.TitleOpts(title="词频折线图"),
        xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45))
    )
    return line

def generate_pie_chart(word_counts):
    pie = Pie()
    words, counts = zip(*word_counts.items())
    pie.add(
        "",
        [list(z) for z in zip(words, counts)],
        radius=["30%", "75%"],
        rosetype="area"
    )
    pie.set_global_opts(
        title_opts=opts.TitleOpts(title="词频饼图")
    )
    return pie

# 绘制词频散点图
def generate_scatter_chart(word_counts):
    scatter = Scatter()
    words, counts = zip(*word_counts.items())
    scatter.add_xaxis(list(words))
    scatter.add_yaxis("词频", list(counts))
    scatter.set_global_opts(title_opts=opts.TitleOpts(title="词频散点图"))
    return scatter


# 通过streamlit渲染pyecharts词云图
def render_pyecharts_chart(chart):
    # 渲染并显示pyecharts图表
    chart_html = chart.render_embed()
    components.html(chart_html, height=600)  # 可以调整height参数

# Streamlit UI
def main():

    st.title('中文文章词频分析与词云展示')

    # 输入URL
    url = st.text_input("请输入文章URL:")

    if url:
        try:
            # 步骤 1：抓取网页内容
            text = fetch_url_content(url)

            if not text:
                st.warning("未抓取到网页内容，请检查URL或网站内容。")
                return

            # 显示原始文本
            st.subheader("抓取的网页内容")
            st.write(text[:500] + '...')  # 显示部分抓取的文本

            # 步骤 2：去除HTML标签
            text = remove_html_tags(text)

            # 显示去除HTML标签后的文本
            st.subheader("去除HTML标签后的内容")
            st.write(text[:500] + '...')

            # 步骤 3：去除标点符号
            text = remove_punctuation(text)

            # 显示去除标点后的文本
            st.subheader("去除标点符号后的内容")
            st.write(text[:500] + '...')

            # 步骤 4：分词
            words = segment_text(text)

            # 步骤 5：统计词频
            word_count = get_word_frequency(words)

            # 自动获取词频的最大值和最小值
            min_freq = min(word_count.values())
            max_freq = max(word_count.values())

            # 输入筛选词频范围
            min_freq_slider = st.sidebar.slider("选择最小词频", min_value=min_freq, max_value=max_freq, value=min_freq, step=1)
            max_freq_slider = st.sidebar.slider("选择最大词频", min_value=min_freq_slider, max_value=max_freq, value=max_freq, step=1)

            # 筛选词频
            filtered_word_count = filter_word_frequency(word_count, min_freq_slider, max_freq_slider)

            # 展示筛选后的词频前20的词
            st.subheader('筛选后的词频排名前20的词')
            top_20_words = filtered_word_count.most_common(20)
            for word, freq in top_20_words:
                st.write(f"{word}: {freq}")

            # 图形筛选
            chart_type = st.sidebar.selectbox(
                "选择图形类型",
                ["词云图", "词频柱状图", "词频条形图", "词频面积图", "词频折线图", "词频饼图", "词频散点图"]
            )
            st.sidebar.write(f"当前选择的图形类型: {chart_type}")
            if chart_type == "词云图":
                wc_chart = generate_wordcloud(filtered_word_count)
                render_pyecharts_chart(wc_chart)

            elif chart_type == "词频柱状图":
                bar_chart = generate_bar_chart(filtered_word_count)
                render_pyecharts_chart(bar_chart)

            elif chart_type == "词频条形图":
                bar_horizontal_chart = generate_bar_chart_horizontal(filtered_word_count)
                render_pyecharts_chart(bar_horizontal_chart)

            elif chart_type == "词频面积图":
                area_chart = generate_area_chart(filtered_word_count)
                render_pyecharts_chart(area_chart)

            elif chart_type == "词频折线图":
                line_chart = generate_line_chart(filtered_word_count)
                render_pyecharts_chart(line_chart)

            elif chart_type == "词频饼图":
                pie_chart = generate_pie_chart(filtered_word_count)
                render_pyecharts_chart(pie_chart)

            elif chart_type == "词频散点图":
                scatter = generate_scatter_chart(filtered_word_count)
                st.subheader('词频散点图')
                render_pyecharts_chart(scatter)

        except Exception as e:
            st.error(f"抓取或处理文本时出错: {e}")

if __name__ == '__main__':
    main()
