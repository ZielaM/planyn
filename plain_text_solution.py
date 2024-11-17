import json

PLAIN_TEXT_SOLUTION: dict[str, str] = dict()

with open('./JSON/plain_text.json', 'r', encoding='utf-8') as f:
    PLAIN_TEXT: dict[str, dict[str, dict[str, str]]] = json.load(f)

for grade in PLAIN_TEXT:
    for day in PLAIN_TEXT[grade]:
        for lesson in PLAIN_TEXT[grade][day]:
            if PLAIN_TEXT_SOLUTION.get(PLAIN_TEXT[grade][day][lesson]) is not None:
                continue
            print(f'{grade}/{day}/{lesson}: {PLAIN_TEXT[grade][day][lesson]}: ', end='')
            w=input()
            PLAIN_TEXT_SOLUTION[PLAIN_TEXT[grade][day][lesson]] = w if w != '' else None
            print()
with open('./JSON/plain_text_solution.json', 'w', encoding='utf-8') as f:
    json.dump(PLAIN_TEXT_SOLUTION, f, ensure_ascii=False, indent=4)