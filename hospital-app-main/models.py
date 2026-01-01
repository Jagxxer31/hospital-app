import sqlalchemy
from datetime import date, datetime
from sqlalchemy import Column, Integer, String, Date, ForeignKey, create_engine
from sqlalchemy.orm import relationship, declarative_base, sessionmaker

Base = declarative_base()

class Admin(Base):
    __tablename__ = 'admins'
    id = Column(Integer,autoincrement=True,primary_key=True)
    name = Column(String)
    passw = Column(String)

a = Admin(name="Jag", passw="Sonicdash")

class D(Base):
    __tablename__ = 'd'
    id = Column(Integer,autoincrement=True,primary_key=True)
    name = Column(String, nullable=False)
    passw = Column(String, nullable=False)
    dept = Column(String)
    exp = Column(Integer)
    dscr = Column(String)
    pic = Column(String)

d1 = D(name="Dr. Ramesh", dept="Cardiology", exp=15, passw="1", dscr="Senior cardiologist specialized in heart failure.")
d2 = D(name="Dr. Siresh", dept="Ophthalmology", exp=10, passw="12", dscr="Eye care specialist with expertise in cataract surgery.")
d3 = D(name="Dr. Ganesh", dept="Gynecology", exp=5, passw="123", dscr="Focuses on prenatal care and women's health.")
d4 = D(name="Dr. Kavitha", dept="Neurology", exp=12, passw="234", dscr="Brain and nerve specialist with 12+ years experience.")
d5 = D(name="Dr. Arvind", dept="Dermatology", exp=8, passw="345", dscr="Expert in skin allergies and cosmetic treatments.")


class P(Base):
    __tablename__ = 'p'
    id = Column(Integer,autoincrement=True,primary_key=True)
    name = Column(String)
    passw = Column(String)

p1 = P(name="Arun Kumar", passw="1")
p2 = P(name="Varun Kumar", passw="12")
p3 = P(name="Karun Kumar", passw="123")
p4 = P(name="Sahana Devi", passw="234")
p5 = P(name="Raghav Rao", passw="345")


class Slot(Base):
    __tablename__ = 'slot'
    id = Column(Integer,autoincrement=True,primary_key=True)
    d_id = Column(Integer, ForeignKey('d.id'))
    p_id = Column(Integer, ForeignKey('p.id'), nullable=True)
    dept = Column(String)
    date = Column(Date)
    time = Column(String)
    status = Column(String, default="free")
    d = relationship("D")
    p = relationship("P")

s1 = Slot(d_id=2, dept="Ophthalmology", date=date(2025, 12, 1), time="AN", status="booked", p_id=1)
s2 = Slot(d_id=1, dept="Cardiology", date=date(2025, 12, 2), time="FN", status="booked", p_id=3)
s3 = Slot(d_id=4, dept="Neurology", date=date(2025, 12, 3), time="AN", status="free", p_id=None)
s4 = Slot(d_id=5, dept="Dermatology", date=date(2025, 12, 4), time="FN", status="booked", p_id=5)
s5 = Slot(d_id=3, dept="Gynecology", date=date(2025, 12, 5), time="AN", status="free", p_id=None)

class Comp(Base):
    __tablename__ = 'comp'
    id = Column(Integer,autoincrement=True,primary_key=True)
    d_id = Column(Integer, ForeignKey('d.id'))
    p_id = Column(Integer, ForeignKey('p.id'), nullable=True)
    dept = Column(String)
    date = Column(Date)
    time = Column(String)
    status = Column(String, default="free")
    d = relationship("D")
    p = relationship("P")

class P_his(Base):
    __tablename__ = 'p_his'
    id = Column(Integer,autoincrement=True,primary_key=True)
    date = Column(Date)
    p_id = Column(Integer, ForeignKey('p.id'))
    d_id = Column(Integer, ForeignKey('d.id'))
    test = Column(String)
    diag = Column(String)
    presc = Column(String)
    meds = Column(String)
    d = relationship("D")
    p = relationship("P")

h1 = P_his(date=date(2025, 4, 10), p_id=1, d_id=2, test="Vision Test", diag="Short-sightedness", presc="Corrective lenses", meds="None")
h2 = P_his(date=date(2025, 5, 21), p_id=3, d_id=1, test="ECG", diag="Minor arrhythmia", presc="Lifestyle changes", meds="None")
h3 = P_his(date=date(2025, 6, 15), p_id=4, d_id=4, test="MRI", diag="Normal", presc="None", meds="None")
h4 = P_his(date=date(2025, 7, 3), p_id=2, d_id=3, test="Ultrasound", diag="No issues", presc="Routine checkup advised", meds="None")
h5 = P_his(date=date(2025, 8, 19), p_id=5, d_id=5, test="Skin Allergy Test", diag="Dust allergy", presc="Antihistamines", meds="Cetirizine")


engine = create_engine('sqlite:///hospital.db', echo=False)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

'''
#If you just want to add the admin
session.add_all([a])
session.commit()
print(" Data inserted successfully!")

'''

'''
#If you also want example entries for all tables
session.add_all([d1,d2,d3,d4,d5,p1,p2,p3,p4,p5,a,s1,s2,s3,s4,s5,h1,h2,h3,h4,h5])
session.commit()
print(" Data inserted successfully!")

'''

