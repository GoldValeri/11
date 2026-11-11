"""
Лабораторная работа № 11. Вариант 6.

Алгоритмы поиска подстроки и вычисления редакционного расстояния.

Параметры варианта 6 (табл. 1):
  - образец для π: ababaca
  - тип текста: естественный
  - длины n: 10⁴; 5·10⁴
  - порог сходства: 0,80
  - доп. Л6: блокирование кандидатов (первая буква / близкая длина)

Дисциплина: Основы алгоритмизации и программирование
Студент: Голдаева Валерия Валентиновна, группа БИ 2-1
"""

import random
import re
import time
from typing import List, Tuple

# ===========================================================================
# 1. ПОИСК ПОДСТРОКИ
# ===========================================================================

def prefix_function(pattern: str) -> List[int]:
    """
    Префикс-функция π[i] — длина наибольшего собственного префикса
    P[0..i], совпадающего с его суффиксом.
    """
    pi = [0] * len(pattern)
    k = 0
    for i in range(1, len(pattern)):
        while k > 0 and pattern[i] != pattern[k]:
            k = pi[k - 1]                 # откат по уже посчитанному π
        if pattern[i] == pattern[k]:
            k += 1
        pi[i] = k
    return pi


def naive_search(text: str, pattern: str) -> Tuple[List[int], int]:
    """Наивный поиск. Возвращает (позиции, число сравнений символов)."""
    n, m = len(text), len(pattern)
    positions, comparisons = [], 0
    for i in range(n - m + 1):
        j = 0
        while j < m:
            comparisons += 1
            if text[i + j] != pattern[j]:
                break
            j += 1
        if j == m:
            positions.append(i)
    return positions, comparisons


def kmp_search(text: str, pattern: str) -> Tuple[List[int], int]:
    """Алгоритм Кнута — Морриса — Пратта. Θ(n + m)."""
    n, m = len(text), len(pattern)
    pi = prefix_function(pattern)
    positions, comparisons = [], 0
    k = 0
    for i in range(n):
        while k > 0 and text[i] != pattern[k]:
            comparisons += 1
            k = pi[k - 1]
        comparisons += 1
        if text[i] == pattern[k]:
            k += 1
        if k == m:
            positions.append(i - m + 1)
            k = pi[k - 1]
    return positions, comparisons


# ===========================================================================
# 2. РАССТОЯНИЕ ЛЕВЕНШТЕЙНА
# ===========================================================================

def levenshtein(a: str, b: str) -> int:
    """Расстояние Левенштейна. Θ(nm) времени, Θ(min(n,m)) памяти."""
    if len(a) < len(b):
        a, b = b, a
    previous = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        current = [i]
        for j, cb in enumerate(b, start=1):
            # удаление / вставка / замена (или совпадение)
            current.append(min(
                previous[j] + 1,
                current[j - 1] + 1,
                previous[j - 1] + (ca != cb),
            ))
        previous = current
    return previous[-1]


def similarity(a: str, b: str) -> float:
    """Нормированная мера сходства ∈ [0; 1]."""
    if not a and not b:
        return 1.0
    return 1.0 - levenshtein(a, b) / max(len(a), len(b))


# ===========================================================================
# 3. СОПОСТАВЛЕНИЕ ЗАПИСЕЙ + Л6 (БЛОКИРОВАНИЕ)
# ===========================================================================

LEGAL_FORMS = {'ооо', 'оао', 'зао', 'пао', 'ао', 'ип', 'нко'}


def normalize(name: str) -> str:
    """Нормализация: регистр, ё→е, пунктуация, орг.-правовые формы."""
    s = name.lower().replace('ё', 'е')
    s = re.sub(r'[\"\'«»„“”.,()\-–—]', ' ', s)
    words = [w for w in s.split() if w not in LEGAL_FORMS]
    return ' '.join(words)


def match_records(list_a, list_b, threshold=0.8, blocking=False):
    """
    Сопоставление двух списков.
    blocking=True (Л6): сравниваем только если совпадает первая буква
    нормализованной строки ИЛИ длины отличаются не более чем на 3.
    Возвращает (результаты, число_сравнений_нечётких).
    """
    norm_b = [(b, normalize(b)) for b in list_b]
    result = []
    comparisons = 0
    for a in list_a:
        na = normalize(a)
        best, best_sim, kind = None, 0.0, ''
        for b, nb in norm_b:
            # Л6: блокирование кандидатов
            if blocking:
                if not na or not nb:
                    continue
                same_first = na[0] == nb[0]
                close_len = abs(len(na) - len(nb)) <= 3
                if not (same_first or close_len):
                    continue
            if na == nb:
                best, best_sim, kind = b, 1.0, 'точное'
                break
            comparisons += 1
            s = similarity(na, nb)
            if s > best_sim:
                best, best_sim, kind = b, s, 'нечёткое'
        if best_sim >= threshold:
            result.append((a, best, best_sim, kind))
        else:
            result.append((a, None, best_sim, 'не найдено'))
    return result, comparisons


