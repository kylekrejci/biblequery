import sqlite3
from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import SubmitField, SelectField, validators

app = Flask(__name__)
app.config.from_pyfile('config.py')
csrf = CSRFProtect(app)

biblebooks = [("GEN", "Genesis"), ("EXO", "Exodus"), ("LEV", "Leviticus"), ("NUM", "Numbers"), ("DEU", "Deuteronomy"),
              ("JOS", "Joshua"), ("JDG", "Judges"), ("RUT", "Ruth"), ("1SA", "1 Samuel"), ("2SA", "2 Samuel"),
              ("1KI", "1 Kings"), ("2KI", "2 Kings"), ("1CH", "1 Chronicles"), ("2CH", "2 Chronicles"), ("EZR", "Ezra"),
              ("NEH", "Nehemiah"), ("EST", "Esther"), ("JOB", "Job"), ("PSA", "Psalms"), ("PRO", "Proverbs"),
              ("ECC", "Ecclesiastes"), ("SNG", "Song of Solomon"), ("ISA", "Isaiah"), ("JER", "Jeremiah"),
              ("LAM", "Lamentations"), ("EZK", "Ezekiel"), ("DAN", "Daniel"), ("HOS", "Hosea"), ("JOL", "Joel"),
              ("AMO", "Amos"), ("OBA", "Obadiah"), ("JON", "Jonah"), ("MIC", "Micah"), ("NAM", "Nahum"),
              ("HAB", "Habakkuk"), ("ZEP", "Zephaniah"), ("HAG", "Haggai"), ("ZEC", "Zechariah"), ("MAL", "Malachi"),
              ("MAT", "Matthew"), ("MRK", "Mark"), ("LUK", "Luke"), ("JHN", "John"), ("ACT", "Acts"), ("ROM", "Romans"),
              ("1CO", "1 Corinthians"), ("2CO", "2 Corinthians"), ("GAL", "Galatians"), ("EPH", "Ephesians"),
              ("PHP", "Philipians"), ("COL", "Colossians"), ("1TH", "1 Thessalonians"), ("2TH", "2 Thessalonians"),
              ("1TI", "1 Timothy"), ("2TI", "2 Timothy"), ("TIT", "Titus"), ("PHM", "Philemon"), ("HEB", "Hebrews"),
              ("JAS", "James"), ("1PE", "1 Peter"), ("2PE", "2 Peter"), ("1JN", "1 John"), ("2JN", "2 John"),
              ("3JN", "3 John"), ("JUD", "Jude"), ("REV", "Revelation"), ("1ES", "1 Esdras"), ("2ES", "2 Esdras"),
              ("TOB", "Tobit"), ("JDT", "Judith"), ("ESG", "Additions to Esther"), ("WIS", "Wisdom of Solomon"),
              ("BAR", "Baruch"), ("SIR", "Sirach"), ("LJE", "Letter of Jeremiah"), ("S3Y", "Prayer of Azariah"),
              ("DAG", "Additions to Daniel"), ("SUS", "Susanna"), ("BEL", "Bel and the Dragon"),
              ("MAN", "Prayer of Manasseh"), ("1MA", "1 Maccabees"), ("2MA", "2 Maccabees"), ("3MA", "3 Maccabees"),
              ("4MA", "4 Maccabees"), ("PSS", "Psalms of Solomon"), ("PS2", "Psalm 151")]

class Biblequery(FlaskForm):
    language = SelectField("Language:", [validators.DataRequired()], id='language')
    title = SelectField("Title:", [validators.DataRequired()], id='title')
    book = SelectField("Book:", [validators.DataRequired()], id='book')
    chapter = SelectField("Chapter:", [validators.DataRequired()], id='chapter')
    startverse = SelectField("Starting Verse:", [validators.DataRequired()], id='startverse')
    endverse = SelectField("Ending Verse:", [validators.DataRequired()], id='endverse')
    submit = SubmitField("Submit")

# class Reset(FlaskForm):
#     resetbutton = SubmitField("Reset")

globallang = ""
globalbibleid = ""
globalbook = ""
globalchapter = 0
range0 = 0
range1 = 0

