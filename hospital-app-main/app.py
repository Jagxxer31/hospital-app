from flask import Flask, render_template, request, redirect, url_for,flash
from models import D, Admin, Slot, P_his, P, session,Comp
from datetime import date, timedelta

r = request
rt = render_template

app = Flask(__name__)
app.secret_key = "Sonicdash"

def check_login(model, u, pa):
    return session.query(model).filter_by(name=u, passw=pa).first()

def checkAvFor7days():
    today = date.today()
    nxt = [today + timedelta(days=i) for i in range(7)]
    dids = [d[0] for d in session.query(D.id).all()]

    for did in dids:
        for d in nxt:
            for t in ["AN", "FN"]:
                ex = session.query(Slot).filter_by(d_id=did, date=d, time=t).first()
                if not ex:
                    doc = session.query(D).filter_by(id=did).first()
                    session.add(Slot(d_id=did, dept=doc.dept, date=d, time=t, status="free"))

    session.commit()

checkAvFor7days()

@app.route('/', methods = ["GET","POST"])
def login():
    if r.method == "GET":
        return rt("login.html")
    
    elif r.method == "POST":
        u = r.form.get("uname")
        pa = r.form.get("password")

        admin = check_login(Admin, u, pa)
        if admin:
            return redirect(url_for("addash", aname=u))

        patient = check_login(P, u, pa)
        if patient:
            print("hi")
            return redirect(url_for("patdash", pname=u))

        doctor = check_login(D, u, pa)
        if doctor:
            return redirect(url_for("docdash", dname=u))
        
        flash("Invalid Username or Password", "danger")
        return redirect("/")

@app.route('/register', methods = ["GET","POST"])
def register():
    if r.method == "GET":
        return rt("register.html")
    
    elif r.method == "POST":
        u = r.form["uname"]
        pa = r.form["password"]

        existing = session.query(P).filter_by(name=u).first()
        if existing:
            flash("Username already taken. Try another name.", "warning")
            return redirect("/register")
        
        us = P(name=u,passw=pa)
        session.add(us)
        session.commit()

        flash("Registered, now you can login", "info")
        return redirect("/")

@app.route('/doc/<dname>', methods = ["GET","POST"])
def docdash(dname):
    did = session.query(D.id).filter(D.name == dname).first()
    did = did[0]
    a = session.query(Slot).filter_by(d_id=did, status="booked").all()
    return rt("docdash.html", appts = a, did=did, dname = dname)

@app.route("/updAv/<int:di>")
def updAv(di):
    slots = session.query(Slot).filter_by(d_id=di).order_by(Slot.date, Slot.time).all()

    grouped = {}
    for s in slots:
        if s.date not in grouped:
            grouped[s.date] = {"AN": None, "FN": None}
        grouped[s.date][s.time] = s

    doc = session.query(D).filter_by(id=di).first()
    return render_template("editdocAv.html", avData=grouped, d=doc)


@app.route("/toggle/<int:di>/<string:day>/<string:slot>")
def toggle(di, day, slot):
    d = date.fromisoformat(day)
    s = session.query(Slot).filter_by(d_id=di, date=d, time=slot).first()
    if s:
        if s.status == "free":
            s.status = "off"
        elif s.status == "off":
            s.status = "free"
        session.commit()
    return redirect(f"/updAv/{di}")


@app.route("/makeAppnt/<int:di>/<pname>", methods=["GET","POST"])
def makeAppnt(di, pname):
    checkAvFor7days()  
    slots = session.query(Slot).filter_by(d_id=di).order_by(Slot.date, Slot.time).all()

    avData = {}
    for s in slots:
        if s.date not in avData:
            avData[s.date] = {"AN": None, "FN": None}
        avData[s.date][s.time] = s

    doc = session.query(D).filter_by(id=di).first()
    return render_template("docAv.html", avData=avData, d=doc, pname=pname)



