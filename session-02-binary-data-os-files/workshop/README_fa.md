# کارگاه ۰۲: آزمایشگاه چهار قالب روی یک مجموعه‌داده (حدود ۴۵ دقیقه)

نشست ۱ یاد داد چطور یک فایل متنی را *بخوانی*. امروز تصمیم می‌گیری آن را چطور *ذخیره* کنی، و می‌بینی سریع‌ترین قالب، کوچک‌ترین قالب نیست. همین غافلگیری کل درس است: هر قالب چیزی را از دست می‌دهد، و کار یک مهندس کارآورد این است که بداند کدام از دست دادن را می‌تواند تحمل کند. خزنده‌ای که ۱۲۰۰۰ رکورد محصول می‌نویسد باید انتخاب کند؛ پایگاه‌داده‌ی برداری که در نشست ۱۲ ماتریس تعبیه (embedding) می‌نویسد هم همین‌طور؛ و تو هم، حدود چهل دقیقه دیگر.

**آنچه با خود می‌بری:** یک `format_lab.py` که همان ۱۲ رکورد را به CSV، JSON، NDJSON و pickle می‌نویسد، ثابت می‌کند هر چهار قالب یکسان برمی‌گردند، زمان هر بارگذاری را می‌گیرد، یک **جدول نتایج** چاپ می‌کند، و لاگی می‌نویسد که یک `tail -f` می‌تواند زنده دنبالش کند، به‌علاوه‌ی یک فایل تست با ۶ TODO که هر عدد را سر جایش قفل می‌کند.

پایتون پایه را می‌دانی، یعنی متغیر، حلقه و تابع، و `open()` و حلقه‌های `for` نشست ۱ را. هر چیز تازه در ادامه درون‌متنی توضیح داده می‌شود، همراه با خط‌های نمونه و شکل کدی که لازم داری. هیچ گشتنی میان فایل‌ها لازم نیست.

## راه‌اندازی (حدود ۳ دقیقه)

اول محیط مجازی دوره را فعال کن. راه‌اندازی یک‌باره در `README.md` اصلی آمده است. بعد همه‌چیز را از همین پوشه (`session-02-binary-data-os-files/`) با `python` ساده اجرا کن:

```
cd session-02-binary-data-os-files
python workshop/starter/format_lab.py
```

باید ببینی:

```
TODO-1 not done yet - read the CSV with csv.DictReader
(6 TODOs total - open starter/format_lab.py and work top to bottom.)
```

هیچ‌چیز خراب نشد و هیچ‌چیزی هم پاک نشد. آن شکستِ دوستانه عمدی است. یکی‌یکی TODOها را خاموش می‌کنی.

## بیمارت را بشناسیم
`workshop/data/records.csv`، با ۱۲ سطر و دو نکته که اهمیت دارند:

```
id,name,price,category,description
p-001,Desk Lamp,19.99,lighting,"Warm LED desk lamp, brushed steel, 3-year warranty"
...
p-012,"Cable, 3-pack",11.00,electronics,"Three braided cables, 1m each, mixed lengths, spare"
```

سطر دوازدهم یک **ویرگول درون نام** دارد، آن هم داخل گیومه. همان یک نویسه دلیل آن است که از ماژول `csv` استفاده می‌کنیم و نه `line.split(",")` که به جای ۵ فیلد، ۶ فیلد به تو می‌داد. هر عددی که در ادامه می‌بینی با دست در همین فایل قابل بررسی است.

همه‌ی خروجی‌ها به `workshop/out/` می‌روند. استارتر این پوشه را با `os.makedirs(OUT_DIR, exist_ok=True)` می‌سازد، و `exist_ok=True` یعنی «اگر از قبل هست، شکایت نکن».

## سفر

### ایستگاه ۱ — CSV را بدون شکستن روی ویرگول بخوانیم (حدود ۱۲ دقیقه)

هنوز هیچ‌چیز کار نمی‌کند: `load_csv()` پیش از آن‌که چیزی را باز کند، خطا می‌دهد. این همان مهارتی است که کل نشست رویش ایستاده.

