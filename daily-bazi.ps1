# Daily Bazi Prediction Script for อวี้เวิน
# ทำนายดวงประจำวันสำหรับบอส (นิภาวดี ตั้งเส้ง)
# Run every day at 07:30 AM

function Get-DayStem($date) {
    # คำนวณ 天干 ของวัน
    $stems = @("甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸")
    $elements = @("Wood", "Wood", "Fire", "Fire", "Earth", "Earth", "Metal", "Metal", "Water", "Water")
    $thaiNames = @("เจีย", "ยี่", "ปิง", "ติง", "อู๋", "จี", "เจิง", "ซิน", "เร็น", "กวย")
    
    # สูตรคำนวณ: (Julian Day Number) % 10
    $jd = [Math]::Floor(($date - (Get-Date "1900-01-01")).TotalDays)
    $index = ($jd + 9) % 10
    
    return @{
        Stem = $stems[$index]
        Element = $elements[$index]
        ThaiName = $thaiNames[$index]
        Index = $index
    }
}

function Get-ElementEmoji($element) {
    switch ($element) {
        "Wood" { return "🌳" }
        "Fire" { return "🔥" }
        "Earth" { return "🌍" }
        "Metal" { return "⚙️" }
        "Water" { return "💧" }
    }
}

function Get-ColorRecommendation($dayElement, $bossFavorable) {
    # บอสถูกโชค: น้ำ, ไม้, โลหะ
    # บอสไม่ถูกโชค: ไฟ, ดิน
    
    $best = ""
    $good = ""
    $avoid = ""
    
    switch ($dayElement) {
        "Wood" {
            $best = "🥇 ดำ, น้ำเงิน (ธาตุน้ำหล่อเลี้ยงไม้)"
            $good = "🥈 เขียว (ธาตุไม้เสริมแกร่ง)"
            $avoid = "❌ ขาว, เทา (โลหะตัดไม้), แดง, ส้ม (ไฟเผาไม้)"
        }
        "Fire" {
            $best = "🥇 ดำ, น้ำเงิน (ธาตุน้ำดับไฟ)"
            $good = "🥈 ขาว, เทา, ทอง (ธาตุโลหะถูกชะตา)"
            $avoid = "❌ แดง, ส้ม, ชมพู (ไฟเพิ่มไฟ), เหลือง, น้ำตาล (ดินดูดพลัง)"
        }
        "Earth" {
            $best = "🥇 ขาว, เงิน, ทอง (ธาตุโลหะระบายดิน)"
            $good = "🥈 ดำ, น้ำเงิน (น้ำหล่อเลี้ยง)"
            $avoid = "❌ เหลือง, น้ำตาล, ครีม (ดินเพิ่มดิน), แดง, ส้ม (ไฟแผดเผา)"
        }
        "Metal" {
            $best = "🥇 เหลือง, น้ำตาล (ธาตุดินกำเนิดโลหะ)"
            $good = "🥈 ขาว, เงิน, ทอง (โลหะเสริมโลหะ)"
            $avoid = "❌ แดง, ส้ม (ไฟหลอมโลหะ), เขียว (ไม้สิ้นเปลือง)"
        }
        "Water" {
            $best = "🥇 เขียว (ธาตุไม้กำเนิดน้ำ)"
            $good = "🥈 ดำ, น้ำเงิน (น้ำเสริมน้ำ)"
            $avoid = "❌ เหลือง, น้ำตาล (ดินดูดน้ำ), ขาว, เทา (โลหะสิ้นเปลือง)"
        }
    }
    
    return @($best, $good, $avoid)
}

