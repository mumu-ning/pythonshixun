import time
import random
import re
import requests
import seaborn as sns
import pandas as pd
from bs4 import BeautifulSoup
import jieba
from collections import Counter
import streamlit as st
from pyecharts import options as opts
from pyecharts.charts import WordCloud
import matplotlib.pyplot as plt
from streamlit.components.v1 import html
import matplotlib.font_manager as fm

# 步骤 1：抓取网页内容
def fetch_url_content(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            print("成功抓取网页！")
        else:
            print(f"网页抓取失败，状态码: {response.status_code}")
            return ""
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all(['p', 'div', 'span'])
        text = ' '.join([p.get_text(strip=True) for p in paragraphs])
        if not text:
            print("没有抓取到有效的文本内容")
            return ""
        return text
    except requests.exceptions.Timeout:
        print("请求超时，尝试重新连接...")
        return fetch_url_content(url)
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
    words_str = ' '.join(list(words))
    return words_str

# 步骤 5：统计词频
def get_word_frequency(segmented_text):
    words = segmented_text.split()
    word_count = Counter(words)
    return word_count

# 筛选词频
def filter_word_frequency(word_count, min_freq, max_freq):
    return Counter({word: freq for word, freq in word_count.items() if min_freq <= freq <= max_freq})

# 步骤 6：生成 pyecharts 词云
def generate_wordcloud(word_count):
    sorted_word_count = dict(sorted(word_count.items(), key=lambda item: item[1], reverse=True)[:20])
    wc = WordCloud()
    wc.add("词云", list(sorted_word_count.items()), word_size_range=[20, 50])
    wc.set_global_opts(title_opts=opts.TitleOpts(title="词云图"))
    return wc

# 步骤 7：绘制词频图
def plot_word_freq(word_count):
    word_freq = word_count.most_common(20)
    words, freqs = zip(*word_freq)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(words, freqs, color='skyblue')
    ax.set_xlabel('词频')
    ax.set_title('词频柱状图')
    ax.set_ylim(0, len(words) + 1)
    plt.tight_layout()
    st.pyplot(fig)

# 绘制词频折线图
def plot_word_freq_line(word_count):
    word_freq = word_count.most_common(20)
    words, freqs = zip(*word_freq)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(words, freqs, marker='o', linestyle='-', color='b')
    ax.set_xlabel('词汇')
    ax.set_ylabel('词频')
    ax.set_title('词频折线图')
    ax.set_xticklabels(words, rotation=90)
    plt.tight_layout()
    st.pyplot(fig)

# 绘制词频饼图
def plot_word_freq_pie(word_count):
    word_freq = word_count.most_common(10)
    words, freqs = zip(*word_freq)
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(freqs, labels=words, autopct='%1.1f%%', startangle=90)
    ax.set_title('词频饼图')
    plt.tight_layout()
    st.pyplot(fig)

# 绘制词频条形图
def plot_word_freq_bar(word_count):
    word_freq = word_count.most_common(20)
    words, freqs = zip(*word_freq)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(words, freqs, color='skyblue')
    ax.set_xlabel('词汇')
    ax.set_ylabel('词频')
    ax.set_title('词频条形图')
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    st.pyplot(fig)

# 绘制词频面积图
def plot_word_freq_area(word_count):
    word_freq = word_count.most_common(20)
    words, freqs = zip(*word_freq)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.fill_between(words, freqs, alpha=0.4, color='skyblue')
    ax.plot(words, freqs, color='skyblue')
    ax.set_xlabel('词汇')
    ax.set_ylabel('词频')
    ax.set_title('词频面积图')
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    st.pyplot(fig)

# 绘制词频热力图
def plot_word_freq_heatmap(word_count):
    word_freq = dict(word_count.most_common(20))
    words = list(word_freq.keys())
    freqs = list(word_freq.values())
    data = pd.DataFrame({'词汇': words, '词频': freqs})
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(data.set_index('词汇'), annot=True, cmap='YlGnBu', ax=ax)
    ax.set_title('词频热力图')
    st.pyplot(fig)

# 通过streamlit渲染pyecharts词云图
def st_pyecharts_chart(wc):
    html_code = wc.render_embed()
    html(html_code, height=600)

# Streamlit UI
def main():
    st.title('中文文章词频分析与词云展示')
    url = st.text_input("请输入文章URL:")
    if url:
        try:
            text = fetch_url_content(url)
            if not text:
                st.warning("未抓取到网页内容，请检查URL或网站内容。")
                return
            st.subheader("抓取的网页内容")
            st.write(text[:500] + '...')
            text = remove_html_tags(text)
            st.subheader("去除HTML标签后的内容")
            st.write(text[:500] + '...')
            text = remove_punctuation(text)
            st.subheader("去除标点符号后的内容")
            st.write(text[:500] + '...')
            words = segment_text(text)
            word_count = get_word_frequency(words)
            min_freq = min(word_count.values())
            max_freq = max(word_count.values())
            min_freq_slider = st.sidebar.slider("选择最小词频", min_value=min_freq, max_value=max_freq, value=min_freq, step=1)
            max_freq_slider = st.sidebar.slider("选择最大词频", min_value=min_freq_slider, max_value=max_freq, value=max_freq, step=1)
            filtered_word_count = filter_word_frequency(word_count, min_freq_slider, max_freq_slider)
            st.subheader('筛选后的词频排名前20的词')
            top_20_words = filtered_word_count.most_common(20)
            for word, freq in top_20_words:
                st.write(f"{word}: {freq}")
            chart_type = st.sidebar.selectbox(
                "选择图形类型",
                ["词云图", "词频柱状图", "词频条形图", "词频面积图", "词频折线图", "词频饼图", "词频热力图"]
            )
            st.sidebar.write(f"当前选择的图形类型: {chart_type}")
            if chart_type == "词云图":
                wc_chart = generate_wordcloud(filtered_word_count)
                st_pyecharts_chart(wc_chart)
            elif chart_type == "词频柱状图":
                plot_word_freq(filtered_word_count)
            elif chart_type == "词频条形图":
                plot_word_freq_bar(filtered_word_count)
            elif chart_type == "词频面积图":
                plot_word_freq_area(filtered_word_count)
            elif chart_type == "词频折线图":
                plot_word_freq_line(filtered_word_count)
            elif chart_type == "词频饼图":
                plot_word_freq_pie(filtered_word_count)
            elif chart_type == "词频热力图":
                plot_word_freq_heatmap(filtered_word_count)

        except Exception as e:
            st.error(f"抓取或处理文本时出错: {e}")

if __name__ == '__main__':
    main()
