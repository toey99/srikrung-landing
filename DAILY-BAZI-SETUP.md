# คู่มือตั้งค่า อวี้เวิน ทำนายดวงประจำวัน

## 📅 รายละเอียด
- **เวลา:** 07:30 น. ทุกวัน
- **ผู้ส่ง:** อวี้เวิน (หัวหน้าแผนกซินแส)
- **เนื้อหา:** ดวงประจำวัน สีเสื้อ ทิศมงคล เรื่องควรทำ/หลีกเลี่ยง
- **ผู้รับ:** บอส (Discord)

---

## 🛠️ ขั้นตอนตั้งค่า

### ขั้นตอนที่ 1: ตรวจสอบไฟล์
ตรวจสอบว่าไฟล์ `daily-bazi.ps1` อยู่ในโฟลเดอร์:
```
C:\Users\User\.openclaw\workspace\srikrung-landing\daily-bazi.ps1
```

### ขั้นตอนที่ 2: สร้าง Scheduled Task

**เปิด PowerShell แล้วรันคำสั่งนี้:**

```powershell
# สร้าง Action (สิ่งที่ต้องทำ)
$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `"C:\Users\User\.openclaw\workspace\srikrung-landing\daily-bazi.ps1`""

# สร้าง Trigger (เวลาที่ต้องทำ)
$Trigger = New-ScheduledTaskTrigger -Daily -At "07:30"

# ตั้งค่าให้รันทุกวัน แม้ไม่ได้ล็อกอิน
$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -LogonType Interactive

# ตั้งค่า Settings
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# ลงทะเบียน Task
Register-ScheduledTask -TaskName "อวี้เวิน_ดวงประจำวัน" -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings -Force

Write-Host "✅ ตั้งค่าสำเร็จ! อวี้เวินจะส่งดวงประจำวันให้ทุกเช้า 07:30 น."
```

### ขั้นตอนที่ 3: ตรวจสอบว่าสร้างสำเร็จ

```powershell
Get-ScheduledTask -TaskName "อวี้เวิน*"
```

ถ้าขึ้นชื่อ Task แสดงว่าสำเร็จ

---

## 🧪 ทดสอบรันทันที (ไม่ต้องรอพรุ่งนี้)

```powershell
Start-ScheduledTask -TaskName "อวี้เวิน_ดวงประจำวัน"
```

หรือรันสคริปต์โดยตรง:
```powershell
powershell -ExecutionPolicy Bypass -File "C:\Users\User\.openclaw\workspace\srikrung-landing\daily-bazi.ps1"
```

---

## ❌ วิธีลบ (ถ้าต้องการยกเลิก)

```powershell
Unregister-ScheduledTask -TaskName "อวี้เวิน_ดวงประจำวัน" -Confirm:$false
```

---

## 📝 หมายเหตุ

1. **OpenClaw ต้องทำงานอยู่** - Task จะใช้คำสั่ง `openclaw message send` ส่งข้อความมาที่ Discord
2. **เครื่องต้องเปิดอยู่** - ถ้าปิดเครื่องตอน 07:30 น. จะไม่ได้รับข้อความ (หรืออาจ delay ถ้าตั้งค่า `StartWhenAvailable`)
3. **โหมด Offline** - สคริปต์คำนวณดวงจากวันที่เครื่อง ไม่ต้องต่ออินเทอร์เน็ตก็คำนวณได้

---

## 🔧 แก้ไขเวลา (ถ้าต้องการเปลี่ยน)

```powershell
# ลบอันเก่าก่อน
Unregister-ScheduledTask -TaskName "อวี้เวิน_ดวงประจำวัน" -Confirm:$false

# สร้างใหม่ด้วยเวลาที่ต้องการ (เช่น 08:00 น.)
$Trigger = New-ScheduledTaskTrigger -Daily -At "08:00"
# ... (ตามด้วยคำสั่งสร้าง Task เหมือนข้างบน)
```

---

**พร้อมแล้วรันคำสั่งในขั้นตอนที่ 2 ได้เลยครับ!** 🔮
