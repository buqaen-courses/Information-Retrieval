# Scenario brief — "shop search" for a small online store

You have just been hired as the search engineer for **Northwind Outdoor**, a
small online shop. The site is the bundled static store in `setup/mock_shop/`
(128 product pages, four listing pages, four categories). It runs offline, on
your laptop, and it is the only site this project is allowed to crawl.

The shop manager has written down eight things the search box must do. They are
in the numbered block at the bottom of this file. Your job today is **not** to
build the engine — that is Sessions 5 through 23. Your job is to decide **which
box of the IR architecture each requirement belongs in**, and to prove that your
vocabulary about search is grounded in real documents rather than vibes.

## What the manager says

> "People search us by typing words they can see. They also type words we never
> wrote. And they never scroll past the first screen, so whatever ends up at the
> top is the whole product."

## Why the numbers matter

Every requirement below is answered by exactly one box of the architecture
diagram in `images/04-01-ir-architecture.png`. Eight requirements, eight boxes:
`CRAWL`, `PARSE`, `DEDUPE`, `INDEX`, `EMBED`, `QUERY`, `RANK`, `EVALUATE`. If
your annotation leaves a box empty, either the requirement list is wrong or your
mapping is — check both before moving on.

The words people type are not the words the catalogue contains. Our own corpus
shows the gap: a shopper who types `rover` finds nothing, because no document
in `datasets/corpus/` contains the word `rover` — they all say `rovers`. That
single fact is why the `EMBED` box exists, and why `STEMMING` in Session 5 exists.

## Requirements

R1 | Fetch all 128 product pages from the bundled mock shop, one page per second.
R2 | Pull the name, price and description out of each HTML page.
R3 | Eight products repeat almost the same description; do not show the shopper ten copies.
R4 | Shoppers type exact product words, so keep a term dictionary of every word.
R5 | A shopper searching "soccer" should still find the football boots.
R6 | One search box per page, and the "under 100" filter must be applied.
R7 | Show the ten most relevant products first, ordered by score.
R8 | Log every click so we can measure whether the new ordering helped.