# کارگاه ۰۱: نخستین ابزار بازیابی اطلاعات، آمار فایل متنی (حدود ۴۵ دقیقه)

هر موتور جست‌وجویی که در عمرت ساخته می‌شود با یک کار ساده و humble آغاز می‌شود: باز کردن یک فایل متنی و پرسیدن این‌که «تویش چیست؟». گوگل این کار را روزی یک میلیارد بار انجام می‌دهد. تو امروز همین کار را دستی انجام می‌دهی، با چیزی جز `open()`، یک حلقه‌ی `for` و یک `dict`، و در پایان ابزاری به دست می‌آوری که می‌تواند هر فایلی را در پیکره‌ی ۲۰۴ سندی دوره زیر سؤال ببرد.

**آنچه با خود می‌بری:** یک `text_stats.py` کارآمد که برای هر فایل `.txt` تعداد خط، واژه و نویسه و پُرکاربردترین واژه‌ها را گزارش می‌کند، به‌همراه یک جست‌وجوی واژه، که بذرِ همه‌ی موتورهایی است که در ادامه می‌سازی.

تو فقط پایتون پایه را می‌دانی: متغیر، حلقه، تابع. هر چیز دیگری در ادامه توضیح داده می‌شود، با خط‌های واقعی فایل و شکل کد به‌صورت درون‌متنی. نیازی به گشتن میان فایل‌های دیگر نیست.

## راه‌اندازی (حدود ۵ دقیقه)
اول محیط مجازی دوره را فعال کن. راه‌اندازی یک‌باره در `README.md` اصلی آمده است. بعد هر دستور را از همین پوشه (`session-01-text-file-io/`) به شکل ساده‌ی `python` اجرا کن:

```
cd session-01-text-file-io
python workshop/starter/text_stats.py workshop/data/sample.txt
```

باید پیام `TODO-6 not done yet` را ببینی. اسکریپت اجرا می‌شود، راهنماها را چاپ می‌کند و چیزی خراب نمی‌شود. این شکستِ دوستانه عمدی است: هر TODO را یکی‌یکی خاموش می‌کنی.

## بیمارت را بشناس
`workshop/data/sample.txt`، متن ساده، ۳ خط، بدون هیچ چیز پنهان:

```
Search engines index text.
Search engines rank text.
Evaluation measures ranking quality.
```

این سه خط را نگه دار: هر عددی که در ۴۰ دقیقه‌ی آینده تولید کنی باید با دست قابل بررسی باشد.

## سفر

### ایستگاه ۱ — فایل را باز کن و همه‌چیز را بشمار (حدود ۱۵ دقیقه)
الان `count_stats()` حتی نمی‌تواند فایلی باز کند. بیا درستش کنیم. این مهارت پراستفاده‌ترین چیزی است که در کل این دوره یاد می‌گیری.

فراخوانی تازه، در یک خط: `open(path, mode="r", encoding="utf-8")`. یعنی حالت `mode="r"` برای خواندن و `encoding="utf-8"` تا متن روی همه‌ی دستگاه‌ها یکسان رمزگشایی شود. یک شیء فایل برمی‌گرداند که با `for line in f:` روی آن حرکت می‌کنی، یعنی یک خط در هر بار، پس حتی فایل‌های غول‌پیکر هم در حافظه جا می‌شوند.

فایل `workshop/starter/text_stats.py` را باز کن و **TODO-1 و TODO-2** را جایگزین کن:

```python
f = open(path, mode="r", encoding="utf-8")   # TODO-1
lines = 0                                    # TODO-2: three counters ...
words = 0
chars = 0
for line in f:                               # ... fed by one loop
    lines = lines + 1
    words = words + len(line.split())        # .split() cuts a line into words
    chars = chars + len(line)                # len(line) counts the newline too
f.close()
return {"lines": lines, "words": words, "chars": chars}
```

نقطه‌ی کنترل، دوباره اجرا کن:

```
python workshop/starter/text_stats.py workshop/data/sample.txt
```

حالا به جای شکایت درباره‌ی TODO-1، شکایت درباره‌ی TODO-3 را می‌بینی. پیشرفتی که دیده می‌شود. (مسیر فایل خالی: اگر قطعه‌ی بالا را در یک `my_stats.py` خالی بنویسی و یک `print(...)` اضافه کنی، خروجی `{'lines': 3, 'words': 12, 'chars': 90}` است. با دست چک کن: ۳ خط، ۴ به‌علاوه‌ی ۴ به‌علاوه‌ی ۴ واژه، درست است.)

*آنچه همین حالا آموختی: باز کردن فایل، پیمایش خط‌به‌خط، و شمردن با متغیرهای ساده.*

### ایستگاه ۲ — واژه‌ها را بشمار و یک برنده انتخاب کن (حدود ۱۵ دقیقه)
شمردن خوب است، رتبه‌بندی یعنی جست‌وجو. حالا `top_words()` یاد می‌گیرد کدام واژه‌ها بر یک فایل مسلط‌اند، همان غریزه‌ای که پشت TF-IDF در نشست ۷ است. همان ۳ خط نمونه ورودی توست.

ایده‌ی تازه، در یک خط: یک `dict` برای شمارش. یعنی `counts[word] = counts.get(word, 0) + 1` یعنی یکی به شمارنده اضافه کن، از صفر شروع کن اگر تازه است.

**TODO-3 و TODO-4** را جایگزین کن:

