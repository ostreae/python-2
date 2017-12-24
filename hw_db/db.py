# Нужно посчитать и визуализировать на графике все глоссы.
# Нужно подсчитать, каких из этих глосс в базе больше:
# лучше подсчитать число падежей отдельно, число частей речи -- отдельно.
# Отдельный график для падежей, отдельный график для частей речи и т. д.

import sqlite3
import re
import matplotlib.pyplot as plt

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
                  ''', (pure_glosses[i], i + 1))

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
            glosses = [n]
            c.execute('SELECT id FROM Glosses WHERE Abbreviation = ?', glosses)
            a = c.fetchall()
            if a:
                c.execute('INSERT INTO words_glosses (id_word, id_gloss) VALUES (?, ?)',
                          (i[0], a[0][0]))
    return c


def graph():
    c.execute("SELECT id_gloss FROM words_glosses")
    num = c.fetchall()
    id_num = {}

    for n in num:
        if n[0] in id_num:
            id_num[n[0]] += 1
        else:
            id_num[n[0]] = 1

    c.execute("SELECT id, Abbreviation FROM glosses")
    glosses = c.fetchall()
    gl = []
    n = []

    for g in glosses:
        for i in id_num:
            if g[0] == i:
                gl.append(g[1])
                n.append(id_num[i])

    plt.bar(gl, n)
    plt.title("All glosses")
    plt.xlabel("Glosses")
    plt.ylabel("Number of glosses")
    plt.show()

    case = ['ACC', 'DAT', 'INSTR', 'LOC', 'DAT-LOC' 'NOM', 'ABL', 'VOC']
    case_gl = []
    case_num = []

    pos = ['ADJ', 'ADV', 'AUX', 'COMP', 'CONJ', 'DEM', 'INDEF', 'N', 'NEG', 'P', 'PART',
           'POSS', 'PRON', 'PRV', 'PTCP', 'REL', 'V']
    pos_gl = []
    pos_num = []

    person = ['1PL', '1SG', '2PL', '2SG', '3PL', '3SG']
    person_gl = []
    person_num = []

    for k, gloss in enumerate(gl):
        for cs in case:
            if cs == gloss:
                case_gl.append(cs)
                case_num.append(n[k])
        for p in pos:
            if p == gloss:
                pos_gl.append(p)
                pos_num.append(n[k])
        for per in person:
            if per == gloss:
                person_gl.append(per)
                person_num.append(n[k])

    plt.bar(case_gl, case_num)
    plt.title("Case")
    plt.xlabel("Glosses")
    plt.ylabel("Number of glosses")
    plt.show()

    plt.bar(pos_gl, pos_num)
    plt.title("Part of speech")
    plt.xlabel("Glosses")
    plt.ylabel("Number of glosses")
    plt.show()

    plt.bar(person_gl, person_num)
    plt.title("Person and number")
    plt.xlabel("Glosses")
    plt.ylabel("Number of glosses")
    plt.show()

    return c


def main():
    table_words()
    table_glosses()
    table_words_glosses()
    conn.commit()
    conn.close()
    graph()


if __name__ == '__main__':
    main()
