import sqlite3
from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import SubmitField, SelectField, validators

app = Flask(__name__)
app.config.from_pyfile('config.py')
csrf = CSRFProtect(app)

def get_db_connection():
    conn = sqlite3.connect('bible.sqlite')
    conn.row_factory = sqlite3.Row
    return conn

db = SQLAlchemy(app)

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

class Verse(db.Model):
    __tablename__ = 'verse'
    id = db.Column(db.Integer, primary_key=True)
    book = db.Column(db.String)
    chapter = db.Column(db.Integer)
    start_verse = db.Column(db.Integer)
    end_verse = db.Column(db.Integer)
    text = db.Column(db.String)

class Version(db.Model):
    __tablename__ = 'version'
    id = db.Column(db.String, primary_key=True)
    territory = db.Column(db.String)
    language = db.Column(db.String)
    language_english = db.Column(db.String)
    vernacular_title = db.Column(db.String)
    english_title = db.Column(db.String)

class Biblequery(FlaskForm):
    language = SelectField("Language:", [validators.DataRequired()], id='language')
    title = SelectField("Title:", [validators.DataRequired()], id='title')
    book = SelectField("Book:", [validators.DataRequired()], id='book')
    chapter = SelectField("Chapter:", [validators.DataRequired()], id='chapter')
    startverse = SelectField("Starting Verse:", [validators.DataRequired()], id='startverse')
    endverse = SelectField("Ending Verse:", [validators.DataRequired()], id='endverse')
    submit = SubmitField("Submit")

class Reset(FlaskForm):
    resetbutton = SubmitField("Reset")

globallanguage = ""
globaltitleid = ""
globalbook = ""
globalchapter = ""
range0 = 0
range1 = 0
verselist = []

@app.route("/", methods=["GET", "POST"])
def index():
    global range0, range1
    form = Biblequery()
    conn = get_db_connection()
    languagechoices = conn.execute('SELECT DISTINCT language_english from version;')
    languagechoices = languagechoices.fetchall()
    languagechoicesarray0 = []
    languagechoicesarray1 = [""]
    for i in languagechoices:
        j = dict(i)
        languagechoicesarray0.append(j)
    for k in languagechoicesarray0:
        for l in k.values():
            languagechoicesarray1.append(l)
    form.language.choices = languagechoicesarray1
    if request.method == "POST":
        range0 = request.form['startverse']
        range1 = int(request.form['endverse']) + 1
        return redirect(url_for('results'))
    conn.close()
    return render_template("index.html", form=form)

@app.route("/language/<lang>")
def language(lang):
    global globallanguage
    conn = get_db_connection()
    titlequery = conn.execute('SELECT id, english_title from version where language_english=(?);', (lang, ))
    titlequery = titlequery.fetchall()
    titlearray = [{'id': '', 'english_title': ''}]
    for i in titlequery:
        j = dict(i)
        titlearray.append(j)
    conn.close()
    return jsonify({'titlesofbibles': titlearray})

@app.route("/book/<bibleid>")
def titleofbible(bibleid):
    global globaltitleid
    globaltitleid = bibleid
    conn = get_db_connection()
    bookquery = conn.execute('SELECT DISTINCT book from verse where version_id=(?) ORDER BY canon_order;', (bibleid, ))
    bookquery = bookquery.fetchall()
    bookarray = [{'book': ''}]
    for i in bookquery:
        j = dict(i)
        bookarray.append(j)
    conn.close()
    return jsonify({'books': bookarray})

@app.route("/chapter/<book>")
def chapter(book):
    global globalbook, globaltitleid
    globalbook = book
    conn = get_db_connection()
    chapters = conn.execute('SELECT DISTINCT chapter FROM verse WHERE book=(?) AND version_id=(?);', (book, globaltitleid))
    chapters = chapters.fetchall()
    chapterarray = [{'chapter': ''}]
    for i in chapters:
        j = dict(i)
        chapterarray.append(j)
    conn.close()
    return jsonify({'chapters': chapterarray})

@app.route("/startverse/<chapter>")
def startverse(chapter):
    global globalchapter
    globalchapter = chapter
    conn = get_db_connection()
    verses = conn.execute('SELECT DISTINCT start_verse FROM verse WHERE book=(?) AND chapter=(?) AND version_id=(?);', (globalbook, chapter, globaltitleid))
    verses = verses.fetchall()
    sversesarray = [{'start_verse': ''}]
    for i in verses:
        j = dict(i)
        sversesarray.append(j)
    conn.close()
    return jsonify({'startverses': sversesarray})

@app.route("/endverse/<chapter>")
def endverse(chapter):
    conn = get_db_connection()
    verses = conn.execute('SELECT DISTINCT end_verse FROM verse WHERE book=(?) AND chapter=(?) AND version_id=(?);', (globalbook, chapter, globaltitleid))
    verses = verses.fetchall()
    eversesarray = [{'end_verse': ''}]
    for i in verses:
        j = dict(i)
        eversesarray.append(j)
    conn.close()
    return jsonify({'endverses': eversesarray})

@app.route("/results", methods=["GET", "POST"])
def results():
    global verselist
    verselist = range(int(range0), int(range1))
    conn = get_db_connection()
    resulttext = conn.execute('SELECT text FROM verse WHERE version_id=(?) AND book=(?) AND chapter=(?) AND start_verse BETWEEN (?) and (?);', (globaltitleid, globalbook, globalchapter, range0, range1))
    resulttext = resulttext.fetchall()
    resultarray0 = []
    resultarray1 = []
    resultarray2 = []
    resultarray3 = [""]
    for i in resulttext:
        j = dict(i)
        resultarray0.append(j)
    for k in resultarray0:
        for l in k.values():
            resultarray1.append(l)
    resultarray2 = list(zip(verselist, resultarray1))
    for m in resultarray2:
        n = str(m)[1:-1]
        resultarray3.append(n)
    for o in biblebooks:
        if o[0] == globalbook:
            p = o[1]
    conn.close()
    return render_template("results.html", result=resultarray3, globalbook=p, globalchapter=globalchapter)

if __name__ == '__main__':
    app.run()

