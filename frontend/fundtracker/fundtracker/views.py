from multiprocessing.connection import wait
from re import template
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template import loader
import requests
from bson.objectid import ObjectId
from . import db
from . import hashing


def index(request):
    return HttpResponse("Hiiiii")

def get_user_data(request):
    email=request.session["email"]
    user = db.users.find_one({"email": {"$eq": email}})
    context={"email":email,"role":user["role"],"id":str(user["_id"])}
    return context

def login(request):
    # template=loader.get_template('fundtracker/login.html')
    if request.session.has_key("email"):
        email = request.session["email"]
        return redirect('home')
    if request.POST:
        email = request.POST["email"]
        password = request.POST["password"]
        role = request.POST["role"]
        user = db.users.find_one({"email": {"$eq": email}})
        if user == None:
            context = {}
            return render(request, 'fundtracker/login.html', context)
        if hashing.verify_hash(password, user["password"]) and user["role"] == role:
            request.session["email"] = user["email"]
            return home(request)
    else:
        context = {}
        return render(request, 'fundtracker/login.html', context)


def logout(request):
    try:
        del request.session["email"]
    except:
        pass
    context = {}
    return redirect('login')

def home(request):
    if request.session.has_key("email"):
        context=get_user_data(request)
        return render(request,'fundtracker/index.html',context)
    else:
        context = {}
        return redirect('login')

def add_user(request):
    if request.session.has_key("email"):
        if request.POST:
            data=dict(request.POST)
            del data["csrfmiddlewaretoken"]
            db.users.insert_one({
                'name':data["name"][0],
                'email':data["email"][0],
                "password":hashing.create_hash(data["password"][0]),
                "role":data["role"][0],
                "tags":data["tags"],
                "wallet":0
            })
            context=get_user_data(request)
            return render(request,'fundtracker/add_admin_sub.html',context)
        else:
            context=get_user_data(request)
            return render(request,'fundtracker/add_admin_sub.html',context)
    else:
        context = {}
        return redirect('login')

def make_tran(request):
    if request.session.has_key("email"):
        if request.POST:
            data=dict(request.POST)
            context=get_user_data(request)
            rec_data=db.users.find_one({"email":{"$eq":data["email"][0]}})
            
            rec_id=str(rec_data["_id"])
            body={
                "sender_id": context["id"],
                "receiver_id": rec_id,
                "amount": data["amount"][0],
                "desp": data["desp"][0],
                "tags": data["tags"]
                }
            headers={
                "content-type":"application/json",
                "accept": "application/json"
            }
            print(body)
            
            if "gensis" in data.keys():
                res = requests.post("http://127.0.0.1:8080/create_genesis_block",json=body,headers=headers)
                print(res)
            else:
                res = requests.post("http://127.0.0.1:8080/add_transaction",json=body,headers=headers)
                print(res)
            context=get_user_data(request)
            return render(request,"fundtracker/make_tran.html",context)
        else:
            context=get_user_data(request)
            return render(request,"fundtracker/make_tran.html",context)
    else:
        return redirect('login')

def addCont(request):
    if request.session.has_key("email"):
        if request.POST:
            data=dict(request.POST)
            del data["csrfmiddlewaretoken"]
            db.users.insert_one({
                'name':data["name"][0],
                'email':data["email"][0],
                "password":hashing.create_hash(data["password"][0]),
                "role":"Contractor",
                "tags":data["tags"],
                "wallet":0
            })
            context=get_user_data(request)
            return render(request,'fundtracker/add_cont.html',context)
        else:
            context=get_user_data(request)
            return render(request,"fundtracker/add_cont.html",context)
    else:
        return redirect('login')

def view_tran(request):
    if request.session.has_key("email"):
        context=get_user_data(request)
        context["transaction"]=[]
        data=db.tran.find({"sender_id":context["id"]}).sort("time",-1)
        for i in data:
            print(i["receiver_id"])
            rec_data= db.users.find_one({"_id":{"$eq":ObjectId(str(i["receiver_id"]))}})
            print(rec_data)
            tran={}
            tran["to"]=rec_data["name"]
            tran["amount"]=i["amount"]
            tran["desp"]=i["desp"]
            tran["time"]=i["time"]
            tran["tags"]=i["tags"]
            context["transaction"].append(tran)
        return render(request,"fundtracker/view_tran.html",context)

    else:
        return redirect('login')