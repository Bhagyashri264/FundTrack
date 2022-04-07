from http.client import HTTPResponse
from multiprocessing import context
from multiprocessing.connection import wait
from re import template
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template import loader
import requests
from bson.objectid import ObjectId
from . import db
from django.utils.safestring import mark_safe
from . import hashing
import random
import json

ips=["http://127.0.0.1:8080"]
headers={
                    "content-type":"application/json",
                    "accept": "application/json"
                }
def index(request):
    return HttpResponse("Hiiiii")

def analysis():
    
    return render('fundtracker/analysis.html')


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
                "state":data["state"][0],
                "district":data["district"][0],
                "wallet":0
            })
            context=get_user_data(request)
            context["users"]=[]
            data=db.users.find()
            for i in data:
                temp_data={}
                temp_data["name"]=i["name"]
                temp_data["email"]=i["email"]
                temp_data["state"]=i["state"]
                temp_data["district"]=i["district"]
                context["users"].append(temp_data)
            return render(request,'fundtracker/add_admin_sub.html',context)
        else:
            context=get_user_data(request)
            context["users"]=[]
            data=db.users.find()
            for i in data:
                temp_data={}
                temp_data["name"]=i["name"]
                temp_data["email"]=i["email"]
                temp_data["state"]=i["state"]
                temp_data["district"]=i["district"]
                context["users"].append(temp_data)
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
                "purpose": data["purpose"][0],
                "state": data["state"][0],
                "district": data["district"][0],
                "bill_no": data["bill_no"][0],
                "role":rec_data["role"]
                }
            headers={
                "content-type":"application/json",
                "accept": "application/json"
            }
            
            
            if "gensis" in data.keys():
                res = requests.post("http://127.0.0.1:8080/create_genesis_block",json=body,headers=headers)
                print(res.json())
            else:
                #res = requests.post("http://127.0.0.1:8080/add_transaction",json=body,headers=headers)
                for ip in ips:
                    res = requests.post(ip+"/validate_chain",json=body,headers=headers)
                    if res == False:
                        context=get_user_data(request)
                        return render(request,"fundtracker/make_tran.html",context)
                for ip in ips:
                    res = requests.post(ip+"/add_transaction",json=body,headers=headers)
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
                "state":data["state"][0],
                "district":data["district"][0],
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
            context["transaction"].append(tran)
        return render(request,"fundtracker/view_tran.html",context)

    else:
        return redirect('login')


def guest_login(request):
    if request.session.has_key("guest"):
        if request.POST:
            data=dict(request.POST)
            print(data)
            if "send" in data.keys():
                
                body={
                    "bill_no":data["bill_no"][0],
                    "desc":data["desc"][0],
                    "state":data["state"][0],
                    "district":data["district"][0]
                }
                headers={
                    "content-type":"application/json",
                    "accept": "application/json"
                }
                res = requests.post("http://127.0.0.1:8080/send_complaint",json=body,headers=headers)
                return render(request,"fundtracker/guest_home.html")
            else:
                bill_no=data["bill_no"][0]
                body={
                    "bill_no":bill_no
                }
                headers={
                    "content-type":"application/json",
                    "accept": "application/json"
                }
                res = requests.post("http://127.0.0.1:8080/get_tree_from_bill",json=body,headers=headers)

                context={"data":mark_safe(res.json())}
                return render(request,"fundtracker/guest_home.html",context=context)
        else:
            return render(request,"fundtracker/guest_home.html")
    else:
        if request.POST:
            data=dict(request.POST)
            if "otp" in data.keys():
                if str(data["otp"][0])==str(request.session["otp"]):
                    request.session["guest"]=data["email"]
                    return render(request,"fundtracker/guest_home.html")
                else:
                    return render(request,"fundtracker/guest.html")
            else:
                email=data["email"][0]
                otp=random.randint(100000,999999)
                request.session["otp"]=otp
                body={
                    "email": email,
                    "otp": otp
                    }
                headers={
                    "content-type":"application/json",
                    "accept": "application/json"
                }
                res = requests.post("http://127.0.0.1:8080/sendotp",json=body,headers=headers)
                context={
                    "otp":"something",
                    "email":email
                }
                return render(request,"fundtracker/guest.html",context)
        else:
            return render(request,"fundtracker/guest.html")
