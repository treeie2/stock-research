#!/usr/bin/env python3
"""
Phase 6: Railway 部署版 - 最小可运行版本
"""

from flask import Flask, render_template_string, jsonify, request
import os
from datetime import datetime

app = Flask(__name__)

# 示例数据
SAMPLE_DATA = {
    "stats": {
        "total_stocks": 1502,
        "total_mentions": 4610,
        "total_companies": 1502,
        "total_articles": 731,
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M")
    },
    "top_10": [
        {"rank": 1, "code": "300024", "name": "机器人", "mentions": 68, "with_target": 2, "concepts": ["机器人", "AI", "自动化"]},
        {"rank": 2, "code": "300308", "name": "中际旭创", "mentions": 27, "with_target": 1, "concepts": ["CPO", "光模块", "AI"]},
        {"rank": 3, "code": "300502", "name": "新易盛", "mentions": 25, "with_target": 1, "concepts": ["CPO", "光模块"]},
    ],
    "industry_distribution": {
        "沪市主板": 456,
        "深市主板": 415,
        "创业板": 405,
        "科创板": 226
    },
    "stocks": [
        {"code": "300024", "name": "机器人", "board": "创业板", "mention_count": 68, "concepts": ["机器人", "AI"]},
        {"code": "300308", "name": "中际旭创", "board": "创业板", "mention_count": 27, "concepts": ["CPO", "光模块"]},
    ]
}

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>个股研究数据库</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body class="bg-gray-50">
    <nav class="bg-white shadow-sm border-b sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 py-4">
            <div class="flex justify-between items-center">
                <h1 class="text-xl font-bold">📊 个股研究数据库</h1>
                <div class="space-x-4">
                    <a href="/" class="text-blue-600">仪表板</a>
                    <a href="/stocks" class="text-gray-600">股票列表</a>
                    <a href="/search" class="text-gray-600">搜索</a>
                </div>
            </div>
        </div>
    </nav>

    <main class="max-w-7xl mx-auto px-4 py-8">
        <div class="grid grid-cols-4 gap-6 mb-8">
            <div class="bg-white p-6 rounded-lg shadow">
                <div class="text-sm text-gray-600">股票池</div>
                <div class="text-3xl font-bold text-blue-600">{{ stats.total_stocks }}</div>
            </div>
            <div class="bg-white p-6 rounded-lg shadow">
                <div class="text-sm text-gray-600">有效提及</div>
                <div class="text-3xl font-bold text-green-600">{{ stats.total_mentions }}</div>
            </div>
            <div class="bg-white p-6 rounded-lg shadow">
                <div class="text-sm text-gray-600">覆盖公司</div>
                <div class="text-3xl font-bold text-purple-600">{{ stats.total_companies }}</div>
            </div>
            <div class="bg-white p-6 rounded-lg shadow">
                <div class="text-sm text-gray-600">文章数量</div>
                <div class="text-3xl font-bold text-orange-600">{{ stats.total_articles }}</div>
            </div>
        </div>

        <div class="bg-white rounded-lg shadow">
            <div class="px-6 py-4 border-b">
                <h2 class="text-lg font-semibold">📈 Top 10</h2>
            </div>
            <table class="min-w-full">
                <thead class="bg-gray-50">
                    <tr>
                        <th class="px-6 py-3 text-left text-xs text-gray-500">排名</th>
                        <th class="px-6 py-3 text-left text-xs text-gray-500">股票</th>
                        <th class="px-6 py-3 text-left text-xs text-gray-500">提及</th>
                        <th class="px-6 py-3 text-left text-xs text-gray-500">概念</th>
                    </tr>
                </thead>
                <tbody>
                    {% for stock in top_10 %}
                    <tr class="border-b hover:bg-gray-50">
                        <td class="px-6 py-4">{{ stock.rank }}</td>
                        <td class="px-6 py-4">
                            <a href="/stock/{{ stock.code }}" class="text-blue-600">
                                {{ stock.name }} ({{ stock.code }})
                            </a>
                        </td>
                        <td class="px-6 py-4">{{ stock.mentions }}</td>
                        <td class="px-6 py-4">
                            {% for c in stock.concepts %}
                            <span class="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded mr-1">{{ c }}</span>
                            {% endfor %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </main>
</body>
</html>
"""

STOCKS_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>股票列表</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50">
    <nav class="bg-white border-b">
        <div class="max-w-7xl mx-auto px-4 py-4 flex justify-between">
            <h1 class="text-xl font-bold">📊 个股研究数据库</h1>
            <div class="space-x-4">
                <a href="/" class="text-gray-600">仪表板</a>
                <a href="/stocks" class="text-blue-600">股票列表</a>
            </div>
        </div>
    </nav>
    <main class="max-w-7xl mx-auto px-4 py-8">
        <h1 class="text-2xl font-bold mb-6">📋 股票列表</h1>
        <div class="bg-white rounded-lg shadow">
            <table class="min-w-full">
                <thead class="bg-gray-50">
                    <tr>
                        <th class="px-6 py-3 text-left">代码</th>
                        <th class="px-6 py-3 text-left">名称</th>
                        <th class="px-6 py-3 text-left">板块</th>
                        <th class="px-6 py-3 text-left">提及</th>
                    </tr>
                </thead>
                <tbody>
                    {% for stock in stocks %}
                    <tr class="border-b">
                        <td class="px-6 py-4 font-mono">{{ stock.code }}</td>
                        <td class="px-6 py-4">
                            <a href="/stock/{{ stock.code }}" class="text-blue-600">{{ stock.name }}</a>
                        </td>
                        <td class="px-6 py-4">{{ stock.board }}</td>
                        <td class="px-6 py-4">{{ stock.mention_count }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </main>
</body>
</html>
"""

STOCK_DETAIL_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{{ code }} - 个股详情</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body class="bg-gray-50">
    <nav class="bg-white border-b">
        <div class="max-w-7xl mx-auto px-4 py-4 flex justify-between">
            <h1 class="text-xl font-bold">📊 个股研究数据库</h1>
            <a href="/" class="text-gray-600">仪表板</a>
        </div>
    </nav>
    <main class="max-w-7xl mx-auto px-4 py-8">
        <div id="loading" class="text-center py-12">
            <i class="fas fa-spinner fa-spin text-4xl text-blue-600"></i>
            <p class="mt-4">加载中...</p>
        </div>
        <div id="content" class="hidden">
            <!-- 内容由 JS 动态加载 -->
        </div>
    </main>
    <script>
        const code = "{{ code }}";
        fetch('/api/stock/' + code)
            .then(r => r.json())
            .then(data => {
                document.getElementById('loading').classList.add('hidden');
                document.getElementById('content').classList.remove('hidden');
                document.getElementById('content').innerHTML = `
                    <div class="bg-white rounded-lg shadow p-6 mb-6">
                        <h1 class="text-2xl font-bold mb-4">\${data.basic.name} (\${data.basic.code})</h1>
                        <div class="grid grid-cols-4 gap-4">
                            <div><div class="text-sm text-gray-600">代码</div><div class="text-xl font-bold">\${data.basic.code}</div></div>
                            <div><div class="text-sm text-gray-600">提及</div><div class="text-xl font-bold text-green-600">\${data.total_mentions}</div></div>
                            <div><div class="text-sm text-gray-600">板块</div><div class="text-xl font-bold">\${data.basic.board || '-'}</div></div>
                            <div><div class="text-sm text-gray-600">行业</div><div class="text-xl font-bold">\${data.basic.industry || '-'}</div></div>
                        </div>
                    </div>
                    <div class="grid grid-cols-2 gap-6 mb-6">
                        <div class="bg-white rounded-lg shadow p-6">
                            <h2 class="font-bold mb-4">🏷️ 概念</h2>
                            <div class="flex flex-wrap gap-2">
                                \${data.layer2.concepts.map(c => '<span class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">'+c+'</span>').join('')}
                            </div>
                        </div>
                        <div class="bg-white rounded-lg shadow p-6">
                            <h2 class="font-bold mb-4">📦 产品</h2>
                            <div class="flex flex-wrap gap-2">
                                \${data.layer2.products.map(p => '<span class="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm">'+p+'</span>').join('')}
                            </div>
                        </div>
                    </div>
                    <div class="bg-white rounded-lg shadow p-6">
                        <h2 class="font-bold mb-4">📰 提及记录</h2>
                        <table class="min-w-full">
                            <thead><tr class="border-b"><th class="text-left py-2">文章</th><th>行业</th><th>概念</th></tr></thead>
                            <tbody>
                                \${data.mentions.map(m => `
                                    <tr class="border-b">
                                        <td class="py-3">\${m.source?.title || '-'}</td>
                                        <td>\${m.classification?.level1 || '-'}</td>
                                        <td>\${(m.concepts||[]).join(', ')}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                `;
            });
    </script>
</body>
</html>
"""

SEARCH_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>搜索</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50">
    <nav class="bg-white border-b">
        <div class="max-w-7xl mx-auto px-4 py-4 flex justify-between">
            <h1 class="text-xl font-bold">📊 个股研究数据库</h1>
            <a href="/" class="text-gray-600">仪表板</a>
        </div>
    </nav>
    <main class="max-w-7xl mx-auto px-4 py-8">
        <h1 class="text-2xl font-bold mb-6">🔍 搜索</h1>
        <div class="bg-white rounded-lg shadow p-6">
            <div class="flex gap-4 mb-6">
                <input type="text" id="search-input" placeholder="输入关键词..." 
                       class="flex-1 px-4 py-2 border rounded-lg">
                <button onclick="search()" class="px-6 py-2 bg-blue-600 text-white rounded-lg">搜索</button>
            </div>
            <div id="results"></div>
        </div>
    </main>
    <script>
        async function search() {
            const q = document.getElementById('search-input').value;
            const r = await fetch('/api/search?q=' + encodeURIComponent(q));
            const data = await r.json();
            document.getElementById('results').innerHTML = data.results.map(s => `
                <div class="p-4 border-b">
                    <a href="/stock/\${s.code}" class="text-blue-600 font-bold">\${s.name} (\${s.code})</a>
                    <span class="text-gray-600 ml-4">\${s.mention_count} 次提及</span>
                </div>
            `).join('');
        }
        document.getElementById('search-input').addEventListener('keypress', e => {
            if (e.key === 'Enter') search();
        });
    </script>
</body>
</html>
"""

# 路由
@app.route('/')
def dashboard():
    return render_template_string(DASHBOARD_HTML, **SAMPLE_DATA)

@app.route('/stocks')
def stocks():
    return render_template_string(STOCKS_HTML, stocks=SAMPLE_DATA["stocks"])

@app.route('/stock/<code>')
def stock_detail(code):
    return render_template_string(STOCK_DETAIL_HTML, code=code)

@app.route('/search')
def search():
    return render_template_string(SEARCH_HTML)

@app.route('/api/dashboard')
def api_dashboard():
    return jsonify(SAMPLE_DATA)

@app.route('/api/stocks')
def api_stocks():
    return jsonify({"stocks": SAMPLE_DATA["stocks"]})

@app.route('/api/stock/<code>')
def api_stock(code):
    # 示例数据
    data = {
        "basic": {"code": code, "name": "示例股票", "board": "创业板", "industry": "电子"},
        "layer2": {"concepts": ["AI", "机器人"], "products": ["产品 A"], "events": {}, "supply_chain": []},
        "mentions": [
            {"source": {"title": "文章 1"}, "classification": {"level1": "电子"}, "concepts": ["AI"]},
        ],
        "total_mentions": 1
    }
    return jsonify(data)

@app.route('/api/search')
def api_search():
    q = request.args.get('q', '')
    results = [s for s in SAMPLE_DATA["stocks"] if q in s["name"] or q in s["code"]]
    return jsonify({"results": results})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
