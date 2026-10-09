# کارگاه دوم — آزمایشگاه قالب‌ها: چهار قالب، یک مجموعهٔ داده (حدود ۴۵ دقیقه)

در جلسهٔ اول یاد گرفتیم که یک فایل متنی را **بخوانیم**. امروز تصمیم می‌گیریم که داده‌ها را **چگونه ذخیره کنیم** و می‌بینیم قالب سریع‌ترین، قالب کوچک‌تر نیست. این غافلگیری کل درس است: هر قالب چیزی را قربانی می‌کند و کار یک مهندس عملی این است که بداند کدام قربانی را می‌توان کرد. خزش‌گری که ۱۲٬۰۰۰ رکورد محصول می‌نویسد باز باید انتخاب کند؛ پایگاه دادهٔ برداری که در جلسهٔ دوازدهم ماتریس تعبیه می‌نویسد هم باید؛ و شما هم تا حدود چهل دقیقه دیگر باید.

**چه چیزی با خود می‌بری:** یک `format_lab.py` که همان ۱۲ رکورد را به‌صورت CSV، JSON، NDJSON و Pickle ذخیره می‌کند، **۱۰٬۰۰۰ پروفایل جعلی** تولید می‌کند، آن‌ها را در هر چهار قالب ذخیره می‌کند، ثابت می‌کند همهٔ فایل‌ها یکسان برمی‌گردند، هر بار بارگذاری را زمان‌گیری می‌کند، **جدول نتایج** چاپ می‌کند و گزارشی می‌نویسد که `tail -f` بتواند زنده دنبال کند.

شما پایتون پایه را می‌دانی (متغیر، حلقه، تابع) و `open()` و حلقه‌های `for` جلسهٔ اول را. هر چیز جدید اینجا توضیح داده شده، با خطوط فایل نمونه و شکل کدی که لازم داری. نیازی به گشتن نیست.

## راه‌اندازی (حدود ۳ دقیقه)

ابتدا محیط مجازی دوره را فعال کن (راه‌اندازی یک‌باره در `README.md` اصلی) و سپس همه‌چیز را از این پوشه (`session-02-binary-data-os-files/`) به‌صورت `python` ساده اجرا کن:

```
cd session-02-binary-data-os-files
python workshop/starter/format_lab.py
```

باید این را ببینی:

```
TODO-1 not done yet - read the CSV with csv.DictReader
(11 TODOs total - open starter/format_lab.py and work top to bottom.)
```

هیچ‌چیز کرش نکرد و هیچ‌چیز پاک نشد؛ این شکست دوستانه عمدی است. یکی‌یکی TODOها را خاموش می‌کنی.

## بیمارت را بشناسیم

پوشهٔ `workshop/data/` **همان ۱۲ رکورد را در هر چهار قالب** نگه می‌دارد:

```
records.csv      — id,name,price,description,category (عنوان + ۱۲ ردیف)
records.json     — همان ۱۲ ردیف، قالب‌بندی‌شده
records.ndjson   — همان ۱۲ ردیف، یک شیء JSON در هر خط
records.pkl      — همان ۱۲ ردیف، اشیاء Pickle شدهٔ پایتون
```

دو جزئیت که مهم‌اند:

```
id,name,price,category,description
p-001,Desk Lamp,19.99,lighting,"Warm LED desk lamp, brushed steel, 3-year warranty"
...
p-012,"Cable, 3-pack",11.00,electronics,"Three braided cables, 1m each, mixed lengths, spare"
```

ردیف دوازدهم **ویرگولی داخل نام** دارد، داخل نقل‌قول. همین نویسهٔ واحد دلیل این است که به‌جای `line.split(",")` از ماژول `csv` استفاده می‌کنیم؛ split به تو ۶ فیلد می‌داد نه ۵. هر عدد پایین را می‌توانی با دست از این فایل بررسی کنی.

همهٔ خروجی‌ها به `workshop/out/` می‌روند (starter آن را با `os.makedirs(OUT_DIR, exist_ok=True)` می‌سازد؛ `exist_ok=True` یعنی «اگر از قبل وجود دارد اعتراض نکن»).