فراخوانی‌های تازه، هر کدام یک خط. `csv.DictReader(f)` روی یک شیء فایل CSV حرکت می‌کند و برای هر سطر یک `dict` به تو می‌دهد، با کلیدهایی برابر خط سرآیند، پس به جای `row[0]` می‌نویسی `row["price"]`. مقدار `newline=""` در `open()` یعنی «پایان‌خط‌ها را ترجمه نکن». مستندات csv همین را می‌خواهند، و همین باعث می‌شود شمارش بایت‌ها روی ویندوز و لینوکس یکسان بماند.

فایل `workshop/starter/format_lab.py` را باز کن و **TODO-1** را جایگزین کن:

```python
rows = []                                  # our growing list of rows
f = open(path, mode="r", encoding="utf-8", newline="")
reader = csv.DictReader(f)                 # one dict per row, keyed by header
for row in reader:                         # iterate rows, not lines
    rows.append(row)                       # keep it
f.close()                                  # let go of the handle
return rows                                # hand the list back
```

نقطه‌ی کنترل، دوباره استارتر را اجرا کن:

```
python workshop/starter/format_lab.py
```

```
TODO-2 not done yet - write the CSV with csv.DictWriter
(6 TODOs total - open starter/format_lab.py and work top to bottom.)
```

پیشرفتی که می‌بینی. (مسیر فایل خالی: قطعه‌ی بالا را در یک `my_lab.py` خالی بنویس، چهار خط `print` پایین `main()` را اضافه کن، و دقیقاً همین را می‌بینی: ۱۲ سطر، `Cable, 3-pack` سالم، و `price` با نوع `str`.)

*آنچه همین حالا آموختی: `csv.DictReader` یک سرآیند به‌علاوه‌ی چند خط را به دیکشنری تبدیل می‌کند، و گیومه‌گذاری همان چیزی است که ویرگولِ درون مقدارها را بی‌خطر می‌کند.*

### ایستگاه ۲ — همان سطرها را به سه شکل متنی بنویسیم (حدود ۱۲ دقیقه)

خواندن نیمی از کار است. حالا نوشتن: CSV بیرون، JSON خوش‌ظاهر، و NDJSON.

فراخوانی‌های تازه، هر کدام یک خط. `csv.DictWriter(f, fieldnames=FIELDS)` یک شیء نویسنده می‌سازد، و `fieldnames=` همان **ترتیب ستون‌ها** است، پس آن فهرست اسکیمای توست. `writer.writeheader()` خط `id,name,...` را می‌نویسد. `json.dump(obj, f, indent=2)` یک شیء پایتون را در فایلی می‌نویسد که *خودت* باز کرده‌ای. مقادیر پرکاربرد `indent`: `2` یعنی خوانا و همان که ما استفاده می‌کنیم، `4` یعنی جادارتر، و `None` یعنی یک خط بلند و کوچک‌ترین فایل. `json.dumps(obj)` همان کار است، ولی به جای نوشتن در فایل، یک **رشته** برمی‌گرداند.

**TODO-2** مربوط به CSV و **TODO-3** مربوط به JSON را جایگزین کن:

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

بعد نوبت **TODO-4** برای NDJSON است: همان داده، ولی هر خط یک شیء.

```python
f = open(path, mode="w", encoding="utf-8", newline="")
for row in rows:
    f.write(json.dumps(row) + "\n")             # json.dumps -> a string
f.close()
return os.path.getsize(path)
```

نقطه‌ی کنترل، استارتر حالا به TODO-5 می‌رسد. (مسیر فایل خالی: آن سه تابع و یک حلقه را اضافه کن تا شمارش بایت‌های زیر به دست بیاید. چک دستی CSV: سرآیند ۴۰ بایت است و آن ۱۲ سطر هر مقدار دارای ویرگول را داخل `"` می‌گذارند.)

```
csv     1050
json    2101
ndjson  1774
```

دو عدد ارز دیدن دارند: JSON **۲٫۰۰ برابر** اندازه‌ی CSV است. خوش‌ظاهر کردن، به‌علاوه‌ی تکرار ۱۲ باره‌ی هر کلید، بیش از همه‌چیز دیگر هزینه دارد.