@app.route("/mtoggle/<int:di>/<string:day>/<string:slot>/<pname>")
def mtoggle(di, day, slot, pname):
    d = date.fromisoformat(day)
    s = session.query(Slot).filter_by(d_id=di, date=d, time=slot).first()
    if not s:
        return redirect("/")

    if s.status == "free":
        p = session.query(P).filter_by(name=pname).first()
        s.status = "booked"
        s.p_id = p.id
    elif s.status == "booked":
        s.status = "free"
        s.p_id = None

    session.commit()
    doc = session.query(D).filter_by(id=di).first()
    return redirect(f"/dept/{doc.dept}/{pname}")

@app.route("/docAv/<int:di>")
def docAv(di):
    slots = session.query(Slot).filter_by(d_id=di).order_by(Slot.date, Slot.time).all()

    grouped = {}
    for s in slots:
        if s.date not in grouped:
            grouped[s.date] = {"AN": None, "FN": None}
        grouped[s.date][s.time] = s

    doc = session.query(D).filter_by(id=di).first()
    return render_template("docAvV.html", avData=grouped, d=doc)

@app.route('/pHistUpd/<p_id>/<d_id>', methods = ["GET","POST"])
def pHistUpd(p_id,d_id):
    dname = session.query(D.name).filter_by(id = d_id).first()
    if r.method == "GET":
        return rt("patHistUpd.html", pid = p_id, did = d_id)
    else:
        tests = r.form["tests"]
        diag = r.form["diag"]
        pres = r.form["pres"]
        meds = r.form["meds"]
        his = P_his(date=date.today(),
                    p_id=p_id,
                    d_id= d_id,
                    test=tests,
                    diag=diag,
                    presc=pres,
                    meds=meds)
        session.add(his)
        session.commit()
        return redirect(f"/doc/{dname[0]}")

@app.route('/pAppntComp/<id>', methods = ["GET","POST"])
def pAppntComp(id):
    s = session.query(Slot).filter_by(id=id).first()
    l = 50
    if s:
        comp = Comp(
            d_id=s.d_id,
            p_id=s.p_id,
            dept=s.dept,
            date=s.date,
            time=s.time,
            status="Done"
        )
        session.add(comp)
        session.commit()

        excess = session.query(Comp).order_by(Comp.id.asc()).all()
        if len(excess) > l:
            to_delete = excess[:len(excess) - l]
            for row in to_delete:
                session.delete(row)
            session.commit()

        s.status = "free"
        s.p_id = None
        session.commit()
    return redirect(request.referrer or request.url)

@app.route('/pAppntCancel/<id>', methods = ["GET","POST"])
def pAppntCancel(id):
    s = session.query(Slot).filter_by(id=id).first()
    l = 50
    if s:
        comp = Comp(
            d_id=s.d_id,
            p_id=s.p_id,
            dept=s.dept,
            date=s.date,
            time=s.time,
            status="Cancelled"
        )
        session.add(comp)
        session.commit()

        excess = session.query(Comp).order_by(Comp.id.asc()).all()
        if len(excess) > l:
            to_delete = excess[:len(excess) - l]
            for row in to_delete:
                session.delete(row)
            session.commit()

        s.status = "free"
        s.p_id = None
        session.commit()
    return redirect(request.referrer or request.url)


@app.route('/pat/<pname>', methods = ["GET","POST"])
def patdash(pname):
    de = session.query(D.dept).distinct().all()
    pid = session.query(P.id).filter(P.name == pname).first()
    a = session.query(Slot).filter_by(p_id=pid[0], status="booked").all() if pid else []
    return rt("patdash.html", depts=de, appts=a, p=pname)

@app.route('/pat/appntdel/<pname>/<int:aid>', methods = ["GET","POST"])
def appntdel(pname,aid):
    s = session.query(Slot).filter_by(id=aid).first()
    if s:
        s.status = "free"
        s.p_id = None
        session.commit()

    return redirect(url_for("patdash", pname=pname))