## سفر

### ایستگاه ۱ — خواندن CSV بدون شکستن روی ویرگول‌ها (حدود ۸ دقیقه)

هنوز هیچ‌چیز کار نمی‌کند: `load_csv()` پیش از باز کردن هر فایلی خطا می‌دهد. این مهارتی است که کل جلسه روی آن بنا شده.

توابع جدید، هرکدام در یک خط. `csv.DictReader(f)`؛ یک شیء فایل CSV را می‌پیماید و هر ردیف را به‌صورت یک دیکشنری برمی‌گرداند و نام ستون‌ها را از سطر عنوان می‌گیرد، پس به‌جای `row[0]` می‌نویسی `row["price"]`. `newline=""` در `open()`؛ به پایتون می‌گوید «پایان خط را ترجمه نکن»؛ مستندات csv آن را می‌خواهند و باعث می‌شود شمارش بایت‌ها روی ویندوز و لینوکس یکسان بماند.

`workshop/starter/format_lab.py` را باز کن و **TODO-1** را جایگزین کن:

```python
rows = []                                  # our growing list of rows
f = open(path, mode="r", encoding="utf-8", newline="")
reader = csv.DictReader(f)                 # one dict per row, keyed by header
for row in reader:                         # iterate rows, not lines
    rows.append(row)                       # keep it
f.close()                                  # let go of the handle
return rows                                # hand the list back
```

نقطهٔ بازبینی — starter را دوباره اجرا کن:

```
python workshop/starter/format_lab.py
```

```
TODO-2 not done yet - write the CSV with csv.DictWriter
(8 TODOs total - open starter/format_lab.py and work top to bottom.)
```

پیشرفتی که می‌بینی. (مسیر فایل خالی: قطعهٔ بالا را در یک `my_lab.py` خالی تایپ کن، چهار خط `print` از `main()` را در انتهایش اضافه کن و دقیقاً همین را می‌بینی؛ ۱۲ ردیف، `Cable, 3-pack` سالم، `price` با نوع `str`.)

*آنچه یاد گرفتی: `csv.DictReader` عنوان و خطوط را تبدیل به دیکشنری می‌کند و نقل‌قول همان چیزی است که ویرگول‌های داخل مقادیر را امن می‌کند.*

### ایستگاه ۲ — نوشتن همان ردیف‌ها به سه روش متنی (حدود ۸ دقیقه)

خواندن نیمی از کار است. اکنون می‌نویسی: CSV خروجی، JSON قالب‌بندی‌شده و NDJSON.

توابع جدید، هرکدام در یک خط. `csv.DictWriter(f, fieldnames=FIELDS)`؛ یک شیء نویسنده؛ `fieldnames=` **ترتیب ستون‌ها** است، پس آن فهرست طرح‌بندی تو است. `writer.writeheader()` خط `id,name,...` را می‌نویسد. `json.dump(obj, f, indent=2)`؛ یک شیء پایتون را در فایلی که **خودت** باز کردی می‌نویسد. مقادیر پرکاربرد `indent`: `۲` (خوانا، همانی که استفاده می‌کنیم)، `۴` (جادارتر)، `None` (یک خط بلند، کوچک‌ترین فایل). `json.dumps(obj)`؛ همان کار اما یک **رشته** برمی‌گرداند به‌جای نوشتن در فایل.

**TODO-2** (CSV) و **TODO-3** (JSON) را جایگزین کن:

```python
f = open(path, mode="w", encoding="utf-8", newline="")
writer = csv.DictWriter(f, fieldnames=FIELDS)   # column order lives here
writer.writeheader()                            # the "id,name,..." line
for row in rows:
    writer.writerow(row)                        # quotes any value with a comma
f.close()
return os.path.getsize(path)                    # bytes on disk, no reading
```

```python
f = open(path, mode="w", encoding="utf-8", newline="")
json.dump(rows, f, indent=2)                     # pretty JSON
f.write("\n")                                   # one trailing newline
f.close()
return os.path.getsize(path)
```

سپس **TODO-4** (NDJSON)؛ همان داده، یک شیء در هر خط:

