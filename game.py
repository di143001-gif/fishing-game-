import pygame
import random
import time
import json
import sys
import os
from math import log

# --- CẤU HÌNH MÔI TRƯỜNG WEB ---
WEB_ENVIRONMENT = True
pygame.init()

# Cấu hình màn hình cho web
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 1000
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Cắm Câu Cá Lóc - Web Version")

# Giảm FPS cho web
FPS = 20
clock = pygame.time.Clock()

# --- QUẢN LÝ BẢNG XẾP HẠNG ---
class LeaderboardManager:
    def __init__(self):
        self.leaderboard_file = "leaderboard.json"
        self.leaderboard = self.load_leaderboard()
    
    def load_leaderboard(self):
        """Tải bảng xếp hạng từ file"""
        try:
            if os.path.exists(self.leaderboard_file):
                with open(self.leaderboard_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except:
            return []
    
    def save_leaderboard(self):
        """Lưu bảng xếp hạng vào file"""
        try:
            with open(self.leaderboard_file, 'w', encoding='utf-8') as f:
                json.dump(self.leaderboard, f, ensure_ascii=False, indent=2)
            return True
        except:
            return False
    
    def submit_score(self, player_name, level, coins, fish_count):
        """Gửi điểm số lên bảng xếp hạng"""
        try:
            player_data = {
                "name": player_name,
                "level": level,
                "coins": coins,
                "fish_count": fish_count,
                "timestamp": time.time(),
                "total_score": level * 100 + coins + fish_count * 10
            }
            
            # Tìm xem player đã có trong bảng xếp hạng chưa
            existing_index = -1
            for i, player in enumerate(self.leaderboard):
                if player["name"] == player_name:
                    existing_index = i
                    break
            
            # Nếu đã tồn tại, cập nhật nếu điểm cao hơn
            if existing_index >= 0:
                if player_data["total_score"] > self.leaderboard[existing_index]["total_score"]:
                    self.leaderboard[existing_index] = player_data
            else:
                # Thêm player mới
                self.leaderboard.append(player_data)
            
            # Sắp xếp theo điểm số
            self.leaderboard.sort(key=lambda x: x["total_score"], reverse=True)
            
            # Giới hạn top 50
            self.leaderboard = self.leaderboard[:50]
            
            # Lưu bảng xếp hạng
            self.save_leaderboard()
            
            return True, "Điểm số đã được cập nhật!"
        except Exception as e:
            return False, f"Lỗi: {str(e)}"
    
    def get_leaderboard(self, limit=10):
        """Lấy bảng xếp hạng"""
        return self.leaderboard[:limit]

# Khởi tạo leaderboard manager
leaderboard_manager = LeaderboardManager()

# --- ẢNH NỀN ---
background_image = None
background_rect = None

def load_image_web_safe(filename):
    """Load ảnh an toàn cho web environment"""
    try:
        paths_to_try = [
            filename,
            f"./{filename}",
            f"assets/{filename}",
            f"images/{filename}"
        ]
        
        for path in paths_to_try:
            try:
                if os.path.exists(path):
                    img = pygame.image.load(path)
                    print(f"Đã load ảnh từ: {path}")
                    return img
            except:
                continue
                
        print(f"Không thể load ảnh: {filename}")
        return None
    except Exception as e:
        print(f"Lỗi load ảnh {filename}: {e}")
        return None

# Thử load ảnh nền
background_image = load_image_web_safe("background.jpg")
if background_image:
    background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    background_rect = background_image.get_rect()
    print("Đã load ảnh nền thành công!")
else:
    print("Sử dụng màu nền mặc định")
    background_image = None

# --- HẰNG SỐ GAME ---
GAME_SAVE_FILE = "fishing_save.json"
MAX_RODS = 2 
NUM_SLOTS = 10 
STEAL_COST = 20 
MAX_HEALTH = 100 
MARKET_SLOT_COST = 10 
MARKET_SLOT_DURATION = 30 * 60

# --- SỰ KIỆN ---
EVENT_DURATION = 5 * 60
EVENT_COOLDOWN = 5 * 60
current_event = None
event_start_time = 0
event_end_time = 0
event_cooldown_end = 0
last_event_check_time = time.time()

# --- SỰ KIỆN GIÁNG SINH ---
CHRISTMAS_EVENT_DURATION = 7 * 24 * 60 * 60
CHRISTMAS_EVENT_START = None
CHRISTMAS_EVENT_END = None
is_christmas_event_active = False

# --- THIẾT LẬP BỐ CỤC ---
BUTTON_MARGIN_RATIO = 0.05 
BUTTON_MARGIN = int(SCREEN_WIDTH * BUTTON_MARGIN_RATIO) 
BUTTON_H = int(SCREEN_HEIGHT * 0.06)
TITLE_Y = int(SCREEN_HEIGHT * 0.04)
BACK_BUTTON_W = int(SCREEN_WIDTH * 0.3)
BUTTON_Y_STEP = BUTTON_H + int(SCREEN_HEIGHT * 0.02)

# --- MÀU SẮC ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN_BG = (10, 100, 10)
BLUE_WATER = (0, 70, 150)
YELLOW_BUTTON = (255, 200, 0)
RED_FISH = (200, 0, 0)
GRAY_INACTIVE = (100, 100, 100)
MENU_COLOR = (50, 50, 50)
EXP_COLOR = (0, 255, 255) 
HP_COLOR = (255, 0, 0) 
LOCKED_COLOR = (150, 50, 50) 
UPGRADE_BG_COLOR = (30, 30, 80)
COIN_COLOR = (255, 215, 0)
MARKET_COLOR = (180, 180, 0)
EVENT_COLOR = (255, 105, 180)
CHRISTMAS_COLOR = (255, 0, 0)

# --- FONTS ---
try:
    FONT_VERY_SMALL = pygame.font.SysFont('Arial', int(SCREEN_HEIGHT * 0.012))
    FONT_SMALL = pygame.font.SysFont('Arial', int(SCREEN_HEIGHT * 0.018)) 
    FONT_MEDIUM = pygame.font.SysFont('Arial', int(SCREEN_HEIGHT * 0.024)) 
    FONT_LARGE = pygame.font.SysFont('Arial', int(SCREEN_HEIGHT * 0.035)) 
except:
    FONT_VERY_SMALL = pygame.font.Font(None, int(SCREEN_HEIGHT * 0.012))
    FONT_SMALL = pygame.font.Font(None, int(SCREEN_HEIGHT * 0.018)) 
    FONT_MEDIUM = pygame.font.Font(None, int(SCREEN_HEIGHT * 0.024)) 
    FONT_LARGE = pygame.font.Font(None, int(SCREEN_HEIGHT * 0.035)) 

# --- CẦN CÂU ---
MAX_LEVEL_ROD = 10 
UPGRADE_COST_MULTIPLIER = 2 

ROD_TEMPLATES = {
    "Cần Tre": {
        "base_rate_bonus": 0.000, 
        "base_exp_bonus": 0.0, 
        "max_level": MAX_LEVEL_ROD, 
        "rate_per_level": 0.0005, 
        "exp_per_level": 0.02,
        "base_cast_time": 30, 
        "base_upgrade_cost": 100, 
        "buy_price": None 
    },
    "Cần Sắt": {
        "base_rate_bonus": 0.005, 
        "base_exp_bonus": 0.1, 
        "max_level": MAX_LEVEL_ROD, 
        "rate_per_level": 0.001,
        "exp_per_level": 0.03,
        "base_cast_time": 60, 
        "base_upgrade_cost": 200, 
        "buy_price": 10000 
    },
    "Cần Giáng Sinh": {
        "base_rate_bonus": 0.015, 
        "base_exp_bonus": 0.3, 
        "max_level": 1,
        "rate_per_level": 0.0, 
        "exp_per_level": 0.0,
        "base_cast_time": 90, 
        "base_upgrade_cost": 0, 
        "buy_price": None,
        "expiry_time": None
    }
}
DEFAULT_ROD_TEMPLATE = "Cần Tre"

# --- GIÁ CÁ ---
FISH_PRICE_PER_KG = {
    "Cá Lóc": 100, 
}

# --- VẬT PHẨM GIÁNG SINH ---
CHRISTMAS_ITEMS = {
    "Tất Giáng Sinh": {"type": "collectible", "weight": 0.1},
    "Mũ Giáng Sinh": {"type": "collectible", "weight": 0.2},
    "Kẹo Giáng Sinh": {"type": "collectible", "weight": 0.05}
}

CHRISTMAS_EXCHANGE_REQUIREMENT = {
    "Tất Giáng Sinh": 10,
    "Mũ Giáng Sinh": 10, 
    "Kẹo Giáng Sinh": 10,
    "Cá Lóc": 10.0
}

CHRISTMAS_EXCHANGE_SUCCESS_RATE = 0.05

# --- ĐỊA ĐIỂM ---
LOCATIONS = {
    "Khu Đồng Lớn": {
        "Rate_Per_Minute": 0.15,
        "required_level": 1, 
        "Channels": {
            "Kênh A": {},
            "Kênh B": {},
        }
    },
    "Khu Rừng Tràm": {
        "Rate_Per_Minute": 0.10,
        "required_level": 10, 
        "Channels": {
            "Kênh C": {},
            "Kênh D": {},
        }
    }
}

# --- BIẾN TOÀN CỤC ---
player_level = 1 
player_exp = 0
player_coins = 0 
player_name = "Ngư Phủ Làng Chài"
player_health = MAX_HEALTH
last_hp_regen_time = time.time() 
rods_inventory = [] 
fish_inventory = []
christmas_items_inventory = []

game_state = "MAIN_MENU" 
current_location = None
current_channel = None
message_display = None 
steal_slots_data = [] 
selected_rod_id = None 
fishing_slots = [{"slot_id": i, "rod_id": None} for i in range(NUM_SLOTS)]

fish_to_sell_selected_type = None 
fish_to_sell_quantity = 0 

market_slot_end_time = 0 
market_selling_fish = []
market_customer = None
last_customer_time = time.time()
CUSTOMER_SPAWN_INTERVAL = 10

christmas_exchange_selected = False

# --- HÀM LOGIC GAME ---

def check_christmas_event_status():
    global is_christmas_event_active, CHRISTMAS_EVENT_START, CHRISTMAS_EVENT_END
    
    now = time.time()
    
    if is_christmas_event_active and CHRISTMAS_EVENT_END and now >= CHRISTMAS_EVENT_END:
        end_christmas_event()
        return
    
    try:
        current_month = time.localtime(now).tm_mon
        current_day = time.localtime(now).tm_mday
        
        if not is_christmas_event_active and current_month == 12 and current_day >= 15:
            start_christmas_event()
    except:
        pass

def start_christmas_event():
    global is_christmas_event_active, CHRISTMAS_EVENT_START, CHRISTMAS_EVENT_END
    
    is_christmas_event_active = True
    CHRISTMAS_EVENT_START = time.time()
    CHRISTMAS_EVENT_END = CHRISTMAS_EVENT_START + CHRISTMAS_EVENT_DURATION
    
    display_message("SỰ KIỆN GIÁNG SINH AN LÀNH ĐÃ BẮT ĐẦU!", 5)
    display_message("Khi câu dính cá lóc, có 50% cơ hội nhận vật phẩm Giáng Sinh!", 5)

def end_christmas_event():
    global is_christmas_event_active, CHRISTMAS_EVENT_START, CHRISTMAS_EVENT_END
    
    is_christmas_event_active = False
    CHRISTMAS_EVENT_START = None
    CHRISTMAS_EVENT_END = None
    
    now = time.time()
    for rod in rods_inventory:
        if rod.get("template") == "Cần Giáng Sinh" and rod.get("expiry_time") and rod.get("expiry_time") < now:
            rod["status"] = "Đã hết hạn"
            for key in ["cast_time", "last_check_time", "location", "channel", "slot_index", "catch_data"]:
                if key in rod: del rod[key]
    
    display_message("Sự kiện Giáng Sinh đã kết thúc. Cảm ơn bạn đã tham gia!", 5)

def get_random_christmas_item():
    item_name = random.choice(list(CHRISTMAS_ITEMS.keys()))
    return item_name, CHRISTMAS_ITEMS[item_name]["weight"]

def add_christmas_item_to_inventory(item_name, weight):
    christmas_items_inventory.append({
        "name": item_name,
        "weight": weight,
        "type": "christmas_item"
    })

def get_christmas_items_summary():
    summary = {}
    for item in christmas_items_inventory:
        name = item['name']
        if name not in summary:
            summary[name] = {'count': 0, 'total_weight': 0.0}
        summary[name]['count'] += 1
        summary[name]['total_weight'] += item['weight']
    return summary

def can_exchange_christmas_gift():
    summary = get_christmas_items_summary()
    fish_summary = get_fish_inventory_summary()
    
    for item_name, required in CHRISTMAS_EXCHANGE_REQUIREMENT.items():
        if item_name == "Cá Lóc":
            continue
        if item_name not in summary or summary[item_name]['count'] < required:
            return False
    
    if "Cá Lóc" not in fish_summary or fish_summary["Cá Lóc"]['total_weight'] < CHRISTMAS_EXCHANGE_REQUIREMENT["Cá Lóc"]:
        return False
        
    return True

def exchange_christmas_gift():
    global player_coins, rods_inventory, fish_inventory, christmas_items_inventory
    
    if not can_exchange_christmas_gift():
        return False, "Không đủ vật phẩm để đổi quà Giáng Sinh!"
    
    for item_name, required in CHRISTMAS_EXCHANGE_REQUIREMENT.items():
        if item_name == "Cá Lóc":
            temp_fish_inventory = [fish for fish in fish_inventory]
            fish_to_remove = [fish for fish in temp_fish_inventory if fish['name'] == "Cá Lóc"]
            
            if len(fish_to_remove) < required:
                return False, "Lỗi: Không đủ cá Lóc!"
                
            removed_weight = 0
            removed_count = 0
            new_fish_inventory = []
            
            for fish in fish_inventory:
                if fish['name'] == "Cá Lóc" and removed_weight < CHRISTMAS_EXCHANGE_REQUIREMENT["Cá Lóc"]:
                    removed_weight += fish['weight']
                    removed_count += 1
                else:
                    new_fish_inventory.append(fish)
                    
            fish_inventory = new_fish_inventory
        else:
            items_to_remove = [item for item in christmas_items_inventory if item['name'] == item_name]
            if len(items_to_remove) < required:
                return False, f"Lỗi: Không đủ {item_name}!"
                
            kept_items = []
            removed_count = 0
            
            for item in christmas_items_inventory:
                if item['name'] == item_name and removed_count < required:
                    removed_count += 1
                else:
                    kept_items.append(item)
                    
            christmas_items_inventory = kept_items
    
    if random.random() < CHRISTMAS_EXCHANGE_SUCCESS_RATE:
        expiry_time = time.time() + (5 * 24 * 60 * 60)
        
        new_rod_id = max((r['id'] for r in rods_inventory), default=-1) + 1
        new_rod = {
            "id": new_rod_id,
            "status": "Trống", 
            "name": "Cần Giáng Sinh",
            "template": "Cần Giáng Sinh", 
            "level": 1, 
            "current_rate_bonus": ROD_TEMPLATES["Cần Giáng Sinh"]["base_rate_bonus"],    
            "total_rate_bonus": 0.0,       
            "current_exp_bonus": ROD_TEMPLATES["Cần Giáng Sinh"]["base_exp_bonus"],      
            "max_cast_minutes": ROD_TEMPLATES["Cần Giáng Sinh"]["base_cast_time"], 
            "total_time_bonus": 0,
            "expiry_time": expiry_time
        }
        rods_inventory.append(new_rod)
        
        return True, "CHÚC MỪNG! Bạn đã nhận được Cần Giáng Sinh (hạn dùng 5 ngày)!"
    else:
        rand_val = random.random()
        if rand_val < 0.4:
            coins = 5000
        elif rand_val < 0.65:
            coins = 10000
        elif rand_val < 0.85:
            coins = 20000
        elif rand_val < 0.95:
            coins = 30000
        else:
            coins = 50000
            
        player_coins += coins
        return True, f"Bạn nhận được {coins} Xu thay thế!"

def check_event_status():
    global current_event, event_start_time, event_end_time, event_cooldown_end, last_event_check_time
    
    now = time.time()
    
    if current_event and now >= event_end_time:
        display_message(f"Sự kiện {current_event['name']} đã kết thúc!", 5)
        current_event = None
        event_cooldown_end = now + EVENT_COOLDOWN
    
    if not current_event and now >= event_cooldown_end:
        if now - last_event_check_time >= 60:
            last_event_check_time = now
            start_random_event()
    
    check_christmas_event_status()

def start_random_event():
    global current_event, event_start_time, event_end_time
    
    rand_val = random.random()
    
    if rand_val < 0.10:
        current_event = {
            "name": "Cá Lóc Hoàng Kim",
            "description": "Tỉ lệ bắt được cá Lóc tăng 20%!",
            "effect": "boost_rate",
            "color": (255, 215, 0)
        }
    elif rand_val < 0.30:
        current_event = {
            "name": "Ngày Hội EXP", 
            "description": "Nhận thêm 50% EXP khi bắt cá!",
            "effect": "boost_exp",
            "color": (0, 255, 150)
        }
    elif rand_val < 0.35:
        current_event = {
            "name": "Ngày Sốt Giá",
            "description": "NPC trong chợ mua với giá cao hơn 50%!",
            "effect": "boost_market",
            "color": (200, 200, 200)
        }
    else:
        return
    
    event_start_time = time.time()
    event_end_time = event_start_time + EVENT_DURATION
    
    display_message(f"SỰ KIỆN: {current_event['name']} - {current_event['description']} (5 phút)", 5)

def get_event_multiplier(event_type):
    if not current_event:
        return 1.0
    
    if event_type == "rate" and current_event["effect"] == "boost_rate":
        return 1.2
    elif event_type == "exp" and current_event["effect"] == "boost_exp":
        return 1.5
    elif event_type == "market" and current_event["effect"] == "boost_market":
        return 1.5
    
    return 1.0

def get_upgrade_cost(rod):
    template = ROD_TEMPLATES.get(rod["template"])
    if not template: return None
    
    current_level = rod['level']
    base_cost = template['base_upgrade_cost']
    
    cost = base_cost * (UPGRADE_COST_MULTIPLIER ** (current_level - 1))
    return int(cost)

def display_message(text, duration=3):
    global message_display
    message_display = {"text": text, "start_time": time.time(), "duration": duration}

def update_message():
    global message_display
    if message_display and (time.time() - message_display["start_time"]) > message_display["duration"]:
        message_display = None

def exp_to_next_level(level):
    if level <= 0: return 0
    return int(100 * (level ** 2.0))

def check_level_up():
    global player_level, player_exp 
    while player_exp >= exp_to_next_level(player_level):
        exp_needed = exp_to_next_level(player_level)
        player_exp -= exp_needed
        player_level += 1
        display_message(f"Lên Cấp {player_level}! Kỹ năng câu cá tăng.")

def get_slot_rate(): 
    rates = [loc.get("Rate_Per_Minute", 0) for loc in LOCATIONS.values() if isinstance(loc, dict) and "Rate_Per_Minute" in loc]
    return max(rates) if rates else 0.0

def get_location_rate(loc_name):
    return LOCATIONS.get(loc_name, {}).get("Rate_Per_Minute", 0.0)

def check_fish(rate_per_minute, rod_rate_bonus=0, rod_exp_bonus=0):
    event_multiplier = get_event_multiplier("rate")
    adjusted_rate = rate_per_minute * event_multiplier
    
    weight = (1 - random.random()) ** 4 * 2.9 + 0.1
    
    exp_multiplier = get_event_multiplier("exp")
    exp_gained = int(weight * 50 * (1 + rod_exp_bonus) * exp_multiplier)
    
    christmas_item_gained = None
    if is_christmas_event_active and random.random() < 0.5:
        item_name, item_weight = get_random_christmas_item()
        christmas_item_gained = {"name": item_name, "weight": item_weight}
    
    return "Cá Lóc", round(weight, 2), exp_gained, christmas_item_gained

def calculate_rod_stats(template_name, level):
    template = ROD_TEMPLATES.get(template_name)
    if not template: return 0, 0, 0
    
    rate = template["base_rate_bonus"] + (level - 1) * template["rate_per_level"]
    exp = template["base_exp_bonus"] + (level - 1) * template["exp_per_level"]
    cast_time = template["base_cast_time"]
    
    return round(rate, 4), round(exp, 4), cast_time

def create_default_rod(id_num, template_name):
    rate, exp, cast_time = calculate_rod_stats(template_name, 1)
    return {
        "id": id_num, 
        "status": "Trống", 
        "name": template_name, 
        "template": template_name, 
        "level": 1, 
        "current_rate_bonus": rate,    
        "total_rate_bonus": 0.0,       
        "current_exp_bonus": exp,      
        "max_cast_minutes": cast_time, 
        "total_time_bonus": 0          
    }

def upgrade_rod(rod_id):
    global player_coins
    rod = next((r for r in rods_inventory if r["id"] == rod_id), None)
    
    if not rod: return False, "Cần câu không tồn tại!"
    template = ROD_TEMPLATES.get(rod["template"])
    if not template: return False, "Template cần câu lỗi!"
    if rod["status"] == "Đang Cắm": return False, "Cần câu đang được sử dụng!"
    
    if rod["level"] >= template.get("max_level", MAX_LEVEL_ROD):
        return False, "Đã đạt cấp tối đa!"
        
    cost = get_upgrade_cost(rod) 
    
    if player_coins < cost:
        return False, f"Không đủ Xu! Cần {cost} Xu để nâng cấp."
    
    player_coins -= cost
    
    upgrade_type = random.randint(0, 1) 
    upgrade_text = ""
    
    MIN_BONUS_RATE = 0.001
    MAX_BONUS_RATE = 0.005
    MIN_BONUS_TIME = 1
    MAX_BONUS_TIME = 5
    
    if upgrade_type == 0:
        rand_rate = random.random()
        biased_rate = rand_rate ** 10 
        rate_bonus = MIN_BONUS_RATE + biased_rate * (MAX_BONUS_RATE - MIN_BONUS_RATE)
        rate_bonus = round(rate_bonus, 4)
        
        rod["total_rate_bonus"] += rate_bonus
        upgrade_text = f"Tỉ lệ Dính Cá: +{rate_bonus * 100:.2f}%"
        
    else:
        rand_prob = random.random()
        time_bonus = 0
        
        if rand_prob < 0.70: time_bonus = 1
        elif rand_prob < 0.90: time_bonus = random.randint(2, 3)
        else: time_bonus = random.randint(4, MAX_BONUS_TIME)
            
        rod["total_time_bonus"] += time_bonus
        rod["max_cast_minutes"] += time_bonus
        upgrade_text = f"Thời gian Cắm Câu: +{time_bonus} phút"
        
    rod["level"] += 1
    rate_base, exp_base, _ = calculate_rod_stats(rod["template"], rod["level"])
    rod["current_rate_bonus"] = rate_base
    rod["current_exp_bonus"] = exp_base
    
    msg = f"Nâng cấp thành công! Cần {rod['name']} lên Lv {rod['level']}: {upgrade_text}. (Tốn {cost} Xu)"
    return True, msg

def buy_rod(template_name):
    global player_coins, MAX_RODS, rods_inventory
    template = ROD_TEMPLATES.get(template_name)
    if not template: return False, "Loại cần câu không tồn tại!"
    
    price = template.get("buy_price")
    if price is None: return False, "Cần câu này không được bán!"
    
    if player_coins < price:
        return False, f"Không đủ Xu! Cần {price} Xu để mua {template_name}."

    if len(rods_inventory) >= MAX_RODS:
         return False, f"Đã đạt giới hạn cần câu ({MAX_RODS} cần). Vui lòng nâng cấp sức chứa."
         
    player_coins -= price
    
    new_rod_id = max((r['id'] for r in rods_inventory), default=-1) + 1
    new_rod = create_default_rod(new_rod_id, template_name)
    rods_inventory.append(new_rod)
    
    return True, f"Mua thành công {template_name} với giá {price} Xu!"

def get_fish_inventory_summary():
    summary = {}
    for i, fish in enumerate(fish_inventory):
        fish_id = fish.get('id', i)
        fish['id'] = fish_id
        name = fish['name']
        if name not in summary:
            summary[name] = {'count': 0, 'total_weight': 0.0, 'items': []}
        summary[name]['count'] += 1
        summary[name]['total_weight'] += fish['weight']
        summary[name]['items'].append(fish)
    return summary

def sell_fish(fish_name, quantity):
    global player_coins, fish_inventory
    
    summary = get_fish_inventory_summary()
    if fish_name not in summary or quantity <= 0 or quantity > summary[fish_name]['count']:
        return False, "Số lượng cá bán không hợp lệ!"

    price_per_kg = FISH_PRICE_PER_KG.get(fish_name, 0)
    if price_per_kg == 0:
        return False, "Cá này không thể bán cho thương lái!"

    temp_fish_inventory = [fish for fish in fish_inventory]
    fish_to_sell_list = [fish for fish in temp_fish_inventory if fish['name'] == fish_name]
    
    if quantity > len(fish_to_sell_list):
        return False, "Số lượng bán không khớp với kho đồ!"
        
    fish_to_sell = fish_to_sell_list[:quantity]
    total_weight_kg = sum(f['weight'] for f in fish_to_sell)
    
    coin_multiplier = get_event_multiplier("coins")
    total_earnings = int(total_weight_kg * price_per_kg * coin_multiplier)

    player_coins += total_earnings
    
    new_fish_inventory = []
    sold_count = 0
    
    fish_to_sell_ids = [f.get('id', idx) for idx, f in enumerate(fish_to_sell)]
    
    for idx, fish in enumerate(fish_inventory):
        fish_id = fish.get('id', idx)
        
        if fish_name == fish['name'] and sold_count < quantity:
            sold_count += 1
        else:
            new_fish_inventory.append(fish)
            
    fish_inventory = new_fish_inventory

    bonus_text = ""
    if coin_multiplier > 1.0:
        bonus_text = f" (x{coin_multiplier} sự kiện)"
        
    return True, (f"Đã bán {quantity} con {fish_name} ({total_weight_kg:.2f} kg) "
            f"và nhận được {total_earnings} Xu.{bonus_text}")

def generate_fish_id():
    return int(time.time() * 1000) + random.randint(1, 1000)

def prepare_fish_inventory():
    for i, fish in enumerate(fish_inventory):
        if fish.get('id') is None:
            fish['id'] = generate_fish_id()

def check_for_customer():
    global market_customer, last_customer_time, market_selling_fish
    
    if market_customer: return
    if not market_selling_fish: return

    now = time.time()
    if now - last_customer_time < CUSTOMER_SPAWN_INTERVAL: return
    
    if random.random() < 0.2: 
        fish_to_buy = random.choice(market_selling_fish)
        price_per_kg = FISH_PRICE_PER_KG.get(fish_to_buy['name'], 0)
        merchant_value = fish_to_buy['weight'] * price_per_kg
        market_multiplier = get_event_multiplier("market")
        
        rand_val = random.random()
        max_multiplier = 1.5 * market_multiplier
        
        if rand_val < 0.3:
            offer_multiplier = random.uniform(0.70, 0.99)
            customer_name = random.choice(["Lái Buôn Keo Kiệt", "Bà Tám Kì Kèo"])
        elif rand_val < 0.7:
            offer_multiplier = random.uniform(1.00, 1.10)
            customer_name = random.choice(["Ông Tư Hào Phóng", "Cô Ba Dễ Tính"])
        else:
            offer_multiplier = random.uniform(1.11, max_multiplier)
            customer_name = random.choice(["Đại Gia Bỏ Tiền", "Khách Hàng VIP"])
            
        offer_price = int(merchant_value * offer_multiplier)
        
        market_customer = {
            'name': customer_name,
            'offer': max(1, offer_price),
            'fish_id': fish_to_buy['id'],
            'fish_name': fish_to_buy['name'],
            'fish_weight': fish_to_buy['weight'],
            'time': now
        }
        last_customer_time = now
        
        event_bonus_text = ""
        if market_multiplier > 1.0:
            event_bonus_text = " (SỰ KIỆN NGÀY SỐT GIÁ!)"
            
        display_message(f"Có khách hàng {customer_name} đến trả giá {market_customer['offer']} Xu cho {fish_to_buy['name']}!{event_bonus_text}", 3)

def accept_market_offer():
    global market_customer, player_coins, market_selling_fish, fish_inventory
    
    if not market_customer: return False, "Không có khách hàng nào đang trả giá!"
    
    fish_id = market_customer['fish_id']
    offer = market_customer['offer']
    
    player_coins += offer
    market_selling_fish = [f for f in market_selling_fish if f['id'] != fish_id]
    fish_inventory = [f for f in fish_inventory if f.get('id') != fish_id]
    
    event_bonus_text = ""
    if get_event_multiplier("market") > 1.0:
        event_bonus_text = " (SỰ KIỆN NGÀY SỐT GIÁ!)"
        
    msg = f"Đã bán {market_customer['fish_name']} ({market_customer['fish_weight']:.2f} kg) cho {market_customer['name']} với giá {offer} Xu!{event_bonus_text}"
    market_customer = None
    
    return True, msg

def reject_market_offer():
    global market_customer
    if not market_customer: return False, "Không có khách hàng nào để từ chối!"
    
    msg = f"Khách hàng {market_customer['name']} đã bỏ đi sau khi bị từ chối."
    market_customer = None
    last_customer_time = time.time() - CUSTOMER_SPAWN_INTERVAL + 5
    
    return True, msg

def reset_market_state():
    global market_slot_end_time, market_selling_fish, market_customer
    market_slot_end_time = 0
    
    if market_customer:
        display_message("Hủy giao dịch chợ! Khách hàng bỏ đi.", 3)
        market_customer = None
        
    market_selling_fish = [] 

def prepare_steal_slots():
    global steal_slots_data
    steal_slots_data = []
    
    STEAL_CATCH_RATE = 0.4 
    
    for i in range(3):
        random_chan = random.choice(["Kênh A", "Kênh B", "Kênh C", "Kênh D"]) 

        slot = {
            "id": i,
            "revealed": False,
            "catch_data": None,
            "chan": random_chan 
        }
        
        if random.random() < STEAL_CATCH_RATE:
            fish_name, weight, exp_gained, _ = check_fish(0.0) 
            slot["catch_data"] = {
                "name": fish_name, 
                "weight": weight, 
                "exp": exp_gained,
                "loc": "Thăm Trộm", 
                "chan": random_chan 
            }
        
        steal_slots_data.append(slot)

# --- LƯU/TẢI GAME ---

def save_game():
    global player_level, player_exp, rods_inventory, fish_inventory, player_health, last_hp_regen_time, MAX_RODS, player_coins, market_slot_end_time, current_event, event_start_time, event_end_time, event_cooldown_end, last_event_check_time, is_christmas_event_active, CHRISTMAS_EVENT_START, CHRISTMAS_EVENT_END, christmas_items_inventory
    
    save_data = {
        "player_level": player_level,
        "player_exp": player_exp,
        "player_coins": player_coins, 
        "player_health": player_health, 
        "last_hp_regen_time": last_hp_regen_time,
        "rods_inventory": rods_inventory, 
        "fish_inventory": fish_inventory,
        "last_exit_time": time.time(),
        "MAX_RODS": MAX_RODS,
        "market_slot_end_time": market_slot_end_time,
        "current_event": current_event,
        "event_start_time": event_start_time,
        "event_end_time": event_end_time,
        "event_cooldown_end": event_cooldown_end,
        "last_event_check_time": last_event_check_time,
        "is_christmas_event_active": is_christmas_event_active,
        "CHRISTMAS_EVENT_START": CHRISTMAS_EVENT_START,
        "CHRISTMAS_EVENT_END": CHRISTMAS_EVENT_END,
        "christmas_items_inventory": christmas_items_inventory
    }
    
    try:
        with open(GAME_SAVE_FILE, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=4)
        print("Game saved successfully!")
    except Exception as e:
        print(f"Lỗi khi lưu game: {e}")

def load_game():
    global player_level, player_exp, rods_inventory, fish_inventory, current_location, current_channel, fishing_slots, MAX_RODS, player_health, last_hp_regen_time, player_coins, market_slot_end_time, current_event, event_start_time, event_end_time, event_cooldown_end, last_event_check_time, is_christmas_event_active, CHRISTMAS_EVENT_START, CHRISTMAS_EVENT_END, christmas_items_inventory
    
    INITIAL_RODS = 5 
    
    try:
        if not os.path.exists(GAME_SAVE_FILE):
            raise FileNotFoundError("Save file not found")
            
        with open(GAME_SAVE_FILE, 'r', encoding='utf-8') as f:
            load_data = json.load(f)
            
        player_level = load_data.get("player_level", 1)
        player_exp = load_data.get("player_exp", 0)
        player_coins = load_data.get("player_coins", 0) 
        player_health = load_data.get("player_health", MAX_HEALTH) 
        last_hp_regen_time = load_data.get("last_hp_regen_time", time.time())
        fish_inventory = load_data.get("fish_inventory", [])
        market_slot_end_time = load_data.get("market_slot_end_time", 0) 
        
        current_event = load_data.get("current_event", None)
        event_start_time = load_data.get("event_start_time", 0)
        event_end_time = load_data.get("event_end_time", 0)
        event_cooldown_end = load_data.get("event_cooldown_end", 0)
        last_event_check_time = load_data.get("last_event_check_time", time.time())
        
        is_christmas_event_active = load_data.get("is_christmas_event_active", False)
        CHRISTMAS_EVENT_START = load_data.get("CHRISTMAS_EVENT_START", None)
        CHRISTMAS_EVENT_END = load_data.get("CHRISTMAS_EVENT_END", None)
        christmas_items_inventory = load_data.get("christmas_items_inventory", [])
        
        if market_slot_end_time > 0 and market_slot_end_time < time.time():
            market_slot_end_time = 0 
            display_message("Thời gian thuê chỗ chợ đã hết khi offline.", 3)
            
        now = time.time()
        if current_event and event_end_time < now:
            display_message(f"Sự kiện {current_event['name']} đã kết thúc khi offline.", 3)
            current_event = None
            event_cooldown_end = now + EVENT_COOLDOWN
            
        if is_christmas_event_active and CHRISTMAS_EVENT_END and CHRISTMAS_EVENT_END < now:
            end_christmas_event()
            
        loaded_max_rods = load_data.get("MAX_RODS", MAX_RODS)
        
        if not load_data.get("rods_inventory"):
             rods_inventory = [create_default_rod(i, "Cần Tre") for i in range(INITIAL_RODS)] 
        else:
             rods_inventory = load_data.get("rods_inventory", [])
        
        MAX_RODS = loaded_max_rods 
        
        for rod in rods_inventory:
            if rod.get("template") is None: rod["template"] = DEFAULT_ROD_TEMPLATE
            if rod.get("level") is None: rod["level"] = 1
            if rod.get("name") is None: rod["name"] = rod["template"]
            
            template_data = ROD_TEMPLATES.get(rod["template"], ROD_TEMPLATES[DEFAULT_ROD_TEMPLATE])

            rate_base, exp_base, base_time = calculate_rod_stats(rod["template"], rod["level"])
            rod["current_rate_bonus"] = rate_base
            rod["current_exp_bonus"] = exp_base
            
            if rod.get("total_rate_bonus") is None: rod["total_rate_bonus"] = 0.0
            if rod.get("total_time_bonus") is None: rod["total_time_bonus"] = 0
            
            rod["max_cast_minutes"] = base_time + rod.get("total_time_bonus", 0)
            
            if rod.get("status") == "Đã thu cá": 
                rod["status"] = "Trống"
                for key in ["cast_time", "last_check_time", "location", "channel", "slot_index"]:
                    if key in rod: del rod[key]

        last_exit_time = load_data.get("last_exit_time", time.time())
        now = time.time()
        
        time_since_last_regen_seconds = now - last_hp_regen_time
        hp_regen_minutes = int(time_since_last_regen_seconds / 60)
        
        if hp_regen_minutes > 0 and player_health < MAX_HEALTH:
            hp_recovered = min(hp_regen_minutes, MAX_HEALTH - player_health)
            if hp_recovered > 0:
                player_health += hp_recovered
                last_hp_regen_time = now
        
        time_elapsed_seconds = now - last_exit_time

        if time_elapsed_seconds > 60: 
            for rod in rods_inventory:
                if rod.get("status") == "Đang Cắm" and rod.get("location") and rod.get("channel"):
                    
                    loc_name = rod["location"]
                    rate_per_minute = get_location_rate(loc_name)
                    last_check_time = max(rod.get("last_check_time", last_exit_time), rod.get("cast_time", last_exit_time))
                    
                    offline_time_seconds = now - last_check_time
                    offline_time_minutes = int(offline_time_seconds / 60)
                    
                    rod_rate_bonus = rod.get("current_rate_bonus", 0) + rod.get("total_rate_bonus", 0) 
                    rod_exp_bonus = rod.get("current_exp_bonus", 0)
                    rod_max_time = rod.get("max_cast_minutes", ROD_TEMPLATES["Cần Tre"]["base_cast_time"])

                    cast_duration_minutes = int((now - rod.get("cast_time", now)) / 60)

                    if cast_duration_minutes >= rod_max_time:
                         rod["status"] = "Hết Giờ (Offline)"
                         rod["last_check_time"] = now
                         continue
                    
                    elif offline_time_minutes > 0:
                        total_catches = 0
                        total_exp = 0

                        minutes_to_check = min(offline_time_minutes, rod_max_time - cast_duration_minutes)

                        for _ in range(minutes_to_check):
                            adjusted_rate = rate_per_minute + rod_rate_bonus 
                            if random.random() < adjusted_rate: 
                                fish_name, weight, exp_gained, christmas_item = check_fish(rate_per_minute, rod_rate_bonus, rod_exp_bonus) 
                                if weight > 0:
                                    total_catches += 1
                                    total_exp += exp_gained
                                    fish_inventory.append({
                                        "name": fish_name, 
                                        "weight": weight, 
                                        "loc": rod["location"], 
                                        "chan": rod["channel"], 
                                        "exp": exp_gained,
                                        "id": generate_fish_id()
                                    })
                                    
                                    if christmas_item:
                                        add_christmas_item_to_inventory(christmas_item["name"], christmas_item["weight"])
                                    
                                    break 
                        
                        player_exp += total_exp
                        if total_catches > 0:
                            rod["status"] = f"Dính Offline: {total_catches} cá!" 

                        if cast_duration_minutes + minutes_to_check >= rod_max_time:
                            if rod["status"] == "Đang Cắm": 
                                rod["status"] = "Hết Giờ (Offline)"

                        rod["last_check_time"] = now 
                
        check_level_up() 
        print("Game loaded successfully!")

    except FileNotFoundError:
        rods_inventory = [create_default_rod(i, "Cần Tre") for i in range(INITIAL_RODS)]
        player_coins = 1000 
        MAX_RODS = INITIAL_RODS
        christmas_items_inventory = []
        print("New game started!")
    except Exception as e:
        print(f"Lỗi khi tải game: {e}. Bắt đầu game mới.")
        rods_inventory = [create_default_rod(i, "Cần Tre") for i in range(INITIAL_RODS)] 
        player_coins = 1000
        MAX_RODS = INITIAL_RODS
        christmas_items_inventory = []
        
# --- TẢI GAME ---
load_game() 

# --- CẬP NHẬT TRẠNG THÁI ONLINE ---

def update_online_status():
    global rods_inventory, player_health, MAX_HEALTH, last_hp_regen_time, market_slot_end_time, game_state, christmas_items_inventory
    
    now = time.time()
    
    # Hồi phục HP Online
    time_since_last_regen = now - last_hp_regen_time
    minutes_to_regen = int(time_since_last_regen / 60)
    
    if minutes_to_regen >= 1 and player_health < MAX_HEALTH:
        hp_to_recover = min(minutes_to_regen, MAX_HEALTH - player_health)
        player_health += hp_to_recover
        last_hp_regen_time += minutes_to_regen * 60

    # Kiểm tra Dính Cá Online
    for rod in rods_inventory:
        if rod.get("status") == "Đang Cắm" and rod.get("location") and rod.get("channel"):
            loc_name = rod["location"]
            rate_per_minute = get_location_rate(loc_name)
            
            if "last_check_time" not in rod:
                rod["last_check_time"] = rod.get("cast_time", now)
                
            time_since_last_check = now - rod["last_check_time"]
            minutes_to_check = int(time_since_last_check / 60)
            
            rod_rate_bonus = rod.get("current_rate_bonus", 0) + rod.get("total_rate_bonus", 0)
            rod_exp_bonus = rod.get("current_exp_bonus", 0)
            rod_max_time = rod.get("max_cast_minutes", ROD_TEMPLATES["Cần Tre"]["base_cast_time"])

            cast_duration_minutes = int((now - rod.get("cast_time", now)) / 60)
            
            if cast_duration_minutes >= rod_max_time:
                rod["status"] = "Hết Giờ"
                continue
                
            if minutes_to_check >= 1:
                minutes_to_check_effective = min(minutes_to_check, rod_max_time - cast_duration_minutes)

                for _ in range(minutes_to_check_effective):
                    adjusted_rate = rate_per_minute + rod_rate_bonus
                    if random.random() < adjusted_rate: 
                        fish_name, weight, exp_gained, christmas_item = check_fish(rate_per_minute, rod_rate_bonus, rod_exp_bonus) 
                        if weight > 0:
                            rod["status"] = f"Đã Dính Cá ({round(weight, 2)}kg)!"
                            rod["catch_data"] = {
                                "name": fish_name, 
                                "weight": weight, 
                                "exp": exp_gained, 
                                "loc": rod["location"], 
                                "chan": rod["channel"],
                                "id": generate_fish_id(),
                                "christmas_item": christmas_item
                            }
                            break 
                
                rod["last_check_time"] += minutes_to_check * 60
                
                current_cast_duration = int((now - rod.get("cast_time", now)) / 60)
                if current_cast_duration >= rod_max_time and rod["status"] == "Đang Cắm":
                    rod["status"] = "Hết Giờ"

    # MARKET - Kiểm tra hết giờ chợ và Khách hàng
    if game_state == "MARKET_SELL":
        if market_slot_end_time > 0 and now >= market_slot_end_time:
            reset_market_state()
            game_state = "MARKET_MENU"
            display_message("Hết giờ thuê chỗ chợ! Quay lại Menu Chợ.", 3)
        else:
            check_for_customer()
    
    # Kiểm tra sự kiện
    check_event_status()

# --- HÀM VẼ ---

def draw_text(surface, text, font, color, x, y, center=False):
    try:
        text_surf = font.render(text, True, color)
        text_rect = text_surf.get_rect()
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
        
        if text_rect.right > SCREEN_WIDTH:
            x_shift = text_rect.right - SCREEN_WIDTH + 5 
            text_rect.x -= x_shift
        if text_rect.left < 0:
            text_rect.x = 5 
            
        surface.blit(text_surf, text_rect)
        return text_rect
    except:
        return pygame.Rect(0,0,0,0)

def draw_multiline_text(surface, text, font, color, rect, align="center"):
    try:
        words = text.split(' ')
        lines = []
        current_line = ''
        max_width = rect.width * 0.95 
        
        for word in words:
            test_line = current_line + ' ' + word if current_line else word
            test_surface = font.render(test_line, True, color)
            
            if test_surface.get_width() > max_width:
                lines.append(current_line)
                current_line = word
            else:
                current_line = test_line
                
        lines.append(current_line)
        
        line_height = font.get_linesize()
        y = rect.y + (rect.height - len(lines) * line_height) // 2
        
        for line in lines:
            text_surface = font.render(line, True, color)
            text_rect = text_surface.get_rect()
            
            text_rect.centerx = rect.centerx
            text_rect.top = y
            surface.blit(text_surface, text_rect)
            y += line_height
    except:
        pass

def draw_button(surface, rect, text, font, color, text_color):
    try:
        pygame.draw.rect(surface, color, rect, border_radius=5)
        draw_text(surface, text, font, text_color, rect.centerx, rect.centery, center=True)
        return rect
    except:
        return pygame.Rect(0,0,0,0)

def draw_bar(surface, rect, current_value, max_value, bar_color):
    try:
        pygame.draw.rect(surface, GRAY_INACTIVE, rect, border_radius=5)
        fill_width = 0
        if max_value > 0:
            fill_width = rect.width * (current_value / max_value)
        fill_rect = pygame.Rect(rect.x, rect.y, fill_width, rect.height)
        pygame.draw.rect(surface, bar_color, fill_rect, border_radius=5)
        pygame.draw.rect(surface, WHITE, rect, 2, border_radius=5)
    except:
        pass

def draw_global_message():
    global message_display
    if message_display:
        text = message_display["text"]
        
        OVERLAY_W = int(SCREEN_WIDTH * 0.8)
        OVERLAY_H = int(SCREEN_HEIGHT * 0.1) 
        
        try:
            overlay = pygame.Surface((OVERLAY_W, OVERLAY_H))
            overlay.set_alpha(180) 
            overlay.fill(BLACK)
            
            rect = overlay.get_rect(center=(SCREEN_WIDTH // 2, int(SCREEN_HEIGHT * 0.5)))
            screen.blit(overlay, rect)
            
            MESSAGE_FONT = FONT_MEDIUM 
            draw_multiline_text(screen, text, MESSAGE_FONT, EXP_COLOR, rect, align="center")
        except:
            pass

def draw_character_screen():
    global player_level, player_exp, fish_inventory, player_name, player_health, MAX_HEALTH, player_coins, christmas_items_inventory
    try:
        screen.fill(MENU_COLOR)
        draw_text(screen, "THÔNG TIN NHÂN VẬT", FONT_LARGE, WHITE, SCREEN_WIDTH // 2, TITLE_Y, center=True)
        
        LINE_STEP = int(SCREEN_HEIGHT * 0.04) 
        y_start_info = int(SCREEN_HEIGHT * 0.15) 
        
        draw_text(screen, f"Tên: {player_name}", FONT_MEDIUM, WHITE, BUTTON_MARGIN, y_start_info)
        draw_text(screen, f"Cấp độ: {player_level}", FONT_MEDIUM, WHITE, BUTTON_MARGIN, y_start_info + LINE_STEP)
        draw_text(screen, f"Xu: {player_coins}", FONT_MEDIUM, COIN_COLOR, BUTTON_MARGIN, y_start_info + 2 * LINE_STEP) 
        
        BAR_W = SCREEN_WIDTH - 2 * BUTTON_MARGIN
        BAR_H = int(SCREEN_HEIGHT * 0.015) 
        
        hp_text = f"HP: {player_health} / {MAX_HEALTH}"
        draw_text(screen, hp_text, FONT_SMALL, HP_COLOR, BUTTON_MARGIN, y_start_info + 4 * LINE_STEP)
        hp_rect = pygame.Rect(BUTTON_MARGIN, y_start_info + 5 * LINE_STEP, BAR_W, BAR_H)
        draw_bar(screen, hp_rect, player_health, MAX_HEALTH, HP_COLOR)
        
        exp_needed = exp_to_next_level(player_level)
        exp_text = f"EXP: {player_exp} / {exp_needed}"
        exp_y_pos = y_start_info + 6 * LINE_STEP + BAR_H + int(SCREEN_HEIGHT * 0.01)
        draw_text(screen, exp_text, FONT_SMALL, EXP_COLOR, BUTTON_MARGIN, exp_y_pos)
        exp_rect = pygame.Rect(BUTTON_MARGIN, exp_y_pos + LINE_STEP - int(SCREEN_HEIGHT * 0.01), BAR_W, BAR_H)
        draw_bar(screen, exp_rect, player_exp, exp_needed, EXP_COLOR)
        
        draw_text(screen, f"Cá đã bắt: {len(fish_inventory)} con ({sum(f['weight'] for f in fish_inventory):.2f} kg)", 
                  FONT_MEDIUM, WHITE, BUTTON_MARGIN, exp_rect.bottom + int(SCREEN_HEIGHT * 0.05))
        
        if is_christmas_event_active:
            christmas_count = len(christmas_items_inventory)
            draw_text(screen, f"Vật phẩm Giáng Sinh: {christmas_count} món", 
                      FONT_MEDIUM, CHRISTMAS_COLOR, BUTTON_MARGIN, exp_rect.bottom + int(SCREEN_HEIGHT * 0.09))
                  
        back_rect = pygame.Rect(BUTTON_MARGIN, SCREEN_HEIGHT - BUTTON_H - 10, BACK_BUTTON_W, BUTTON_H)
        LOCATIONS["Back_Rect_Character"] = draw_button(screen, back_rect, "Quay Lại", FONT_SMALL, GRAY_INACTIVE, WHITE)
    except Exception as e:
        print(f"Lỗi vẽ character screen: {e}")

def draw_upgrade_screen():
    global player_coins, selected_rod_id
    try:
        rod = next((r for r in rods_inventory if r["id"] == selected_rod_id), None)
        if not rod: 
            global game_state 
            game_state = "INVENTORY_SCREEN" 
            return
            
        screen.fill(UPGRADE_BG_COLOR)
        draw_text(screen, f"NÂNG CẤP CẦN: {rod.get('name', 'Mặc Định')} (Lv{rod['level']})", FONT_LARGE, YELLOW_BUTTON, 
                  SCREEN_WIDTH // 2, TITLE_Y, center=True) 
        draw_text(screen, f"Xu hiện tại: {player_coins}", FONT_MEDIUM, COIN_COLOR, 
                  SCREEN_WIDTH // 2, TITLE_Y + int(SCREEN_HEIGHT * 0.05), center=True)
                  
        INFO_W = SCREEN_WIDTH - 2 * BUTTON_MARGIN
        INFO_H = int(SCREEN_HEIGHT * 0.45) 
        INFO_X = BUTTON_MARGIN
        INFO_Y = int(SCREEN_HEIGHT * 0.15)
        info_rect = pygame.Rect(INFO_X, INFO_Y, INFO_W, INFO_H)
        pygame.draw.rect(screen, MENU_COLOR, info_rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, info_rect, 2, border_radius=10)
        
        LEFT_MARGIN = INFO_X + 30 
        LINE_STEP = int(SCREEN_HEIGHT * 0.045)  
        y_info = INFO_Y + 20 
        
        template = ROD_TEMPLATES.get(rod["template"])
        base_cast_time = template["base_cast_time"] if template else 30
        
        total_rate_bonus = rod.get('total_rate_bonus', 0.0)
        total_time_bonus = rod.get('total_time_bonus', 0)
        
        draw_text(screen, f"Trạng thái: {rod['status']}", FONT_MEDIUM, WHITE, LEFT_MARGIN, y_info)
        draw_text(screen, f"Loại cần: {rod['template']}", FONT_MEDIUM, WHITE, LEFT_MARGIN, y_info + LINE_STEP)
        
        time_text = f"Max Cast Time: {base_cast_time} phút"
        if total_time_bonus > 0:
            time_text += f" (+{total_time_bonus} phút bonus)"
        
        draw_text(screen, time_text, FONT_MEDIUM, HP_COLOR, LEFT_MARGIN, y_info + 2 * LINE_STEP)
        
        total_rate_display = rod.get('current_rate_bonus', 0) + total_rate_bonus
        rate_text = f"Tỉ lệ Dính Cá Bonus: {total_rate_display * 100:.2f}%"
        
        draw_text(screen, rate_text, FONT_MEDIUM, EXP_COLOR, LEFT_MARGIN, y_info + 3 * LINE_STEP)
        
        draw_text(screen, f"EXP Bonus: +{rod.get('current_exp_bonus', 0) * 100:.0f}%", 
                  FONT_MEDIUM, EXP_COLOR, LEFT_MARGIN, y_info + 4 * LINE_STEP)
        
        LOCATIONS["Upgrade_Rod_Detail"] = None 
        
        UPGRADE_BUTTON_W = SCREEN_WIDTH - 2 * BUTTON_MARGIN
        UPGRADE_Y = INFO_Y + INFO_H + 20
        
        if template and rod["level"] < template.get("max_level", MAX_LEVEL_ROD):
            next_level = rod["level"] + 1
            cost = get_upgrade_cost(rod)
            can_upgrade = rod["status"] != "Đang Cắm" and player_coins >= cost
            button_color = YELLOW_BUTTON if can_upgrade else LOCKED_COLOR
            button_text = f"NÂNG CẤP LÊN Lv{next_level} (Tốn: {cost} Xu)"
            
            upgrade_rect = pygame.Rect(BUTTON_MARGIN, UPGRADE_Y, UPGRADE_BUTTON_W, BUTTON_H)
            LOCATIONS["Upgrade_Rod_Detail"] = draw_button(screen, upgrade_rect, button_text, FONT_MEDIUM, button_color, BLACK) 
            
            WARNING_Y = UPGRADE_Y + BUTTON_H + 5
            
            if rod["status"] == "Đang Cắm":
                 draw_text(screen, "-> Thu cần trước khi nâng cấp", FONT_SMALL, RED_FISH, 
                           SCREEN_WIDTH // 2, WARNING_Y, center=True) 
            elif player_coins < cost:
                 deficit = cost - player_coins
                 draw_text(screen, f"-> Xu hiện tại: {player_coins}. Bạn cần thêm {deficit} Xu", FONT_SMALL, RED_FISH, 
                           SCREEN_WIDTH // 2, WARNING_Y, center=True) 
        else:
            draw_text(screen, "ĐÃ ĐẠT CẤP TỐI ĐA!", FONT_LARGE, RED_FISH, 
                      SCREEN_WIDTH // 2, UPGRADE_Y, center=True) 
            
        back_rect = pygame.Rect(BUTTON_MARGIN, SCREEN_HEIGHT - BUTTON_H - 10, BACK_BUTTON_W, BUTTON_H)
        LOCATIONS["Back_Rect_Upgrade"] = draw_button(screen, back_rect, "Quay Lại", FONT_SMALL, GRAY_INACTIVE, WHITE)
    except Exception as e:
        print(f"Lỗi vẽ upgrade screen: {e}")

def draw_inventory_screen():
    global rods_inventory, MAX_RODS
    try:
        screen.fill(MENU_COLOR)
        draw_text(screen, "TÚI ĐỒ (INVENTORY)", FONT_LARGE, WHITE, SCREEN_WIDTH // 2, TITLE_Y, center=True)
        draw_text(screen, f"Cần câu: {len(rods_inventory)}/{MAX_RODS} | Xu: {player_coins}", FONT_MEDIUM, COIN_COLOR, 
                  SCREEN_WIDTH // 2, TITLE_Y + int(SCREEN_HEIGHT * 0.05), center=True)
        
        GRID_START_Y = int(SCREEN_HEIGHT * 0.15)
        PADDING = int(SCREEN_WIDTH * 0.02)
        COLS = 3
        SLOT_SIZE = (SCREEN_WIDTH - 2 * BUTTON_MARGIN - (COLS - 1) * PADDING) // COLS
        
        LOCATIONS["Inventory_Slots"] = []
        
        draw_text(screen, "--- Cần Câu ---", FONT_SMALL, YELLOW_BUTTON, BUTTON_MARGIN, GRID_START_Y)
        y_rod_start = GRID_START_Y + int(SCREEN_HEIGHT * 0.03)

        for i, rod in enumerate(rods_inventory):
            col = i % COLS
            row = i // COLS
            
            x = BUTTON_MARGIN + col * (SLOT_SIZE + PADDING)
            y = y_rod_start + row * (SLOT_SIZE + PADDING)
            
            rect = pygame.Rect(x, y, SLOT_SIZE, SLOT_SIZE)
            
            color = BLUE_WATER if rod["status"] == "Đang Cắm" else GRAY_INACTIVE
                
            pygame.draw.rect(screen, color, rect, border_radius=5)
            pygame.draw.rect(screen, WHITE, rect, 2, border_radius=5)
            
            rod_name = f"{rod.get('name', 'Mặc Định')}"
            rod_level = f"Lv{rod['level']}"
            rod_status = rod['status']
            
            draw_text(screen, rod_name, FONT_SMALL, WHITE, rect.centerx, rect.centery - int(SLOT_SIZE * 0.2), center=True) 
            draw_text(screen, rod_level, FONT_MEDIUM, YELLOW_BUTTON, rect.centerx, rect.centery, center=True) 
            draw_text(screen, rod_status, FONT_VERY_SMALL, WHITE, rect.centerx, rect.centery + int(SLOT_SIZE * 0.25), center=True) 
                      
            LOCATIONS["Inventory_Slots"].append({"id": rod["id"], "rect": rect})
            
        y_button_area = y_rod_start + (len(rods_inventory) // COLS + 1) * (SLOT_SIZE + PADDING) + int(SCREEN_HEIGHT * 0.02)
        
        BUTTON_SIDE_W = int(SCREEN_WIDTH * 0.45)
        
        shop_rect = pygame.Rect(BUTTON_MARGIN, y_button_area, BUTTON_SIDE_W, BUTTON_H)
        LOCATIONS["Shop_Rect"] = draw_button(screen, shop_rect, "CỬA HÀNG (SHOP)", FONT_MEDIUM, GREEN_BG, WHITE)
        
        sell_rect = pygame.Rect(SCREEN_WIDTH - BUTTON_MARGIN - BUTTON_SIDE_W, y_button_area, BUTTON_SIDE_W, BUTTON_H)
        LOCATIONS["Sell_Fish_Rect"] = draw_button(screen, sell_rect, "BÁN CÁ", FONT_MEDIUM, RED_FISH, WHITE)
            
        back_rect = pygame.Rect(BUTTON_MARGIN, SCREEN_HEIGHT - BUTTON_H - 10, BACK_BUTTON_W, BUTTON_H)
        LOCATIONS["Back_Rect_Inventory"] = draw_button(screen, back_rect, "Quay Lại", FONT_SMALL, GRAY_INACTIVE, WHITE)
    except Exception as e:
        print(f"Lỗi vẽ inventory screen: {e}")

def draw_shop_screen():
    global player_coins
    try:
        screen.fill(MENU_COLOR)
        draw_text(screen, "CỬA HÀNG (SHOP)", FONT_LARGE, WHITE, SCREEN_WIDTH // 2, TITLE_Y, center=True)
        draw_text(screen, f"Xu hiện tại: {player_coins}", FONT_MEDIUM, COIN_COLOR, 
                  SCREEN_WIDTH // 2, TITLE_Y + int(SCREEN_HEIGHT * 0.05), center=True)
                  
        y_start = int(SCREEN_HEIGHT * 0.2)
        y_step = BUTTON_H + int(SCREEN_HEIGHT * 0.02)
        BUTTON_W_SHOP = SCREEN_WIDTH - 2 * BUTTON_MARGIN
        
        LOCATIONS["Shop_Items"] = []

        rod_meta = ROD_TEMPLATES["Cần Sắt"]
        price = rod_meta["buy_price"]
        
        can_buy = player_coins >= price and len(rods_inventory) < MAX_RODS
        button_color = YELLOW_BUTTON if can_buy else LOCKED_COLOR
        button_text = f"Cần Sắt (Max Cắm {rod_meta['base_cast_time']}p) - GIÁ: {price} Xu"
        
        rod_rect = pygame.Rect(BUTTON_MARGIN, y_start, BUTTON_W_SHOP, BUTTON_H)
        LOCATIONS["Shop_Items"].append({
            "name": "Cần Sắt", 
            "rect": draw_button(screen, rod_rect, button_text, FONT_MEDIUM, button_color, BLACK)
        })
        
        if len(rods_inventory) >= MAX_RODS:
             draw_text(screen, f"Đã đạt giới hạn cần câu ({MAX_RODS} cần).", FONT_SMALL, RED_FISH, 
                       SCREEN_WIDTH // 2, rod_rect.bottom + 5, center=True)
                       
        upgrade_rod_limit_cost = 50000 
        y_start_upgrade = y_start + y_step * 2
        
        upgrade_can_buy = player_coins >= upgrade_rod_limit_cost and MAX_RODS < 5 
        upgrade_color = BLUE_WATER if upgrade_can_buy else LOCKED_COLOR
        
        upgrade_text = f"Mở giới hạn Cần Câu lên {MAX_RODS + 1} (GIÁ: {upgrade_rod_limit_cost} Xu)"
        upgrade_rect = pygame.Rect(BUTTON_MARGIN, y_start_upgrade, BUTTON_W_SHOP, BUTTON_H)

        if MAX_RODS < 5:
            LOCATIONS["Shop_Upgrade_Rod_Limit_Rect"] = draw_button(screen, upgrade_rect, upgrade_text, FONT_MEDIUM, upgrade_color, WHITE)
        else:
            draw_text(screen, "Đã đạt giới hạn tối đa cho phép nâng cấp!", FONT_MEDIUM, WHITE, SCREEN_WIDTH // 2, y_start_upgrade + BUTTON_H // 2, center=True)


        back_rect = pygame.Rect(BUTTON_MARGIN, SCREEN_HEIGHT - BUTTON_H - 10, BACK_BUTTON_W, BUTTON_H)
        LOCATIONS["Back_Rect_Shop"] = draw_button(screen, back_rect, "Quay Lại", FONT_MEDIUM, GRAY_INACTIVE, WHITE)
    except Exception as e:
        print(f"Lỗi vẽ shop screen: {e}")

def draw_sell_fish_screen():
    global player_coins, fish_to_sell_selected_type, fish_to_sell_quantity
    
    try:
        screen.fill(MENU_COLOR)
        draw_text(screen, "BÁN CÁ CHO THƯƠNG LÁI", FONT_LARGE, WHITE, SCREEN_WIDTH // 2, TITLE_Y, center=True)
        draw_text(screen, f"Xu hiện tại: {player_coins}", FONT_MEDIUM, COIN_COLOR, 
                  SCREEN_WIDTH // 2, TITLE_Y + int(SCREEN_HEIGHT * 0.05), center=True)
                  
        y_start = int(SCREEN_HEIGHT * 0.15)
        y_step = int(SCREEN_HEIGHT * 0.05)
        
        summary = get_fish_inventory_summary()
        LOCATIONS["Sell_Fish_Options"] = []
        
        draw_text(screen, f"Giá bán Cá Lóc: {FISH_PRICE_PER_KG.get('Cá Lóc', 0)} Xu/kg", FONT_MEDIUM, YELLOW_BUTTON, BUTTON_MARGIN, y_start)

        y_list_start = y_start + y_step
        
        for i, (name, data) in enumerate(summary.items()):
            
            if name not in FISH_PRICE_PER_KG: continue 

            text = f"[{name}] - Có {data['count']} con ({data['total_weight']:.2f} kg)"
            
            rect_select = pygame.Rect(BUTTON_MARGIN, y_list_start + i * y_step, SCREEN_WIDTH - 2 * BUTTON_MARGIN, BUTTON_H // 2)
            
            is_selected = (name == fish_to_sell_selected_type)
            color = BLUE_WATER if is_selected else GRAY_INACTIVE
            
            LOCATIONS["Sell_Fish_Options"].append({
                "name": name, 
                "max_count": data['count'],
                "rect": draw_button(screen, rect_select, text, FONT_SMALL, color, WHITE)
            })
            
        y_control = y_list_start + len(LOCATIONS["Sell_Fish_Options"]) * y_step + int(SCREEN_HEIGHT * 0.05)
        
        LOCATIONS["Sell_Controls"] = {}
        
        if fish_to_sell_selected_type:
            
            max_count = next((item['max_count'] for item in LOCATIONS["Sell_Fish_Options"] if item['name'] == fish_to_sell_selected_type), 0)
            
            draw_text(screen, f"Số lượng muốn bán: {fish_to_sell_quantity} / {max_count}", FONT_MEDIUM, WHITE, SCREEN_WIDTH // 2, y_control, center=True)
            
            minus_rect = pygame.Rect(BUTTON_MARGIN, y_control + y_step, BUTTON_H, BUTTON_H)
            LOCATIONS["Sell_Controls"]["Minus"] = draw_button(screen, minus_rect, "-", FONT_LARGE, RED_FISH, WHITE)
            
            plus_rect = pygame.Rect(SCREEN_WIDTH - BUTTON_MARGIN - BUTTON_H, y_control + y_step, BUTTON_H, BUTTON_H)
            LOCATIONS["Sell_Controls"]["Plus"] = draw_button(screen, plus_rect, "+", FONT_LARGE, BLUE_WATER, WHITE)

            max_rect = pygame.Rect(SCREEN_WIDTH // 2 - BUTTON_H // 2, y_control + y_step, BUTTON_H, BUTTON_H)
            LOCATIONS["Sell_Controls"]["Max"] = draw_button(screen, max_rect, "Max", FONT_SMALL, YELLOW_BUTTON, BLACK)

            sell_button_w = int(SCREEN_WIDTH * 0.6)
            sell_rect = pygame.Rect(SCREEN_WIDTH // 2 - sell_button_w // 2, y_control + 2 * y_step + 10, sell_button_w, BUTTON_H)
            
            can_sell = fish_to_sell_quantity > 0
            sell_color = RED_FISH if can_sell else GRAY_INACTIVE
            
            LOCATIONS["Sell_Controls"]["Sell"] = draw_button(screen, sell_rect, f"BÁN {fish_to_sell_quantity} CON", FONT_LARGE, sell_color, WHITE)


        back_rect = pygame.Rect(BUTTON_MARGIN, SCREEN_HEIGHT - BUTTON_H - 10, BACK_BUTTON_W, BUTTON_H)
        LOCATIONS["Back_Rect_Sell_Fish"] = draw_button(screen, back_rect, "Quay Lại", FONT_MEDIUM, GRAY_INACTIVE, WHITE)
    except Exception as e:
        print(f"Lỗi vẽ sell fish screen: {e}")
    
def draw_market_menu():
    global player_coins, market_slot_end_time, MARKET_SLOT_COST
    try:
        screen.fill(MARKET_COLOR)
        draw_text(screen, "CHỢ CÁ TỰ DO", FONT_LARGE, WHITE, SCREEN_WIDTH // 2, TITLE_Y, center=True)
        draw_text(screen, f"Xu: {player_coins}", FONT_MEDIUM, COIN_COLOR, SCREEN_WIDTH // 2, TITLE_Y + int(SCREEN_HEIGHT * 0.05), center=True)
        
        BUTTON_W = SCREEN_WIDTH - 2 * BUTTON_MARGIN
        y_start = int(SCREEN_HEIGHT * 0.25) 
        
        LOCATIONS["Market_Rent_Slot_Rect"] = None
        LOCATIONS["Market_Go_Selling_Rect"] = None
        
        if market_slot_end_time > time.time():
            time_left_seconds = market_slot_end_time - time.time()
            time_left_minutes = int(time_left_seconds // 60)
            time_left_seconds_rem = int(time_left_seconds % 60)
            
            time_text = f"Đang thuê chỗ: {time_left_minutes} phút {time_left_seconds_rem} giây"
            draw_text(screen, time_text, FONT_MEDIUM, WHITE, SCREEN_WIDTH // 2, y_start, center=True)

            go_sell_rect = pygame.Rect(BUTTON_MARGIN, y_start + BUTTON_Y_STEP, BUTTON_W, BUTTON_H)
            LOCATIONS["Market_Go_Selling_Rect"] = draw_button(screen, go_sell_rect, "VÀO BÀY BÁN CÁ", FONT_LARGE, RED_FISH, WHITE)
            
        else:
            cost = MARKET_SLOT_COST
            
            rent_text = f"THUÊ CHỖ NGỒI - Tốn {cost} Xu"
            rent_color = YELLOW_BUTTON if player_coins >= cost else LOCKED_COLOR
            
            rent_rect = pygame.Rect(BUTTON_MARGIN, y_start, BUTTON_W, BUTTON_H)
            LOCATIONS["Market_Rent_Slot_Rect"] = draw_button(screen, rent_rect, rent_text, FONT_LARGE, rent_color, BLACK)
            
        back_rect = pygame.Rect(BUTTON_MARGIN, SCREEN_HEIGHT - BUTTON_H - 10, BACK_BUTTON_W, BUTTON_H)
        LOCATIONS["Back_Rect_Market_Menu"] = draw_button(screen, back_rect, "Quay Lại", FONT_MEDIUM, GRAY_INACTIVE, WHITE)
    except Exception as e:
        print(f"Lỗi vẽ market menu: {e}")

def draw_market_sell_screen():
    global player_coins, market_selling_fish, fish_inventory, market_customer
    try:
        screen.fill(MARKET_COLOR)
        
        time_left_seconds = market_slot_end_time - time.time()
        time_left_minutes = int(time_left_seconds // 60)
        time_left_seconds_rem = int(time_left_seconds % 60)
        
        draw_text(screen, "ĐANG BÀY BÁN CÁ", FONT_LARGE, WHITE, SCREEN_WIDTH // 2, TITLE_Y, center=True)
        draw_text(screen, f"Xu: {player_coins} | Thời gian còn lại: {time_left_minutes}:{time_left_seconds_rem:02d}", FONT_MEDIUM, COIN_COLOR, SCREEN_WIDTH // 2, TITLE_Y + int(SCREEN_HEIGHT * 0.05), center=True)
        
        y_start_list = int(SCREEN_HEIGHT * 0.15)
        
        draw_text(screen, "--- Cá đang bày bán ---", FONT_MEDIUM, YELLOW_BUTTON, BUTTON_MARGIN, y_start_list)
        
        SLOT_W = SCREEN_WIDTH - 2 * BUTTON_MARGIN
        SLOT_H = int(SCREEN_HEIGHT * 0.05)
        y_step = SLOT_H + 5
        
        current_selling_ids = [f['id'] for f in market_selling_fish]
        LOCATIONS["Market_Selling_Fish_Rects"] = []
        
        for i, fish in enumerate(market_selling_fish):
            rect = pygame.Rect(BUTTON_MARGIN, y_start_list + (i + 1) * y_step, SLOT_W, SLOT_H)
            text = f"{fish['name']} ({fish['weight']:.2f} kg)"
            
            draw_button(screen, rect, text, FONT_SMALL, RED_FISH, WHITE)
            LOCATIONS["Market_Selling_Fish_Rects"].append({'id': fish['id'], 'rect': rect})

        y_list_end = y_start_list + (len(market_selling_fish) + 1) * y_step + 10
        
        if market_customer:
            customer = market_customer
            draw_text(screen, f"KHÁCH HÀNG: {customer['name']}", FONT_MEDIUM, EXP_COLOR, BUTTON_MARGIN, y_list_end)
            
            offer_text = f"Trả giá {customer['offer']} Xu cho {customer['fish_name']} ({customer['fish_weight']:.2f} kg)?"
            draw_text(screen, offer_text, FONT_MEDIUM, WHITE, BUTTON_MARGIN, y_list_end + SLOT_H)
            
            BUTTON_W_HALF = int(SCREEN_WIDTH * 0.45)
            y_button = y_list_end + SLOT_H * 2
            
            accept_rect = pygame.Rect(BUTTON_MARGIN, y_button, BUTTON_W_HALF, BUTTON_H)
            LOCATIONS["Market_Accept_Offer_Rect"] = draw_button(screen, accept_rect, "ĐỒNG Ý BÁN", FONT_MEDIUM, GREEN_BG, WHITE)
            
            reject_rect = pygame.Rect(SCREEN_WIDTH - BUTTON_MARGIN - BUTTON_W_HALF, y_button, BUTTON_W_HALF, BUTTON_H)
            LOCATIONS["Market_Reject_Offer_Rect"] = draw_button(screen, reject_rect, "TỪ CHỐI", FONT_MEDIUM, RED_FISH, WHITE)
            
            y_back_button = y_button + BUTTON_Y_STEP + 10
        else:
            draw_text(screen, "Đang chờ khách hàng...", FONT_MEDIUM, WHITE, BUTTON_MARGIN, y_list_end)
            y_back_button = y_list_end + BUTTON_Y_STEP + 10
            
        if not market_customer:
            back_rect = pygame.Rect(BUTTON_MARGIN, SCREEN_HEIGHT - BUTTON_H - 10, BACK_BUTTON_W, BUTTON_H)
            LOCATIONS["Back_Rect_Market_Sell"] = draw_button(screen, back_rect, "RÚT LUI (Về Menu Chợ)", FONT_SMALL, GRAY_INACTIVE, WHITE)
        else:
            if "Back_Rect_Market_Sell" in LOCATIONS: del LOCATIONS["Back_Rect_Market_Sell"]
    except Exception as e:
        print(f"Lỗi vẽ market sell screen: {e}")
    
def draw_market_select_fish():
    global fish_inventory, market_selling_fish
    
    try:
        screen.fill(MENU_COLOR)
        draw_text(screen, "CHỌN CÁ BÀY BÁN (TẠI CHỢ)", FONT_LARGE, WHITE, SCREEN_WIDTH // 2, TITLE_Y, center=True)
        draw_text(screen, f"Đã chọn: {len(market_selling_fish)} con", FONT_MEDIUM, YELLOW_BUTTON, SCREEN_WIDTH // 2, TITLE_Y + int(SCREEN_HEIGHT * 0.05), center=True)
        
        y_start_list = int(SCREEN_HEIGHT * 0.15)
        
        SLOT_W = SCREEN_WIDTH - 2 * BUTTON_MARGIN
        SLOT_H = int(SCREEN_HEIGHT * 0.05)
        y_step = SLOT_H + 5
        
        prepare_fish_inventory() 
        
        LOCATIONS["Market_Fish_Inventory"] = []
        
        selling_fish_ids = [f['id'] for f in market_selling_fish]
        fish_available_to_sell = [f for f in fish_inventory if f.get('id') not in selling_fish_ids]
        
        if not fish_available_to_sell:
            draw_text(screen, "Không còn cá trong kho để bày bán.", FONT_MEDIUM, RED_FISH, SCREEN_WIDTH // 2, y_start_list + 50, center=True)

        for i, fish in enumerate(fish_available_to_sell):
            rect = pygame.Rect(BUTTON_MARGIN, y_start_list + i * y_step, SLOT_W, SLOT_H)
            text = f"[{fish['name']}] - {fish['weight']:.2f} kg"
            
            LOCATIONS["Market_Fish_Inventory"].append({'id': fish['id'], 'rect': draw_button(screen, rect, text, FONT_SMALL, BLUE_WATER, WHITE)})

        
        BUTTON_W_HALF = int(SCREEN_WIDTH * 0.45)
        
        finish_rect = pygame.Rect(SCREEN_WIDTH - BUTTON_MARGIN - BUTTON_W_HALF, SCREEN_HEIGHT - BUTTON_H - 10, BUTTON_W_HALF, BUTTON_H)
        LOCATIONS["Finish_Selecting_Fish"] = draw_button(screen, finish_rect, "HOÀN TẤT (Vào Chợ)", FONT_MEDIUM, GREEN_BG, WHITE)
        
        back_rect = pygame.Rect(BUTTON_MARGIN, SCREEN_HEIGHT - BUTTON_H - 10, BUTTON_W_HALF, BUTTON_H)
        LOCATIONS["Back_Rect_Market_Select_Fish"] = draw_button(screen, back_rect, "QUAY LẠI", FONT_MEDIUM, GRAY_INACTIVE, WHITE)
    except Exception as e:
        print(f"Lỗi vẽ market select fish: {e}")

def draw_christmas_gift_screen():
    global christmas_items_inventory, player_coins, fish_inventory, christmas_exchange_selected
    
    try:
        screen.fill(CHRISTMAS_COLOR)
        draw_text(screen, "QUÀ GIÁNG SINH", FONT_LARGE, WHITE, SCREEN_WIDTH // 2, TITLE_Y, center=True)
        
        y_start = int(SCREEN_HEIGHT * 0.15)
        draw_text(screen, "Vật phẩm Giáng Sinh của bạn:", FONT_MEDIUM, WHITE, BUTTON_MARGIN, y_start)
        
        summary = get_christmas_items_summary()
        fish_summary = get_fish_inventory_summary()
        
        y_list = y_start + int(SCREEN_HEIGHT * 0.05)
        line_height = int(SCREEN_HEIGHT * 0.03)
        
        for i, (item_name, data) in enumerate(summary.items()):
            required = CHRISTMAS_EXCHANGE_REQUIREMENT.get(item_name, 0)
            has_enough = data['count'] >= required
            color = WHITE if has_enough else GRAY_INACTIVE
            
            text = f"{item_name}: {data['count']}/{required}"
            draw_text(screen, text, FONT_SMALL, color, BUTTON_MARGIN, y_list + i * line_height)
        
        fish_y = y_list + len(summary) * line_height + int(SCREEN_HEIGHT * 0.02)
        fish_required = CHRISTMAS_EXCHANGE_REQUIREMENT["Cá Lóc"]
        fish_has = fish_summary.get("Cá Lóc", {}).get('total_weight', 0)
        fish_has_enough = fish_has >= fish_required
        fish_color = WHITE if fish_has_enough else GRAY_INACTIVE
        
        fish_text = f"Cá Lóc: {fish_has:.1f}/{fish_required}kg"
        draw_text(screen, fish_text, FONT_SMALL, fish_color, BUTTON_MARGIN, fish_y)
        
        exchange_y = fish_y + int(SCREEN_HEIGHT * 0.05)
        exchange_rect = pygame.Rect(BUTTON_MARGIN, exchange_y, SCREEN_WIDTH - 2 * BUTTON_MARGIN, BUTTON_H)
        
        can_exchange = can_exchange_christmas_gift()
        exchange_color = CHRISTMAS_COLOR if can_exchange else GRAY_INACTIVE
        
        exchange_text = "ĐỔI QUÀ GIÁNG SINH"
        LOCATIONS["Christmas_Exchange_Rect"] = draw_button(screen, exchange_rect, exchange_text, FONT_MEDIUM, exchange_color, WHITE)
        
        if christmas_exchange_selected:
            result_y = exchange_rect.bottom + int(SCREEN_HEIGHT * 0.02)
            draw_text(screen, christmas_exchange_selected, FONT_SMALL, WHITE, SCREEN_WIDTH // 2, result_y, center=True)
        
        back_rect = pygame.Rect(BUTTON_MARGIN, SCREEN_HEIGHT - BUTTON_H - 10, BACK_BUTTON_W, BUTTON_H)
        LOCATIONS["Back_Rect_Christmas"] = draw_button(screen, back_rect, "Quay Lại", FONT_MEDIUM, GRAY_INACTIVE, WHITE)
    except Exception as e:
        print(f"Lỗi vẽ christmas gift screen: {e}")

def draw_leaderboard_screen():
    try:
        screen.fill((30, 30, 60))
        draw_text(screen, "🏆 BẢNG XẾP HẠNG", FONT_LARGE, (255, 215, 0), SCREEN_WIDTH // 2, TITLE_Y, center=True)
        
        leaderboard_data = leaderboard_manager.get_leaderboard(15)
        
        y_start = int(SCREEN_HEIGHT * 0.15)
        row_height = int(SCREEN_HEIGHT * 0.06)
        
        header_rect = pygame.Rect(BUTTON_MARGIN, y_start, SCREEN_WIDTH - 2 * BUTTON_MARGIN, row_height)
        pygame.draw.rect(screen, (70, 70, 120), header_rect, border_radius=5)
        
        headers = ["Hạng", "Tên", "Cấp", "Xu", "Cá"]
        header_widths = [0.1, 0.4, 0.15, 0.2, 0.15]
        
        x_pos = BUTTON_MARGIN + 10
        for i, header in enumerate(headers):
            width = (SCREEN_WIDTH - 2 * BUTTON_MARGIN) * header_widths[i]
            draw_text(screen, header, FONT_SMALL, WHITE, x_pos, y_start + row_height // 2, center=False)
            x_pos += width
        
        for i, player in enumerate(leaderboard_data):
            y_pos = y_start + (i + 1) * row_height
            row_color = (50, 50, 80) if i % 2 == 0 else (60, 60, 90)
            
            row_rect = pygame.Rect(BUTTON_MARGIN, y_pos, SCREEN_WIDTH - 2 * BUTTON_MARGIN, row_height)
            pygame.draw.rect(screen, row_color, row_rect, border_radius=3)
            
            if i == 0:
                rank_color = (255, 215, 0)
            elif i == 1:
                rank_color = (192, 192, 192)
            elif i == 2:
                rank_color = (205, 127, 50)
            else:
                rank_color = WHITE
            
            x_pos = BUTTON_MARGIN + 10
            draw_text(screen, str(i + 1), FONT_MEDIUM, rank_color, x_pos, y_pos + row_height // 2, center=False)
            x_pos += (SCREEN_WIDTH - 2 * BUTTON_MARGIN) * header_widths[0]
            
            draw_text(screen, player["name"], FONT_SMALL, WHITE, x_pos, y_pos + row_height // 2, center=False)
            x_pos += (SCREEN_WIDTH - 2 * BUTTON_MARGIN) * header_widths[1]
            
            draw_text(screen, str(player["level"]), FONT_SMALL, EXP_COLOR, x_pos, y_pos + row_height // 2, center=False)
            x_pos += (SCREEN_WIDTH - 2 * BUTTON_MARGIN) * header_widths[2]
            
            draw_text(screen, str(player["coins"]), FONT_SMALL, COIN_COLOR, x_pos, y_pos + row_height // 2, center=False)
            x_pos += (SCREEN_WIDTH - 2 * BUTTON_MARGIN) * header_widths[3]
            
            draw_text(screen, str(player["fish_count"]), FONT_SMALL, RED_FISH, x_pos, y_pos + row_height // 2, center=False)
        
        submit_rect = pygame.Rect(BUTTON_MARGIN, SCREEN_HEIGHT - BUTTON_H * 2 - 20, SCREEN_WIDTH - 2 * BUTTON_MARGIN, BUTTON_H)
        LOCATIONS["Submit_Score_Rect"] = draw_button(screen, submit_rect, "📤 GỬI ĐIỂM CỦA TÔI", FONT_MEDIUM, GREEN_BG, WHITE)
        
        back_rect = pygame.Rect(BUTTON_MARGIN, SCREEN_HEIGHT - BUTTON_H - 10, BACK_BUTTON_W, BUTTON_H)
        LOCATIONS["Back_Rect_Leaderboard"] = draw_button(screen, back_rect, "Quay Lại", FONT_MEDIUM, GRAY_INACTIVE, WHITE)
    except Exception as e:
        print(f"Lỗi vẽ leaderboard screen: {e}")

def draw_main_menu():
    global player_level, player_exp, player_health, STEAL_COST, player_coins, current_event, is_christmas_event_active
    
    try:
        if background_image:
            screen.blit(background_image, background_rect)
        else:
            screen.fill(MENU_COLOR)
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        draw_text(screen, "TRÒ CHƠI CẮM CÂU CÁ LÓC", FONT_LARGE, WHITE, SCREEN_WIDTH // 2, TITLE_Y, center=True)
        draw_text(screen, f"Cấp: {player_level} | Xu: {player_coins}", 
                  FONT_MEDIUM, COIN_COLOR, SCREEN_WIDTH // 2, TITLE_Y + int(SCREEN_HEIGHT * 0.05), center=True)
                  
        y_offset = TITLE_Y + int(SCREEN_HEIGHT * 0.1)
        
        if is_christmas_event_active:
            event_rect = pygame.Rect(BUTTON_MARGIN, y_offset, 
                                    SCREEN_WIDTH - 2 * BUTTON_MARGIN, BUTTON_H)
            event_text = "🎄 SỰ KIỆN GIÁNG SINH ĐANG DIỄN RA!"
            draw_button(screen, event_rect, event_text, FONT_MEDIUM, CHRISTMAS_COLOR, WHITE)
            y_offset += BUTTON_Y_STEP
        
        if current_event:
            event_rect = pygame.Rect(BUTTON_MARGIN, y_offset, 
                                    SCREEN_WIDTH - 2 * BUTTON_MARGIN, BUTTON_H)
            event_text = f"🎯 {current_event['name']} - {current_event['description']}"
            draw_button(screen, event_rect, event_text, FONT_MEDIUM, EVENT_COLOR, WHITE)
            y_offset += BUTTON_Y_STEP
        
        BUTTON_W = SCREEN_WIDTH - 2 * BUTTON_MARGIN
        
        char_rect = pygame.Rect(BUTTON_MARGIN, y_offset, BUTTON_W, BUTTON_H)
        LOCATIONS["Char_Info_Rect"] = draw_button(screen, char_rect, "THÔNG TIN NHÂN VẬT", FONT_MEDIUM, BLUE_WATER, WHITE)
        
        inventory_rect = pygame.Rect(BUTTON_MARGIN, y_offset + BUTTON_Y_STEP, BUTTON_W, BUTTON_H)
        LOCATIONS["Inventory_Rect"] = draw_button(screen, inventory_rect, "TÚI ĐỒ & SHOP", FONT_MEDIUM, YELLOW_BUTTON, BLACK)
        
        market_rect = pygame.Rect(BUTTON_MARGIN, y_offset + 2 * BUTTON_Y_STEP, BUTTON_W, BUTTON_H)
        LOCATIONS["Market_Rect"] = draw_button(screen, market_rect, "CHỢ CÁ TỰ DO", FONT_MEDIUM, MARKET_COLOR, WHITE)
        
        start_rect = pygame.Rect(BUTTON_MARGIN, y_offset + 3 * BUTTON_Y_STEP, BUTTON_W, BUTTON_H)
        LOCATIONS["Start_Rect"] = draw_button(screen, start_rect, "ĐI CẮM CÂU", FONT_MEDIUM, GREEN_BG, WHITE)
        
        steal_rect = pygame.Rect(BUTTON_MARGIN, y_offset + 4 * BUTTON_Y_STEP, BUTTON_W, BUTTON_H)
        steal_text = f"THĂM TRỘM CẦN (Tốn {STEAL_COST} HP)"
        
        if player_health >= STEAL_COST:
            LOCATIONS["Steal_Rect"] = draw_button(screen, steal_rect, steal_text, FONT_MEDIUM, RED_FISH, WHITE)
        else:
            LOCATIONS["Steal_Rect"] = draw_button(screen, steal_rect, steal_text + " (HP Thấp!)", FONT_MEDIUM, GRAY_INACTIVE, WHITE)
        
        leaderboard_rect = pygame.Rect(BUTTON_MARGIN, y_offset + 5 * BUTTON_Y_STEP, BUTTON_W, BUTTON_H)
        LOCATIONS["Leaderboard_Rect"] = draw_button(screen, leaderboard_rect, "🏆 BẢNG XẾP HẠNG", FONT_MEDIUM, (255, 215, 0), BLACK)
        
        quit_rect = pygame.Rect(BUTTON_MARGIN, SCREEN_HEIGHT - BUTTON_H - 10, BACK_BUTTON_W, BUTTON_H)
        LOCATIONS["Quit_Rect"] = draw_button(screen, quit_rect, "THOÁT", FONT_MEDIUM, RED_FISH, WHITE)
    except Exception as e:
        print(f"Lỗi vẽ main menu: {e}")

def draw_steal_menu():
    global STEAL_COST, player_health
    try:
        screen.fill(MENU_COLOR)
        draw_text(screen, "XÁC NHẬN THĂM TRỘM CẦN", FONT_LARGE, RED_FISH, SCREEN_WIDTH // 2, TITLE_Y, center=True)
        
        warning_text = f"Hành động này tốn {STEAL_COST} HP. Bạn có chắc muốn đi luôn không?"
        draw_text(screen, warning_text, FONT_MEDIUM, WHITE, SCREEN_WIDTH // 2, TITLE_Y + int(SCREEN_HEIGHT * 0.1), center=True)
        draw_text(screen, f"HP hiện tại: {player_health}/{MAX_HEALTH}", FONT_MEDIUM, HP_COLOR, SCREEN_WIDTH // 2, TITLE_Y + int(SCREEN_HEIGHT * 0.15), center=True)
        
        BUTTON_W = int(SCREEN_WIDTH * 0.4)
        y_button = int(SCREEN_HEIGHT * 0.5)
        
        go_rect = pygame.Rect(BUTTON_MARGIN, y_button, BUTTON_W, BUTTON_H)
        LOCATIONS["Go_Rect"] = draw_button(screen, go_rect, "ĐI LUÔN", FONT_MEDIUM, RED_FISH, WHITE)
        
        back_rect = pygame.Rect(SCREEN_WIDTH - BUTTON_MARGIN - BUTTON_W, y_button, BUTTON_W, BUTTON_H)
        LOCATIONS["Back_Rect_Steal_Menu"] = draw_button(screen, back_rect, "SUY NGHĨ LẠI", FONT_MEDIUM, BLUE_WATER, WHITE)
    except Exception as e:
        print(f"Lỗi vẽ steal menu: {e}")

def draw_steal_slots():
    global steal_slots_data 
    try:
        screen.fill(GREEN_BG)
        draw_text(screen, "CHỌN CẦN NGƯỜI KHÁC ĐANG CẮM", FONT_MEDIUM, WHITE, SCREEN_WIDTH // 2, TITLE_Y, center=True)
        draw_text(screen, "Chọn 1 trong 3 ô cắm trộm (Chỉ được chọn 1 lần)", FONT_SMALL, YELLOW_BUTTON, SCREEN_WIDTH // 2, TITLE_Y + int(SCREEN_HEIGHT * 0.05), center=True)
        
        y_start = int(SCREEN_HEIGHT * 0.25)
        SLOT_W = SCREEN_WIDTH - 2 * BUTTON_MARGIN
        SLOT_H = int(SCREEN_HEIGHT * 0.12) 
        y_step = SLOT_H + int(SCREEN_HEIGHT * 0.03)
        
        is_any_slot_clicked = any(slot.get("revealed", False) for slot in steal_slots_data)
        
        for i, slot in enumerate(steal_slots_data):
            rect = pygame.Rect(BUTTON_MARGIN, y_start + i * y_step, SLOT_W, SLOT_H)
            slot["Rect"] = rect
            
            status_text = f"Đang Cắm (Kênh: {slot.get('chan', '???')}) - Cần của người khác"
            color = BLUE_WATER
            
            if slot.get("revealed", False):
                if slot["catch_data"]:
                    status_text = f"CÁ ĐÃ THU HOẠCH: {slot['catch_data']['weight']:.2f} kg cá! (+{slot['catch_data']['exp']} EXP)"
                    color = RED_FISH
                else:
                    status_text = "Không Dính Cá"
                    color = GRAY_INACTIVE
            
            draw_button(screen, rect, status_text, FONT_SMALL, color, WHITE) 

        if is_any_slot_clicked:
            BUTTON_W_LONG = int(SCREEN_WIDTH * 0.6)
            back_rect = pygame.Rect(SCREEN_WIDTH // 2 - BUTTON_W_LONG // 2, SCREEN_HEIGHT - BUTTON_H - 10, BUTTON_W_LONG, BUTTON_H)
            LOCATIONS["Back_Rect_Steal_Slots"] = draw_button(screen, back_rect, "QUAY LẠI MÀN HÌNH CHÍNH", FONT_MEDIUM, GRAY_INACTIVE, WHITE)
        else:
            if "Back_Rect_Steal_Slots" in LOCATIONS:
                del LOCATIONS["Back_Rect_Steal_Slots"]
    except Exception as e:
        print(f"Lỗi vẽ steal slots: {e}")

def draw_select_location():
    global LOCATIONS, current_location, player_level 
    try:
        screen.fill(GREEN_BG)
        draw_text(screen, "CHỌN KHU VỰC CẮM CÂU", FONT_LARGE, WHITE, SCREEN_WIDTH // 2, TITLE_Y, center=True)
        draw_text(screen, f"Cấp hiện tại: {player_level}", FONT_MEDIUM, WHITE, SCREEN_WIDTH // 2, TITLE_Y + int(SCREEN_HEIGHT * 0.05), center=True)
        
        BUTTON_W = SCREEN_WIDTH - 2 * BUTTON_MARGIN
        start_x = BUTTON_MARGIN 
        y_start = int(SCREEN_HEIGHT * 0.2)
        y_step = BUTTON_H + int(SCREEN_HEIGHT * 0.02)
        
        location_keys = [k for k, v in LOCATIONS.items() if isinstance(v, dict) and 'Rate_Per_Minute' in v]
        
        for i, loc_name in enumerate(location_keys):
            loc_data = LOCATIONS[loc_name]
            required_level = loc_data.get("required_level", 1)
            
            can_access = player_level >= required_level
            button_color = BLUE_WATER if can_access else LOCKED_COLOR
            button_text = f"{loc_name} (Yêu cầu Lv: {required_level})"
            
            rect = pygame.Rect(start_x, y_start + i * y_step, BUTTON_W, BUTTON_H)
            LOCATIONS[loc_name]["Rect"] = draw_button(screen, rect, button_text, FONT_MEDIUM, button_color, WHITE)
            
            if not can_access:
                if "Rect" in LOCATIONS[loc_name]: del LOCATIONS[loc_name]["Rect"]
                
        back_rect = pygame.Rect(BUTTON_MARGIN, SCREEN_HEIGHT - BUTTON_H - 10, BACK_BUTTON_W, BUTTON_H)
        LOCATIONS["Back_Rect_Location"] = draw_button(screen, back_rect, "Quay Lại", FONT_MEDIUM, GRAY_INACTIVE, WHITE)
    except Exception as e:
        print(f"Lỗi vẽ select location: {e}")

def draw_select_channel():
    global current_location, LOCATIONS 
    try:
        screen.fill(GREEN_BG)
        draw_text(screen, f"KHU VỰC: {current_location}", FONT_LARGE, WHITE, SCREEN_WIDTH // 2, TITLE_Y, center=True)
        draw_text(screen, f"CHỌN KÊNH", FONT_MEDIUM, WHITE, SCREEN_WIDTH // 2, TITLE_Y + int(SCREEN_HEIGHT * 0.05), center=True)
        
        BUTTON_W = SCREEN_WIDTH - 2 * BUTTON_MARGIN
        start_x = BUTTON_MARGIN
        y_start = int(SCREEN_HEIGHT * 0.2)
        y_step = BUTTON_H + int(SCREEN_HEIGHT * 0.02)
        channels_data = LOCATIONS.get(current_location, {}).get("Channels", {})
        for i, chan_name in enumerate(channels_data.keys()):
            rect = pygame.Rect(start_x, y_start + i * y_step, BUTTON_W, BUTTON_H)
            channels_data[chan_name]["Rect"] = draw_button(screen, rect, chan_name, FONT_MEDIUM, BLUE_WATER, WHITE) 
        back_rect = pygame.Rect(BUTTON_MARGIN, SCREEN_HEIGHT - BUTTON_H - 10, BACK_BUTTON_W, BUTTON_H)
        LOCATIONS["Back_Rect_Channel"] = draw_button(screen, back_rect, "Quay Lại", FONT_MEDIUM, GRAY_INACTIVE, WHITE)
    except Exception as e:
        print(f"Lỗi vẽ select channel: {e}")

def draw_fishing_screen():
    global current_location, current_channel, rods_inventory, fish_inventory, fishing_slots
    try:
        screen.fill(BLUE_WATER)
        draw_text(screen, f"{current_location} - {current_channel}", FONT_LARGE, WHITE, SCREEN_WIDTH // 2, TITLE_Y, center=True)
        
        rods_at_current_location = [
            rod for rod in rods_inventory 
            if rod.get("location") == current_location and rod.get("channel") == current_channel
        ]
        
        current_slots_map = {rod.get("slot_index"): rod["id"] for rod in rods_at_current_location if rod.get("slot_index") is not None}
        
        global NUM_SLOTS
        if len(fishing_slots) != NUM_SLOTS:
            fishing_slots = [{"slot_id": i, "rod_id": None} for i in range(NUM_SLOTS)]

        for i in range(NUM_SLOTS):
            fishing_slots[i]["rod_id"] = current_slots_map.get(i)
        
        col_width = SCREEN_WIDTH // 2
        SLOT_PADDING = int(SCREEN_WIDTH * 0.02)
        SLOT_W = col_width - 2 * SLOT_PADDING 
        SLOT_H = int(SCREEN_HEIGHT * 0.1) 
        
        y_start_slots = int(SCREEN_HEIGHT * 0.12) 
        y_step_slots = SLOT_H + int(SCREEN_HEIGHT * 0.015) 
        
        TEXT_LINE_H = int(SLOT_H * 0.2) 
        
        BUTTON_IN_SLOT_H = int(SLOT_H * 0.3) 
        BUTTON_IN_SLOT_W = int(SLOT_W * 0.5)
        
        for i, slot in enumerate(fishing_slots):
            
            col = i % 2
            row = i // 2
            x = col * col_width + SLOT_PADDING 
            y = y_start_slots + row * y_step_slots
            
            if y + SLOT_H > SCREEN_HEIGHT - int(SCREEN_HEIGHT * 0.15): continue 
            
            slot_rect = pygame.Rect(x, y, SLOT_W, SLOT_H)
            
            slot["Rect"] = slot_rect 
            
            slot_color = GREEN_BG if slot.get("rod_id") is not None else GRAY_INACTIVE
            pygame.draw.rect(screen, slot_color, slot_rect, border_radius=5)
            pygame.draw.rect(screen, WHITE, slot_rect, 2, border_radius=5)
            
            draw_text(screen, f"Ô Cắm {i+1}", FONT_SMALL, WHITE, x + 5, y + 5) 
            
            if slot.get("rod_id") is not None:
                rod_id = slot["rod_id"]
                rod = next((r for r in rods_inventory if r["id"] == rod_id), None)
                
                if rod and rod["status"] == "Đang Cắm":
                    max_time = rod.get("max_cast_minutes", ROD_TEMPLATES["Cần Tre"]["base_cast_time"])
                    cast_time = rod.get("cast_time", time.time())
                    time_elapsed = int((time.time() - cast_time) / 60)
                    
                    draw_text(screen, f"Cần: {rod.get('name', 'Mặc Định')} (Lv {rod['level']})", FONT_VERY_SMALL, YELLOW_BUTTON, x + 5, y + 5 + TEXT_LINE_H) 
                    draw_text(screen, f"Đang cắm ({time_elapsed}/{max_time} phút)", FONT_VERY_SMALL, WHITE, x + 5, y + 5 + 2 * TEXT_LINE_H) 
                    
                    reel_in_rect = pygame.Rect(x + 5, y + SLOT_H - BUTTON_IN_SLOT_H - 5, BUTTON_IN_SLOT_W, BUTTON_IN_SLOT_H)
                    slot["reel_in_rect"] = draw_button(screen, reel_in_rect, "THU CÂU", FONT_VERY_SMALL, GRAY_INACTIVE, WHITE) 
                        
                elif rod and "Dính" in rod["status"]:
                    
                    status_text = rod["status"]
                    draw_text(screen, status_text, FONT_SMALL, RED_FISH, x + 5, y + 5 + TEXT_LINE_H) 
                    draw_text(screen, "THU CÂU NGAY!", FONT_VERY_SMALL, RED_FISH, x + 5, y + 5 + 2 * TEXT_LINE_H) 

                    reel_in_rect = pygame.Rect(x + 5, y + SLOT_H - BUTTON_IN_SLOT_H - 5, BUTTON_IN_SLOT_W, BUTTON_IN_SLOT_H)
                    slot["reel_in_rect"] = draw_button(screen, reel_in_rect, "THU CÂU", FONT_VERY_SMALL, RED_FISH, WHITE) 

                elif rod and "Hết Giờ" in rod["status"]: 
                    
                    status_text = rod["status"]
                    draw_text(screen, "HẾT GIỜ CẮM CÂU!", FONT_SMALL, RED_FISH, x + 5, y + 5 + TEXT_LINE_H) 
                    draw_text(screen, status_text, FONT_VERY_SMALL, WHITE, x + 5, y + 5 + 2 * TEXT_LINE_H) 

                    reel_in_rect = pygame.Rect(x + 5, y + SLOT_H - BUTTON_IN_SLOT_H - 5, BUTTON_IN_SLOT_W, BUTTON_IN_SLOT_H)
                    slot["reel_in_rect"] = draw_button(screen, reel_in_rect, "THU CÂU", FONT_VERY_SMALL, RED_FISH, WHITE)
                    
            else: 
                draw_text(screen, "Slot trống", FONT_SMALL, WHITE, x + 5, y + 5 + TEXT_LINE_H) 
                free_rods = len([r for r in rods_inventory if r["status"] == "Trống"]) 
                
                if free_rods > 0: 
                    cast_rect = pygame.Rect(x + 5, y + SLOT_H - BUTTON_IN_SLOT_H - 5, BUTTON_IN_SLOT_W, BUTTON_IN_SLOT_H)
                    slot["cast_rect"] = draw_button(screen, cast_rect, "CẮM CÂU", FONT_VERY_SMALL, YELLOW_BUTTON, BLACK) 
                else:
                    draw_text(screen, "Hết cần trống!", FONT_VERY_SMALL, RED_FISH, x + 5, y + 5 + 2 * TEXT_LINE_H) 


        STATS_W = SCREEN_WIDTH - 2 * BUTTON_MARGIN
        STATS_H = int(SCREEN_HEIGHT * 0.1) 
        
        stats_rect = pygame.Rect(BUTTON_MARGIN, SCREEN_HEIGHT - STATS_H, STATS_W, STATS_H)
        pygame.draw.rect(screen, BLACK, stats_rect, border_radius=5)
        
        free_rods = len([r for r in rods_inventory if r["status"] == "Trống"]) 
        
        STATS_LINE_H = (STATS_H - 20) // 2 
        draw_text(screen, f"Cần Trống: {free_rods}/{MAX_RODS}", FONT_SMALL, WHITE, BUTTON_MARGIN + 10, SCREEN_HEIGHT - STATS_H + 5)
        draw_text(screen, f"Cá đã bắt: {len(fish_inventory)} con", FONT_SMALL, WHITE, BUTTON_MARGIN + 10, SCREEN_HEIGHT - STATS_H + 5 + STATS_LINE_H)
        
        BACK_BUTTON_W_LONG = int(SCREEN_WIDTH * 0.35) 
        BUTTON_H_SHORT = int(BUTTON_H * 0.6) 
        
        back_rect = pygame.Rect(SCREEN_WIDTH - BACK_BUTTON_W_LONG - BUTTON_MARGIN, SCREEN_HEIGHT - STATS_H + 5 + STATS_LINE_H - BUTTON_H_SHORT // 2, BACK_BUTTON_W_LONG, BUTTON_H_SHORT)
        LOCATIONS["Back_Rect_Fishing"] = draw_button(screen, back_rect, "Quay Lại Kênh", FONT_VERY_SMALL, GRAY_INACTIVE, WHITE)
    except Exception as e:
        print(f"Lỗi vẽ fishing screen: {e}")

# --- XỬ LÝ CLICK ---

def handle_click(pos):
    global game_state, current_location, current_channel, rods_inventory, player_exp, fish_inventory, MAX_RODS, player_health, STEAL_COST, selected_rod_id, player_coins, fish_to_sell_selected_type, fish_to_sell_quantity, market_slot_end_time, MARKET_SLOT_DURATION, MARKET_SLOT_COST, market_selling_fish, market_customer, current_event, event_cooldown_end, christmas_items_inventory, christmas_exchange_selected, is_christmas_event_active, player_name
    
    if game_state == "MAIN_MENU":
        if "Char_Info_Rect" in LOCATIONS and LOCATIONS["Char_Info_Rect"].collidepoint(pos):
            game_state = "CHARACTER_SCREEN"
            return
        if "Inventory_Rect" in LOCATIONS and LOCATIONS["Inventory_Rect"].collidepoint(pos):
            game_state = "INVENTORY_SCREEN"
            return
        if "Market_Rect" in LOCATIONS and LOCATIONS["Market_Rect"].collidepoint(pos):
            game_state = "MARKET_MENU"
            return
        if "Start_Rect" in LOCATIONS and LOCATIONS["Start_Rect"].collidepoint(pos):
            game_state = "SELECT_LOCATION"
            return
        if "Steal_Rect" in LOCATIONS and LOCATIONS["Steal_Rect"].collidepoint(pos):
            if player_health >= STEAL_COST:
                game_state = "STEAL_MENU"
            else:
                display_message(f"HP thấp! Cần tối thiểu {STEAL_COST} HP để thăm trộm.", 3)
            return
        if "Leaderboard_Rect" in LOCATIONS and LOCATIONS["Leaderboard_Rect"].collidepoint(pos):
            game_state = "LEADERBOARD_SCREEN"
            return
        if "Quit_Rect" in LOCATIONS and LOCATIONS["Quit_Rect"].collidepoint(pos):
            save_game() 
            global running 
            running = False
            return
            
    elif game_state == "LEADERBOARD_SCREEN":
        if "Submit_Score_Rect" in LOCATIONS and LOCATIONS["Submit_Score_Rect"].collidepoint(pos):
            success, message = leaderboard_manager.submit_score(
                player_name, 
                player_level, 
                player_coins, 
                len(fish_inventory)
            )
            display_message(message, 3)
            return
            
        if "Back_Rect_Leaderboard" in LOCATIONS and LOCATIONS["Back_Rect_Leaderboard"].collidepoint(pos):
            game_state = "MAIN_MENU"
            return

    elif game_state == "MARKET_MENU":
        if "Market_Rent_Slot_Rect" in LOCATIONS and LOCATIONS["Market_Rent_Slot_Rect"] and LOCATIONS["Market_Rent_Slot_Rect"].collidepoint(pos):
            if player_coins >= MARKET_SLOT_COST:
                player_coins -= MARKET_SLOT_COST
                market_slot_end_time = time.time() + MARKET_SLOT_DURATION
                display_message(f"Thuê chỗ thành công! Bắt đầu bày bán cá.", 3)
                game_state = "MARKET_SELECT_FISH"
            else:
                display_message(f"Không đủ Xu! Cần {MARKET_SLOT_COST} Xu để thuê chỗ.", 3)
            return
            
        if "Market_Go_Selling_Rect" in LOCATIONS and LOCATIONS["Market_Go_Selling_Rect"] and LOCATIONS["Market_Go_Selling_Rect"].collidepoint(pos):
            if market_slot_end_time > time.time():
                 if market_selling_fish:
                     game_state = "MARKET_SELL"
                 else:
                     game_state = "MARKET_SELECT_FISH"
            return
            
        if "Back_Rect_Market_Menu" in LOCATIONS and LOCATIONS["Back_Rect_Market_Menu"].collidepoint(pos):
            game_state = "MAIN_MENU"
            return

    elif game_state == "MARKET_SELECT_FISH":
        if "Back_Rect_Market_Select_Fish" in LOCATIONS and LOCATIONS["Back_Rect_Market_Select_Fish"].collidepoint(pos):
            market_selling_fish = [] 
            game_state = "MARKET_MENU"
            display_message("Đã hủy bày bán cá.", 1)
            return
            
        if "Market_Fish_Inventory" in LOCATIONS:
            for item in LOCATIONS["Market_Fish_Inventory"]:
                if item["rect"].collidepoint(pos):
                    fish_id = item["id"]
                    fish = next((f for f in fish_inventory if f.get('id') == fish_id), None)
                    if fish and fish_id not in [f['id'] for f in market_selling_fish]:
                        market_selling_fish.append({'id': fish['id'], 'name': fish['name'], 'weight': fish['weight']})
                        display_message(f"Đã bày bán 1 con {fish['name']}.", 1)
                        return
                        
        if "Finish_Selecting_Fish" in LOCATIONS and LOCATIONS["Finish_Selecting_Fish"].collidepoint(pos):
            if not market_selling_fish:
                display_message("Chưa chọn cá nào để bày bán!", 2)
                return
            game_state = "MARKET_SELL"
            return

    elif game_state == "MARKET_SELL":
        if market_customer and "Market_Accept_Offer_Rect" in LOCATIONS and LOCATIONS["Market_Accept_Offer_Rect"].collidepoint(pos):
            success, msg = accept_market_offer()
            display_message(msg, 3)
            return
            
        if market_customer and "Market_Reject_Offer_Rect" in LOCATIONS and LOCATIONS["Market_Reject_Offer_Rect"].collidepoint(pos):
            success, msg = reject_market_offer()
            display_message(msg, 3)
            return
            
        if not market_customer and "Back_Rect_Market_Sell" in LOCATIONS and LOCATIONS["Back_Rect_Market_Sell"].collidepoint(pos):
            game_state = "MARKET_MENU"
            return

    elif game_state == "CHRISTMAS_GIFT":
        if "Christmas_Exchange_Rect" in LOCATIONS and LOCATIONS["Christmas_Exchange_Rect"].collidepoint(pos):
            if can_exchange_christmas_gift():
                success, msg = exchange_christmas_gift()
                christmas_exchange_selected = msg
                display_message(msg, 5)
            else:
                display_message("Không đủ vật phẩm để đổi quà!", 3)
            return
            
        if "Back_Rect_Christmas" in LOCATIONS and LOCATIONS["Back_Rect_Christmas"].collidepoint(pos):
            game_state = "MAIN_MENU"
            return
            
    elif game_state == "CHARACTER_SCREEN":
        if "Back_Rect_Character" in LOCATIONS and LOCATIONS["Back_Rect_Character"].collidepoint(pos):
            game_state = "MAIN_MENU"
            return
            
    elif game_state == "INVENTORY_SCREEN":
        if "Shop_Rect" in LOCATIONS and LOCATIONS["Shop_Rect"].collidepoint(pos):
             game_state = "SHOP"
             return
             
        if "Sell_Fish_Rect" in LOCATIONS and LOCATIONS["Sell_Fish_Rect"].collidepoint(pos):
             fish_to_sell_selected_type = None 
             fish_to_sell_quantity = 0
             game_state = "SELL_FISH"
             return
             
        if "Inventory_Slots" in LOCATIONS:
            for item in LOCATIONS["Inventory_Slots"]:
                if item["rect"].collidepoint(pos):
                    selected_rod_id = item["id"]
                    game_state = "UPGRADE_SCREEN"
                    return

        if "Back_Rect_Inventory" in LOCATIONS and LOCATIONS["Back_Rect_Inventory"].collidepoint(pos):
            game_state = "MAIN_MENU"
            return
            
    elif game_state == "UPGRADE_SCREEN":
        if "Upgrade_Rod_Detail" in LOCATIONS and LOCATIONS["Upgrade_Rod_Detail"] is not None and LOCATIONS["Upgrade_Rod_Detail"].collidepoint(pos):
            rod = next((r for r in rods_inventory if r["id"] == selected_rod_id), None)
            if rod and rod["status"] != "Đang Cắm":
                success, msg = upgrade_rod(selected_rod_id) 
                display_message(msg, 3)
            else:
                display_message("Không thể nâng cấp! Cần câu đang được sử dụng.", 3)
            return
            
        if "Back_Rect_Upgrade" in LOCATIONS and LOCATIONS["Back_Rect_Upgrade"].collidepoint(pos):
            selected_rod_id = None
            game_state = "INVENTORY_SCREEN"
            return
            
    elif game_state == "SHOP":
        if "Shop_Items" in LOCATIONS:
            for item in LOCATIONS["Shop_Items"]:
                if item["name"] == "Cần Sắt" and item["rect"].collidepoint(pos):
                    success, msg = buy_rod("Cần Sắt")
                    display_message(msg, 3)
                    return
                    
        if "Shop_Upgrade_Rod_Limit_Rect" in LOCATIONS and LOCATIONS["Shop_Upgrade_Rod_Limit_Rect"] is not None and LOCATIONS["Shop_Upgrade_Rod_Limit_Rect"].collidepoint(pos):
            upgrade_rod_limit_cost = 50000 
            if player_coins >= upgrade_rod_limit_cost and MAX_RODS < 5:
                player_coins -= upgrade_rod_limit_cost
                MAX_RODS += 1
                display_message(f"Nâng cấp giới hạn cần câu thành công lên {MAX_RODS}!", 3)
            elif MAX_RODS >= 5:
                display_message("Đã đạt giới hạn nâng cấp tối đa.", 3)
            else:
                display_message(f"Không đủ Xu! Cần {upgrade_rod_limit_cost} Xu.", 3)
            return
            
        if "Back_Rect_Shop" in LOCATIONS and LOCATIONS["Back_Rect_Shop"].collidepoint(pos):
            game_state = "INVENTORY_SCREEN"
            return
            
    elif game_state == "SELL_FISH":
        if "Sell_Fish_Options" in LOCATIONS:
            for item in LOCATIONS["Sell_Fish_Options"]:
                if item["rect"].collidepoint(pos):
                    fish_to_sell_selected_type = item["name"]
                    fish_to_sell_quantity = 1 
                    return
                    
        if "Sell_Controls" in LOCATIONS and fish_to_sell_selected_type:
            max_count = next((item['max_count'] for item in LOCATIONS["Sell_Fish_Options"] if item['name'] == fish_to_sell_selected_type), 0)
            
            if "Minus" in LOCATIONS["Sell_Controls"] and LOCATIONS["Sell_Controls"]["Minus"].collidepoint(pos):
                fish_to_sell_quantity = max(1, fish_to_sell_quantity - 1)
                return
                
            if "Plus" in LOCATIONS["Sell_Controls"] and LOCATIONS["Sell_Controls"]["Plus"].collidepoint(pos):
                fish_to_sell_quantity = min(max_count, fish_to_sell_quantity + 1)
                return
                
            if "Max" in LOCATIONS["Sell_Controls"] and LOCATIONS["Sell_Controls"]["Max"].collidepoint(pos):
                fish_to_sell_quantity = max_count
                return
                
            if "Sell" in LOCATIONS["Sell_Controls"] and LOCATIONS["Sell_Controls"]["Sell"].collidepoint(pos) and fish_to_sell_quantity > 0:
                success, msg = sell_fish(fish_to_sell_selected_type, fish_to_sell_quantity)
                display_message(msg, 3)
                fish_to_sell_selected_type = None 
                fish_to_sell_quantity = 0
                return
                
        if "Back_Rect_Sell_Fish" in LOCATIONS and LOCATIONS["Back_Rect_Sell_Fish"].collidepoint(pos):
            game_state = "INVENTORY_SCREEN"
            return
            
    elif game_state == "STEAL_MENU":
        if "Back_Rect_Steal_Menu" in LOCATIONS and LOCATIONS["Back_Rect_Steal_Menu"].collidepoint(pos):
            game_state = "MAIN_MENU"
            return
        if "Go_Rect" in LOCATIONS and LOCATIONS["Go_Rect"].collidepoint(pos):
            if player_health >= STEAL_COST:
                player_health -= STEAL_COST
                prepare_steal_slots() 
                game_state = "STEAL_SLOTS"
            else:
                game_state = "MAIN_MENU"
                display_message("HP không đủ để tiếp tục thăm trộm.", 3)
            return

    elif game_state == "STEAL_SLOTS":
        if "Back_Rect_Steal_Slots" in LOCATIONS and LOCATIONS["Back_Rect_Steal_Slots"].collidepoint(pos):
            game_state = "MAIN_MENU"
            return
            
        is_any_slot_clicked = any(slot.get("revealed", False) for slot in steal_slots_data)
        
        if not is_any_slot_clicked:
            for slot in steal_slots_data:
                if "Rect" in slot and slot["Rect"].collidepoint(pos):
                    slot["revealed"] = True 
                    
                    if slot["catch_data"]:
                        catch = slot["catch_data"]
                        player_exp += catch["exp"] 
                        check_level_up()
                        fish_inventory.append({
                            "name": catch['name'], 
                            "weight": catch['weight'], 
                            "loc": catch.get('loc', 'Thăm Trộm'), 
                            "chan": catch.get('chan', 'Kênh ???'), 
                            "exp": catch['exp'],
                            "id": generate_fish_id()
                        })
                        display_message(f"THÀNH CÔNG! Trộm được {catch['weight']:.2f} kg cá! (+{catch['exp']} EXP)", 3)
                    else:
                        display_message("Không có cá! Mất công rồi.", 3)
                    for s in steal_slots_data:
                        s["revealed"] = True
                    return

    elif game_state == "SELECT_LOCATION":
        if "Back_Rect_Location" in LOCATIONS and LOCATIONS["Back_Rect_Location"].collidepoint(pos):
            game_state = "MAIN_MENU"
            return
        
        location_keys = [k for k, v in LOCATIONS.items() if isinstance(v, dict) and 'Rate_Per_Minute' in v]
        for loc_name in location_keys:
            loc_data = LOCATIONS[loc_name]
            required_level = loc_data.get("required_level", 1)
            if loc_name in LOCATIONS and "Rect" in LOCATIONS[loc_name] and LOCATIONS[loc_name]["Rect"].collidepoint(pos):
                if player_level >= required_level:
                    current_location = loc_name
                    game_state = "SELECT_CHANNEL"
                    return 
                else:
                    display_message(f"Yêu cầu Level {required_level} để vào {loc_name}!")
                    return

    elif game_state == "SELECT_CHANNEL":
        if "Back_Rect_Channel" in LOCATIONS and LOCATIONS["Back_Rect_Channel"].collidepoint(pos):
            current_location = None
            game_state = "SELECT_LOCATION"
            return
            
        channels_data = LOCATIONS.get(current_location, {}).get("Channels", {})
        for chan_name, data in channels_data.items():
            if "Rect" in data and data["Rect"].collidepoint(pos):
                current_channel = chan_name
                game_state = "FISHING"
                return

    elif game_state == "FISHING":
        if "Back_Rect_Fishing" in LOCATIONS and LOCATIONS["Back_Rect_Fishing"].collidepoint(pos):
            current_channel = None
            game_state = "SELECT_CHANNEL"
            return
        
        if current_location and current_channel:
            for slot in fishing_slots:
                rod_id = slot.get("rod_id")
                rod = next((r for r in rods_inventory if r["id"] == rod_id), None)
                
                if rod_id is None and "cast_rect" in slot and slot["cast_rect"].collidepoint(pos):
                    free_rod = next((r for r in rods_inventory if r["status"] == "Trống"), None)
                    if free_rod:
                        free_rod["status"] = "Đang Cắm"
                        free_rod["cast_time"] = time.time()
                        free_rod["last_check_time"] = free_rod["cast_time"] 
                        free_rod["location"] = current_location
                        free_rod["channel"] = current_channel
                        free_rod["slot_index"] = slot["slot_id"] 
                        slot["rod_id"] = free_rod["id"]
                        display_message(f"Đã cắm {free_rod['name']} vào Ô {slot['slot_id'] + 1} (Max: {free_rod['max_cast_minutes']} phút)", 3)
                    else:
                        display_message("Hết cần câu trống để cắm!", 3)
                elif rod and "reel_in_rect" in slot and slot["reel_in_rect"].collidepoint(pos):
                    if "catch_data" in rod:
                        catch = rod["catch_data"]
                        player_exp += catch["exp"] 
                        check_level_up()
                        fish_inventory.append({
                            "name": catch['name'], 
                            "weight": catch['weight'], 
                            "loc": catch['loc'], 
                            "chan": catch['chan'], 
                            "exp": catch['exp'],
                            "id": catch['id']
                        })
                        if catch.get("christmas_item"):
                            item = catch["christmas_item"]
                            add_christmas_item_to_inventory(item["name"], item["weight"])
                            display_message(f"Nhận được {item['name']} từ cá Lóc!", 3)
                        del rod["catch_data"] 
                        display_message(f"Thu được {catch['weight']:.2f} kg cá! (+{catch['exp']} EXP)", 3)
                    elif rod["status"] == "Đang Cắm":
                        display_message("Thu câu! Cần đã trở về kho.", 3)
                    elif rod["status"] == "Hết Giờ" or rod["status"] == "Hết Giờ (Offline)":
                        display_message("Thu câu! Cần đã hết giờ cắm.", 3)
                    rod["status"] = "Trống" 
                    for key in ["cast_time", "last_check_time", "location", "channel", "slot_index", "catch_data"]:
                         if key in rod: del rod[key]
                    slot["rod_id"] = None

# --- VÒNG LẶP GAME CHÍNH ---
running = True

def main_game_loop():
    global running, game_state
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_game()
                running = False
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                handle_click(event.pos)
        
        update_online_status()
        update_message()
        
        screen.fill(BLACK)
        
        if game_state == "MAIN_MENU":
            draw_main_menu()
        elif game_state == "LEADERBOARD_SCREEN":
            draw_leaderboard_screen()
        elif game_state == "CHARACTER_SCREEN":
            draw_character_screen()
        elif game_state == "INVENTORY_SCREEN":
            draw_inventory_screen()
        elif game_state == "UPGRADE_SCREEN":
            draw_upgrade_screen()
        elif game_state == "SHOP":
            draw_shop_screen()
        elif game_state == "SELL_FISH":
            draw_sell_fish_screen()
        elif game_state == "SELECT_LOCATION":
            draw_select_location()
        elif game_state == "SELECT_CHANNEL":
            draw_select_channel()
        elif game_state == "FISHING":
            draw_fishing_screen()
        elif game_state == "STEAL_MENU":
            draw_steal_menu()
        elif game_state == "STEAL_SLOTS":
            draw_steal_slots()
        elif game_state == "MARKET_MENU":
            draw_market_menu()
        elif game_state == "MARKET_SELECT_FISH":
            draw_market_select_fish()
        elif game_state == "MARKET_SELL":
            draw_market_sell_screen()
        elif game_state == "CHRISTMAS_GIFT":
            draw_christmas_gift_screen()
        
        draw_global_message()
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()

# --- CHẠY GAME ---
if __name__ == "__main__":
    print("Game đã sẵn sàng!")
    main_game_loop()
