import random
from flask import Flask
from flask import request, render_template
import pickle
import numpy as np

from numpy.f2py.auxfuncs import throw_error

app = Flask(__name__,static_url_path='',
            static_folder='templates')

thetas_AC=[]
thetas_CE=[]
thetas_BC=[]
thetas_CD=[]

def predict_CE(xs):
    i = thetas_CE
    times = []
    for x in xs:
        times.append(i)
    return times

def predict_CD(xs):
    [i,a,b,c,d,e,f,m,a1,b1,c1,d1,e1,f1,m1]=thetas_CD
    times = []
    for x in xs:
        times.append(i+a1*((x-i)%m1)+b1 + float(c1)/(1+np.exp(min(25,-d1*np.abs(x-i-e1)+f1)))-(a*((x-i)%m)+b + float(c)/(1+np.exp(min(25,-d*np.abs(x-i-e)+f)))))
    return times

def predict_AC(xs):
    [i,a,b,c,d,e,f,m]=thetas_AC
    times = []
    for x in xs:
        times.append(a*(x%m)+b + float(c)/(1+np.exp(min(25,-d*np.abs(x-e)+f)))-i)
    return times

def predict_BC(xs):
    [i,a,b,c,d,e,f,m]=thetas_BC
    times = []
    for x in xs:
        times.append(a*(x%m)+b + float(c)/(1+np.exp(min(25,-d*np.abs(x-e)+f)))-i)
    return times

def get_best_road(time):
    msg=""
    road=""
    s=""
    earliest = 1440
    for i in range(time, 1030):
        if earliest > i + predict_AC([i])[0]:
            earliest = i + predict_AC([i])[0]
            if i!=time:
                msg="Wait {} minutes before leaving for A".format(i-time)
            s="A"
        if earliest > i + predict_BC([i])[0]:
            earliest = i + predict_BC([i])[0]
            if i!=time:
                msg="Wait {} minutes before leaving for B".format(i-time)
            s="B"
    time2 = int(np.ceil(earliest))
    road=s+"->C->"
    s=""
    earliest = 100000
    for i in range(time2, 1030+time2-time):
        if earliest > i + predict_CD([i])[0]:
            earliest = i + predict_CD([i])[0]
            if i!=time2:
                if msg!="":
                    msg=" and {} minutes in C".format(i-time2)
                else:
                    msg = "Wait {} minutes in C".format(i-time2)
            s = "D"
        if earliest > i + predict_CE([i])[0]:
            earliest = i + predict_CE([i])[0]
            if i!=time2:
                if msg!="":
                    msg=" and {} minutes in C".format(i-time2)
                else:
                    msg = "Wait {} minutes in C".format(i-time2)
            s = "E"
    road+=s
    return road+"\n"+msg

def get_best_time(time):
    earliest = 1440
    for i in range(time,1030):
        earliest = min(earliest, i + predict_AC([i])[0])
        earliest = min(earliest, i + predict_BC([i])[0])

    time2 = int(np.ceil(earliest))
    earliest = 100000
    for i in range(time2, 1030+time2-time):
        earliest = min(earliest, i + predict_CD([i])[0])
        earliest = min(earliest, i + predict_CE([i])[0])
    return int(np.ceil(earliest))-time


def get_the_best_route_as_a_text_informatic(dep_hour, dep_min):
    roads = ["A->C->D", "A->C->E", "B->C->D", "B->C->E"]
    # perform some magic here - instead of just a random selection
    est_travel_time = get_best_time(60*int(dep_hour)+int(dep_min))
    best_road = get_best_road(60*int(dep_hour)+int(dep_min))
    if est_travel_time >= 70:
        if est_travel_time >= 90:
            color = "#b30f00"
        else:
            color = "#b38300"
    else:
        color = "#2088c8"
    out = render_template("get_route.html",dep_hr=dep_hour,dep_min=dep_min,trav_time=est_travel_time,route=best_road,color=color)
    return out
@app.route('/')
def get_departure_time():
    return render_template("get_time.html")
@app.route("/get_best_route")
def get_route():
    departure_h = request.args.get('hour')
    departure_m = request.args.get('mins')
    route_info = get_the_best_route_as_a_text_informatic(departure_h, departure_m)
    return route_info

if __name__ == '__main__':
    savefile = open('knutknut_thetas_ind.bin', 'rb')
    thetas = pickle.load(savefile)
    if "AC" in thetas:
        thetas_AC = thetas["AC"]
    else:
        throw_error("Bad savefile.")
    if "CE" in thetas:
        thetas_CE = thetas["CE"]
    else:
        throw_error("Bad savefile.")
    if "BC" in thetas:
        thetas_BC = thetas["BC"]
    else:
        throw_error("Bad savefile.")
    if "CD" in thetas:
        thetas_CD = thetas["CD"]
    else:
        throw_error("Bad savefile.")
    savefile.close()
    print("<starting>")
    app.run(debug=True)
    print("<done>")