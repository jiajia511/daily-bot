import os
import praw
import random
import schedule
import time
import threading
import json
from flask import Flask, render_template_string
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

reddit = praw.Reddit(
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
    user_agent=os.getenv("USER_AGENT")
)

SUBREDDITS = ['AskReddit', 'AskWomen', 'nosleep', 'NoStupidQuestions']

def fetch_and_save_posts():
    result = []
    for sub in SUBREDDITS:
        subreddit = reddit.subreddit(sub)
        top_posts = list(subreddit.top(time_filter='month', limit=100))
        sampled = random.sample(top_posts, k=3) if len(top_posts) >= 3 else top_posts
        for post in sampled:
            result.append({
                "subreddit": sub,
                "title": post.title,
                "selftext": post.selftext[:500],
                "url": post.url,
                "score": post.score
            })
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("✅ Posts refreshed.")

# 每小时整点自动抓一次
schedule.every().hour.at(":00").do(fetch_and_save_posts)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(60)

threading.Thread(target=run_scheduler, daemon=True).start()
fetch_and_save_posts()

@app.route('/')
def home():
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            posts = json.load(f)
    except:
        posts = []
    html = """
    <html>
    <head>
        <title>Hourly Reddit Highlights</title>
        <style>
            body { font-family: sans-serif; padding: 40px; }
            h1 { color: #cc0000; }
            .post { margin-bottom: 50px; border-bottom: 1px solid #ccc; padding-bottom: 30px; }
            .meta { font-size: 0.9em; color: #666; }
        </style>
    </head>
    <body>
        <h1>Hourly Reddit Highlights</h1>
        {% for post in posts %}
            <div class="post">
                <h2>{{ post.title }}</h2>
                <p class="meta">Subreddit: {{ post.subreddit }} | Score: {{ post.score }}</p>
                <p>{{ post.selftext }}</p>
                <p><a href="{{ post.url }}" target="_blank">[Read more]</a></p>
            </div>
        {% endfor %}
    </body>
    </html>
    """
    return render_template_string(html, posts=posts)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
