# Нужно посчитать и визуализировать на графике все глоссы.
# Нужно подсчитать, каких из этих глосс в базе больше:
# лучше подсчитать число падежей отдельно, число частей речи -- отдельно.
# Отдельный график для падежей, отдельный график для частей речи и т. д.

import sqlite3
import re
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

conn = sqlite3.connect('hittite.db')
c = conn.cursor()


def table_words():
    c.executescript('''DROP TABLE IF EXISTS words;
            CREATE TABLE IF NOT EXISTS words
            (id INTEGER PRIMARY KEY,
            Lemma TEXT,
            Wordform TEXT,
            Glosses TEXT);
            ''')

    c.execute('''INSERT INTO words (Lemma, Wordform)
            SELECT lemma, Wordform
            FROM wordforms;
            ''')

    c.execute('''SELECT Glosses FROM wordforms''')
    fetch_glosses = c.fetchall()
    glosses = []
    for i in fetch_glosses:
        for gloss in i:
            sg = gloss.split('.')
            glosses.append(' '.join(sg))

    pure_glosses = []

    for gloss in glosses:
        pure_glosses.append(re.sub("([^A-Z0-9— ]*)", '', gloss))
    pure_glosses = [i.strip('  ') if len(i) > 2 else '—' for i in pure_glosses]

    for i in range(0, len(pure_glosses)):
        c.execute('''UPDATE words
                  SET Glosses = ?
                  WHERE id = ?
                  ''', (pure_glosses[i], i+1))

    return c


def table_glosses():
    abbreviation = []
    meaning = []
    glosses = []
    with open('glossing_rules.txt', 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()
        for line in lines:
            glosses.append(line.split(' — '))
        for i in range(0, len(glosses) - 1):
            abbreviation.append(glosses[i][0])
            meaning.append(glosses[i][1])

    c.executescript('''DROP TABLE IF EXISTS glosses;
        CREATE TABLE IF NOT EXISTS glosses
        (id INTEGER PRIMARY KEY,
        Abbreviation TEXT,
        Meaning TEXT);
        ''')

    for i in range(1, len(abbreviation) + 1):
        c.execute('INSERT INTO glosses (Abbreviation, Meaning) VALUES (?, ?)',
                  [abbreviation[i - 1], meaning[i - 1]])
    return c


def table_words_glosses():
    c.executescript('''DROP TABLE IF EXISTS words_glosses;
        CREATE TABLE IF NOT EXISTS words_glosses
        (id_word INTEGER,
        id_gloss INTEGER);
        ''')

    c.execute('SELECT id, Glosses FROM words')
    word_glosses = c.fetchall()

    for i in word_glosses:
        gloss = i[1].split(' ')
        for n in gloss:
            glosses = []
            glosses.append(n)
            c.execute('SELECT id FROM Glosses WHERE Abbreviation = ?', (glosses))
            a = c.fetchall()
            if a:
                c.execute('INSERT INTO words_glosses (id_word, id_gloss) VALUES (?, ?)',
                              (i[0], a[0][0]))
    c.execute('DROP TABLE IF EXISTS wordforms')
    return c


def graph():
    return()


def main():
    table_words()
    table_glosses()
    table_words_glosses()
    conn.commit()
    conn.close()
    # graph()


if __name__ == '__main__':
    main()
