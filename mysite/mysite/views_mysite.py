from django.http import HttpResponse
from django.shortcuts import render

def home(request):
    return render(request, "home.html")

def grid(request):
    return render(request, "grid.html")

def forms(request):
    return render(request, "forms.html")

def one(request):
    return render(request, "one.html")

def bootstrap(request):
    return render(request, "bootstrap.html")

def contacts(request):
    return HttpResponse("This is Contacts Page")

def example1(request):
    return render(request, "example1.html")

def example1(request):
    myname = "roshan"
    list1 = {"toyota", "maruti", "subaru"}

    name = ""
    if request.method == "POST":
        name = request.POST.get("name")

    return render(request, 'example1.html', {
        'myname' : myname,
        'list1' : list1,
        'name' : name
    })

def AgeExample(request):
    age = None
    msg = ""
    if request.method == "POST":
        age = int(request.POST.get("age"))


        if(age>0 and age <101):
            if(age<18):
                msg = "Not eligible for voting"
            elif(age>18):
                msg = "Eligible for voting"
        else: msg = "Invalid age, should be around 1-100"

    return render(request, 'AgeExample.html', {
        'age' : age,
        'msg' : msg
    })