```python
f = open(path, mode="w", encoding="utf-8", newline="")
for row in rows:
    f.write(json.dumps(row) + "\n")             # json.dumps -> a string
f.close()
return os.path.getsize(path)
```

نقطهٔ بازبینی — starter اکنون به TODO-5 می‌رسد. (مسیر فایل خالی: هر سه تابع و یک حلقه را اضافه کن و شمارش بایت‌های پایین را می‌گیری. CSV را با دست بررسی کن: عنوان ۴۰ بایت است و ۱۲ ردیف `"` را دور هر مقدار دارای ویرگول می‌گیرند.)

```
csv     1050
json    2101
ndjson  1774
```

دو عددی که ارزش خیره شدن دارند: JSON **۲٫۰۰ برابر** اندازهٔ CSV است. قالب‌بندی به‌علاوهٔ تکرار هر کلید ۱۲ بار، بیشتر از همهٔ چیزهای دیگر با هم هزینه داشته است.

*آنچه یاد گرفتی: CSV هیچ‌چیز را تکرار نمی‌کند، JSON کلیدها را تکرار و فاصله اضافه می‌کند، NDJSON کلیدها را تکرار می‌کند اما دربرگیرنده را حذف می‌کند؛ و `os.path.getsize` هر فایلی را بدون خواندن اندازه می‌گیرد.*

### ایستگاه ۳ — افزودن قالب دودویی (حدود ۶ دقیقه)

اکنون متفرقه. Pickle اشیاء پایتون را مستقیم ذخیره می‌کند، پس قانون نقل‌قولی ندارد، خط طرح‌بندی ندارد و هنگام برگشت تجزیه‌ای صورت نمی‌گیرد.

تابع جدید، در یک خط: `open(path, mode="wb")`؛ حالت **باینری**؛ `b` لازم است چون Pickle `bytes` می‌نویسد و حالت متنی فقط `str` می‌پذیرد. مقادیر پرکاربرد: `"rb"` خواندن باینری، `"wb"` نوشتن باینری، `"ab"` افزودن باینری. `protocol=pickle.HIGHEST_PROTOCOL`؛ جدیدترین و سریع‌ترین رمزنگاری پایتون؛ روی پایتون‌های مدرن ۵ است و دلیلی برای استفاده از چیز دیگری وجود ندارد.

**TODO-5** را جایگزین کن:

```python
f = open(path, mode="wb")                      # "b" = binary, pickle requires it
pickle.dump(rows, f, protocol=pickle.HIGHEST_PROTOCOL)   # returns nothing
f.close()
return os.path.getsize(path)
```

نقطهٔ بازبینی — رفت‌وبرگشت اکنون برای هر چهار قالب اجرا می‌شود:

```
csv     1050
json    2101
ndjson  1774
pickle  1321
```

```
--- round trip: load each file back ---
csv     12 rows | first id p-001
json    12 rows | first id p-001
ndjson  12 rows | first id p-001
pickle  12 rows | first id p-001
```

هر چهار ۱۲ ردیف با `p-001` در ابتدا و `Cable, 3-pack` سالم برمی‌گردانند. نکتهٔ صادقانه را ببین: `price` در **هر چهار** `str` است، چون ردیف‌ها از ابتدا از CSV آمده‌اند؛ Pickle وفادارانه متن را حفظ کرده است. اگر به `save_pickle` دیکشنری با `float` واقعی بدهی (به Stretch نگاه کن)، Pickle تنها کسی است که `float` برمی‌گرداند.

*آنچه یاد گرفتی: Pickle کوچک‌تر از JSON قالب‌بندی‌شده است و طرح‌بندی نمی‌خواهد، اما فقط انواعی را حفظ می‌کند که خودت به آن داده‌ای.*

### ایستگاه ۴ — بزرگ کردن مقیاس: ۱۰٬۰۰۰ پروفایل جعلی (حدود ۸ دقیقه)

دوازده ردیف در یک خط حافظه جا می‌شوند؛ دنیای واقعی بزرگ‌تر است. starter فایل `fake_data.py` را دارد، یک تولیدکنندهٔ فقط با کتابخانهٔ استاندارد (دانه ۴۲، پس پروفایل‌های تو با ما یکسان‌اند):