*آنچه همین حالا آموختی: CSV چیزی را تکرار نمی‌کند، JSON کلیدها را تکرار و تورفتگی می‌دهد، NDJSON کلیدها را تکرار می‌کند ولی پوشاننده را کنار می‌گذارد، و `os.path.getsize` هر فایلی را بدون خواندنش اندازه می‌گیرد.*

### ایستگاه ۳ — قالب دودویی را هم اضافه کنیم (حدود ۱۰ دقیقه)

حالا آن یکی که فرق دارد. pickle اشیای پایتون را مستقیم ذخیره می‌کند، پس نه قاعده‌ی گیومه‌گذاری در کار است، نه خطی برای اعلام اسکیما، نه تجزیه‌ای در راه برگشت.

فراخوانی تازه، یک خط: `open(path, mode="wb")` یعنی حالت **دودویی**. حرف `b` لازم است چون `pickle` مقدار `bytes` می‌نویسد و حالت متنی فقط `str` می‌پذیرد. مقادیر پرکاربرد: `"rb"` خواندن دودویی، `"wb"` نوشتن دودویی، `"ab"` افزودن دودویی. مقدار `protocol=pickle.HIGHEST_PROTOCOL` تازه‌ترین و سریع‌ترین رمزگذاری‌ای را انتخاب می‌کند که پایتون تو دارد؛ روی پایتون‌های امروزی ۵ است و هیچ دلیلی برای چیز دیگری نیست.

**TODO-5** را جایگزین کن:

```python
f = open(path, mode="wb")                      # "b" = binary, pickle requires it
pickle.dump(rows, f, protocol=pickle.HIGHEST_PROTOCOL)   # returns nothing
f.close()
return os.path.getsize(path)
```

نقطه‌ی کنترل، رفت و برگشت حالا برای هر چهار قالب اجرا می‌شود:

```
csv     1050
json    2101
ndjson  1774
pickle  1321
```

```
--- round trip: load each file back ---
csv     12 rows | first id p-001 | price type str
json    12 rows | first id p-001 | price type str
ndjson  12 rows | first id p-001 | price type str
pickle  12 rows | first id p-001 | price type str
```

هر چهار قالب ۱۲ سطر را با `p-001` در ابتدا برمی‌گردانند و `Cable, 3-pack` سالم می‌ماند. یک نکته‌ی صادقانه را هم ببین: `price` در *هر چهار* قالب یک `str` است، چون این سطرها از ابتدا از یک CSV آمده‌اند؛ pickle متن را همان‌طور که بود نگه داشت. اگر به `save_pickle` یک دیکشنری با یک `float` واقعی بدهی (بخش اهداف کش‌دادنی را ببین)، pickle تنها قالبی است که `float` برمی‌گرداند.

*آنچه همین حالا آموختی: pickle از JSON خوش‌ظاهر کوچک‌تر است و اسکیما نمی‌خواهد، ولی فقط نوع‌هایی را نگه می‌دارد که واقعاً به آن داده باشی.*

### ایستگاه ۴ — زمان بگیریم، بعد یک لاگ را flush کنیم (حدود ۸ دقیقه)

اندازه نیمی از مقایسه است و زمان نیم دیگر، و جواب همانی نیست که انتظارش را داری.

حلقه‌ی زمان‌گیری در `measure()` **به تو داده شده**؛ بخوانش، بازنویسیش نکن:

```python
load_any(path, fmt)                            # warm-up: page the bytes in
total = 0.0
for _ in range(repeats):                       # repeats = 200 by default
    start = time.perf_counter()                # a monotonic clock, in seconds
    load_any(path, fmt)
    total = total + (time.perf_counter() - start)
return total * 1000.0 / repeats                 # -> average milliseconds
```

آن فراخوانی اول که دور می‌اندازی تزئین نیست: نخستین بارگذاری هزینه‌ی پر شدن حافظه نهان صفحه‌ی سیستم‌عامل را می‌دهد، پس اگر بماند، قالبی که *اول* اجرا می‌شود بی‌دلیل کندترین به نظر می‌رسد. اجرایش کن:

```
python workshop/solution/format_lab.py 200 1
```

```
--- average load time over 200 runs (ms) ---
csv     0.1523
json    0.1336
ndjson  0.1393
pickle  0.0991
```

pickle سریع‌ترین بارگذاری و CSV کندترین را دارد، در حالی که CSV *کوچک‌ترین* فایل است. عددهای تو به این‌ها نزدیک می‌شوند ولی یکی نیستند؛ این زمان‌سنجی واقعی روی سخت‌افزار واقعی است و ادعای ما ترتیب است، نه رقم سوم اعشار.

حالا آخرین TODO، و دلیلِ وجود `flush()`. برنامه‌ی `tail -f app.log` روی ترمینال تو فقط خط‌هایی را می‌تواند نشان دهد که از بافر پایتون بیرون آمده‌اند، پس یک حلقه‌ی لاگ‌نویسی باید هر خط را همان لحظه که می‌نویسد، بیرون هل بدهد.

فراخوانی تازه، یک خط: `f.flush()` بافر را همین حالا به سیستم‌عامل می‌راند. `close()` هم flush می‌کند، ولی *بعد* از تمام شدن حلقه، و این همان هدف لاگ زنده را از بین می‌برد.

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

همان ترفند جلو بردن مُهر زمانی را `tail_log()` نشست ۲۳ هم لازم دارد.

نقطه‌ی کنترل، استارترِ تمام‌شده را اجرا کن:

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
fastest load:  pickle (0.0991 ms)
csv/json size ratio: 2.00
```

مهرهای زمانی دقیقاً هر خط یک ثانیه جلو رفتند: `00`، `01`، `02`، `03`. اگر مهر زمانی تکراری دیدی، خط `stamp = stamp[:-2] + ...` تو جا افتاده است.

*آنچه همین حالا آموختی: چطور زمان بارگذاری یک فایل را منصفانه بگیری، یعنی اول گرم کن و بعد میانگینِ چند اجرا را، و این‌که `flush()` چطور لاگ را پیش از پایان یافتن برنامه خواندنی می‌کند.*

## خروجی مورد انتظار

خروجی دقیق راه‌حل درست، کپی‌شده از یک اجرای واقعی در محیط مجازی روی `python workshop/solution/format_lab.py 200 1` از همین پوشه. هر چیزی بالای این خط روی هر ماشینی بایت‌به‌بایت یکسان است. چهار مقدار `load_ms` و خطِ «سریع‌ترین بارگذاری» زمان‌سنجی واقعی‌اند و کمی با دستگاه به دستگاه فرق می‌کنند.

```
rows loaded: 12
first row: p-001 | Desk Lamp | 19.99
name holding a comma: Cable, 3-pack
price came back as type: str -> you must convert it yourself

--- writing the same 12 rows in four formats ---
format   bytes
csv     1050
json    2101
ndjson  1774
pickle  1321

--- round trip: load each file back ---
csv     12 rows | first id p-001 | price type str
json    12 rows | first id p-001 | price type str
ndjson  12 rows | first id p-001 | price type str
pickle  12 rows | first id p-001 | price type str

--- average load time over 200 runs (ms) ---
format   load_ms
csv     0.1523
json    0.1336
ndjson  0.1393
pickle  0.0991

--- log tailing with flush() (flush every 1 lines) ---
lines written: 3
  2026-05-04 12:00:00 INFO  server started
  2026-05-04 12:00:01 INFO  crawler indexed document #1
  2026-05-04 12:00:02 INFO  crawler indexed document #2
  2026-05-04 12:00:03 INFO  crawler indexed document #3