@app.route("/", methods=["GET", "POST"])
def index():
    global range0, range1
    form = Biblequery()
    conn = sqlite3.connect('bible.sqlite')
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT language_english from version;')
    languagechoices = cursor.fetchall()
    languagechoicesarray = ["",]
    for i in languagechoices:
        j = i[0]
        languagechoicesarray.append(j)
    form.language.choices = languagechoicesarray
    conn.close()
    if request.method == "POST":
        range0 = request.form['startverse']
        range1 = int(request.form['endverse']) + 1
        return redirect(url_for('results'))
    return render_template("index.html", form=form)

@app.route("/language/<lang>")
def language(lang):
    global globallang
    globallang = lang
    conn = sqlite3.connect('bible.sqlite')
    cursor = conn.cursor()
    cursor.execute('SELECT id, english_title from version where language_english=(?);', (lang, ))
    titlequery = cursor.fetchall()
    titlearray = [{'ident': '', 'english_title': ''} ]
    for i in titlequery:
        j = {}
        j['ident'] = i[0]
        j['english_title'] = i[1]
        titlearray.append(j)
    conn.close()
    return jsonify({'titlesofbibles': titlearray})

@app.route("/book/<bibleid>")
def titleofbible(bibleid):
    global globalbibleid
    globalbibleid = bibleid
    conn = sqlite3.connect('bible.sqlite')
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT book from verse where version_id=(?);', (bibleid, ))
    bookquery = cursor.fetchall()
    bookarray = ["", ]
    for i in bookquery:
        j = i[0]
        bookarray.append(j)
    conn.close()
    return jsonify({'books': bookarray})

@app.route("/chapter/<book>")
def chapter(book):
    global globalbook, globalbibleid
    globalbook = book
    conn = sqlite3.connect('bible.sqlite')
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT chapter FROM verse WHERE book=(?) AND version_id=(?);', (book, globalbibleid))
    chapters = cursor.fetchall()
    chapterarray = ["", ]
    for i in chapters:
        j = i[0]
        chapterarray.append(j)
    conn.close()
    return (jsonify({'chapters': chapterarray}), book)

@app.route("/startverse/<chapter>")
def startverse(chapter):
    global globalbook, globalchapter, globalbibleid
    globalchapter = chapter
    conn = sqlite3.connect('bible.sqlite')
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT start_verse FROM verse WHERE book=(?) AND chapter=(?) AND version_id=(?);', (globalbook, chapter, globalbibleid))
    verses = cursor.fetchall()
    sversesarray = ["", ]
    for i in verses:
        j = i[0]
        sversesarray.append(j)
    conn.close()
    return jsonify({'startverses': sversesarray}), chapter

@app.route("/endverse/<chapter>")
def endverse(chapter):
    conn = sqlite3.connect('bible.sqlite')
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT end_verse FROM verse WHERE book=(?) AND chapter=(?) AND version_id=(?);', (globalbook, chapter, globalbibleid))
    verses = cursor.fetchall()
    eversesarray = ["", ]
    for i in verses:
        j = i[0]
        eversesarray.append(j)
    conn.close()
    return jsonify({'endverses': eversesarray})

@app.route("/results", methods=["GET", "POST"])
def results():
    global range1, range0, globalchapter, globalbook, globalbibleid
    verselist = range(int(range0), int(range1))
    conn = sqlite3.connect('bible.sqlite')
    cursor = conn.cursor()
    cursor.execute('SELECT text FROM verse WHERE version_id=(?) AND book=(?) AND chapter=(?) AND start_verse BETWEEN (?) and (?);', (globalbibleid, globalbook, globalchapter, range0, range1))
    resulttext = cursor.fetchall()
    resultarray0 = []
    resultarray1 = []
    resultarray2 = ["", ]
    p = ""
    for i in resulttext:
        j = i[0]
        resultarray0.append(j)
    resultarray1 = list(zip(verselist, resultarray0))
    for m in resultarray1:
        n = str(m)[1:-1]
        resultarray2.append(n)
    for o in biblebooks:
        if o[0] == globalbook:
            p = o[1]
    conn.close()
    return render_template("results.html", result1=resultarray2, globalbook1=p, globalchapter1=globalchapter)

if __name__ == '__main__':
    app.run()