```python
from fake_data import generate_profiles
profiles = generate_profiles(10000)
print("first profile:", profiles[0]["id"], "|", profiles[0]["name"],
      "|", profiles[0]["email"])
```

```
first profile: u-00001 | Umar Brown | umar.brown@gmail.com
```

هر پروفایل ۱۱ فیلد دارد، از جمله فهرست تو‌درتوی `tags`؛ ساختار کافی برای اینکه انتخاب قالب مهم شود. **TODO-7** را جایگزین کن:

```python
sizes_big = save_all(profiles, "profiles", PROFILE_FIELDS)
print("format   bytes")
for fmt in FORMATS:
    print(fmt.ljust(8) + str(sizes_big[fmt]))
print("json/csv ratio: " + ("%.2f" % (sizes_big["json"] / sizes_big["csv"])))
```

نقطهٔ بازبینی — جدول کامل نتایج برای ۱۰٬۰۰۰ پروفایل:

```
format   bytes
csv     1170270
json    2975033
ndjson  2330282
pickle  1200456

json/csv ratio: 2.54
```

CSV همچنان کوچک‌تر است، اما Pickle را ببین: فقط **۳۰ کیلوبایت بیشتر** از CSV برای ۱۰٬۰۰۰ رکورد. در ۱۲ ردیف Pickle از CSV بزرگ‌تر بود؛ در مقیاس بزرگ فاصله می‌بندد چون Pickle اعداد را به‌صورت بایت خام ذخیره می‌کند در حالی که CSV ارقام را به‌صورت متن ذخیره می‌کند.

*آنچه یاد گرفتی: رتبه‌بندی قالب‌ها در مقیاس بزرگ هم برقرار می‌ماند، اما حاشیه‌ها جابه‌جا می‌شوند؛ و فهرست تو‌درتوی `tags` چیزی است که CSV و NDJSON به‌طور بومی نمی‌توانند نمایش دهند.*

### ایستگاه ۵ — زمان‌گیری (حدود ۶ دقیقه)

اندازه نیمی از مقایسه است؛ زمان نیمهٔ دیگر و پاسخ چیزی نیست که انتظار داری.

حلقهٔ زمان‌گیری به تو داده شده در `measure()`؛ آن را بخوان، بازنویسی نکن:

```python
load_any(path, fmt)                            # warm-up: page the bytes in
total = 0.0
for _ in range(repeats):                       # repeats = 200 by default
    start = time.perf_counter()                # a monotonic clock, in seconds
    load_any(path, fmt)
    total = total + (time.perf_counter() - start)
return total * 1000.0 / repeats                 # -> average milliseconds
```

آن فراخوانی اول دورریزی تزئینی نیست: اولین بارگذاری هزینهٔ پر کردن حافظهٔ نهان سیستم‌عامل را می‌دهد، پس اگر درش بماندیم هر قالبی که **اول** اجرا شود بی‌دلیل کندتر به نظر می‌رسد. اجراش کن:

```
python workshop/solution/format_lab.py 200 1
```

```
--- average load time over 200 runs (ms) ---
format   load_ms
csv     48.2418
json    42.7324
ndjson  63.6525
pickle  19.2290
```

Pickle سریع‌ترین (۱۹٫۲ میلی‌ثانیه) و NDJSON کندترین (۶۳٫۷ میلی‌ثانیه) است؛ **۳٫۳ برابر** با هم. CSV دومین کند با ۴۸٫۲ میلی‌ثانیه است. اعداد تو نزدیک اما یکسان نخواهد بود؛ این زمان‌گیری واقعی روی سخت‌افزار واقعی است و ترتیب ادعاست، نه رقم سوم اعشار.

*آنچه یاد گرفتی: قالب‌های دودویی تجزیه را نمی‌کنند، پس Pickle در هر مقیاسی سرعت برنده است؛ اما فاصله با بزرگ شدن فایل بیشتر می‌شود.*

### ایستگاه ۶ — تخلیهٔ گزارش (حدود ۶ دقیقه)

