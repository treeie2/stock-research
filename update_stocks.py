#!/usr/bin/env python3
"""
Update stocks_master.json with new stock data.
Adds new stocks or merges articles for existing stocks.
"""
import json
from pathlib import Path
from datetime import datetime

MASTER_FILE = Path(__file__).parent / 'data' / 'master' / 'stocks_master.json'


def update_stocks(new_stocks_data):
    """
    Update stocks_master.json with new stock data.
    
    Args:
        new_stocks_data: dict with "stocks" key containing list of stock objects
    """
    print("🔄 Updating stocks_master.json...")
    
    # Load existing master data
    with open(MASTER_FILE, 'r', encoding='utf-8') as f:
        master_data = json.load(f)
    
    master_stocks = master_data.get('stocks', [])
    existing_codes = {s.get('code'): s for s in master_stocks}
    
    new_count = 0
    updated_count = 0
    
    for new_stock in new_stocks_data.get('stocks', []):
        code = new_stock.get('code')
        name = new_stock.get('name')
        
        if not code:
            print(f"  ⚠️ Skipping stock without code: {name}")
            continue
        
        if code in existing_codes:
            # Existing stock - merge articles
            master_stock = existing_codes[code]
            
            # Ensure articles array exists
            if 'articles' not in master_stock:
                master_stock['articles'] = []
            
            # Add new articles
            for new_article in new_stock.get('articles', []):
                # Check if article already exists (by source URL)
                source = new_article.get('source', '')
                exists = any(a.get('source') == source for a in master_stock['articles'])
                
                if not exists:
                    master_stock['articles'].insert(0, new_article)
                    print(f"  ➕ Added article to {code} {name}")
                else:
                    print(f"  ⏭️ Article already exists for {code} {name}")
            
            # Update mention count
            master_stock['mention_count'] = master_stock.get('mention_count', 0) + new_stock.get('mention_count', 0)
            
            # Update last_updated
            master_stock['last_updated'] = datetime.now().strftime('%Y-%m-%d')
            
            updated_count += 1
        else:
            # New stock - add with default fields
            stock_entry = {
                'name': name,
                'code': code,
                'board': new_stock.get('board', 'SZ' if code.startswith('0') or code.startswith('3') else 'SH'),
                'industry': new_stock.get('industry', ''),
                'concepts': new_stock.get('concepts', []),
                'products': new_stock.get('products', []),
                'core_business': new_stock.get('core_business', []),
                'industry_position': new_stock.get('industry_position', []),
                'chain': new_stock.get('chain', []),
                'partners': new_stock.get('partners', []),
                'mention_count': new_stock.get('mention_count', 1),
                'articles': new_stock.get('articles', []),
                'last_updated': datetime.now().strftime('%Y-%m-%d')
            }
            master_stocks.append(stock_entry)
            print(f"  ✨ Added new stock: {code} {name}")
            new_count += 1
    
    # Save updated data
    master_data['stocks'] = master_stocks
    master_data['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    with open(MASTER_FILE, 'w', encoding='utf-8') as f:
        json.dump(master_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Complete! Added {new_count} new stocks, updated {updated_count} existing stocks.")
    print(f"📊 Total stocks in database: {len(master_stocks)}")
    
    return {'new': new_count, 'updated': updated_count}


if __name__ == '__main__':
    # Example usage with your data
    example_data = {
        "stocks": [
            {
                "name": "汇绿生态",
                "code": "001267",
                "board": "SZ",
                "industry": "",
                "concepts": [],
                "products": [],
                "core_business": [],
                "industry_position": [],
                "chain": [],
                "partners": [],
                "mention_count": 1,
                "articles": [
                    {
                        "title": "",
                        "date": "2026-03-30",
                        "source": "https://mp.weixin.qq.com/s/WC9ztrSmpyth3o193tWcSQ",
                        "accidents": [],
                        "insights": [
                            "中信通信观点：二线光投资首先看物料锁定能力（DSP、CW、EML、硅光芯片、隔离器等），其次看1.6T出海进度与订单总量，最后看产业链纵横向布局。",
                            "文中表述：'仍然首推汇绿生态'。"
                        ],
                        "key_metrics": [
                            "行业需求口径：1.6T光模块26/27年需求分别约3000万、7000-8000万只；800G光模块保持年化约5000万只需求。"
                        ],
                        "target_valuation": []
                    }
                ]
            }
            # Add more stocks here...
        ]
    }
    
    # Uncomment to run with example data:
    # update_stocks(example_data)
    
    print("Usage: Import this module and call update_stocks(your_data)")