function Get-DoAndAvoid($dayElement) {
    $do = @()
    $avoid = @()
    
    switch ($dayElement) {
        "Wood" {
            $do = @("เริ่มต้นโปรเจกต์ใหม่", "เจรจาต่อรอง", "เรียนรู้สิ่งใหม่", "ออกกำลังกายเบาๆ")
            $avoid = @("ตัดสินใจเร่งรีบ", "ทะเลาะเบาะแว้ง", "ใช้จ่ายฟุ่มเฟือย")
        }
        "Fire" {
            $do = @("วางแผนล่วงหน้า", "ทำงานออนไลน์", "พูดคุยสร้างความสัมพันธ์", "ดื่มน้ำมากๆ")
            $avoid = @("ตัดสินใจใหญ่", "เซ็นสัญญา", "ขับรถไกล", "ทำงานหนักเกินไป")
        }
        "Earth" {
            $do = @("จัดระเบียบ", "วิเคราะห์ข้อมูล", "ทบทวนแผนงาน", "พักผ่อนให้เพียงพอ")
            $avoid = @("เริ่มธุรกิจใหม่", "ลงทุนใหญ่", "เปลี่ยนแปลงกะทันหัน")
        }
        "Metal" {
            $do = @("ตัดสินใจเด็ดขาด", "เจรจาธุรกิจ", "จัดการปัญหาค้างคา", "วางแผนการเงิน")
            $avoid = @("ยืดเยื้อเรื่องเดิม", "ใช้อารมณ์", "ประมาทเรื่องสุขภาพ")
        }
        "Water" {
            $do = @("สร้างสรรค์", "เขียน content", "ติดต่อสื่อสาร", "เดินทางสั้นๆ")
            $avoid = @("ตัดสินใจเร่งรีบ", "ลงนามสัญญา", "เปลี่ยนงาน")
        }
    }
    
    return @($do, $avoid)
}

function Get-LuckyDirection($dayElement) {
    switch ($dayElement) {
        "Wood" { return "ตะวันออก (E) - ธาตุไม้" }
        "Fire" { return "ใต้ (S) - ธาตุไฟ" }
        "Earth" { return "ตะวันตกเฉียงใต้ (SW) - ธาตุดิน" }
        "Metal" { return "ตะวันตก (W) - ธาตุโลหะ" }
        "Water" { return "เหนือ (N) - ธาตุน้ำ" }
    }
}

# Main Script
$today = Get-Date
$dayInfo = Get-DayStem $today
$elementEmoji = Get-ElementEmoji $dayInfo.Element
$colors = Get-ColorRecommendation $dayInfo.Element
$activities = Get-DoAndAvoid $dayInfo.Element
$direction = Get-LuckyDirection $dayInfo.Element

# Generate Message
$message = @"
🔮 **ดวงประจำวัน: $($today.ToString('dddd d MMMM yyyy', [System.Globalization.CultureInfo]::GetCultureInfo('th-TH')))**

| รายการ | รายละเอียด |
|--------|-----------|
| **干支** | $($dayInfo.Stem) ($($dayInfo.ThaiName)) - $($dayInfo.Element) $elementEmoji |
| **ธาตุวัน** | $($dayInfo.Element) |

---

👕 **สีเสื้อแนะนำวันนี้**

$($colors[0])
$($colors[1])
$($colors[2])

---

✅ **ควรทำ**
$($activities[0] | ForEach-Object { "• $_`n" })

❌ **ควรหลีกเลี่ยง**
$($activities[1] | ForEach-Object { "• $_`n" })

---

💡 **เคล็ดลับเสริมดวง**
• 🧭 **ทิศมงคล:** $direction
• 💧 **ดื่มน้ำ:** อย่างน้อย 8 แก้ว (เติมธาตุน้ำให้ร่างกาย)
• 🍽️ **อาหาร:** เน้นผัก ผลไม้ (ธาตุไม้) และน้ำเย็น
• 🧘 **อารมณ์:** ใจเย็น หายใจลึกๆ ก่อนตอบโต้

---

> 💬 **คำทำนาย:** $(if ($dayInfo.Element -eq "Fire" -or $dayInfo.Element -eq "Earth") { "วันนี้ธาตุ$($dayInfo.Element) บอสอาจเหนื่อยหน่อย แต่ถ้าดูแลตัวเองตามคำแนะนำ จะผ่านไปด้วยดี" } else { "วันนี้ธาตุ$($dayInfo.Element) เอื้ออำนวยต่อบอส ทำอะไรก็ราบรื่น" })

ขอให้วันนี้โชคดีครับ 🙏
- อวี้เวิน (玉雯)
"@

# Send message via OpenClaw
# Note: This requires OpenClaw to be configured
$encodedMessage = [System.Web.HttpUtility]::UrlEncode($message)
Start-Process "openclaw" -ArgumentList "message send --to 845247710784520192 --message `"$message`"" -NoNewWindow

Write-Output "Bazi prediction sent for $($today.ToString('yyyy-MM-dd'))"