اکنون آخرین TODO و دلیل وجود `flush()`. `tail -f app.log` در ترمینال تو فقط خطوطی را می‌تواند نشان دهد که از بافر پایتون خارج شده باشند، پس حلقهٔ ثبت گزارش باید آن‌ها را در حین نوشتن بیرون بدهد.

تابع جدید، در یک خط: `f.flush()`؛ بافر را همین حالا به سیستم‌عامل تحویل می‌دهد. `close()` هم تخلیه می‌کند، اما فقط *پس از پایان حلقهٔ تو* که هدف از گزارش زنده را خنثی می‌کند.

**TODO-6** را جایگزین کن:

```python
stamp = "2026-05-04 12:00:00"
f = open(path, mode="a", encoding="utf-8", newline="")   # "a" = append
written = 0
for i in range(count):
    second = int(stamp[-2:]) + 1         # read the seconds field as a number
    stamp = stamp[:-2] + ("%02d" % second)   # zero-padded, back on the string
    f.write(stamp + " INFO  " + message + " #" + str(i + 1) + "\n")
    written = written + 1
    if tail_every > 0 and written % tail_every == 0:
        f.flush()                        # tailer can see this line NOW
f.close()                                # always flushes whatever is left
return written
```

همین ترفند افزایش زمان همان چیزی است که `tail_log()` جلسهٔ بیست‌ووسوم لازم دارد.

نقطهٔ بازبینی — starter تمام‌شده را اجرا کن:

```
python workshop/starter/format_lab.py 200 1
```

```
--- log tailing with flush() (flush every 1 lines) ---
lines written: 3
  2026-05-04 12:00:00 INFO  server started
  2026-05-04 12:00:01 INFO  crawler indexed document #1
  2026-05-04 12:00:02 INFO  crawler indexed document #2
  2026-05-04 12:00:03 INFO  crawler indexed document #3

smallest file: csv (1050 bytes)
fastest load:  pickle (0.1060 ms)
csv/json size ratio: 2.00
```

زمان‌ها دقیقاً یک ثانیه در هر خط جلو رفته‌اند: `00`، `01`، `02`، `03`. اگر زمان تکراری می‌بینی، خط `stamp = stamp[:-2] + ...` جا افتاده است.

*آنچه یاد گرفتی: چگونه بارگذاری فایل را منصفانه زمان‌گیری کنی (اول گرم‌کردن، بعد میانگین چند بار) و چگونه `flush()` گزارش را در حالی که برنامه هنوز در حال اجراست خوانا می‌کند.*

### ایستگاه ۷ — به‌روزرسانی یک رکورد (حدود ۴ دقیقه)

قالب‌ها نیمی از ماجرا هستند؛ نیمهٔ دیگر این است که با داده‌ها پس از بارگذاری **چه می‌کنی**. ساده‌ترین عملیات: تغییر یک فیلد در یک رکورد.

**TODO-8** را جایگزین کن:

```python
records[index][field] = value
```

همین. یک خط. فهرست تغییرپذیر است، دیکشنری تغییرپذیر است، پس تغییر در محل اتفاق می‌افتد.

نقطهٔ بازبینی:

```
updated price of first profile: 999.99
```

*آنچه یاد گرفتی: فهرستی از دیکشنری‌ها ساختار تغییرپذیر در محل است؛ `records[index][field] = value` اصل را تغییر می‌دهد.*

### ایستگاه ۸ — حذف رکوردها بر اساس شرط (حدود ۵ دقیقه)

حالا رکوردهایی که با شرط مطابقت دارند را حذف کن. این یک فیلتر است؛ همه‌چیزی که مطابقت **ندارد** را نگه دار.

**TODO-9** را جایگزین کن:

```python
kept = []
for rec in records:
    if not predicate(rec):
        kept.append(rec)
return kept
```

predicate تابعی است که برای رکوردهایی که باید حذف شوند `True` برمی‌گرداند. برای مثال، `lambda p: p["state"] == "CA"` همهٔ پروفایل‌های کالیفرنیا را حذف می‌کند.

نقطهٔ بازبینی:

