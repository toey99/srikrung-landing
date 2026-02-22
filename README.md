# Sri Krung Landing Page

Landing Page สำหรับโปรโมทประกันรถยนต์ผ่าน Sri Krung Broker 724

## 🚀 วิธี Deploy บน GitHub Pages

### ขั้นตอนที่ 1: สร้าง GitHub Repository
1. เข้าไปที่ [github.com](https://github.com)
2. คลิก "New Repository"
3. ตั้งชื่อ: `srikrung-landing` (หรือชื่ออื่นที่ต้องการ)
4. เลือก "Public"
5. คลิก "Create repository"

### ขั้นตอนที่ 2: อัพโหลดไฟล์
```bash
# ในโฟลเดอร์ srikrung-landing
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/srikrung-landing.git
git push -u origin main
```

### ขั้นตอนที่ 3: เปิดใช้ GitHub Pages
1. ใน Repository คลิก "Settings"
2. เลือก "Pages" จากเมนูซ้าย
3. ที่ "Source" เลือก "Deploy from a branch"
4. เลือก Branch "main" และโฟลเดอร์ "/ (root)"
5. คลิก "Save"
6. รอ 2-3 นาที แล้วเข้า URL: `https://YOUR_USERNAME.github.io/srikrung-landing`

## 📊 การตั้งค่า Google Ads

### Conversion Tracking
เพิ่ม Google Ads Conversion Tag ใน `<head>`:
```html
<!-- Global site tag (gtag.js) - Google Ads: YOUR_CONVERSION_ID -->
<script async src="https://www.googletagmanager.com/gtag/js?id=AW-XXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'AW-XXXXXXXXX');
</script>
```

### Event Tracking
สำหรับปุ่ม "แอดไลน์":
```javascript
gtag('event', 'conversion', {
  'send_to': 'AW-XXXXXXXXX/label_name',
  'value': 1.0,
  'currency': 'THB'
});
```

## 🔍 Long-tail Keywords ที่แนะนำ

ดูไฟล์ `keywords.md`

## 📝 ข้อมูลติดต่อ
- Line: @vax7479a
- โทร: 084-161-5554
- Affiliate Link: https://insure.724.co.th/u/AM00441133
