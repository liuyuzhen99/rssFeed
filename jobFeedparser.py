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
    "hacker news": "https://rsshub.app/hackernews/jobs",
    "WeWorkRemotely": "https://weworkremotely.com/categories/remote-product-jobs.rss"
}

# 关键词过滤：包含这些词的内容会被打上“高价值”标签
KEYWORDS = ["AI", "LLM", "Agent", "Fintech", "Web3", "Crypto" "Engineer", "Developer", "Product Manager"]

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
        # Role
        你是一位拥有 15 年经验的高级技术猎头和职业发展教练，专长于 FinTech、企业级金融科技以及前沿 AI 领域。你非常擅长从复杂的 Job Description (JD) 中嗅出高价值机会。

        # User Profile (我的背景快照)
        - 核心身份：金融科技产品经理 & 工程师（2.5年经验）。
        - 技术栈：Python, LangGraph (AI Agent 开发), 自动化流水线, Web3 协议。
        - 业务领域：SAP FICO 模块, ERP 系统集成, 财务资金结算, 跨境支付合规。
        - 核心优势：能够用 AI 解决传统金融/财务流程的痛点，具备从业务需求到技术落地全链路能力。
        - 感兴趣领域：{KEYWORDS}

        # Input Data
        待评估的职位列表（包含标题、来源、链接及摘要/JD）：
        {input_data}

        # Task
        请对上述职位进行“三维深度匹配”分析，并筛选出匹配度 > 80% 的岗位。

        # Evaluation Dimensions
        1. **技能硬匹配 (40%)**：JD 是否需要 Python/AI 开发能力？是否涉及金融结算逻辑？
        2. **背景加分项 (30%)**：是否属于 Web3、FinTech 创新、或传统企业数字化转型（AI+ERP）？我的跨界背景是否能成为该岗位的 Unfair Advantage？
        3. **职业天花板 (30%)**：该岗位是纯维护执行，还是具备产品定义权/架构设计权？

        # Output Format (Markdown)
        请按以下结构输出筛选结果：

        ## 🎯 首席推荐：高契合度机会
        ---
        ### [职位名称] @ [公司/来源] | 匹配度：[XX]%
        - **🔗 快速投递**: [点击访问原文]({item['link']})
        - **🔥 为什么选它 (Match Points)**: 
        > 例如：该岗位要求优化财务自动化流程，你的 SAP FICO + AI Agent 开发背景能完美解决其“传统 ERP 效率低”的痛点。
        - **⚠️ 挑战/差距 (Gaps)**: 
        > 指出 JD 中我不具备或较弱的要求，并给出弥补建议。
        - **📝 投递锦囊 (Action Plan)**: 
        > 如果投递，简历中应重点强调哪个项目？（给出 1-2 句话的针对性话术建议）。

        ## 🛰️ 潜力/跨界机会 (70%-80% 匹配)
        *简要列出 2-3 个值得关注但可能需要稍微“跨界”一下的岗位。*

        ---
        *注：请忽略任何由于 RSS 抓取错误导致的非招聘类资讯。*
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
    
    print(f"\n--- 过去 24 小时兴趣岗位 (共 {len(results)} 条) ---")
    # 先展示高价值资讯
    for news in results:
        print(f"🌟 [{news['source']}] {news['time']} - {news['title']}")
        print(f"   Link: {news['link']}")
    print("\n--- AI 评选结果 ---")
    ai_result = ai_curate_news(results)
    print(ai_result)