```
deleted 847 CA profiles; 9153 remain
```

*آنچه یاد گرفتی: فیلتر کردن با `if not predicate(rec)` فهرست جدیدی می‌سازد؛ اصل دست‌نخورده می‌ماند.*

### ایستگاه ۹ — درج در شاخص مشخص (حدود ۴ دقیقه)

گاهی لازم است رکوردی در موقعیت مشخص اضافه کنی، نه فقط به انتهای فهرست. برش‌گیری پایتون این کار را تمیز می‌کند.

**TODO-10** را جایگزین کن:

```python
result = records[:index] + [record] + records[index:]
return result
```

`records[:index]` همه‌چیز قبل از آن است، `[record]` آیتم جدید، `records[index:]` همه‌چیز از `index` به بعد. الحاق فهرست جدیدی می‌سازد که رکورد دقیقاً در `index` درج شده است.

نقطهٔ بازبینی:

```
inserted at index 5; profile at index 5: u-new | Test User
```

*آنچه یاد گرفتی: `list[:i] + [item] + list[i:]` در موقعیت `i` درج می‌کند؛ فهرست اصلی تغییر نمی‌کند.*

### ایستگاه ۱۰ — عملیات‌های ترکیبی (حدود ۵ دقیقه)

اکنون آن‌ها را به هم متصل کن. **TODO-11** را جایگزین کن:

```python
ca_count = len([p for p in profiles if p["state"] == "CA"])
profiles = delete_records(profiles, lambda p: p["state"] == "CA")
new_profile = {"id": "u-new", "name": "Test User", "email": "test@example.org",
               "age": 30, "price": 42.00, "city": "Testville", "state": "TS",
               "zip": 12345, "street": "1 Test St", "product": "test product",
               "tags": ["test"]}
profiles = insert_at(profiles, 5, new_profile)
print("deleted", ca_count, "CA profiles; inserted at index 5")
print("profile at index 5:", profiles[5]["id"], "|", profiles[5]["name"])
```

نقطهٔ بازبینی:

```
deleted 847 CA profiles; inserted at index 5
profile at index 5: u-new | Test User
```

*آنچه یاد گرفتی: به‌روزرسانی، حذف و درج سه عملیات اولیهٔ رکورد هستند؛ بقیه ترکیب آن‌هاست.*

## خروجی مورد انتظار

خروجی دقیق راه‌حل درست، کپی‌شده از اجرای واقعی `python workshop/solution/format_lab.py 200 1` از این پوشه. همه‌چیز بالای این خط روی هر دستگاهی یکسان است؛ مقادیر `load_ms` و خطوط «fastest load» زمان‌گیری واقعی است و کمی متفاوت خواهد بود.

```
rows loaded: 12
first row: p-001 | Desk Lamp | 19.99
name holding a comma: Cable, 3-pack
price came back as type: str -> you must convert it yourself

--- 12 rows: same 12 rows, four formats ---
format   bytes
csv     1050
json    2101
ndjson  1774
pickle  1321

--- round trip: load each file back ---
csv     12 rows | first id p-001
json    12 rows | first id p-001
ndjson  12 rows | first id p-001
pickle  12 rows | first id p-001

--- average load time over 200 runs (ms) ---
format   load_ms
csv     0.1867
json    0.1471
ndjson  0.1706
pickle  0.1060

smallest file: csv (1050 bytes)
fastest load:  pickle (0.1060 ms)
csv/json size ratio: 2.00

generated 10000 fake profiles
first profile: u-00001 | Umar Brown | umar.brown@gmail.com

--- 10000 profiles: same 10000 rows, four formats ---
format   bytes
csv     1170270
json    2975033
ndjson  2330282
pickle  1200456

--- round trip: load each file back ---
csv     10000 rows | first id u-00001
json    10000 rows | first id u-00001
ndjson  10000 rows | first id u-00001
pickle  10000 rows | first id u-00001

--- average load time over 200 runs (ms) ---
format   load_ms
csv     48.2418
json    42.7324
ndjson  63.6525
pickle  19.2290

smallest file: csv (1170270 bytes)
fastest load:  pickle (19.2290 ms)
csv/json size ratio: 2.54

--- log tailing with flush() (flush every 1 lines) ---
lines written: 3
  2026-05-04 12:00:00 INFO  server started
  2026-05-04 12:00:01 INFO  crawler indexed document #1
  2026-05-04 12:00:02 INFO  crawler indexed document #2
  2026-05-04 12:00:03 INFO  crawler indexed document #3
```

