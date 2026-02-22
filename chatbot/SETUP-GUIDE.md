# AI Chatbot Setup Guide - Sri Krung Broker
# คู่มือตั้งค่า AI Chatbot Claude 3.5

## 📋 สิ่งที่ต้องเตรียมก่อนเริ่ม

### 1. API Keys ที่ต้องมี

| Service | ใช้ทำอะไร | สมัครที่ไหน |
|---------|----------|------------|
| **Anthropic API** | AI Brain (Claude 3.5) | https://console.anthropic.com/ |
| **Line Channel Token** | รับ-ส่งข้อความ Line | Line OA Manager |
| **Discord Webhook** (optional) | แจ้งเตือนบอส | Discord Server Settings |

---

## 🚀 Phase 1: สมัคร Anthropic API (Claude)

### ขั้นตอนที่ 1: สมัครบัญชี
1. ไปที่ https://console.anthropic.com/
2. คลิก **"Sign Up"** หรือ **"Get API Access"**
3. ใช้อีเมลสมัคร (แนะนำใช้อีเมลธุรกิจ)
4. ยืนยันอีเมล

### ขั้นตอนที่ 2: ขอ API Key
1. เข้า Console → ไปที่ **"API Keys"**
2. กด **"Create Key"**
3. ตั้งชื่อ: `SriKrung-LineBot`
4. **คัดลอก API Key เก็บไว้** (ขึ้นครั้งเดียว!)

### ขั้นตอนที่ 3: เติมเงิน (หรือใช้เครดิตฟรี)
- มีเครดิตทดลอง $5 ฟรี
- เติมเงินขั้นต่ำ $5 (ประมาณ 170 บาท)
- ใช้ได้หลายเดือนขึ้นอยู่กับจำนวนลูกค้า

---

## 🚀 Phase 2: ตั้งค่า Line Webhook

### ขั้นตอนที่ 1: เปิดใช้ Messaging API
1. Line OA Manager → **"Settings"** → **"Messaging API"**
2. กด **"Enable Messaging API"**
3. เลือก **"Existing Provider"** หรือสร้างใหม่
4. บันทึก **Channel Access Token** (Long-lived)
5. บันทึก **Channel Secret**

### ขั้นตอนที่ 2: ตั้งค่า Webhook URL
1. ต้องมี Server หรือใช้บริการ Cloud (Heroku, Railway, etc.)
2. ตั้งค่า Webhook URL: `https://your-server.com/webhook`
3. กด **"Verify"** เพื่อทดสอบ

---

## 🚀 Phase 3: ตั้งค่า Discord Webhook (แจ้งเตือนบอส)

### ขั้นตอนที่ 1: สร้าง Webhook
1. ไปที่ Discord Server ของบอส
2. Server Settings → **"Integrations"** → **"Webhooks"**
3. กด **"New Webhook"**
4. ตั้งชื่อ: `SriKrung-Notifications`
5. เลือก Channel ที่ต้องการให้แจ้งเตือน
6. **คัดลอก Webhook URL**

---

## 🚀 Phase 4: Deploy Chatbot

### ตัวเลือกที่ 1: Heroku (ฟรี ง่าย)

```bash
# 1. สมัคร Heroku
https://signup.heroku.com/

# 2. ติดตั้ง Heroku CLI
https://devcenter.heroku.com/articles/heroku-cli

# 3. Deploy
cd srikrung-landing/chatbot
git init
git add .
git commit -m "Initial commit"
heroku create srikrung-chatbot
heroku config:set ANTHROPIC_API_KEY=your_key
heroku config:set LINE_CHANNEL_ACCESS_TOKEN=your_token
heroku config:set LINE_CHANNEL_SECRET=your_secret
heroku config:set BOSS_NOTIFY_URL=your_discord_webhook
git push heroku main
```

### ตัวเลือกที่ 2: Railway (ง่ายกว่า)

1. ไปที่ https://railway.app/
2. สมัครด้วย GitHub
3. New Project → Deploy from GitHub repo
4. เลือก repo ที่มีโค้ด chatbot
5. Add Environment Variables:
   - `ANTHROPIC_API_KEY`
   - `LINE_CHANNEL_ACCESS_TOKEN`
   - `LINE_CHANNEL_SECRET`
   - `BOSS_NOTIFY_URL`
6. Deploy

### ตัวเลือกที่ 3: PythonAnywhere (ถ้าต้องการแค่ทดสอบ)

1. สมัคร https://www.pythonanywhere.com/
2. Upload ไฟล์ `ai_chatbot.py`
3. ตั้งค่า Environment Variables
4. รัน Flask/Django app

---

## 🧪 Phase 5: ทดสอบระบบ

### ทดสอบการทำงาน
1. ทักไปที่ @vax7479a
2. พิมพ์: "สวัสดี"
3. ควรได้รับคำตอบจาก AI ภายใน 3-5 วินาที

### ทดสอบแจ้งเตือนบอส
1. พิมพ์คำถามยาก: "เคลมประกันรถยนต์ BMW สีแดง ที่อู่เพื่อน แต่ไม่มีใบเสร็จทำไงดี"
2. AI ควรตอบ + แจ้งเตือนบอสใน Discord

---

## 💰 ค่าใช้จ่ายโดยประมาณ

### Claude API (Anthropic)
| จำนวนลูกค้า/เดือน | ค่าใช้จ่ายโดยประมาณ |
|------------------|-------------------|
| 100 คน | ~50-100 บาท |
| 500 คน | ~300-500 บาท |
| 1,000 คน | ~600-1,000 บาท |

### Server/Hosting
- Heroku (Hobby): ~$7/เดือน (~240 บาท)
- Railway: ~$5/เดือน (~170 บาท) - ฟรี $5 เครดิตทุกเดือน
- PythonAnywhere: ฟรี (จำกัด)

---

## ⚠️ ข้อควรระวัง

1. **อย่าเผยแพร่ API Keys** - เก็บใน Environment Variables เท่านั้น
2. **ทดสอบก่อนใช้จริง** - ลองคุยกับ AI หลายรูปแบบก่อนเปิดให้ลูกค้าใช้
3. **Monitor ค่าใช้จ่าย** - ตั้งงบประมาณใน Anthropic Console
4. **มี Plan B** - เตรียมข้อความสำรองกรณี AI ล่ม

---

## 📞 ติดต่อช่วยเหลือ

หากติดปัญหา:
- Anthropic API: https://support.anthropic.com/
- Line API: https://developers.line.biz/
- ชางหลาน: แจ้งใน Discord ได้เลย

---

**พร้อมแล้วเริ่ม Phase 1 เลยครับ!** 🚀
