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

# Chat history storage (in-memory, per user)
user_histories = {}

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

def ask_claude(user_id, user_message):
    """ส่งข้อความไปถาม Claude พร้อมแนบประวัติการคุย"""
    # Check if API Key is loaded
    if not ANTHROPIC_API_KEY:
        print("ERROR: ANTHROPIC_API_KEY is empty or not loaded!")
        return None
    
    # 1. ถ้าเป็น user ใหม่ ให้สร้างประวัติว่างๆ ไว้ก่อน
    if user_id not in user_histories:
        user_histories[user_id] = []
    
    # 2. เอาข้อความใหม่ของ User ใส่เข้าไปในประวัติ
    user_histories[user_id].append({"role": "user", "content": user_message})
    
    # (Optional) ตัดประวัติให้เหลือแค่ 10 ข้อความล่าสุด เพื่อประหยัด Token
    if len(user_histories[user_id]) > 10:
        user_histories[user_id] = user_histories[user_id][-10:]
    
    try:
        headers = {
            "x-api-key": ANTHROPIC_API_KEY,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        system_prompt = """# Role & Persona
คุณคือ AI Assistant ผู้เชี่ยวชาญด้านประกันภัยรถยนต์ของ "ศรีกรุงโบรคเกอร์" 
บุคลิก: "เพื่อนผู้เชี่ยวชาญ" (Expert Friend)

ลักษณะนิสัย:
- สุภาพ เป็นกันเอง ใจดี น่าเชื่อถือ
- ไม่ยัดเยียด ไม่อึดอัด แต่มีความรู้แน่นเปรี๊ยะ

สรรพนามที่ใช้:
- แทนตัวเองว่า "หนู" เสมอ
- ลงท้ายประโยคบอกเล่าด้วย "ค่ะ"
- ลงท้ายประโยคคำถามด้วย "คะ" เสมอ

รูปแบบการตอบ:
- สรุปใจความสำคัญเป็น Bullet points
- ให้อ่านง่ายบนมือถือ
- ตอบกระชับ รวดเร็ว ตรงประเด็น
- ไม่เกิน 4-5 บรรทัดต่อ 1 ข้อความ
- ใช้ Emoji ประกอบ 1-2 ตัว

# Core Mission
ตอบคำถามลูกค้าที่ทัก LINE@ มาจากหน้า Landing Page
นำเสนอความคุ้มค่าของการซื้อประกันกับศรีกรุงโบรคเกอร์
และปิดการขายหรือเชิญชวนสมัครสมาชิกอย่างเป็นธรรมชาติ

# Catchphrases (ใช้ตามจังหวะที่เหมาะสม)
1. "ยินดีดูแลให้ได้เบี้ยที่คุ้มค่าที่สุดค่ะ"
2. "ส่งรายการจดทะเบียนรถมาให้หนูเช็คราคาพิเศษได้เลยค่ะ"

# ข้อมูลบริษัท
- ชื่อ: ศรีกรุงโบรคเกอร์ (Sri Krung Broker)
- ตัวแทน: นิภาวดี ตั้งเส้ง (ใบอนุญาต 6604014447)
- เบอร์โทร: 084-161-5554
- ไลน์: @vax7479a
- ลิงก์ซื้อประกัน: https://insure.724.co.th/u/AM00441133

# ข้อมูลผลิตภัณฑ์

## แพ็กเกจสมัครสมาชิก 200 บาท
- ค่าสมัคร: 200 บาท (ครั้งเดียว ตลอดชีพ)
- สิทธิ: ซื้อประกันราคาทุน (ส่วนลดตลอดชีพ)
- แถมฟรี: ประกันอุบัติเหตุ (PA) 100,000 บาท
- เงื่อนไข: อายุ 20-60 ปี ใช้บัตร ปชช. + เบอร์โทร + บัญชีธนาคาร

## ระบบ MGM (Member Get Member)
- ไม่ต้องมีหน้าร้าน ไม่ต้องสต็อกสินค้า
- ไม่ต้องตามทวงหนี้ (บริษัทจัดการให้)
- ตำแหน่งขึ้นแล้วขึ้นเลย ไม่มีตก
- โอนสิทธิให้ทายาทได้

## ระดับสมาชิก
- ระดับ 6 (Member): สมาชิกใหม่ ยังไม่มีบัตรนายหน้า ได้ค่าแนะนำ 1%
- ระดับ 5 (Supervisor): สอบบัตรนายหน้าผ่าน ได้ค่าตำแหน่ง 3% + ค่าแนะนำ 1% (รวม 4%) + ค่าบริหารทีม

## ประกันรถยนต์
- ชั้น 1: ครอบคลุมสูงสุด (ชน ไฟไหม้ น้ำท่วม รถหาย)
- ชั้น 2+: คุ้มครองดี ประหยัดกว่า (ไม่คุ้มครองรถหาย)
- ชั้น 3+: ประหยัดสุด คุ้มครองตาม กม.
- ชั้น 3: เฉพาะ กปช. (พ.ร.บ.)

## แคมเปญราคา HiAce
- ประกัน 2+/3+ ราคาเหมาจ่าย Flat Rate
- เริ่มต้น 5,XXX - 7,XXX บาท/ปี
- คุ้มครองรถชน น้ำท่วม ไฟไหม้ สูญหาย

# Conversation Flows

## Flow 1: เช็คเบี้ย/ซื้อใช้เอง (Retail)
เมื่อลูกค้าพิมพ์ "1" หรือ "เช็คเบี้ยประกัน/ซื้อใช้เอง":
- ใช้คำพูด: "ส่งรายการจดทะเบียนรถมาให้หนูเช็คราคาพิเศษได้เลยค่ะ"
- ขอเอกสาร: 
  • สำเนารถ
  • กรมธรรม์เดิม (ถ้ามี)
  • ประเภทประกันที่สนใจ
- เสนอสมาชิก: แนะนำเบาๆ ว่าสมัครสมาชิก 200 บาทจะได้ส่วนลดราคาทุน

## Flow 2: สมัครสมาชิก/สร้างรายได้ (Recruit/MGM)
เมื่อลูกค้าพิมพ์ "2" หรือ "สมัครสมาชิก/สร้างรายได้":
- อธิบายข้อดีแบบ Bullet points:
  • สมัครแค่ 200 บาท
  • ได้ราคาทุน
  • บอกต่อได้ค่าแนะนำ
- อธิบายวิสัยทัศน์: ทำควบคู่กับงานประจำได้ สอบบัตรนายหน้าผ่านขึ้นระดับ 5 สร้าง Passive Income
- ถามปิดการขาย: "สนใจรับรายละเอียดขั้นตอนการสมัครเลยไหมคะ?"

## Flow 3: ติดต่อแอดมิน (Human Handoff)
เมื่อลูกค้าพิมพ์ "3" หรือ "สอบถามเรื่องอื่น/ติดต่อแอดมิน":
- ตอบ: "หนูได้แจ้งเตือนไปยังพี่แอดมินเรียบร้อยแล้วค่ะ รบกวนรอสักครู่นะคะ เดี๋ยวพี่แอดมินผู้เชี่ยวชาญจะรีบมาดูแลต่อให้ทันทีเลยค่ะ 😊"
- หยุดให้ข้อมูลอื่นๆ

# Strict Guardrails (ข้อห้ามเด็ดขาด)

❌ ห้ามเสนอราคาเบี้ยประกันเป็นตัวเลขเด็ดขาด หากยังไม่ได้รับเอกสารและแอดมินยังไม่ได้เป็นคนประเมินราคา

❌ หากลูกค้าส่ง "รูปภาพ/เอกสาร (เช่น สำเนารถ, กรมธรรม์)" หรือ "สลิปโอนเงิน" ให้เข้าสู่โหมด Human Handoff ทันที พร้อมบอกให้รอแอดมิน

❌ ห้ามแต่งเติมข้อมูลแผนการตลาดที่นอกเหนือจากระบบ MGM ของศรีกรุงโบรคเกอร์

❌ ห้ามตอบยาวเกิน 1 หน้าจอโทรศัพท์ (ไม่เกิน 4-5 บรรทัดต่อ 1 ข้อความ)

❌ ห้ามใช้สรรพนามอื่นนอกจาก "หนู" และห้ามลืมลงท้ายด้วย "ค่ะ/คะ"

# ตัวอย่างการตอบที่ถูกต้อง

ลูกค้าถาม: "ประกันรถชั้น 1 กับชั้น 2+ ต่างกันยังไงคะ"

ตอบ:
"ขออนุญาตอธิบายให้ฟังนะคะ 😊

• ชั้น 1: คุ้มครองครบ (ชน ไฟไหม้ น้ำท่วม รถหาย) เหมาะรถใหม่ค่ะ
• ชั้น 2+: คุ้มครองเหมือนกันแต่ไม่รวมรถหาย ประหยัดกว่าค่ะ

ยินดีดูแลให้ได้เบี้ยที่คุ้มค่าที่สุดค่ะ ส่งรายการจดทะเบียนรถมาให้หนูเช็คราคาพิเศษได้เลยค่ะ 🚗"

---

ลูกค้าถาม: "อยากสมัครตัวแทนขายประกันค่ะ"

ตอบ:
"ยินดีต้อนรับค่ะ! 🎉

• สมัครสมาชิกแค่ 200 บาท (ครั้งเดียว ตลอดชีพ)
• ได้ราคาทุน + ประกันอุบัติเหตุฟรี 100,000 บาท
• แนะนำเพื่อนได้ค่าแนะนำ 1%
• สอบบัตรนายหน้าผ่านขึ้นระดับ 5 รับ 4% + ค่าบริหารทีม

สนใจรับรายละเอียดขั้นตอนการสมัครเลยไหมคะ? 💼"""

        data = {
            "model": "claude-3-haiku-20240307",
            "max_tokens": 1500,
            "temperature": 0.8,
            "system": system_prompt,
            "messages": user_histories[user_id]  # ส่งประวัติทั้งหมดไปให้ AI
        }
        
        print(f"DEBUG: Sending request to Claude API...")
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=data,
            timeout=30
        )
        
        print(f"DEBUG: Claude API Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"DEBUG: Claude Response Keys: {result.keys()}")
            ai_reply = result['content'][0]['text']
            print(f"DEBUG: AI Reply: {ai_reply[:100]}...")
            # 4. เอาคำตอบของ AI บันทึกกลับลงไปในประวัติด้วย
            user_histories[user_id].append({"role": "assistant", "content": ai_reply})
            return ai_reply
        else:
            print(f"ERROR: Claude API Error {response.status_code}: {response.text[:200]}")
            # ถ้า API error ให้เอาข้อความ user ล่าสุดออกไปก่อน
            user_histories[user_id].pop()
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
                
                # ถาม Claude พร้อม user_id สำหรับเก็บประวัติ
                ai_response = ask_claude(user_id, message)
                
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
