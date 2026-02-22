from flask import Flask, request, jsonify
import os
import requests
import json
from datetime import datetime

app = Flask(__name__)

# API Keys
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
BOSS_NOTIFY_URL = os.environ.get('BOSS_NOTIFY_URL')

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
    try:
        headers = {
            "x-api-key": ANTHROPIC_API_KEY,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        system_prompt = """คุณคือผู้ช่วยของศรีกรุงโบรคเกอร์ ชื่อ "อวี้เวิน"
ดูแลโดยคุณนิภาวดี ตั้งเส้ง (ใบอนุญาต 6604014447)

บริการ: ประกันรถยนต์ชั้น 1/2+/3+ ราคาพิเศษผ่าน 724
เบอร์โทร: 084-161-5554 | ไลน์: @vax7479a

ตอบสุภาพ กระชับ ให้ข้อมูลถูกต้อง หากไม่แน่ใจให้ติดต่อเจ้าหน้าที่"""

        data = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 500,
            "temperature": 0.7,
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
