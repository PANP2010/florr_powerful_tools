"""
Florr.io 知识库组件
自动从 Wiki 获取并更新游戏数据
"""

import json
import requests
import time
import re
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from dataclasses import dataclass, asdict


WIKI_BASE_URL = "https://official-florrio.fandom.com"
WIKI_API_URL = f"{WIKI_BASE_URL}/api.php"

USER_AGENT = "FlorrKnowledgeBase/1.0"


@dataclass
class WikiEntry:
    title: str
    content: str
    url: str
    updated_at: str
    categories: List[str]


class FlorrKnowledgeBase:
    
    GAME_KEYWORDS = [
        "Ant", "Bee", "Beetle", "Centipede", "Crab", "Fly", "Hornet",
        "Jellyfish", "Ladybug", "Mantis", "Moth", "Scorpion", "Spider",
        "Wasp", "Worm", "Bubble", "Cactus", "Rock", "Shell", "Petal",
        "Mob", "Area", "Garden", "Desert", "Ocean", "Jungle", "Hel",
        "Factory", "Sewers", "Ant Hell", "Fire Ant", "Termite",
        "AFK", "Armor", "Health", "Damage", "Rarity", "Crafting",
        "Achievement", "Level", "Talent", "Build", "Strategy",
        "Air", "Ankh", "Amulet", "Basic", "Bone", "Bulb", "Bur",
        "Card", "Claw", "Clover", "Coin", "Corn", "Dice", "Disc",
        "Fangs", "Faster", "Glass", "Heavy", "Honey", "Iris", "Jelly",
        "Leaf", "Light", "Lotus", "Magnet", "Mark", "Mimic", "Moon",
        "Nazar", "Orb", "Pearl", "Peas", "Plank", "Pollen", "Poo",
        "Powder", "Relic", "Rice", "Root", "Rose", "Rubber", "Salt",
        "Sand", "Shovel", "Soil", "Sponge", "Square", "Stick", "Tomato",
        "Totem", "Wax", "Web", "Wing", "Yucca", "Yggdrasil",
        "Gambler", "Trader", "Oracle", "Titan", "Assembler", "Dandelion",
        "Digger", "Dummy", "Firefly", "Leech", "Roach", "Sandstorm",
        "Starfish", "Bush", "Bumble", "Leafbug", "Laser", "Stinger",
        "Egg", "Queen", "Soldier", "Worker", "Baby", "Overmind", "Mound",
    ]
    
    EXCLUDE_KEYWORDS = [
        "Template:", "Category:", "User:", "User talk:", "Talk:",
        "File:", "MediaWiki:", "Help:", "Project:", "Disambiguation",
        "Article Template", "Petal Template", "Mob Template", "Area Template",
        "Drop ", "/Drop ", "/doc", "/test", "Draft:", "Sandbox",
        "Fantasy", "Fantasty", "Fanon", "Fan-made", "Fan Made",
        "Custom", "Idea", "Concept", "Suggestion", "Proposal",
        "Evil Eye", "Fan Art", "Fanart", "OC", "Original Character",
        "Joke", "Meme", "Parody", "April Fools", "Fake",
    ]
    
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.wiki_file = self.data_dir / "wiki.json"
        self.index_file = self.data_dir / "index.json"
        self.metadata_file = self.data_dir / "metadata.json"
        
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
    
    def _api_request(self, params: dict) -> Optional[dict]:
        try:
            response = self.session.get(WIKI_API_URL, params=params, timeout=30)
            return response.json()
        except Exception as e:
            print(f"API 请求失败: {e}")
            return None
    
    def get_all_pages(self) -> List[str]:
        pages = []
        apcontinue = None
        
        print("获取所有 Wiki 页面...")
        
        while True:
            params = {
                "action": "query",
                "list": "allpages",
                "aplimit": 500,
                "format": "json",
            }
            
            if apcontinue:
                params["apcontinue"] = apcontinue
            
            data = self._api_request(params)
            
            if data and "query" in data:
                for page in data["query"]["allpages"]:
                    pages.append(page["title"])
            
            if data and "continue" in data:
                apcontinue = data["continue"]["apcontinue"]
            else:
                break
        
        print(f"共找到 {len(pages)} 个页面")
        return pages
    
    def get_page_content(self, title: str) -> Optional[WikiEntry]:
        params = {
            "action": "query",
            "prop": "revisions|categories",
            "rvprop": "content|timestamp",
            "rvslots": "main",
            "cllimit": 50,
            "format": "json",
            "titles": title,
        }
        
        data = self._api_request(params)
        
        if not data or "query" not in data:
            return None
        
        pages = data["query"]["pages"]
        for page_id, page_data in pages.items():
            if "revisions" in page_data:
                content = page_data["revisions"][0]["slots"]["main"]["*"]
                timestamp = page_data["revisions"][0].get("timestamp", "")
                
                if content.startswith("#REDIRECT"):
                    return None
                
                categories = []
                if "categories" in page_data:
                    categories = [c["title"].replace("Category:", "") 
                                  for c in page_data["categories"]]
                
                return WikiEntry(
                    title=title,
                    content=content,
                    url=f"{WIKI_BASE_URL}/wiki/{title.replace(' ', '_')}",
                    updated_at=timestamp,
                    categories=categories
                )
        
        return None
    
    def is_game_content(self, title: str) -> bool:
        title_lower = title.lower()
        
        for exclude in self.EXCLUDE_KEYWORDS:
            if exclude.lower() in title_lower:
                return False
        
        for keyword in self.GAME_KEYWORDS:
            if keyword.lower() in title_lower:
                return True
        
        return False
    
    def load_existing_data(self) -> Dict[str, WikiEntry]:
        existing = {}
        
        if self.wiki_file.exists():
            try:
                with open(self.wiki_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data:
                        entry = WikiEntry(
                            title=item.get("title", ""),
                            content=item.get("content", ""),
                            url=item.get("url", ""),
                            updated_at=item.get("updated_at", ""),
                            categories=item.get("categories", [])
                        )
                        existing[entry.title] = entry
                print(f"加载已有数据: {len(existing)} 个条目")
            except Exception as e:
                print(f"加载已有数据失败: {e}")
        
        return existing
    
    def build_index(self, entries: Dict[str, WikiEntry]):
        index = {
            "mobs": [],
            "petals": [],
            "areas": [],
            "mechanics": [],
            "other": []
        }
        
        for title, entry in entries.items():
            categorized = False
            content = entry.content
            categories_lower = [c.lower() for c in entry.categories]
            
            if "Mob Template Infobox" in content:
                index["mobs"].append(title)
                categorized = True
            elif "Petal Template Infobox" in content:
                index["petals"].append(title)
                categorized = True
            elif "Area Template Infobox" in content:
                index["areas"].append(title)
                categorized = True
            
            if not categorized:
                if "areas" in categories_lower or "ant areas" in categories_lower or "dungeons" in categories_lower:
                    index["areas"].append(title)
                    categorized = True
                elif "petals" in categories_lower:
                    index["petals"].append(title)
                    categorized = True
                elif "gameplay" in categories_lower or "mechanics" in categories_lower or "features" in categories_lower:
                    index["mechanics"].append(title)
                    categorized = True
                elif "mobs" in categories_lower:
                    index["mobs"].append(title)
                    categorized = True
            
            if not categorized:
                index["other"].append(title)
        
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
        
        print(f"索引构建完成: mobs={len(index['mobs'])}, petals={len(index['petals'])}, "
              f"areas={len(index['areas'])}, mechanics={len(index['mechanics'])}, "
              f"other={len(index['other'])}")
        
        return index
    
    def update(self, incremental: bool = True, max_pages: int = None) -> dict:
        print("=" * 60)
        print("Florr.io 知识库更新")
        print("=" * 60)
        
        existing = {}
        if incremental:
            existing = self.load_existing_data()
        
        all_pages = self.get_all_pages()
        
        relevant_pages = [p for p in all_pages if self.is_game_content(p)]
        print(f"过滤后相关页面: {len(relevant_pages)} 个")
        
        if max_pages:
            relevant_pages = relevant_pages[:max_pages]
            print(f"限制获取前 {max_pages} 个页面")
        
        entries = {}
        stats = {"new": 0, "updated": 0, "skipped": 0, "failed": 0}
        
        for i, title in enumerate(relevant_pages):
            if incremental and title in existing:
                entries[title] = existing[title]
                stats["skipped"] += 1
                continue
            
            status = "新增" if title not in existing else "更新"
            print(f"[{i+1}/{len(relevant_pages)}] {status}: {title}")
            
            entry = self.get_page_content(title)
            
            if entry:
                entries[title] = entry
                if title not in existing:
                    stats["new"] += 1
                else:
                    stats["updated"] += 1
            else:
                stats["failed"] += 1
            
            time.sleep(0.3)
        
        data = [asdict(e) for e in entries.values()]
        with open(self.wiki_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        self.build_index(entries)
        
        metadata = {
            "last_update": datetime.now().isoformat(),
            "total_entries": len(entries),
            "stats": stats,
            "source": WIKI_BASE_URL
        }
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        print("\n" + "=" * 60)
        print("更新完成!")
        print(f"  新增: {stats['new']} 个")
        print(f"  更新: {stats['updated']} 个")
        print(f"  跳过: {stats['skipped']} 个")
        print(f"  失败: {stats['failed']} 个")
        print(f"  总计: {len(entries)} 个条目")
        print(f"  输出: {self.wiki_file}")
        print("=" * 60)
        
        return metadata
    
    def search(self, query: str, category: str = None) -> List[WikiEntry]:
        if not self.wiki_file.exists():
            return []
        
        with open(self.wiki_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        results = []
        query_lower = query.lower()
        
        for item in data:
            if query_lower in item["title"].lower() or query_lower in item["content"].lower():
                entry = WikiEntry(**item)
                
                if category:
                    with open(self.index_file, 'r', encoding='utf-8') as f:
                        index = json.load(f)
                    if category in index and item["title"] not in index[category]:
                        continue
                
                results.append(entry)
        
        return results
    
    def get_entry(self, title: str) -> Optional[WikiEntry]:
        if not self.wiki_file.exists():
            return None
        
        with open(self.wiki_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for item in data:
            if item["title"].lower() == title.lower():
                return WikiEntry(**item)
        
        return None
    
    def get_stats(self) -> dict:
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Florr.io 知识库管理')
    parser.add_argument('command', choices=['update', 'search', 'get', 'stats'],
                        help='命令: update(更新), search(搜索), get(获取), stats(统计)')
    parser.add_argument('--query', '-q', help='搜索关键词')
    parser.add_argument('--category', '-c', help='分类过滤 (mobs/petals/areas/mechanics)')
    parser.add_argument('--full', '-f', action='store_true', help='全量更新')
    parser.add_argument('--max', '-m', type=int, help='最大获取页面数')
    parser.add_argument('--data-dir', '-d', default='./data', help='数据目录')
    
    args = parser.parse_args()
    
    kb = FlorrKnowledgeBase(args.data_dir)
    
    if args.command == 'update':
        kb.update(incremental=not args.full, max_pages=args.max)
    
    elif args.command == 'search':
        if not args.query:
            print("请提供搜索关键词: --query")
            return
        results = kb.search(args.query, args.category)
        print(f"找到 {len(results)} 个结果:")
        for entry in results[:10]:
            print(f"  - {entry.title}")
    
    elif args.command == 'get':
        if not args.query:
            print("请提供条目标题: --query")
            return
        entry = kb.get_entry(args.query)
        if entry:
            print(f"标题: {entry.title}")
            print(f"URL: {entry.url}")
            print(f"更新时间: {entry.updated_at}")
            print(f"分类: {entry.categories}")
            print(f"\n内容预览:\n{entry.content[:500]}...")
        else:
            print("未找到条目")
    
    elif args.command == 'stats':
        stats = kb.get_stats()
        print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
