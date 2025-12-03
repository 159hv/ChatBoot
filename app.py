import sys
import os
from types import ModuleType

# Mock eventlet.hubs modules that don't exist on Windows to fix PyInstaller issue
if getattr(sys, 'frozen', False) and sys.platform == 'win32':
    for module in ['eventlet.hubs.epolls', 'eventlet.hubs.kqueue', 'eventlet.hubs.poll', 'eventlet.hubs.selects']:
        sys.modules[module] = ModuleType(module)

from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
from config import Config
import eventlet
import openai
import threading
import uuid
import re
import requests

if getattr(sys, 'frozen', False):
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    static_folder = os.path.join(sys._MEIPASS, 'static')
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
else:
    app = Flask(__name__)

app.config.from_object(Config)
socketio = SocketIO(app, cors_allowed_origins="*")

# Store connected users: {sid: nickname}
connected_users = {}

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nickname = request.form.get('nickname')
        password = request.form.get('password')
        server = request.form.get('server')
        
        # Validation logic
        if not nickname:
            return render_template('login.html', error="请输入昵称", servers=app.config['SERVERS'])
        
        if password != '123456':
            return render_template('login.html', error="密码错误", servers=app.config['SERVERS'])
            
        session['nickname'] = nickname
        session['server'] = server
        return redirect(url_for('chat'))
            
    return render_template('login.html', servers=app.config['SERVERS'])