```python
counts = {}                                  # TODO-3: the tally
f = open(path, mode="r", encoding="utf-8")
for line in f:
    for raw in line.lower().split():         # lowercase FIRST ...
        word = raw.strip(".,!?;:\"'()")      # ... then peel punctuation
        if word == "":
            continue
        if word in counts:
            counts[word] = counts[word] + 1
        else:
            counts[word] = 1
f.close()
ordered = sorted(counts, key=counts.get, reverse=True)  # TODO-4: best first
result = []
for word in ordered[:n]:                     # keep the first n
    result.append((word, counts[word]))
return result
```

تابع `.strip(".,!?;:\"'()")` این نویسه‌ها را از دو سر واژه می‌کند، پس `"text."` به `"text"` تبدیل می‌شود. تابع `sorted()` با `key=counts.get` واژه‌ها را بر اساس شمارنده‌شان مرتب می‌کند، بزرگ‌ترین اول. بدون `Counter` و بدون میان‌بر، فقط حلقه و دیکشنری.

نقطه‌ی کنترل: استارتر حالا به TODO-5 می‌رسد. (مسیر فایل خالی: فایل در حال رشد تو حالا آمار را به‌همراه `[('search', 2), ('engines', 2), ('text', 2), ('index', 1), ('rank', 1)]` چاپ می‌کند.)

*آنچه همین حالا آموختی: یکسان‌سازی متن، یعنی کوچک کردن حروف، سپس کندن نقطه‌گذاری و بعد شکستن به واژه، پیش از شمردن، و مرتب کردن دیکشنری از بهترین به ضعیف‌ترین با `sorted()`.*

### ایستگاه ۳ — واژه‌ها را پیدا کن، همه‌چیز را به هم وصل کن، به پیکره‌ی واقعی نشانه بگیر (حدود ۱۰ دقیقه)
تابعی که کسی صدایش نزند فقط یک یادداشت شخصی است. دو کار مانده: جست‌وجوی پیدا کردن واژه (**TODO-5**) و همان `main()` که گزارش را چاپ می‌کند (**TODO-6**).

قطعه‌ی پیدا کردن، همان آزمون `if ... in ...` است که بذرِ هر موتور جست‌وجویی است:

```python
hits = []
f = open(path, mode="r", encoding="utf-8")
for line in f:
    if word in line:              # keep what matches, skip the rest
        hits.append(line.strip())
f.close()
return hits
```

خروجی واقعی روی فایل نمونه، کپی‌شده از یک اجرای واقعی:

```
['Evaluation measures ranking quality.']
```

بعد سرِ هم‌بندی. فراخوانی تازه، در یک خط: `sys.argv`، یعنی فهرست واژه‌هایی که پس از `python` تایپ کرده‌ای، پس `sys.argv[1]` نام فایل است و `sys.argv[2]` اگر داده شود برابر N است:

```python
path = args[0]
if len(args) > 1:
    n = int(args[1])
else:
    n = 10
stats = count_stats(path)
print("file: " + str(path))
print("lines: " + str(stats["lines"]))
print("words: " + str(stats["words"]))
print("chars: " + str(stats["chars"]))
print("top-" + str(n) + " words:")
for pair in top_words(path, n):
    print("  " + pair[0] + ": " + str(pair[1]))
```

حالا پاداش نهایی، اول روی نمونه‌ای که از حفظ بلدی، بعد روی یک سند واقعی از پیکره:

```
python workshop/starter/text_stats.py workshop/data/sample.txt 5
python workshop/starter/text_stats.py ../datasets/corpus/doc-001.txt 5
```

خروجی تو باید با بخش **Expected output** پایین، حرف‌به‌حرف یکی باشد. اگر چنین بود، با دست بر اساس همان ۳ خط چک کن: ۳ خط، ۱۲ واژه، و «search» با ۲. کدی که با دست راست آزمایی شده، قابل اعتماد است.

*آنچه همین حالا آموختی: نگه داشتن خط‌های منطبق با `if word in line`، و تبدیل توابع به یک ابزار خط فرمان با `sys.argv`.*

## خروجی مورد انتظار
خروجی دقیق راه‌حل درست، از همین پوشه:

```
file: workshop/data/sample.txt
lines: 3
words: 12
chars: 90
top-5 words:
  search: 2
  engines: 2
  text: 2
  index: 1
  rank: 1
```

و روی یک سند واقعی از پیکره:

```
file: ../datasets/corpus/doc-001.txt
lines: 3
words: 40
chars: 271
top-5 words:
  the: 5
  with: 4
  director: 3
  framed: 3
  every: 3
```

## اهداف کش‌دادنی (اختیاری)
- رمزگذاری‌های گوناگون را با مهربانی پیش ببر: اول UTF-8 را امتحان کن، به `errors="replace"` برگرد، و گزارش بده کدام فایل‌ها به این راه نیاز داشتند، در کل `../../datasets/corpus/`.
- آمار کل پیکره: هر ۲۰۴ فایل را یکی‌یکی باز کن، با همان حلقه، و پرتکرارترین واژه‌ی کل را چاپ کن.

## راه‌حل
پوشه‌ی `workshop/solution/`. اول سفر را خودت برو. بررسی سلامت، که باید قبول شود:

```
python -m pytest workshop/solution/ -v
```

انتظار: `3 passed`.

## این کار به کجا می‌رسد
چراغ‌قوه‌ای را ساختی که در نشست‌های بعدی برای بازرسی متن به کار می‌آید. نشست ۳ همین مهارتِ باز کردن و پیمایش را نشانه می‌گیرد تا در فایل‌ها جست‌وجو کند، نشست ۵ آن‌ها را توکن‌بندی می‌کند و نمایه‌ی معکوس می‌سازد، و نشست ۱۸ با همین مهارت صفحه‌های وب را تجزیه می‌کند. فایل داخل، تطبیق بیرون. این نیمی از خط لوله‌ای است که تا پایان دوره می‌سازی.