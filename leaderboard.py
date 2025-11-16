from flask import Flask, jsonify, request
import json
import os
from datetime import datetime

app = Flask(__name__)

class Leaderboard:
    def __init__(self):
        self.data_file = "leaderboard_data.json"
        self.load_data()
    
    def load_data(self):
        """Tải dữ liệu bảng xếp hạng"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.players = json.load(f)
            else:
                self.players = []
        except:
            self.players = []
    
    def save_data(self):
        """Lưu dữ liệu bảng xếp hạng"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.players, f, ensure_ascii=False, indent=2)
            return True
        except:
            return False
    
    def add_player(self, player_data):
        """Thêm hoặc cập nhật player"""
        try:
            # Tính điểm tổng
            total_score = (player_data.get('level', 1) * 100 + 
                          player_data.get('coins', 0) + 
                          player_data.get('fish_count', 0) * 10)
            
            player_data['total_score'] = total_score
            player_data['last_updated'] = datetime.now().isoformat()
            
            # Kiểm tra player đã tồn tại chưa
            existing_index = -1
            for i, player in enumerate(self.players):
                if player.get('name') == player_data.get('name'):
                    existing_index = i
                    break
            
            if existing_index >= 0:
                # Cập nhật nếu điểm cao hơn
                if total_score > self.players[existing_index].get('total_score', 0):
                    self.players[existing_index] = player_data
            else:
                # Thêm mới
                self.players.append(player_data)
            
            # Sắp xếp theo điểm
            self.players.sort(key=lambda x: x.get('total_score', 0), reverse=True)
            
            # Giới hạn top 50
            self.players = self.players[:50]
            
            # Lưu dữ liệu
            self.save_data()
            
            return True, "Điểm số đã được cập nhật!"
        except Exception as e:
            return False, f"Lỗi: {str(e)}"
    
    def get_leaderboard(self, limit=10):
        """Lấy bảng xếp hạng"""
        return self.players[:limit]

# Khởi tạo bảng xếp hạng
leaderboard = Leaderboard()

@app.route('/')
def home():
    return jsonify({"message": "Leaderboard API is running!"})

@app.route('/leaderboard')
def get_leaderboard():
    """API lấy bảng xếp hạng"""
    limit = request.args.get('limit', 10, type=int)
    data = leaderboard.get_leaderboard(limit)
    return jsonify({"leaderboard": data})

@app.route('/submit_score', methods=['POST'])
def submit_score():
    """API gửi điểm số"""
    try:
        player_data = request.get_json()
        
        if not player_data:
            return jsonify({"error": "Không có dữ liệu"}), 400
        
        success, message = leaderboard.add_player(player_data)
        
        if success:
            return jsonify({"message": message, "success": True})
        else:
            return jsonify({"error": message}), 400
            
    except Exception as e:
        return jsonify({"error": f"Lỗi server: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
