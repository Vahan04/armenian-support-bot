"""Create the reviewed sample bookstore data and multilingual JSONL benchmark."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STORE = ROOT / "data" / "sample_store"
QUESTIONS = ROOT / "eval" / "questions.jsonl"

products = [
    ("p001", "The Little Prince", "Antoine de Saint-Exupery", 4500, True, "A poetic classic about friendship and seeing beyond appearances."),
    ("p002", "1984", "George Orwell", 5200, True, "A dystopian novel about surveillance, language, and power."),
    ("p003", "Harry Potter and the Philosopher's Stone", "J. K. Rowling", 6800, False, "The first Hogwarts adventure of Harry Potter."),
    ("p004", "The Master and Margarita", "Mikhail Bulgakov", 6100, True, "A magical Russian classic about art, love, and freedom."),
    ("p005", "The Alchemist", "Paulo Coelho", 3900, True, "A philosophical journey about following a dream."),
    ("p006", "Pride and Prejudice", "Jane Austen", 4700, True, "A witty classic romance and social novel."),
    ("p007", "Sapiens", "Yuval Noah Harari", 8200, False, "A history of humankind from early societies to modern life."),
    ("p008", "Clean Code", "Robert C. Martin", 12500, True, "Practical principles for writing maintainable software."),
    ("p009", "Deep Work", "Cal Newport", 7600, True, "Strategies for focused work in a distracted world."),
    ("p010", "Atomic Habits", "James Clear", 7300, True, "A practical system for building good habits."),
    ("p011", "The Design of Everyday Things", "Don Norman", 9100, True, "How design communicates function and prevents errors."),
    ("p012", "Dune", "Frank Herbert", 8800, False, "An epic science-fiction story of politics, ecology, and destiny."),
    ("p013", "The Hobbit", "J. R. R. Tolkien", 5900, True, "Bilbo Baggins leaves home for an unexpected adventure."),
    ("p014", "To Kill a Mockingbird", "Harper Lee", 5400, True, "A coming-of-age story about justice and empathy."),
    ("p015", "Crime and Punishment", "Fyodor Dostoevsky", 5700, True, "A psychological novel about guilt, morality, and redemption."),
    ("p016", "Cosmos", "Carl Sagan", 9900, True, "A popular science journey through space, time, and humanity."),
    ("p017", "A Brief History of Time", "Stephen Hawking", 10500, False, "An accessible introduction to cosmology and black holes."),
    ("p018", "Introduction to Algorithms", "Thomas H. Cormen", 24000, True, "A comprehensive textbook on algorithms and data structures."),
    ("p019", "The Pragmatic Programmer", "David Thomas and Andrew Hunt", 14500, True, "Engineering habits for effective software development."),
    ("p020", "The Brothers Karamazov", "Fyodor Dostoevsky", 7200, True, "A philosophical family novel about faith, reason, and responsibility."),
    ("p021", "Thinking, Fast and Slow", "Daniel Kahneman", 8700, True, "A guide to two systems of human thinking."),
    ("p022", "Man's Search for Meaning", "Viktor Frankl", 4900, True, "Reflections on suffering, purpose, and resilience."),
    ("p023", "The Art of War", "Sun Tzu", 3500, True, "Classical strategic principles and leadership lessons."),
    ("p024", "Meditations", "Marcus Aurelius", 4300, True, "Stoic reflections on discipline and a good life."),
    ("p025", "The Selfish Gene", "Richard Dawkins", 9300, False, "An evolutionary view of genes, behavior, and cooperation."),
    ("p026", "The Republic", "Plato", 5100, True, "A philosophical dialogue about justice and the ideal state."),
    ("p027", "Guns, Germs, and Steel", "Jared Diamond", 8900, True, "An explanation of unequal development across societies."),
    ("p028", "The Name of the Rose", "Umberto Eco", 6400, True, "A historical mystery set in a medieval monastery."),
    ("p029", "Norwegian Wood", "Haruki Murakami", 5600, True, "A reflective novel about memory, love, and loss."),
    ("p030", "The Martian", "Andy Weir", 6200, True, "A stranded astronaut survives through engineering and science."),
]

faqs = [
    ("f001", "delivery", "Delivery is available in Yerevan for 1000 AMD. Orders over 15000 AMD receive free Yerevan delivery.", ["delivery in Yerevan", "1000 AMD", "free delivery over 15000 AMD"]),
    ("f002", "regional delivery", "Delivery outside Yerevan is available through HayPost. The customer pays the shipping fee.", ["outside Yerevan", "HayPost", "customer pays shipping"]),
    ("f003", "payment", "We accept cash on delivery and card payment through Idram.", ["cash on delivery", "card payment", "Idram"]),
    ("f004", "opening hours", "The store is open Monday to Saturday from 10:00 to 20:00. It is closed on Sunday.", ["Monday to Saturday", "10:00", "20:00", "closed on Sunday"]),
    ("f005", "address", "The bookstore is at 12 Abovyan Street, Yerevan.", ["12 Abovyan Street", "Yerevan"]),
    ("f006", "returns", "Unused books can be returned within 14 days with the receipt.", ["unused books", "14 days", "receipt"]),
    ("f007", "exchange", "We exchange damaged books within 7 days when the receipt is provided.", ["damaged books", "7 days", "receipt"]),
    ("f008", "gift wrapping", "Gift wrapping is available for 500 AMD per book.", ["gift wrapping", "500 AMD"]),
    ("f009", "reservations", "We can reserve an in-stock book for 48 hours. Please call the store.", ["in-stock book", "48 hours", "call the store"]),
    ("f010", "bulk orders", "For orders of more than 10 copies, contact us for a business quote.", ["more than 10 copies", "business quote"]),
    ("f011", "student discount", "We do not currently have a student discount.", ["no student discount"]),
    ("f012", "ebook", "We sell printed books only; ebooks are not available.", ["printed books only", "ebooks not available"]),
    ("f013", "contact", "For human support, call +374 10 555 555 during opening hours.", ["human support", "+374 10 555 555"]),
    ("f014", "preorders", "Preorders are not currently available.", ["preorders not available"]),
    ("f015", "lost receipt", "Returns require the original receipt; we cannot process a return without it.", ["original receipt", "no return without receipt"]),
]


def write_store() -> None:
    STORE.mkdir(parents=True, exist_ok=True)
    product_rows = [
        {"id": pid, "title": title, "author": author, "price_amd": price, "in_stock": stock, "description": description}
        for pid, title, author, price, stock, description in products
    ]
    faq_rows = [
        {"id": fid, "topic": topic, "answer": answer, "facts": facts}
        for fid, topic, answer, facts in faqs
    ]
    (STORE / "products.json").write_text(json.dumps(product_rows, ensure_ascii=False, indent=2), encoding="utf-8")
    (STORE / "faqs.json").write_text(json.dumps(faq_rows, ensure_ascii=False, indent=2), encoding="utf-8")


def make_row(base_id: str, form: str, text: str, facts: list[str], answerable: bool, document_ids: list[str]) -> dict:
    return {
        "id": f"{base_id}-{form}",
        "base_id": base_id,
        "form": form,
        "text": text,
        "expected_answer_facts": facts,
        "expected_document_ids": document_ids,
        "answerable": answerable,
        "needs_native_check": form in {"hy", "translit", "mixed"},
    }


def product_question(number: int, product: tuple, kind: str) -> list[dict]:
    pid, title, author, price, stock, _ = product
    stock_hy = "կա" if stock else "առկա չէ"
    stock_translit = "ka" if stock else "chka"
    stock_ru = "есть" if stock else "нет в наличии"
    if kind == "price":
        facts = [title, f"{price} AMD"]
        hy = f"«{title}»-ը ինչքա՞ն արժե։"
        ru = f"Сколько стоит «{title}»?"
        translit = f"«{title}»-y inchqan arje?"
        mixed = f"«{title}»-ը skolko стоит?"
    elif kind == "stock":
        facts = [title, "in stock" if stock else "out of stock"]
        hy = f"«{title}»-ը ունե՞ք, գիրքը {stock_hy}։"
        ru = f"У вас есть «{title}», книга {stock_ru}?"
        translit = f"«{title}»-y uneq, girqy {stock_translit}?"
        mixed = f"«{title}» есть, girqy {stock_translit}?"
    else:
        facts = [title, author]
        hy = f"«{title}»-ի հեղինակը ո՞վ է։"
        ru = f"Кто автор книги «{title}»?"
        translit = f"«{title}»-i heghinaky ov e?"
        mixed = f"«{title}»-i avtor@ ով է?"
    return [
        make_row(f"q{number:03}", "hy", hy, facts, True, [f"product:{pid}"]),
        make_row(f"q{number:03}", "ru", ru, facts, True, [f"product:{pid}"]),
        make_row(f"q{number:03}", "translit", translit, facts, True, [f"product:{pid}"]),
        make_row(f"q{number:03}", "mixed", mixed, facts, True, [f"product:{pid}"]),
    ]


def faq_question(number: int, faq: tuple) -> list[dict]:
    fid, topic, answer, facts = faq
    prompts = {
        "delivery": ("Երևանում առաքումն ինչքա՞ն է։", "Сколько стоит доставка в Ереване?", "Yerevani araqumn inchqan e?", "Yerevanum delivery inchqan e?"),
        "regional delivery": ("Երևանից դուրս առաքո՞ւմ եք։", "Есть доставка за пределы Еревана?", "Yerevanic durs araqum eq?", "Yerevanic durs delivery ka?"),
        "payment": ("Ինչպե՞ս կարող եմ վճարել։", "Как можно оплатить?", "Inchpes karox em vjarel?", "Inchpes mozhno оплатить?"),
        "opening hours": ("Որո՞նք են խանութի աշխատանքային ժամերը։", "Каковы часы работы магазина?", "Vorn en khanut i ashkhatankayin zhamery?", "Kakovy en khanut i jamery?"),
        "address": ("Որտե՞ղ է գտնվում խանութը։", "Где находится магазин?", "Vortegh e gtnvum khanuty?", "Gde e gtnvum khanuty?"),
        "returns": ("Ի՞նչ պայմաններով կարող եմ վերադարձնել գիրքը։", "Как вернуть книгу?", "Inch paymannerov karox em veradardznel girqy?", "Kak veradardnel girqy?"),
        "exchange": ("Կարո՞ղ եմ վնասված գիրքը փոխանակել։", "Можно обменять повреждённую книгу?", "Karogh em vnasvats girqy pokhanakel?", "Mozhno obmenyat vnasvats girqy?"),
        "gift wrapping": ("Նվերային փաթեթավորում ունե՞ք։", "Есть подарочная упаковка?", "Nverayin patetavorum uneq?", "Podarochnaya upakovka ka?"),
        "reservations": ("Կարո՞ղ եք գիրք պահել ինձ համար։", "Можно забронировать книгу?", "Karogh eq girq pahel indz hamar?", "Mozhno bronirovat girq?"),
        "bulk orders": ("Մեծաքանակ պատվերի համար զեղչ կա՞։", "Есть цена для большого заказа?", "Metz qanak patveri hamar gin ka?", "Bolshoy zakaz, gin ka?"),
        "student discount": ("Ուսանողական զեղչ ունե՞ք։", "Есть скидка для студентов?", "Usanoghakan zexch uneq?", "Studentskiy discount ka?"),
        "ebook": ("Էլեկտրոնային գրքեր վաճառո՞ւմ եք։", "Вы продаёте электронные книги?", "Elektronayin grqer vacharum eq?", "Elektronnye knigi vacharum eq?"),
        "contact": ("Ինչպե՞ս կապվել մարդու հետ։", "Как связаться с сотрудником?", "Inchpes kapvel mardu het?", "Kak kapvel ashkhatakci het?"),
        "preorders": ("Նախնական պատվերներ ընդունո՞ւմ եք։", "Вы принимаете предзаказы?", "Nakhakan patverner yndunum eq?", "Predzakazner yndunum eq?"),
        "lost receipt": ("Կարո՞ղ եմ վերադարձ անել առանց կտրոնի։", "Можно вернуть без чека?", "Karogh em veradardznel aranc ktroni?", "Mozhno veradardnel aranc cheki?"),
    }
    hy, ru, translit, mixed = prompts[topic]
    return [
        make_row(f"q{number:03}", "hy", hy, facts, True, [f"faq:{fid}"]),
        make_row(f"q{number:03}", "ru", ru, facts, True, [f"faq:{fid}"]),
        make_row(f"q{number:03}", "translit", translit, facts, True, [f"faq:{fid}"]),
        make_row(f"q{number:03}", "mixed", mixed, facts, True, [f"faq:{fid}"]),
    ]


def write_questions() -> None:
    rows: list[dict] = []
    kinds = ["price", "stock", "author"]
    for index, product in enumerate(products[:20], start=1):
        rows.extend(product_question(index, product, kinds[(index - 1) % len(kinds)]))
    for index, faq in enumerate(faqs[:12], start=21):
        rows.extend(faq_question(index, faq))
    unknowns = [
        ("q033", "Արդյո՞ք այս տարի գրքի փառատոնին մասնակցելու եք։", "Будете участвовать в книжном фестивале в этом году?", "Ays tari grqi festivalin masnakcelu eq?", "Knigi festivalin etot tari masnakcelu eq?"),
        ("q034", "Կարո՞ղ եք խորհուրդ տալ ամենահայտնի գիրքը։", "Какую самую популярную книгу вы советуете?", "Amenահայտni girqy xorhurd ktaq?", "Samuyu popularnuyu girqy xorhurd ktaq?"),
        ("q035", "Այս գիրքը քանի էջ ունի։", "Сколько страниц в этой книге?", "Ays girqy qani ej uni?", "Eta kniga qani ej uni?"),
        ("q036", "Ո՞ր գիրքն է հիմա ամենաշատը վաճառվում։", "Какая книга сейчас продаётся лучше всего?", "Vor girqn e hima amenamec@ vacharvum?", "Kakaya kniga hima lav e vacharvum?"),
        ("q037", "Կարո՞ղ եք նվիրել հեղինակային ստորագրությամբ գիրք։", "Можно купить книгу с автографом автора?", "Karogh eq girq tal heginaki storagrutyamb?", "Avtografov girq ka?"),
        ("q038", "Այսօր անձրև գալո՞ւ է։", "Будет ли сегодня дождь?", "Aysor andzrev galու e?", "Segodnya dozhd linelu e?"),
        ("q039", "Կարո՞ղ եք վերանորոգել իմ հին գիրքը։", "Вы ремонтируете старые книги?", "Veranorogum eq hin grqer?", "Starye knigi remont aneq?"),
        ("q040", "Աշխատակիցները քանի՞ լեզու գիտեն։", "Сколько языков знают сотрудники?", "Ashkhatakicnery qani lezv giten?", "Sotrudniki qani lezv giten?"),
    ]
    for base_id, hy, ru, translit, mixed in unknowns:
        for form, text in (("hy", hy), ("ru", ru), ("translit", translit), ("mixed", mixed)):
            rows.append(make_row(base_id, form, text, [], False, []))
    assert len(rows) == 160
    with QUESTIONS.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    write_store()
    write_questions()