smallest file: csv (1050 bytes)
fastest load:  pickle (0.0991 ms)
csv/json size ratio: 2.00
```

برای این‌که بایت‌های خودت را مستقل از اسکریپت راستی‌آزمایی کنی:

```
python -c "import os; print([os.path.getsize('workshop/out/records.'+e) for e in ['csv','json','ndjson','pkl']])"
```

```
[1050, 2101, 1774, 1321]
```

## اهداف کش‌دادنی (اختیاری)

روشن است که این‌ها بیرون از تحویل اصلی‌اند. فقط وقتی جدولت با خروجی مورد انتظار یکی شد سراغشان برو.

- **نوع‌ها زنده می‌مانند، که همان دلیل وجود pickle است.** مقدار `{"price": 19.99, "tags": ["new"]}` را در هر چهار قالب ذخیره کن، هر کدام را برگردان، و `type(...)` مربوط به `price` را چاپ کن. CSV متن برمی‌گرداند و JSON با تورفتگی یک float واقعی؛ فقط pickle است که `tags` را به شکل لیست *و* همان float را برمی‌گرداند. بعد توضیح بده چرا اندازه بزرگ‌تر شد.
- **`struct` با دست.** عبارت `struct.pack("!i f 8s", 7, 19.99, b"p-001")` دقیقاً ۱۶ بایت است. یک جفت `save_struct` و `load_struct` با ثابت `FORMAT = "!i f 8s"` بنویس و زمانش را در برابر pickle بسنج. (باید خودت `"19.99"` را به `float` تبدیل کنی، چون CSV رشته به تو داد.)
- **رمزگذاری‌های مقاوم.** هر ۲۰۴ فایل در `../../datasets/corpus/` را به شکل رکورد بارگذاری کن و دوباره ذخیره‌اش کن: `encoding="utf-8"` در همه‌جا، و برای هر فایلی که `UnicodeDecodeError` می‌دهد یک راه جایگزین بگذار تا یک بایت خراب نتواند کل اجرا را از کار بیندازد.
- **یک tail واقعی.** در یک ترمینال `python workshop/starter/format_lab.py 200 1` را اجرا کن و در فاصله‌ی اجرای آن، در ترمینال دوم `Get-Content workshop/out/app.log -Wait` را (پاورشل) بزن. تماشای ظاهر شدن خط‌ها یکی‌یکی، تمام دلیل ایستگاه ۴ است.

## راه‌حل
`workshop/solution/`؛ اول سفر را خودت برو، بعد مقایسه کن. بررسی سلامت که باید قبول شود:

```
python -m pytest workshop/solution/ -v
```

انتظار: **۹ تست پاس**. تست‌ها چهار شمارش بایت (۱۰۵۰ / ۲۱۰۱ / ۱۷۷۴ / ۱۳۲۱)، شمارش ۱۲ سطر، رفت و برگشتِ ویرگولِ درون نام، ترتیب سرآیند CSV، نوع `str` برای `price`، حفظ یک `float` و یک `list` واقعی توسط pickle، و خط‌های دقیق لاگ ایستگاه ۴ را قفل می‌کنند، شامل حالت `flush_every=2` که ۴ خط نوشته می‌شود ولی فقط ۲ بار flush انجام می‌گیرد.

## این کار به کجا می‌رسد

حالا یک اسکریپت مقایسه‌ی قالب با جدول نتایج داری، و حسی از این‌که کدام از دست دادن را می‌توانی تحمل کنی. **نشست ۳** پیکره‌ی ۲۰۴ سندی را با همان مهارتِ `open()` و پیمایش بارگذاری می‌کند و پیمایش خطی را در برابر جست‌وجوی dict می‌سنجد؛ نخستین دلیل واقعی برای برتری نمایه بر خواندن دوباره‌ی فایل. **نشست ۷** برای ماتریس TF-IDF سراغ `np.save` می‌رود، **نشست ۱۱** نسبت‌های فشرده‌سازی را همان‌طور می‌سنجد که اینجا قالب‌ها را سنجیدی، و **نشست ۱۹** محصولات خزیده‌شده را به شکل NDJSON می‌نویسد تا یک کرش به جای کل خزیدن، فقط یک خط از دستت بگیرد. آن لاگی هم که در ایستگاه ۴ دنبالش کردی، همان الگویی است که لاگ‌نویسی خط لوله‌ی نشست ۲۳ از آن ساخته می‌شود.