# ===========================================================================
# 4. ЕСТЕСТВЕННЫЙ ТЕКСТ
# ===========================================================================

WORDS = (
    'алгоритм поиск строка текст данные система запись контрагент '
    'нормализация расстояние сходство образец префикс функция проект '
    'документ отчёт анализ процесс структура метод таблица график'
).split()


def natural_text(n: int, seed: int = 42) -> str:
    """Псевдо-естественный текст из слов предметной области."""
    rng = random.Random(seed)
    parts = []
    while sum(len(p) + 1 for p in parts) < n + 50:
        parts.append(rng.choice(WORDS))
    return ' '.join(parts)[:n]


# ===========================================================================
# 5. ЗАПУСК
# ===========================================================================

PATTERN = 'ababaca'


def demo_prefix() -> None:
    print('=' * 70)
    print('Префикс-функция для «ababaca»')
    print('=' * 70)
    pi = prefix_function(PATTERN)
    print(f'π = {pi}')
    print('Ручной расчёт: a→0, ab→0, aba→1, abab→2, ababa→3, ababac→0, ababaca→1')
    print()


def run_search() -> None:
    print('=' * 70)
    print('Сравнение наивного поиска и КМП')
    print('=' * 70)
    print(f"{'n':>8}{'текст':>12}{'наив., с':>10}{'КМП, с':>10}"
          f"{'сравн. наив.':>14}{'сравн. КМП':>12}")
    for n in [10**4, 5 * 10**4]:
        # естественный
        text = natural_text(n)
        text = text[:80] + PATTERN + text[80:400] + PATTERN + text[400:]
        text = text[:n]
        t0 = time.perf_counter(); _, c1 = naive_search(text, PATTERN); tn = time.perf_counter() - t0
        t0 = time.perf_counter(); p2, c2 = kmp_search(text, PATTERN); tk = time.perf_counter() - t0
        print(f'{n:8d}{"естеств.":>12}{tn:10.4f}{tk:10.4f}{c1:14d}{c2:12d}')
        # с повторами (контраст)
        text2 = 'a' * n
        p_bad = 'a' * 6 + 'b'
        t0 = time.perf_counter(); _, c1 = naive_search(text2, p_bad); tn = time.perf_counter() - t0
        t0 = time.perf_counter(); _, c2 = kmp_search(text2, p_bad); tk = time.perf_counter() - t0
        print(f'{n:8d}{"повторы":>12}{tn:10.4f}{tk:10.4f}{c1:14d}{c2:12d}')
    print()


def run_levenshtein() -> None:
    print('=' * 70)
    print('Расстояние Левенштейна')
    print('=' * 70)
    pairs = [('кот', 'скот'), ('Ромашка', 'Ромашки'), ('аналитика', 'аналитик'),
             ('ababaca', 'ababac')]
    for a, b in pairs:
        d = levenshtein(a, b)
        print(f"  d('{a}', '{b}') = {d}, сходство {similarity(a, b):.3f}")
    print()


def run_matching() -> None:
    print('=' * 70)
    print('Сопоставление контрагентов (порог 0,80)')
    print('=' * 70)
    system_a = [
        'ООО "Ромашка"',
        'АО Василёк',
        'ИП Иванов И.И.',
        'ООО "Северный ветер"',
        'ПАО Гранит',
        'ООО Альфа-Строй',
        'ЗАО Бета',
    ]
    system_b = [
        'Ромашка, ООО',
        'ВАСИЛЕК АО',
        'Иванов Иван Иванович',
        'Северный Ветер ООО',
        'Гранит-Строй ПАО',
        'Альфа Строй ООО',
        'Бета ЗАО',
    ]
    # без блокирования
    res, cmp_full = match_records(system_a, system_b, 0.80, blocking=False)
    print('Без блокирования:')
    for a, b, s, kind in res:
        target = b if b else '—'
        print(f'  {a:<24} → {target:<24} {s:.3f} ({kind})')
    print(f'  Нечётких сравнений: {cmp_full}')

    # Л6 с блокированием
    res2, cmp_block = match_records(system_a, system_b, 0.80, blocking=True)
    print('\nС блокированием (Л6):')
    for a, b, s, kind in res2:
        target = b if b else '—'
        print(f'  {a:<24} → {target:<24} {s:.3f} ({kind})')
    print(f'  Нечётких сравнений: {cmp_block}')
    if cmp_full:
        print(f'  Сокращение сравнений: {(1 - cmp_block / cmp_full) * 100:.1f} %')
    print()


if __name__ == '__main__':
    demo_prefix()
    run_search()
    run_levenshtein()
    run_matching()