@app.route('/chat')
def chat():
    if 'nickname' not in session:
        return redirect(url_for('login'))
    return render_template('chat.html', nickname=session['nickname'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# WebSocket Events
@socketio.on('connect')
def handle_connect():
    pass

@socketio.on('join')
def handle_join(data):
    nickname = data.get('nickname')
    if nickname:
        connected_users[request.sid] = nickname
        join_room('general')
        # Broadcast user joined
        emit('system_message', {'msg': f'{nickname} 加入了聊天室'}, room='general')
        # Send user list update
        emit('update_users', {'users': list(connected_users.values())}, room='general')

def call_ai_api(prompt, room_id):
    request_id = str(uuid.uuid4())
    try:
        client = openai.OpenAI(
            api_key=app.config['AI_API_KEY'],
            base_url=app.config['AI_API_URL']
        )
        
        response = client.chat.completions.create(
            model=app.config['AI_MODEL_NAME'],
            messages=[
                {"role": "system", "content": app.config['AI_SYSTEM_PROMPT']},
                {"role": "user", "content": prompt}
            ],
            stream=True
        )
        
        # Emit start of message
        socketio.emit('ai_response_start', {'user': '成小理', 'id': request_id}, room=room_id)
        
        full_response = ""
        for chunk in response:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_response += content
                socketio.emit('ai_response_chunk', {'content': content, 'id': request_id}, room=room_id)
                eventlet.sleep(0) # Yield control to eventlet loop
                
        socketio.emit('ai_response_end', {'id': request_id}, room=room_id)
        
    except Exception as e:
        print(f"AI Error: {e}")
        socketio.emit('system_message', {'msg': '成小理暂时无法回复，请稍后再试。'}, room=room_id)

@socketio.on('send_message')
def handle_message(data):
    nickname = connected_users.get(request.sid, 'Unknown')
    msg = data.get('msg')
    # Timestamp can be added here
    import datetime
    time_str = datetime.datetime.now().strftime('%H:%M')
    
    # List to store assistant responses
    system_responses = []
    
    # Process @电影
    if msg and '@电影' in msg:
        # Regex to find @电影 followed by a URL
        # Supports @电影 http://... or @电影http://...
        match = re.search(r'@电影\s*(https?://\S+)', msg)
        if match:
            video_url = match.group(1)
            iframe_html = f'<iframe src="https://jx.m3u8.tv/jiexi/?url={video_url}" width="400" height="400" frameborder="0" allowfullscreen></iframe>'
            system_responses.append({
                'user': '视频助手',
                'msg': iframe_html
            })
            
    # Process @天气 (Weather)
    # Support: @天气 深圳 or @天气[深圳]
    match_brackets = re.search(r'@天气\[(.*?)\]', msg)
    match_space = re.search(r'@天气\s+(\S+)', msg)
    
    city_name = None
    if match_brackets:
        city_name = match_brackets.group(1)
    elif match_space:
        city_name = match_space.group(1)
    
    # If @天气 is present but no city extracted, check if it's a malformed command
    if not city_name and '@天气' in msg:
        # Optional: Provide help message
        help_card = """
        <div class="bg-blue-50 p-3 rounded-lg border border-blue-200 text-sm text-blue-800">
            <strong>💡 天气查询帮助</strong><br>
            请使用以下格式查询天气：<br>
            • @天气 深圳<br>
            • @天气[北京]
        </div>
        """
        system_responses.append({
            'user': '天气助手',
            'msg': help_card
        })
        
    if city_name:
        try:
            # Open-Meteo Implementation
            is_mock = False
            error_msg = None
            
            try:
                # Step 1: Geocoding
                geo_url = "https://geocoding-api.open-meteo.com/v1/search"
                geo_params = {
                    "name": city_name,
                    "count": 1,
                    "language": "zh",
                    "format": "json"
                }
                # Add User-Agent to avoid being blocked
                headers = {'User-Agent': 'ChatBoot/1.0'}
                
                print(f"Weather query for: {city_name}")
                geo_res = requests.get(geo_url, params=geo_params, headers=headers, timeout=10)
                
                # Retry logic with Pinyin if Chinese search fails
                if geo_res.status_code == 200 and not geo_res.json().get("results"):
                    try:
                        from pypinyin import pinyin, Style
                        
                        def get_pinyin(text):
                            pinyin_list = pinyin(text, style=Style.NORMAL)
                            return "".join([item[0] for item in pinyin_list])
                            
                        pinyin_name = get_pinyin(city_name)
                        print(f"Retrying weather search with Pinyin: {pinyin_name}")
                        
                        geo_params["name"] = pinyin_name
                        if "language" in geo_params:
                            del geo_params["language"]
                            
                        geo_res = requests.get(geo_url, params=geo_params, headers=headers, timeout=10)
                        
                    except ImportError:
                        print("pypinyin not installed, skipping pinyin retry")
                    except Exception as e:
                        print(f"Pinyin retry failed: {e}")
                
                if geo_res.status_code == 200 and geo_res.json().get("results"):
                    location = geo_res.json()["results"][0]
                    lat = location["latitude"]
                    lon = location["longitude"]
                    display_name = location["name"]
                    
                    print(f"Location found: {display_name} ({lat}, {lon})")
                    
                    # Step 2: Weather
                    weather_url = "https://api.open-meteo.com/v1/forecast"
                    weather_params = {
                        "latitude": lat,
                        "longitude": lon,
                        "current": "temperature_2m,weather_code,wind_speed_10m,relative_humidity_2m",
                        "timezone": "auto"
                    }
                    w_res = requests.get(weather_url, params=weather_params, headers=headers, timeout=10)
                    
                    if w_res.status_code == 200:
                        w_data = w_res.json()
                        current = w_data.get("current", {})
                        print("Weather data retrieved successfully")

                        
                        # Map WMO codes to text and icons
                        code = current.get("weather_code", 0)
                        # WMO Code Table: https://open-meteo.com/en/docs
                        if code == 0:
                            weather_desc = "晴朗"
                            icon_url = "https://cdn-icons-png.flaticon.com/512/869/869869.png"
                        elif code in [1, 2, 3]:
                            weather_desc = "多云"
                            icon_url = "https://cdn-icons-png.flaticon.com/512/1163/1163661.png"
                        elif code in [45, 48]:
                            weather_desc = "雾"
                            icon_url = "https://cdn-icons-png.flaticon.com/512/1163/1163624.png"
                        elif code in [51, 53, 55, 61, 63, 65]:
                            weather_desc = "雨"
                            icon_url = "https://cdn-icons-png.flaticon.com/512/116/116251.png"
                        elif code in [71, 73, 75, 77]:
                            weather_desc = "雪"
                            icon_url = "https://cdn-icons-png.flaticon.com/512/642/642102.png"
                        elif code in [95, 96, 99]:
                            weather_desc = "雷雨"
                            icon_url = "https://cdn-icons-png.flaticon.com/512/1146/1146869.png"
                        else:
                            weather_desc = "阴"
                            icon_url = "https://cdn-icons-png.flaticon.com/512/1163/1163661.png"
                            
                        # Prepare data for card
                        temp = f"{current.get('temperature_2m')}°C"
                        wind = f"风速 {current.get('wind_speed_10m')} km/h"
                        humidity = f"湿度 {current.get('relative_humidity_2m')}%"
                        
                        weather_data = {
                            "city": display_name,
                            "date": "实时",
                            "temperature": temp,
                            "weather": weather_desc,
                            "wind": wind,
                            "extra": humidity,
                            "icon": icon_url
                        }
                    else:
                        is_mock = True
                        error_msg = "无法获取天气数据"
                else:
                    is_mock = True
                    error_msg = "未找到该城市"
            except Exception as e:
                print(f"Open-Meteo Error: {e}")
                is_mock = True
                error_msg = "网络请求失败"

            # Fallback to mock if failed
            if is_mock:
                weather_data = {
                    "city": city_name,
                    "date": "演示",
                    "temperature": "20-25℃",
                    "weather": "晴 (API演示)",
                    "wind": "微风",
                    "extra": "良",
                    "icon": "https://cdn-icons-png.flaticon.com/512/869/869869.png"
                }
                
            # Generate Card
            weather_card = f"""
            <div class="bg-gradient-to-br from-blue-400 to-blue-600 p-4 rounded-lg shadow-lg text-white max-w-xs select-none">
                <div class="flex justify-between items-center mb-2">
                    <h3 class="font-bold text-lg">{weather_data['city']}</h3>
                    <span class="text-xs bg-white/20 px-2 py-1 rounded">{weather_data['date']}</span>
                </div>
                <div class="flex items-center justify-between">
                    <div class="flex flex-col">
                        <span class="text-3xl font-bold">{weather_data['temperature']}</span>
                        <span class="text-sm opacity-90">{weather_data['weather']}</span>
                    </div>
                    <img src="{weather_data['icon']}" alt="{weather_data['weather']}" class="w-12 h-12 filter drop-shadow-md bg-white rounded-full p-1">
                </div>
                <div class="mt-3 text-sm opacity-90 flex justify-between border-t border-white/20 pt-2">
                    <span>{weather_data['wind']}</span>
                    <span>{weather_data['extra']}</span>
                </div>
                <div class="text-xs text-center mt-2 opacity-70">数据来源: {"Open-Meteo" if not is_mock else "系统演示 (API不可用)"}</div>
            </div>
            """
            
            system_responses.append({
                'user': '天气助手',
                'msg': weather_card
            })
                
        except Exception as e:
            print(f"Weather Processing Error: {e}")
            import traceback
            traceback.print_exc()

    # Process @音乐
    if msg and '@音乐' in msg:
        try:
            # Primary API
            # User requested replacement: https://api.qqsuu.cn/api/dm-randmusic?sort=热歌榜&format=json
            api_url = "https://api.qqsuu.cn/api/dm-randmusic"
            params = {
                'sort': '热歌榜',
                'format': 'json',
                'apiKey': 'bcd17e20778da30d8cb25f925bbc6290'
            }
            # Add User-Agent to avoid blocks
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            
            music_found = False
            
            # Attempt 1: Primary API
            for _ in range(3):
                try:
                    response = requests.get(api_url, headers=headers, params=params, timeout=5)
                    if response.status_code == 200:
                        res_json = response.json()
                        # New API returns code: 1 for success
                        if res_json.get('code') == 1 and res_json.get('data'):
                            music_data = res_json['data']
                            if music_data.get('url'):
                                # Check URL validity (Head request)
                                is_valid_audio = False
                                try:
                                    # Allow redirects to follow potential 302 -> 404 flow
                                    check_resp = requests.head(music_data.get('url'), headers=headers, allow_redirects=True, timeout=5)
                                    
                                    # Check status code and content type
                                    content_type = check_resp.headers.get('Content-Type', '')
                                    if check_resp.status_code == 200 and ('audio' in content_type or 'application/octet-stream' in content_type):
                                        is_valid_audio = True
                                    else:
                                        print(f"Music URL check failed: Status={check_resp.status_code}, Type={content_type}")
                                except Exception as check_err:
                                    print(f"Music URL check error: {check_err}")
                                    pass

                                if not is_valid_audio:
                                    continue

                                name = music_data.get('name', '未知歌曲')
                                singer = music_data.get('artistsname', '未知歌手') # Changed from 'singer'
                                mp3_url = music_data.get('url')
                                if mp3_url:
                                    mp3_url = mp3_url.replace('http://', 'https://')
                                cover_url = music_data.get('picurl', 'https://via.placeholder.com/64') # Changed from 'image'
                                if cover_url and cover_url.startswith('http://'):
                                    cover_url = cover_url.replace('http://', 'https://')
                                
                                music_card = f"""
                                <div class="bg-white p-3 rounded-lg shadow-md max-w-xs border border-gray-100">
                                    <div class="flex items-center space-x-3 mb-3">
                                        <img src="{cover_url}" alt="{name}" class="w-16 h-16 rounded object-cover shadow-sm">
                                        <div class="overflow-hidden">
                                            <h4 class="font-bold text-gray-800 truncate text-sm">{name}</h4>
                                            <p class="text-xs text-gray-500 truncate">{singer}</p>
                                        </div>
                                    </div>
                                    <audio controls preload="auto" class="w-full h-8" referrerpolicy="no-referrer">
                                        <source src="{mp3_url}" type="audio/mpeg">
                                        您的浏览器不支持音频播放。
                                    </audio>
                                </div>
                                """
                                system_responses.append({
                                    'user': '音乐助手',
                                    'msg': music_card
                                })
                                music_found = True
                                break
                except Exception as e:
                    print(f"Music API attempt failed: {e}")
                    continue
            
            # Attempt 2: Fallback Pool (if API fails)
            if not music_found:
                import random
                
                # Curated list of reliable test music
                fallback_pool = [
                    {
                        "name": "Kalimba (测试)",
                        "singer": "Ninja Tuna",
                        "url": "https://www.learningcontainer.com/wp-content/uploads/2020/02/Kalimba.mp3",
                        "cover": "https://via.placeholder.com/64?text=Kalimba"
                    },
                    {
                        "name": "SoundHelix Song 1",
                        "singer": "SoundHelix Library",
                        "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
                        "cover": "https://via.placeholder.com/64?text=Song+1"
                    },
                    {
                        "name": "SoundHelix Song 3",
                        "singer": "SoundHelix Library",
                        "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",
                        "cover": "https://via.placeholder.com/64?text=Song+3"
                    },
                    {
                        "name": "SoundHelix Song 8",
                        "singer": "SoundHelix Library",
                        "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-8.mp3",
                        "cover": "https://via.placeholder.com/64?text=Song+8"
                    }
                ]
                
                selected_music = random.choice(fallback_pool)
                
                music_card = f"""
                <div class="bg-white p-3 rounded-lg shadow-md max-w-xs border border-gray-100">
                    <div class="flex items-center space-x-3 mb-3">
                        <img src="{selected_music['cover']}" alt="{selected_music['name']}" class="w-16 h-16 rounded object-cover shadow-sm">
                        <div class="overflow-hidden">
                            <h4 class="font-bold text-gray-800 truncate text-sm">{selected_music['name']}</h4>
                            <p class="text-xs text-gray-500 truncate">{selected_music['singer']}</p>
                        </div>
                    </div>
                    <audio controls class="w-full h-8" controlsList="nodownload">
                        <source src="{selected_music['url']}" type="audio/mpeg">
                        您的浏览器不支持音频播放。
                    </audio>
                    <p class="text-xs text-gray-400 mt-1 text-center">随机推荐 (API暂不可用)</p>
                </div>
                """
                system_responses.append({
                    'user': '音乐助手',
                    'msg': music_card
                })
                
        except Exception as e:
            print(f"Music API Error: {e}")

    # Process @新闻
    if msg and '@新闻' in msg:
        try:
            news_api_url = "https://api.qqsuu.cn/api/dm-woman"
            params = {
                "num": 10,
                "apiKey": "2e94642812857d4e72fc13c8af01fefd"
            }
            # Add User-Agent
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            
            response = requests.get(news_api_url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                res_json = response.json()
                if res_json.get('code') == 200 and res_json.get('data') and res_json['data'].get('newslist'):
                    news_list = res_json['data']['newslist']
                    
                    # Build HTML Card
                    news_items_html = ""
                    for item in news_list:
                        title = item.get('title', '无标题')
                        source = item.get('source', '未知来源')
                        url = item.get('url', '#')
                        ctime = item.get('ctime', '')
                        # Format time slightly if possible, or keep as is
                        
                        news_items_html += f"""
                        <a href="{url}" target="_blank" class="block group p-2 hover:bg-gray-50 rounded transition-colors border-b border-gray-50 last:border-0">
                            <h5 class="text-sm text-gray-800 font-medium group-hover:text-primary transition-colors line-clamp-2 mb-1">{title}</h5>
                            <div class="flex items-center justify-between text-xs text-gray-400">
                                <span>{source}</span>
                                <span>{ctime}</span>
                            </div>
                        </a>
                        """
                    
                    news_card = f"""
                    <div class="bg-white rounded-lg shadow-md max-w-sm border border-gray-100 overflow-hidden">
                        <div class="bg-red-50 p-3 border-b border-red-100 flex items-center justify-between">
                            <div class="flex items-center space-x-2">
                                <div class="w-8 h-8 rounded-full bg-red-100 flex items-center justify-center text-red-500">
                                    <i class="fas fa-newspaper"></i>
                                </div>
                                <h4 class="font-bold text-gray-800">实时新闻</h4>
                            </div>
                            <span class="text-xs text-red-400 bg-red-100 px-2 py-0.5 rounded-full">Top 10</span>
                        </div>
                        <div class="max-h-80 overflow-y-auto scrollbar-hide p-1">
                            {news_items_html}
                        </div>
                        <div class="p-2 bg-gray-50 text-center text-xs text-gray-400 border-t border-gray-100">
                            数据来源: API聚合
                        </div>
                    </div>
                    """
                    
                    system_responses.append({
                        'user': '新闻助手',
                        'msg': news_card
                    })
                else:
                    # API Error handling
                    system_responses.append({
                        'user': '新闻助手',
                        'msg': '<div class="bg-red-50 p-3 rounded text-red-600 text-sm">获取新闻失败，请稍后再试。</div>'
                    })
            else:
                 system_responses.append({
                    'user': '新闻助手',
                    'msg': '<div class="bg-red-50 p-3 rounded text-red-600 text-sm">网络请求失败，无法获取新闻。</div>'
                })

        except Exception as e:
            print(f"News API Error: {e}")
            import traceback
            traceback.print_exc()
            system_responses.append({
                'user': '新闻助手',
                'msg': f'<div class="bg-red-50 p-3 rounded text-red-600 text-sm">系统错误: {str(e)}</div>'
            })

    # Emit User Message
    emit('receive_message', {
        'user': nickname, 
        'msg': msg,
        'time': time_str,
        'is_self': False
    }, room='general', include_self=False)
    
    # Send back to sender with is_self=True
    emit('receive_message', {
        'user': nickname, 
        'msg': msg,
        'time': time_str,
        'is_self': True
    }, room=request.sid)

    # Emit System Responses
    for resp in system_responses:
        emit('receive_message', {
            'user': resp['user'],
            'msg': resp['msg'],
            'time': time_str,
            'is_self': False
        }, room='general')
    
    # Check for @成小理
    if msg and '@成小理' in msg:
        original_msg = data.get('msg')
        prompt = original_msg.replace('@成小理', '').strip()
        # If prompt is empty, default to "你好"
        if not prompt:
            prompt = "你好"
            
        # Run in background task to avoid blocking
        socketio.start_background_task(call_ai_api, prompt, 'general')

@socketio.on('disconnect')
def handle_disconnect():
    nickname = connected_users.pop(request.sid, None)
    if nickname:
        leave_room('general')
        emit('system_message', {'msg': f'{nickname} 离开了聊天室'}, room='general')
        emit('update_users', {'users': list(connected_users.values())}, room='general')

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
