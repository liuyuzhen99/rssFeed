import feedparser
from datetime import datetime, timedelta
import time
from openai import OpenAI
import os

client = OpenAI(
            api_key="sk-9fdc22a0cd39441aae1b3badfec3c120", 
            base_url="https://api.deepseek.com/v1"
        )

# 定义你感兴趣的 RSS 源
RSS_FEEDS = {
    "TechCrunch": "https://techcrunch.com/feed/",
    "Wired": "https://www.wired.com/feed/rss",
    "Reuters_Business": "http://feeds.reuters.com/reuters/businessNews",
    "CoinDesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "36kr": "https://36kr.com/feed",
    "meituanTech": "https://tech.meituan.com/feed",
    "MIT Technology Review": "https://www.technologyreview.com/feed/",
    "the Verge": "https://www.theverge.com/rss/index.xml",
    "Hacker News": "https://news.ycombinator.com/rss",
    "Financial Times": "https://www.ft.com/?format=rss",
    "wall street cn": "https://rsshub.app/wallstreetcn/news/global",
    "BeInCrypto": "https://beincrypto.com/feed/",
    "RobotPaper": "https://robotpaper.ai/rss/"
}

# 关键词过滤：包含这些词的内容会被打上“高价值”标签
KEYWORDS = ["AI", "LLM", "Agent", "Fintech", "Web3", "Crypto", "Regulation", "Technichal", "Development"]

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
        ### 🚀 职场进化版：AI & Web3 职业战略情报员
        # 角色定位
        你是一位深耕金融科技（FinTech）领域的**职业发展导师**与**行业观察家**。你擅长从海量资讯中嗅觉出“技术红利期”，能够洞察哪些技术路径是未来的财富密码，哪些是短期泡沫。

        # 核心任务
        从原始资讯列表中筛选出 5-8 条高价值信息，整理成一份\*\*《个人职业进化内参》\*\*。你的目标是帮我过滤噪音，寻找能提升我个人身价、优化自动化工作流、以及在 Web3 领域获取超额收益的机会。

        # 筛选准则（职场增值维度）

        1.  **技术复利 (Technical Leverage)**：该资讯是否涉及 AI Agent 自动化、LLM 微调（如 Unsloth）或高效率工具？能否让我的“一人公司”生产力实现量级提升？
        2.  **行业钱景 (Sector Potential)**：是否涉及 Web3 协议（如 Polymarket 机制、X Layer 动态）、跨境结算支付的代币化？是否有明确的套利或高薪岗位增长机会？
        3.  **认知护城河 (Cognitive Moat)**：该动态是否能帮我理清“什么值得做”与“什么不值得做”，避免在夕阳技术上浪费时间。

        # 待处理资讯
        `{input_data}`

        # 输出要求（Markdown 格式）

        ## ⚡ 职业进化内参 | {datetime.now().strftime('%Y-%m-%d')}

        -----

        ### 🏆 核心战略机遇 (Top Picks)

        *精选 2-3 条可能改变职业轨迹或产生技术红利的重磅资讯：*

        * **[{item['title']}]({item['link']})** ({item['source']}) | **推荐指数：X/10**
            > **职业风向标**：分析该动态反映了行业哪种长期趋势？它预示着哪些技能正变得空前值钱？
            > **实战路径**：结合我目前的 Python 自动化、本地模型（DeepSeek/Whisper）或 Web3 交互经验，我该如何切入？
            > **避坑指南**：在这一领域，哪些是低价值的重复劳动？我应该把精力花在什么地方？

        ### 🛰️ 前沿情报（AI & Web3）

        *精简列出 3-5 条值得关注的技术/市场动向，直接指出其对个人的好处：*

        * **[{item['title']}]({item['link']})**：[简述该技术如何帮我减少工作量，或在 Web3 市场中发现新的流动性机会]。
        # 请务必使用 Markdown 的 [标题](链接) 格式，确保点击即可访问。
        -----

        *💡 导师寄语：专注那些能产生复利的底层技术，忽略短期的市场情绪。*
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