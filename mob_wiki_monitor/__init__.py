"""
Florr.io Mob Wiki Monitor Module
可被其他程序调用的模块，也可单独运行
"""
import os
import sys
import json
import time
import hashlib
import argparse
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = BASE_DIR.parent

WIKI_BASE_URL = "https://official-florrio.fandom.com"
WIKI_MOBS_PAGE = f"{WIKI_BASE_URL}/wiki/Mobs"

MOBS_IMAGES_DIR = PROJECT_ROOT / "mobs_images"
LOGS_DIR = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "data"

MOBS_CACHE_FILE = DATA_DIR / "known_mobs.json"
UPDATE_HISTORY_FILE = DATA_DIR / "update_history.json"

MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 5
REQUEST_TIMEOUT_SECONDS = 30

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

MOB_NAME_MAPPING = {
    "Baby Ant": "ant_baby",
    "Baby Fire Ant": "fire_ant_baby",
    "Baby Termite": "termite_baby",
    "Worker Ant": "ant_worker",
    "Worker Fire Ant": "fire_ant_worker",
    "Worker Termite": "termite_worker",
    "Soldier Ant": "ant_soldier",
    "Soldier Fire Ant": "fire_ant_soldier",
    "Soldier Termite": "termite_soldier",
    "Queen Ant": "ant_queen",
    "Queen Fire Ant": "fire_ant_queen",
    "Ant Egg": "ant_egg",
    "Fire Ant Egg": "fire_ant_egg",
    "Termite Egg": "termite_egg",
    "Ant Hole": "ant_hole",
    "Fire Ant Burrow": "fire_ant_burrow",
    "Termite Mound": "termite_mound",
    "Termite Overmind": "termite_overmind",
    "Beetle (Hel)": "beetle_hel",
    "Beetle (Nazar)": "beetle_nazar",
    "Beetle (Mummy)": "beetle_mummy",
    "Beetle (Pharaoh)": "beetle_pharaoh",
    "Centipede (Desert)": "centipede_desert",
    "Centipede (Hel)": "centipede_hel",
    "Centipede (Jungle)": "centipede_evil",
    "Ladybug (Desert)": "ladybug_dark",
    "Ladybug (Jungle)": "ladybug_shiny",
    "Spider (Hel)": "spider_hel",
    "Wasp (Hel)": "wasp_hel",
    "Hel Beetle": "beetle_hel",
    "Hel Centipede": "centipede_hel",
    "Hel Spider": "spider_hel",
    "Hel Wasp": "wasp_hel",
    "Nazar Beetle": "beetle_nazar",
    "Mummy Beetle": "beetle_mummy",
    "Pharaoh Beetle": "beetle_pharaoh",
    "Jungle Centipede": "centipede_evil",
    "Desert Ladybug": "ladybug_dark",
    "Jungle Ladybug": "ladybug_shiny",
    "Magic Firefly": "firefly_magic",
    "Golden Leafbug": "leafbug_shiny",
    "Target Dummy": "dummy",
    "Mecha Flower": "mecha_flower",
    "Mecha Spider": "spider_mecha",
    "Mecha Wasp": "wasp_mecha",
    "Mecha Crab": "crab_mecha",
    "Worm guts": "worm_guts",
    "Trader": "trader",
    "Oracle": "oracle",
    "Titan": "titan",
    "Assembler": "assembler",
}

for name in ["Rock", "Cactus", "Ladybug", "Bee", "Beetle", "Hornet", "Centipede",
             "Square", "Spider", "Scorpion", "Sandstorm", "Bubble", "Bumble Bee",
             "Shell", "Starfish", "Crab", "Jellyfish", "Digger", "Sponge", "Leech",
             "Dandelion", "Fly", "Leafbug", "Mantis", "Moth", "Firefly", "Wasp",
             "Worm", "Gambler", "Barrel", "Bush", "Roach"]:
    if name not in MOB_NAME_MAPPING:
        MOB_NAME_MAPPING[name] = name.lower().replace(" ", "_")

IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg", ".gif", ".webp"]

