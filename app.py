from flask import Flask, request, jsonify
import os
import requests
import json
from datetime import datetime

app = Flask(__name__)

# API Keys - Read from environment with fallback check
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '').strip()
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN', '').strip()
LINE_CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET', '').strip()
BOSS_NOTIFY_URL = os.environ.get('BOSS_NOTIFY_URL', '').strip()

# Debug: Print to logs (will show in Render logs)
print(f"DEBUG: ANTHROPIC_API_KEY loaded: {bool(ANTHROPIC_API_KEY)} (length: {len(ANTHROPIC_API_KEY)})")
print(f"DEBUG: LINE_CHANNEL_ACCESS_TOKEN loaded: {bool(LINE_CHANNEL_ACCESS_TOKEN)} (length: {len(LINE_CHANNEL_ACCESS_TOKEN)})")
print(f"DEBUG: LINE_CHANNEL_SECRET loaded: {bool(LINE_CHANNEL_SECRET)} (length: {len(LINE_CHANNEL_SECRET)})")

# Knowledge Base
KNOWLEDGE_BASE = {
    "company": {
        "name": "ศรีกรุงโบรคเกอร์",
        "agent": "นิภาวดี ตั้งเส้ง",
        "license": "6604014447",
        "phone": "084-161-5554",
        "line": "@vax7479a"
    },
    "faq": {
        "price": "เช็คราคาเฉพาะบุคคลได้ที่ https://insure.724.co.th/u/AM00441133",
        "claim": "เคลมโทร Hotline บริษัทประกันที่ระบุในกรมธรรม์",
        "installment": "ผ่อน 0% นานสูงสุด 10 เดือน ผ่านบัตรเครดิต",
        "document": "ใช้แค่สำเนาบัตรปชช. + ทะเบียนรถ (ถ่ายรูปได้เลย)"
    }
}

def ask_claude(user_message):
    """ส่งข้อความไปถาม Claude"""
    # Check if API Key is loaded
    if not ANTHROPIC_API_KEY:
        print("ERROR: ANTHROPIC_API_KEY is empty or not loaded!")
        return None
    
    try:
        headers = {
            "x-api-key": ANTHROPIC_API_KEY,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        system_prompt = """คุณคือผู้ช่วย AI ของศรีกรุงโบรคเกอร์ (Sri Krung Broker) ชื่อว่า "อวี้เวิน" 
ดูแลโดยคุณนิภาวดี ตั้งเส้ง (ใบอนุญาตนายหน้า 6604014447)

บทบาทของคุณ:
1. ตอบคำถามลูกค้าเกี่ยวกับประกันรถยนต์ด้วยความสุภาพ เป็นกันเอง
2. ให้ข้อมูลละเอียด ครบถ้วน อธิบายให้เข้าใจง่าย
3. แนะนำประเภทประกันที่เหมาะสมกับลูกค้า พร้อมเหตุผล
4. ใช้ emoji เล็กน้อยเพื่อความเป็นมิตร 😊

ข้อมูลบริษัท:
- ชื่อ: ศรีกรุงโบรคเกอร์ (Sri Krung Broker)
- ตัวแทน: นิภาวดี ตั้งเส้ง
- เบอร์โทร: 084-161-5554
- ไลน์: @vax7479a
- ลิงก์ซื้อประกัน: https://insure.724.co.th/u/AM00441133

ประเภทประกัน:
- ชั้น 1: ครอบคลุมสูงสุด ชน ไฟไหม้ น้ำท่วม รถหาย เหมาะรถใหม่
- ชั้น 2+: คุ้มครองดี ประหยัดกว่า ไม่คุ้มครองรถหาย เหมาะรถ 3-7 ปี
- ชั้น 3: ประหยัดสุด คุ้มครองตาม กม. เหมาะรถอายุมาก

จุดขาย (USP):
- ซื้อเองได้ ไม่ผ่านเซลล์ ไม่ถูกกดดัน
- ราคาพิเศษผ่านระบบ 724
- มีผู้ช่วยให้คำปรึกษา 24/7
- ตัวแทนมีใบอนุญาตถูกต้อง

คำตอบของคุณควร:
- สุภาพ เป็นกันเอง แต่มืออาชีพ
- ละเอียด อธิบายเหตุผลประกอบ
- ยาวประมาณ 3-5 ประโยคขึ้นไป
- มี emoji ประกอบ 1-3 ตัว
- ให้ข้อมูลที่ถูกต้อง ไม่เดา
- แนะนำลิงก์หรือช่องทางติดต่อเพิ่มเติมเมื่อจำเป็น
- ถามกลับเพื่อเข้าใจความต้องการลูกค้า

หากลูกค้าถามเรื่องเฉพาะเช่น ราคาที่แน่นอน การเคลมเฉพาะกรณี หรือปัญหาซับซ้อน 
ให้แนะนำให้ติดต่อคุณนิภาวดีโดยตรงที่เบอร์ 084-161-5554 หรือ @vax7479a"""

        data = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 1500,
            "temperature": 0.8,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_message}]
        }
        
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()['content'][0]['text']
        else:
            return None
            
    except Exception as e:
        print(f"Error: {e}")
        return None

def send_line_reply(reply_token, message):
    """ส่งข้อความตอบกลับไป LINE"""
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
        }
        
        data = {
            "replyToken": reply_token,
            "messages": [{"type": "text", "text": message}]
        }
        
        response = requests.post(
            "https://api.line.me/v2/bot/message/reply",
            headers=headers,
            json=data,
            timeout=10
        )
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"Error sending reply: {e}")
        return False

def notify_boss(user_id, message, ai_response):
    """แจ้งเตือนบอสเมื่อ AI ตอบไม่ได้"""
    if not BOSS_NOTIFY_URL:
        return
    
    try:
        text = f"""🚨 AI Chatbot Alert
👤 User: {user_id}
💬 ถาม: {message[:50]}...
🤖 AI ตอบ: {ai_response[:50] if ai_response else 'Error'}
⏰ {datetime.now().strftime('%H:%M:%S')}"""
        
        requests.post(BOSS_NOTIFY_URL, json={"content": text}, timeout=5)
    except:
        pass

@app.route('/')
def home():
    return jsonify({"status": "ok", "message": "Sri Krung Chatbot is running!"})

@app.route('/webhook', methods=['POST'])
def webhook():
    """รับ Webhook จาก LINE"""
    try:
        data = request.get_json()
        
        # วนลูป events
        for event in data.get('events', []):
            if event.get('type') == 'message':
                user_id = event['source'].get('userId')
                message = event['message'].get('text', '')
                reply_token = event['replyToken']
                
                print(f"Received: {message} from {user_id}")
                
                # ถาม Claude
                ai_response = ask_claude(message)
                
                if ai_response:
                    # ตอบกลับ
                    send_line_reply(reply_token, ai_response)
                    
                    # ถ้าตอบไม่ค่อยมั่นใจ แจ้งบอส
                    if len(ai_response) < 50 or "ติดต่อ" in ai_response:
                        notify_boss(user_id, message, ai_response)
                else:
                    # AI error ส่งข้อความสำรอง
                    fallback = "ขออภัยค่ะ ระบบชั่วคราว กรุณาติดต่อ 084-161-5554 หรือ @vax7479a"
                    send_line_reply(reply_token, fallback)
                    notify_boss(user_id, message, "API Error")
        
        return jsonify({"status": "ok"})
        
    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
