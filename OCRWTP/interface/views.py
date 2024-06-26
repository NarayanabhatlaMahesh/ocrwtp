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
import nltk
from nltk.tokenize import word_tokenize as wt
import math

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
        tok=nltk.word_tokenize(src_text)
        iters=math.ceil(len(tok)/250)
        t=""

        op=wt(src_text)
        # print("context is big")
        b=0
        li=[]
        for i in range(int(len(op)/275)+1):
            if b > (len(op)-275):
                li.append(op[b:len(op)])
            else:
                li.append(op[b:b+275])
            # print("in segmenting context ---",i)
            b+=275

        for i in range(len(li)):
            sen=" ".join(li[i])
            batch = tokenizer(sen, truncation=True, padding='longest', return_tensors="pt").to(device)
            translated = model.generate(**batch)
            tgt_text = tokenizer.batch_decode(translated, skip_special_tokens=True)
            t+=tgt_text[0]
        text=t
        return text

    def translatea(text,lang):
        print(text)
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
            if 'menu' in request.POST:
                return redirect('upload')
        if request.method == "POST":
            if 'upload' in request.POST:
                form = Document(request.POST,request.FILES)
                #if form.is_valid():
                user.handle_uploaded_file(request.FILES['file'])
                if request.FILES['file'].name not in Document.objects.all().values('description'):
                    f=Document(user=user.username,description=request.FILES['file'].name)
                    f.save()
                    user.filename=request.FILES['file'].name
                    return HttpResponseRedirect('extracte')
                else :
                    return redirect('upload')
        
        
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
        if 'menu' in request.POST:
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
        if request.method=="POST":
            if 'menu' in request.POST:
                print('in viewing uploads')
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
            if 'menu' in request.POST:
                print('in summarize main')
                return redirect('upload')
        return render(request,'summarize.html',{'text':user.text})
    translated=""
    def translate(request):
        docs=Document.objects.all()
        if request.method=='POST':
            if 'send' in request.POST:
                lang=request.POST['language']
                user.translated=user.translatea(user.summary,lang)
                docs.filter(user=user.username,description=user.filename,summary=user.summary).update(translated=user.translated)
                return render(request,'translate.html',{'text':user.translated})
            if 'menu' in request.POST:
                print('in translate main')
                return redirect('upload')
        return render(request,'translate.html',{'text':user.summary})
    






# Honestly This Code Sucks










    def view_summaries(request):
        docs=Document.objects.all()
        li=[]
        fna=[]
        for i in docs:
            if i.user==user.username:
                li.append(i.summary)
                fna.append(i.description)
        if request.method=='POST':
            if 'menu' in request.POST:
                print('in summarize main')
                return redirect('upload')
        return render(request,'view_summaries.html',{'names':zip(li,fna)})
    def view_translations(request):
        docs=Document.objects.all()
        li=[]
        fna=[]
        for i in docs:
            if i.user==user.username:
                li.append(i.translated)
                fna.append(i.description)
        if request.method == "POST":
            if 'menu' in request.POST:
                print('in translation main')
                return redirect('upload')
        return render(request,'view_translations.html',{'names':zip(li,fna)})
    def view_extracted(request):
        docs=Document.objects.all()
        li=[]
        fna=[]
        for i in docs:
            if i.user==user.username:
                li.append(i.text)
                fna.append(i.description)
        if request.method == "POST":
            if 'menu' in request.POST:
                print('in extracted main')
                return redirect('upload')
        return render(request,'view_extracted.html',{'names':zip(li,fna)})