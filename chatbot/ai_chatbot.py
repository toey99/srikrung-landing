# AI Chatbot System for Sri Krung Broker
# Powered by Claude 3.5 Sonnet
# ตอบลูกค้า 24/7 พร้อมแจ้งเตือนบอสเมื่อตอบไม่ได้

import os
import json
import requests
from datetime import datetime
from typing import Dict, Any, Optional

class SriKrungChatbot:
    """
    AI Chatbot สำหรับตอบลูกค้าประกันรถยนต์
    ใช้ Claude 3.5 Sonnet API
    """
    
    def __init__(self):
        self.claude_api_key = os.getenv('ANTHROPIC_API_KEY')
        self.line_channel_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
        self.line_channel_secret = os.getenv('LINE_CHANNEL_SECRET')
        self.boss_notify_url = os.getenv('BOSS_NOTIFY_URL')  # Discord Webhook หรือ LINE Notify
        
        # Knowledge Base ประกันภัย
        self.knowledge_base = self._load_knowledge_base()
        
        # ประวัติการสนทนา (เก็บชั่วคราว)
        self.conversation_history = {}
    
    def _load_knowledge_base(self) -> Dict:
        """โหลดข้อมูลความรู้เรื่องประกัน"""
        return {
            "company": {
                "name": "ศรีกรุงโบรคเกอร์ (Sri Krung Broker)",
                "license": "6604014447",
                "agent": "นิภาวดี ตั้งเส้ง",
                "level": "5 (มุ่งสู่ระดับ 1)",
                "contact": {
                    "phone": "084-161-5554",
                    "line": "@vax7479a",
                    "link": "https://lin.ee/e1Vuz3P"
                }
            },
            "products": {
                "724": {
                    "name": "724 Insure",
                    "link": "https://insure.724.co.th/u/AM00441133",
                    "description": "ระบบซื้อประกันออนไลน์ราคาพิเศษ"
                },
                "insurance_types": [
                    {
                        "type": "ชั้น 1",
                        "coverage": "ครอบคลุมทุกกรณี ชน ไฟไหม้ น้ำท่วม รถหาย",
                        "target": "รถใหม่ รถแพง ต้องการความคุ้มครองสูงสุด"
                    },
                    {
                        "type": "ชั้น 2+",
                        "coverage": "ชนรถ ไฟไหม้ น้ำท่วม แต่ไม่คุ้มครองรถหาย",
                        "target": "รถอายุ 3-7 ปี ต้องการความคุ้มครองดี แต่ประหยัด"
                    },
                    {
                        "type": "ชั้น 3",
                        "coverage": "เฉพาะชนแล้วหนี หรือถูกชนโดยไม่มีคู่กรณี",
                        "target": "รถอายุมาก ประหยัดสุด คุ้มครองตาม กม."
                    }
                ]
            },
            "faq": {
                "price": "ราคาเบี้ยประกันขึ้นอยู่กับ ยี่ห้อรถ รุ่น ปีรถ อายุผู้ขับขี่ ประวัติการเคลม เช็คราคาเฉพาะได้ที่ https://insure.724.co.th/u/AM00441133",
                "claim": "เคลมประกันโทร Hotline ของบริษัทประกันที่ระบุในกรมธรรม์ หรือติดต่อเราที่ @vax7479a ช่วยประสานงาน",
                "installment": "สามารถผ่อนชำระ 0% นานสูงสุด 10 เดือน ผ่านบัตรเครดิตที่ร่วมรายการ",
                "document": "ซื้อประกันออนไลน์ใช้แค่สำเนาบัตรประชาชน + สำเนาทะเบียนรถ (ถ่ายรูปได้เลย)",
                "cancel": "ยกเลิกกรมธรรม์ได้ภายใน 14 วัน (Free Look Period) รับเงินคืนเต็มจำนวนหักค่าธรรมเนียม",
                "renew": "ต่ออายุประกันล่วงหน้าได้ 30-60 วัน ก่อนหมดอายุ ได้ส่วนลดและความคุ้มครองต่อเนื่อง"
            },
            "partners": [
                "วิริยะประกันภัย", "ทิพยประกันภัย", "เมืองไทยประกันภัย",
                "กรุงเทพประกันภัย", "สินมั่นคงประกันภัย", "อาคเนย์ประกันภัย",
                "เทเวศประกันภัย", "เจ้าพระยาประกันภัย", "อลิอันซ์ อยุธยา",
                "724 Insure", "LMG Insurance"
            ],
            "usp": [
                "ซื้อเองได้ ไม่ผ่านเซลล์ ไม่ถูกกดดัน",
                "ราคาพิเศษผ่านระบบ 724",
                "มีผู้ช่วยให้คำปรึกษา 24/7 ผ่านไลน์",
                "บริการทั่วประเทศ",
                "ตัวแทนมีใบอนุญาตถูกต้อง"
            ]
        }
    
    def ask_claude(self, user_message: str, user_id: str) -> Dict[str, Any]:
        """
        ส่งข้อความไปถาม Claude 3.5 Sonnet
        """
        # ดึงประวัติการสนทนา
        history = self.conversation_history.get(user_id, [])
        
        # สร้าง System Prompt
        system_prompt = self._create_system_prompt()
        
        # สร้าง Messages
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # เพิ่มประวัติการสนทนา (5 ข้อความล่าสุด)
        for msg in history[-5:]:
            messages.append(msg)
        
        # เพิ่มข้อความปัจจุบัน
        messages.append({"role": "user", "content": user_message})
        
        # เรียก Claude API
        try:
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.claude_api_key,
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": "claude-3-haiku-20240307",
                    "max_tokens": 1000,
                    "temperature": 0.7,
                    "messages": messages
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result['content'][0]['text']
                
                # ประเมินความมั่นใจ (สมมติจาก context)
                confidence = self._evaluate_confidence(user_message, ai_response)
                
                # บันทึกประวัติ
                history.append({"role": "user", "content": user_message})
                history.append({"role": "assistant", "content": ai_response})
                self.conversation_history[user_id] = history[-10:]  # เก็บแค่ 10 ข้อความล่าสุด
                
                return {
                    "success": True,
                    "response": ai_response,
                    "confidence": confidence,
                    "needs_human": confidence < 0.5,
                    "notify_boss": confidence < 0.7
                }
            else:
                return {
                    "success": False,
                    "error": f"API Error: {response.status_code}",
                    "needs_human": True,
                    "notify_boss": True
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "needs_human": True,
                "notify_boss": True
            }
    
    def _create_system_prompt(self) -> str:
        """สร้าง System Prompt สำหรับ Claude"""
        return """คุณเป็นผู้ช่วย AI ของศรีกรุงโบรคเกอร์ (Sri Krung Broker) ชื่อว่า "อวี้เวิน" 
ดูแลโดยคุณนิภาวดี ตั้งเส้ง (ใบอนุญาตนายหน้า 6604014447)

บทบาทของคุณ:
1. ตอบคำถามลูกค้าเกี่ยวกับประกันรถยนต์ด้วยความสุภาพ เป็นกันเอง
2. แนะนำประเภทประกันที่เหมาะสมกับลูกค้า
3. ช่วยแก้ปัญหาและให้ข้อมูลที่ถูกต้อง
4. หากไม่แน่ใจหรือเป็นเรื่องละเอียดเฉพาะบุคคล ให้แนะนำให้ติดต่อคุณนิภาวดีโดยตรง

ข้อมูลบริษัท:
- ชื่อ: ศรีกรุงโบรคเกอร์ (Sri Krung Broker)
- ตัวแทน: นิภาวดี ตั้งเส้ง
- เบอร์โทร: 084-161-5554
- ไลน์: @vax7479a
- ลิงก์ซื้อประกัน: https://insure.724.co.th/u/AM00441133

บริษัทประกันพันธมิตร: วิริยะ, ทิพย์, เมืองไทย, กรุงเทพ, สินมั่นคง, อาคเนย์, เทเวศ, 724 Insure และอื่นๆ

จุดขาย (USP):
- ซื้อเองได้ ไม่ผ่านเซลล์ ไม่ถูกกดดัน
- ราคาพิเศษผ่านระบบ 724
- มีผู้ช่วยให้คำปรึกษา 24/7
- ตัวแทนมีใบอนุญาตถูกต้อง

คำตอบของคุณควร:
- สุภาพ เป็นกันเอง แต่มืออาชีพ
- กระชับ ไม่ยืดเยื้อ
- ให้ข้อมูลที่ถูกต้อง ไม่เดา
- แนะนำลิงก์หรือช่องทางติดต่อเพิ่มเติมเมื่อจำเป็น
- ใช้ emoji เล็กน้อยเพื่อความเป็นมิตร

หากลูกค้าถามเรื่องเฉพาะเช่น ราคาที่แน่นอน การเคลมเฉพาะกรณี หรือปัญหาซับซ้อน 
ให้แนะนำให้ติดต่อคุณนิภาวดีโดยตรงที่เบอร์ 084-161-5554 หรือ @vax7479a"""
    
    def _evaluate_confidence(self, user_msg: str, ai_response: str) -> float:
        """
        ประเมินความมั่นใจของคำตอบ (0.0 - 1.0)
        """
        confidence = 0.8  # เริ่มต้นที่ 0.8
        
        # ลดคะแนนถ้าพบคำเหล่านี้
        uncertain_words = ['ไม่แน่ใจ', 'อาจจะ', 'น่าจะ', 'ไม่ทราบ', 'ขออภัยที่ไม่สามารถ']
        for word in uncertain_words:
            if word in ai_response:
                confidence -= 0.2
        
        # ลดคะแนนถ้าข้อความยาวเกินไป (อาจกำลังเดา)
        if len(ai_response) > 500 and 'ติดต่อ' not in ai_response:
            confidence -= 0.1
        
        # เพิ่มคะแนนถ้ามีการแนะนำให้ติดต่อเจ้าหน้าที่ (แสดงว่ารู้ขอบเขต)
        if 'ติดต่อ' in ai_response or '084-161-5554' in ai_response:
            confidence += 0.1
        
        return max(0.0, min(1.0, confidence))
    
    def notify_boss(self, user_id: str, user_message: str, ai_response: str, 
                    confidence: float, reason: str = ""):
        """
        แจ้งเตือนบอสเมื่อ AI ตอบไม่ได้หรือความมั่นใจต่ำ
        """
        message = f"""🚨 AI Chatbot Alert

👤 User ID: {user_id}
💬 คำถาม: {user_message[:100]}...
 AI ตอบ: {ai_response[:100]}...
📊 ความมั่นใจ: {confidence:.0%}
⚠️ เหตุผล: {reason}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

👉 ตอบกลับผ่าน @vax7479a"""
        
        # ส่งแจ้งเตือนไป Discord หรือ LINE Notify
        if self.boss_notify_url:
            try:
                requests.post(
                    self.boss_notify_url,
                    json={"content": message},
                    timeout=10
                )
            except:
                pass
        
        return True
    
    def handle_message(self, user_id: str, user_message: str) -> Dict:
        """
        จัดการข้อความจากลูกค้าแบบครบวงจร
        """
        # ถาม Claude
        result = self.ask_claude(user_message, user_id)
        
        # ตัดสินใจว่าจะตอบอย่างไร
        if result['success']:
            # ความมั่นใจต่ำ → แจ้งเตือนบอส
            if result['notify_boss']:
                self.notify_boss(
                    user_id, user_message, 
                    result['response'], result['confidence'],
                    "ความมั่นใจต่ำกว่า 70%"
                )
            
            # ต้องการคนตอบ → เพิ่มข้อความขอรอ
            if result['needs_human']:
                result['response'] += "\n\nขออภัยค่ะ เรื่องนี้ต้องสอบถามรายละเอียดเฉพาะบุคคล กรุณารอเจ้าหน้าที่ตอบกลับภายใน 10 นาทีนะคะ 🙏"
        
        else:
            # API Error → แจ้งเตือนด่วน + ตอบสำรอง
            self.notify_boss(
                user_id, user_message,
                "API Error", 0.0,
                f"Error: {result.get('error', 'Unknown')}"
            )
            result['response'] = "ขออภัยค่ะ ระบบชั่วคราว กรุณาติดต่อเจ้าหน้าที่โดยตรง 084-161-5554 หรือ @vax7479a 🙏"
        
        return result


# ตัวอย่างการใช้งาน
if __name__ == "__main__":
    bot = SriKrungChatbot()
    
    # ทดสอบ
    test_message = "ประกันรถชั้น 1 ราคาเท่าไหร่คะ"
    result = bot.handle_message("test_user_001", test_message)
    
    print(f"คำตอบ: {result['response']}")
    print(f"ความมั่นใจ: {result['confidence']:.0%}")
    print(f"ต้องการคน: {result['needs_human']}")
