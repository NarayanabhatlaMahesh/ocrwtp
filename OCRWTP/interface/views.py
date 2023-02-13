from django.shortcuts import render, HttpResponse, HttpResponseRedirect, redirect
from  interface.models import User,Document
from transformers import PegasusForConditionalGeneration, PegasusTokenizer
import torch
from OCRWTP.settings import BASE_DIR
from translate import Translator
from django.views.decorators.csrf import csrf_protect
import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"
import easyocr
class user:
    def show_image(text):
        return text
    
    def extractFromImage(fullpath):
        reader = easyocr.Reader(['en'], gpu = True)
        bounds = reader.readtext(str(BASE_DIR)+"\\docs\\"+fullpath)
        data=""
        for i in bounds:
            data+=i[1]
        print(data)
        return data
    def summarizea(src_text):
        model_name = 'google/pegasus-xsum'
        device ='cpu'
        tokenizer = PegasusTokenizer.from_pretrained(model_name)
        model = PegasusForConditionalGeneration.from_pretrained(model_name).to(device)
        batch = tokenizer(src_text, truncation=True, padding='longest', return_tensors="pt").to(device)
        translated = model.generate(**batch)
        tgt_text = tokenizer.batch_decode(translated, skip_special_tokens=True)
        text=tgt_text

        return text

    def translatea(text,lang):
        translator = Translator(lang)
        text=translator.translate(text)
        return text


    def validate(Username,Password):
        u=User.objects.all()
        flag=0
        for i in range(len(u)):
            if u[i].username == Username:
                if u[i].password == Password :
                    flag=1
                    break
        return flag
    username=""

    # Create your views here.
    @csrf_protect
    def home(request):
        if request.method == "GET":
            return render(request,'home.html')
        else:
            if 'go' in request.POST:
                mail=request.POST['email']
                passw=request.POST['pass']
                user.username=""
                if user.validate(mail,passw):
                    user.username+=mail
                    return HttpResponseRedirect('upload')
                else:
                    return HttpResponse('username or password arent matching. try again')
            else:
                return render(request,'home.html') 
        return render(request,'home.html') 

    def upload(request):
        if request.method == "GET":
            return render(request,'base1.html',{'mail':user.username})
        else:
            if 'upload' in request.POST:
                return HttpResponseRedirect('UploadFile')
            if 'view_upload' in request.POST:
                return HttpResponseRedirect('view_upload')
            if 'view_translations' in request.POST:
                return HttpResponseRedirect('view_translations')
            if 'view_summaries' in request.POST:
                return HttpResponseRedirect('view_summaries')
            if 'view_extracted' in request.POST:
                return HttpResponseRedirect('view_extracted')
            




    def upload_file(request):
        form = Document()
        if request.method == "POST":
            form = Document(request.POST,request.FILES)
            #if form.is_valid():
            user.handle_uploaded_file(request.FILES['file'])
            f=Document(user=user.username,description=request.FILES['file'].name)
            f.save()
            user.filename=request.FILES['file'].name
            if 'main' in request.POST:
                return redirect('upload')
            return HttpResponseRedirect('extracte')
        
        return render(request,'file.html')
    def handle_uploaded_file(f):
        with open(r"docs\\" + f.name,'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)
    def extracte(request):
        docs=Document.objects.all()
        if 'extract' in request.POST:
            user.text=user.extractFromImage(user.filename)
            docs.filter(user=user.username,description=user.filename).update(text=user.text)
            return HttpResponseRedirect('summarize')
        if 'main' in request.POST:
            return redirect('upload')
        li=[]
        li.append(user.filename)
        return render(request,'view_uploads.html',{'names':li})
    
# -------------------------------------------------------------------------------------------------
    def view_upload(request):
        docs=Document.objects.all()
        li=[]
        for i in docs:
            if i.user==user.username:
                li.append(i.description)
        if request.method=="POST":
            if 'extract' in request.POST:
                user.filename=request.POST['fname']
                user.text=user.extractFromImage(user.filename)
                return HttpResponseRedirect('summarize')
            if 'main' in request.POST:
                return redirect('upload')
        return render(request,'view_uploads.html',{'names':li})
# -------------------------------------------------------------------------------------------------


    filename=""
    text=""
    summary=""
    
    def summarize(request):
        docs=Document.objects.all()
        if request.method=="POST":
            if 'summarize' in request.POST:
                user.summary=user.summarizea(user.text)
                print(user.summary)
                docs.filter(user=user.username,description=user.filename).update(summary=user.summary)
                return HttpResponseRedirect('translate')
            if 'main' in request.POST:
                print('in summarize main')
                return redirect('upload')
        return render(request,'summarize.html',{'text':user.text})
    translated=""
    def translate(request):
        docs=Document.objects.all()
        if request.method=='POST':
            if 'send' in request.POST:
                lang=request.POST['language']
                user.translated=user.translatea(user.summary[0],lang)
                docs.filter(user=user.username,description=user.filename).update(translated=user.translated)
                return render(request,'translate.html',{'text':user.translated})
            if 'main' in request.POST:
                print('in translate main')
                return redirect('upload')
        return render(request,'translate.html')
    

















    def view_summaries(request):
        docs=Document.objects.all()
        li=[]
        for i in docs:
            if i.user==user.username:
                li.append(i.summary)
        if request.method=='POST':
            if 'main' in request.POST:
                print('in summarize main')
                return redirect('upload')
        return render(request,'view_summaries.html',{'names':li})
    def view_translations(request):
        docs=Document.objects.all()
        li=[]
        for i in docs:
            if i.user==user.username:
                li.append(i.translated)
        if request.method == "POST":
            if 'main' in request.POST:
                print('in translation main')
                return redirect('upload')
        return render(request,'view_translations.html',{'names':li})
    def view_extracted(request):
        docs=Document.objects.all()
        li=[]
        for i in docs:
            if i.user==user.username:
                li.append(i.text)
        if request.method=='POST':
            if 'main' in request.POST:
                return redirect('upload')
        return render(request,'view_extracted.html',{'names':li})
    