for directory in [LOGS_DIR, DATA_DIR, MOBS_IMAGES_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


class MobWikiMonitor:
    """Florr.io Mob维基监测器"""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
        })
        self.known_mobs: Dict = {}
        self.local_mobs: Set[str] = set()
        self._load_cache()
        self._scan_local_mobs()
    
    def _log(self, message: str, level: str = "info"):
        if not self.verbose:
            return
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level.upper()}] {message}")
    
    def _load_cache(self):
        if MOBS_CACHE_FILE.exists():
            try:
                with open(MOBS_CACHE_FILE, "r", encoding="utf-8") as f:
                    self.known_mobs = json.load(f)
            except Exception as e:
                self._log(f"加载缓存失败: {e}", "warning")
    
    def _save_cache(self):
        try:
            with open(MOBS_CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.known_mobs, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self._log(f"保存缓存失败: {e}", "error")
    
    def _scan_local_mobs(self) -> Set[str]:
        for file_path in MOBS_IMAGES_DIR.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in IMAGE_EXTENSIONS:
                self.local_mobs.add(file_path.stem)
        self._log(f"本地mob图片数量: {len(self.local_mobs)}")
        return self.local_mobs
    
    def _make_request(self, url: str) -> Optional[requests.Response]:
        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
                response.raise_for_status()
                return response
            except requests.exceptions.Timeout:
                self._log(f"请求超时，重试 {attempt + 1}/{MAX_RETRIES}", "warning")
            except requests.exceptions.ConnectionError as e:
                self._log(f"连接错误: {e}", "warning")
            except requests.exceptions.HTTPError as e:
                self._log(f"HTTP错误: {e}", "error")
                if response.status_code == 404:
                    return None
            except Exception as e:
                self._log(f"请求异常: {e}", "error")
            
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY_SECONDS)
        return None
    
    def _normalize_mob_name(self, wiki_name: str) -> str:
        if wiki_name in MOB_NAME_MAPPING:
            return MOB_NAME_MAPPING[wiki_name]
        
        normalized = wiki_name.lower()
        normalized = normalized.replace(" ", "_")
        normalized = normalized.replace("(", "").replace(")", "")
        normalized = re.sub(r'_+', '_', normalized)
        return normalized.strip("_")
    
    def _get_best_image_url(self, url: str) -> str:
        if "/scale-to-width-down/" in url:
            return re.sub(r'/scale-to-width-down/\d+', '', url)
        if "/thumb/" in url:
            match = re.match(r'(.*?/thumb/[^/]+/[^/]+/[^/]+)/[^/]+$', url)
            if match:
                return match.group(1)
        return url
    
    def fetch_mobs_list(self) -> List[Dict]:
        """从维基获取mob列表"""
        self._log(f"正在获取维基mob列表...")
        
        api_url = f"{WIKI_BASE_URL}/api.php"
        params = {
            "action": "parse",
            "page": "Mobs",
            "prop": "text",
            "format": "json",
            "formatversion": "2",
            "origin": "*"
        }
        
        try:
            response = self.session.get(api_url, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
            self._log(f"响应状态码: {response.status_code}", "debug")
            
            if response.status_code != 200:
                self._log(f"HTTP错误: {response.status_code}", "error")
                return []
            
            try:
                data = response.json()
            except Exception as json_err:
                self._log(f"JSON解析失败，响应内容前200字符: {response.text[:200]}", "error")
                return []
            
            if "parse" not in data:
                self._log(f"API返回格式异常: {list(data.keys())}", "error")
                return []
            
            html = data["parse"]["text"]
            soup = BeautifulSoup(html, "html.parser")
            mobs = []
            
            tables = soup.find_all("table", class_=["wikitable", "article-table"])
            
            for table in tables:
                rows = table.find_all("tr")
                for row in rows:
                    cells = row.find_all(["td", "th"])
                    if len(cells) >= 1:
                        name_cell = cells[0]
                        link = name_cell.find("a")
                        if link and link.get("href"):
                            mob_name = link.get_text(strip=True)
                            if mob_name and mob_name not in ["Name", "Mobs", "Mob"]:
                                mobs.append({
                                    "name": mob_name,
                                    "wiki_url": urljoin(WIKI_BASE_URL, link["href"]),
                                    "normalized_name": self._normalize_mob_name(mob_name)
                                })
            
            self._log(f"从维基找到 {len(mobs)} 个mob")
            return mobs
            
        except Exception as e:
            self._log(f"API请求失败: {e}", "error")
            return []
    
    def fetch_mob_image(self, mob_name: str) -> Optional[str]:
        """获取单个mob的图片URL"""
        wiki_name = mob_name.replace(" ", "_")
        if mob_name in ["Rock", "Cactus", "Bubble", "Dandelion", "Shell", 
                        "Starfish", "Sponge", "Square", "Worm"]:
            wiki_name += "_(Mob)"
        
        api_url = f"{WIKI_BASE_URL}/api.php"
        params = {
            "action": "parse",
            "page": wiki_name,
            "prop": "text",
            "format": "json",
            "formatversion": "2"
        }
        
        try:
            response = self.session.get(api_url, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
            response.raise_for_status()
            data = response.json()
            
            if "parse" not in data:
                return None
            
            soup = BeautifulSoup(data["parse"]["text"], "html.parser")
            
            for img in soup.find_all("img"):
                src = img.get("src") or img.get("data-src")
                if src and "static.wikia.nocookie.net" in src:
                    return self._get_best_image_url(src)
            
            return None
            
        except Exception as e:
            self._log(f"获取图片失败 {mob_name}: {e}", "warning")
            return None
    
    def download_image(self, url: str, save_path: Path) -> bool:
        """下载图片到指定路径"""
        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.get(url, timeout=REQUEST_TIMEOUT_SECONDS, stream=True)
                response.raise_for_status()
                
                with open(save_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                self._log(f"图片下载成功: {save_path.name}")
                return True
                
            except Exception as e:
                self._log(f"下载失败 (尝试 {attempt + 1}/{MAX_RETRIES}): {e}", "warning")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY_SECONDS)
        
        return False
    
    def check_updates(self) -> Dict:
        """检查维基更新，返回新增的mob"""
        self._log("=" * 50)
        self._log("开始检查维基更新...")
        
        result = {
            "new_mobs": [],
            "existing_mobs": [],
            "total_wiki_mobs": 0,
            "total_local_mobs": len(self.local_mobs),
            "check_time": datetime.now().isoformat()
        }
        
        wiki_mobs = self.fetch_mobs_list()
        result["total_wiki_mobs"] = len(wiki_mobs)
        
        for mob in wiki_mobs:
            normalized = mob["normalized_name"]
            if normalized not in self.local_mobs:
                result["new_mobs"].append(mob)
                self._log(f"发现新mob: {mob['name']} -> {normalized}")
            else:
                result["existing_mobs"].append(mob)
        
        self._log(f"检查完成: 维基 {len(wiki_mobs)} 个, 本地 {len(self.local_mobs)} 个, 新增 {len(result['new_mobs'])} 个")
        return result
    
    def download_new_mobs(self, check_result: Dict = None) -> Dict:
        """下载新增的mob图片"""
        if check_result is None:
            check_result = self.check_updates()
        
        result = {
            "downloaded": [],
            "failed": [],
            "skipped": []
        }
        
        new_mobs = check_result.get("new_mobs", [])
        
        if not new_mobs:
            self._log("没有新的mob需要下载")
            return result
        
        self._log(f"开始下载 {len(new_mobs)} 个新mob图片...")
        
        for mob in new_mobs:
            mob_name = mob["name"]
            normalized = mob["normalized_name"]
            
            self._log(f"正在处理: {mob_name}")
            
            image_url = self.fetch_mob_image(mob_name)
            if not image_url:
                self._log(f"无法获取图片URL: {mob_name}", "warning")
                result["failed"].append({"name": mob_name, "reason": "no_image_url"})
                continue
            
            save_path = MOBS_IMAGES_DIR / f"{normalized}.png"
            
            if self.download_image(image_url, save_path):
                result["downloaded"].append(normalized)
                self.local_mobs.add(normalized)
                self.known_mobs[normalized] = {
                    "wiki_name": mob_name,
                    "image_url": image_url,
                    "download_time": datetime.now().isoformat()
                }
            else:
                result["failed"].append({"name": mob_name, "reason": "download_failed"})
        
        self._save_cache()
        self._log(f"下载完成: 成功 {len(result['downloaded'])} 个, 失败 {len(result['failed'])} 个")
        
        return result
    
    def run(self) -> Dict:
        """执行完整检查和下载流程"""
        check_result = self.check_updates()
        download_result = self.download_new_mobs(check_result)
        
        return {
            "check": check_result,
            "download": download_result
        }
    
    def get_status(self) -> Dict:
        """获取当前状态"""
        return {
            "local_mobs_count": len(self.local_mobs),
            "known_mobs_count": len(self.known_mobs),
            "local_mobs": sorted(list(self.local_mobs))
        }


def check_and_update(verbose: bool = True) -> Dict:
    """便捷函数：检查并更新mob图片"""
    monitor = MobWikiMonitor(verbose=verbose)
    return monitor.run()


def get_new_mobs(verbose: bool = True) -> List[Dict]:
    """便捷函数：仅检查新mob，不下载"""
    monitor = MobWikiMonitor(verbose=verbose)
    result = monitor.check_updates()
    return result.get("new_mobs", [])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Florr.io Mob维基监测器")
    parser.add_argument("--check", action="store_true", help="仅检查新mob，不下载")
    parser.add_argument("--download", action="store_true", help="检查并下载新mob图片")
    parser.add_argument("--status", action="store_true", help="显示当前状态")
    parser.add_argument("-q", "--quiet", action="store_true", help="静默模式")
    
    args = parser.parse_args()
    
    monitor = MobWikiMonitor(verbose=not args.quiet)
    
    if args.status:
        status = monitor.get_status()
        print(f"\n本地mob数量: {status['local_mobs_count']}")
        print(f"已知mob数量: {status['known_mobs_count']}")
        if not args.quiet:
            print(f"\n本地mob列表:\n{', '.join(status['local_mobs'])}")
    
    elif args.check:
        result = monitor.check_updates()
        print(f"\n维基mob总数: {result['total_wiki_mobs']}")
        print(f"本地mob总数: {result['total_local_mobs']}")
        print(f"新增mob数量: {len(result['new_mobs'])}")
        if result['new_mobs']:
            print("\n新增mob列表:")
            for mob in result['new_mobs']:
                print(f"  - {mob['name']} ({mob['normalized_name']})")
    
    elif args.download:
        result = monitor.run()
        print(f"\n下载完成: {len(result['download']['downloaded'])} 个")
        print(f"下载失败: {len(result['download']['failed'])} 个")
    
    else:
        parser.print_help()
