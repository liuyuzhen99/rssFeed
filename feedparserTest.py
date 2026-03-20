import feedparser
from datetime import datetime, timedelta
import time
from openai import OpenAI
import os

client = OpenAI(
            api_key="sk-9fdc22a0cd39441aae1b3badfec3c120", 
            base_url="https://api.deepseek.com"
        )

# 定义你感兴趣的 RSS 源
RSS_FEEDS = {
    "TechCrunch": "https://techcrunch.com/feed/",
    "Wired": "https://www.wired.com/feed/rss",
    "Reuters_Business": "http://feeds.reuters.com/reuters/businessNews",
    "CoinDesk": "https://www.coindesk.com/arc/outboundfeeds/rss/"
}

# 关键词过滤：包含这些词的内容会被打上“高价值”标签
KEYWORDS = ["AI", "LLM", "Agent", "Fintech", "Web3", "Crypto", "Regulation"]

def fetch_and_filter():
    daily_news = []
    # 设置时间范围：过去 24 小时
    now = datetime.now()
    one_day_ago = now - timedelta(days=1)

    for source_name, url in RSS_FEEDS.items():
        print(f"正在抓取: {source_name}...")
        feed = feedparser.parse(url)
        
        for entry in feed.entries:
            # 解析发布时间并转换格式
            # 注意：不同源的时间格式略有不同，这里做一个通用的解析处理
            published_time = None
            if hasattr(entry, 'published_parsed'):
                published_time = datetime.fromtimestamp(time.mktime(entry.published_parsed))
            
            # 只处理过去 24 小时内的内容
            if published_time and published_time > one_day_ago:
                title = entry.title
                summary = entry.summary if 'summary' in entry else ""
                link = entry.link
                
                # 关键词匹配逻辑
                is_high_value = any(key.lower() in (title + summary).lower() for key in KEYWORDS)
                
                if is_high_value:
                    daily_news.append({
                        "source": source_name,
                        "title": title,
                        "link": link,
                        "time": published_time.strftime("%H:%M")
                    })
    
    return daily_news

def ai_curate_news(news_items):
    """利用 AI 进行去重、打分和点评"""
    if not news_items:
        return "今日无新增资讯。"
    

    # 将新闻列表格式化为文本，喂给 AI
    input_data = ""
    for i, item in enumerate(news_items[:25]): 
        input_data += f"---\n【编号 {i+1}】\n标题：{item['title']}\n来源：{item['source']}\n链接：{item['link']}\n"
    # news_context = "\n".join([f"- [{item['source']}] {item['title']}" for item in news_items])
    
    prompt = f"""
        # 角色定位
        你是一位资深的金融科技部门经理，拥有 10 年以上的金融系统架构与 AI 落地经验。

        # 重点关注领域 {KEYWORDS}，尤其是那些可能引发行业变革的技术动态。

        # 任务背景
        你需要从原始资讯列表中筛选出 5-8 条高价值信息，整理成一份内部决策内参，分发给部门成员。

        # 评估维度（核心判断准则）
        1. **行业影响 (Financial Impact)**：该资讯是否影响跨境支付、监管合规、加息预期或宏观金融稳定？
        2. **技术变革 (Tech Evolution)**：是否涉及 AI Agent、LLM 微调（如 LoRA/Unsloth）、自动化流水线或 Web3 协议的实质性进展？
        3. **落地实用性 (Practicality)**：该技术能否直接优化现有的财务结算流程、降低人力成本或提升系统稳定性？

        # 待处理资讯
        {input_data}

        # 输出要求（Markdown 格式）
        ## 🏦 金融科技决策内参 | {datetime.now().strftime('%Y-%m-%d')}
        ---
        ### 🌟 战略级资讯 (Top Picks)
        *只需保留 2-3 条最重磅的，需包含以下深度解析：*
        * **[{item['title']}]({item['link']})** ({item['source']}) | 综合评分：X/10
        > **业务研判**：说明该动态对金融行业、市场准入或业务流程的影响。
        > **技术透视**：分析底层技术变革点（如：算力优化、Agent 工作流、隐私计算等）。
        > **落地参考**：针对我们现有的金融产品或 ERP 系统，有何借鉴意义？

        ### 🛰️ 行业快讯
        *精简列出 3-5 条值得关注的动态，每条用一句话总结：*
        * **[{item['title']}]({item['link']})**：[简要说明该信息为何值得关注]。

        # 请务必使用 Markdown 的 [标题](链接) 格式，确保点击即可访问。
        ---
        *注：请剔除任何纯娱乐或重复的噪音。*
    """

    response = client.chat.completions.create(
        model="deepseek-chat", # 或使用 deepseek-chat
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content

# 执行抓取并打印结果
if __name__ == "__main__":
    results = fetch_and_filter()
    
    print(f"\n--- 过去 24 小时精选资讯 (共 {len(results)} 条) ---")
    # 先展示高价值资讯
    for news in results:
        print(f"🌟 [{news['source']}] {news['time']} - {news['title']}")
        print(f"   Link: {news['link']}")
    print("\n--- AI 评选结果 ---")
    ai_result = ai_curate_news(results)
    print(ai_result)