@app.route('/adm', methods = ["GET","POST"])
def addash():
    if r.method == "GET":
        a = session.query(Slot).filter_by(status="booked").all()
        c = session.query(Comp).all()
        p = session.query(P).all()
        d = session.query(D).all()
        return rt("addash.html",appts = a,docs =d,pats = p, comp = c)
    else:
        u = r.form["st"]

        doctor = session.query(D).filter(D.name==u).first()
        if doctor:
            return redirect(url_for("docinfo", d=u))

        dept = session.query(D.dept).filter(D.dept == u).first()
        print(dept)
        if dept:
            docs = session.query(D).filter(D.dept == dept[0]).all()
            return rt("dept.html", dept = dept[0], docs = docs)

        patient = session.query(P).filter(P.name==u).first()
        if patient:
            return redirect(url_for("pHist", pname=u))
        
        return redirect(url_for("addash"))

@app.route('/newpat', methods = ["GET","POST"])
def newpat():
    if r.method == "GET":
        return rt("newpat.html")
    
    elif r.method == "POST":
        u = r.form["name"]
        pa = r.form["passw"]

        existing = session.query(P).filter_by(name=u).first()
        if existing:
            flash("Patient already registered. Try another name.", "warning")
            return redirect("/newpat")
        
        p = P(name=u,passw=pa)
        session.add(p)
        session.commit()
        checkAvFor7days()

        return redirect(url_for("addash"))

@app.route('/newdoc', methods = ["GET","POST"])
def newdoc():
    if r.method == "GET":
        return rt("newdoc.html")
    
    elif r.method == "POST":
        u = r.form["name"]
        pa = r.form["passw"]
        e = r.form['exp']
        dept = r.form["dept"]
        dscr = r.form["dscr"]

        existing = session.query(D).filter_by(name=u).first()
        if existing:
            flash("Doctor already registered. Try another name.", "warning")
            return redirect("/newdoc")
        
        d = D(name=u,passw=pa,exp=e,dept=dept,dscr=dscr)
        session.add(d)
        session.commit()
        checkAvFor7days()

        return redirect(url_for("addash"))
    
@app.route('/editdoc/<id>', methods = ["GET","POST"])
def editdoc(id):
    if r.method == "GET":
        doc = session.query(D).filter(D.id==id).first()
        return rt("editdoc.html",d=doc)
    
    elif r.method == "POST":
        u = r.form["name"]
        pa = r.form["passw"]
        e = r.form['exp']
        dept = r.form["dept"]
        
        d = session.query(D).filter_by(id=id).first()
        if d:
            d.name = u
            d.dept = dept
            d.exp = e
            d.passw = pa
            session.commit()

        return redirect(url_for("addash"))

@app.route('/deldoc/<id>', methods = ["GET","POST"])
def deldoc(id):
    session.query(D).filter(D.id==id).delete()
    slots = session.query(Slot).filter_by(d_id=id).all()
    for s in slots:
        session.delete(s)
    session.query(P_his).filter(P_his.d_id == id).delete()
    session.commit()
    return redirect("/adm")

@app.route("/atoggle/<int:di>/<string:day>/<string:slot>")
def atoggle(di, day, slot):
    return 

@app.route('/pdel/<pname>', methods = ["GET","POST"])
def pdel(pname):
    id = session.query(P.id).filter_by(name=pname).first()
    session.query(P).filter(P.name==pname).delete()
    session.query(Slot).filter(Slot.p_id == id[0]).delete()
    session.commit()
    return redirect("/adm")

@app.route('/doc/info/<d>', methods = ["GET","POST"])
def docinfo(d):
    doc = session.query(D).filter(D.name == d).all()
    return rt("docinfo.html", d=doc[0])

@app.route('/pHist/<pname>', methods = ["GET","POST"])
def pHist(pname):
    pid = session.query(P.id).filter(P.name == pname).first()
    h = session.query(P_his).filter(P_his.p_id == pid[0]).all()
    
    return rt("patHist.html",hist=h,p=pname)

@app.route('/dept/<deptname>/<pname>', methods = ["GET","POST"])
def deptdets(deptname,pname):
    docs = session.query(D).filter(D.dept == deptname).all()

    return rt("dept.html", dept = deptname, docs = docs,pname = pname)

if __name__ =='__main__':
    app.debug = True
    app.run()