برای بررسی مستقل بایت‌ها:

```
python -c "import os; print([os.path.getsize('workshop/out/records.'+e) for e in ['csv','json','ndjson','pkl']])"
```

```
[1050, 2101, 1774, 1321]
```

## اهداف تکمیلی (اختیاری)

فراتر از تحویل اصلی — فقط پس از اینکه جدولت با خروجی مورد انتظار یکی است.

* **انواع سالم می‌مانند (نکتهٔ Pickle).** `{"price": 19.99, "tags": ["new"]}` را به‌صورت هر چهار قالب ذخیره کن، هرکدام را برگردان و `type(...)` از `price` را چاپ کن. CSV و JSON با indent به ترتیب متن / عدد اعشاری واقعی می‌دهند؛ فقط Pickle `tags` را به‌صورت فهرست **و** عدد اعشاری برمی‌گرداند. سپس افزایش اندازه را توضیح بده.
* **`struct` با دست.** `struct.pack("!i f 8s", 7, 19.99, b"p-001")` دقیقاً ۱۶ بایت است. جفت `save_struct`/`load_struct` با ثابت `FORMAT = "!i f 8s"` بنویس و در برابر Pickle زمان‌گیری کن. (باید `"19.99"` را خودت به `float` تبدیل کنی؛ CSV به تو رشته داده.)
* **خواندن هر چهار فایل عرضه‌شده.** starter فقط `records.csv` را می‌خواند. حلقه‌ای اضافه کن که `records.json`، `records.ndjson` و `records.pkl` را از `workshop/data/` بارگذاری کند و مطمئن شود هر چهار همان ۱۲ ردیف را برمی‌گردانند.
* **دم واقعی.** `python workshop/starter/format_lab.py 200 1` را در یک ترمینال اجرا کن و در حین اجرا، `Get-Content workshop/out/app.log -Wait` (پاورشل) را در ترمینال دوم. دیدن ظاهر شدن خطوط همان نکتهٔ ایستگاه ۶ است.

## آزمون کار تو

`workshop/workshop_test.py` — ۱۱ تست، یکی برای هر TODO. پس از هر ایستگاه اجراش کن تا پیشرفتت را بررسی کنی:

```
python -m pytest workshop/workshop_test.py -v
```

انتظار: **۱۱ پاس** وقتی همهٔ TODOها کامل شده باشند. تست‌ها بررسی می‌کنند که هر تابع مطابق مشخصات رفتار می‌کند؛ قالب دقیق خروجی را بررسی نمی‌کنند.

## این کار به کجا می‌رسد

اکنون اسکریپت مقایسهٔ قالب با جدول نتایج، بنچمارک ۱۰٬۰۰۰ رکورد و حس انتخاب قابل‌قبول داری. **جلسهٔ سوم** ۲۰۴ سند مجموعه را با همان مهارت `open()` و پیمایش بارگذاری می‌کند و پویش خطی در برابر جست‌وجوی دیکشنری را اندازه‌گیری می‌کند؛ اولین دلیل واقعی که نمایه از بازخوانی فایل بهتر است. **جلسهٔ هفتم** `np.save` را برای ماتریس TF-IDF انتخاب می‌کند. **جلسهٔ یازدهم** نسبت فشرده‌سازی را با همان شیوه‌ای که اینجا قالب‌ها را اندازه‌گیری کردی می‌سنجد. **جلسهٔ نوزدهم** محصولات خزش‌شده را NDJSON می‌نویسد تا یک کرش یک خط تمام خزش را نکشد. و گزارشی که در ایستگاه ۶ تعقیب کردی الگویی است که گزارش‌نویسی خط لولهٔ جلسهٔ بیست‌و‌سوم از آن ساخته می‌شود.
