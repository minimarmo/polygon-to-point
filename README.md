# Polygon to Point QGIS Plugin

## 🔍 Overview

**Polygon to Point** เป็นปลั๊กอินสำหรับโปรแกรม [QGIS](https://qgis.org) ที่ช่วยให้ผู้ใช้งานสามารถแปลงชั้นข้อมูลแบบ Polygon (พื้นที่) ให้กลายเป็นชั้นข้อมูลแบบ Point (จุด) ได้อย่างสะดวกรวดเร็ว

นอกจากนี้ยังสามารถเลือกเก็บค่าของ Field ที่ต้องการจาก Polygon ไปยัง Point ได้ด้วย โดยสามารถตั้งชื่อ Field ใหม่ได้ตามต้องการ

## ✨ Features

- แปลงรูปแบบข้อมูลจาก **Polygon เป็น Point**
- กำหนดได้ว่าจะใช้จุด **Centroid**, **Point on Surface** หรือวิธีอื่น (ขึ้นกับเวอร์ชัน)
- รองรับการ **เลือก Field** ที่ต้องการเก็บจากต้นฉบับ
- ตั้งชื่อ Field ปลายทางได้
- ใช้งานง่ายผ่านหน้าต่าง GUI ใน QGIS

## 🛠️ Installation

เนื่องจากปลั๊กอินนี้ **ยังไม่ได้เผยแพร่ใน QGIS Plugin Repository** หากต้องการใช้งาน ให้ทำตามขั้นตอนดังนี้:

1. ดาวน์โหลดหรือ clone repository นี้:

   ```bash
   git clone https://github.com/yourusername/polygon-to-point.git
   ```

2. คัดลอกโฟลเดอร์ polygon-to-point ไปไว้ที่:

- **Windows**: C:\Users\<your_username>\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\
- **macOS/Linux**: ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/

3. เปิด QGIS แล้วไปที่เมนู **Plugins > Manage and Install Plugins...**

4. ค้นหาและเปิดใช้งานปลั๊กอิน **"Polygon to Point"**

## 🧪 Usage

1. โหลดเลเยอร์ Polygon เข้ามาใน QGIS
2. เปิดปลั๊กอิน `Polygon to Point`
3. เลือกเลเยอร์ต้นทาง
4. เลือก Field ที่ต้องการเก็บไว้
5. ตั้งชื่อ Field สำหรับผลลัพธ์
6. กด **Run**
