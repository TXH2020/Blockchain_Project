from django.shortcuts import render,redirect
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .models import *
from .encryption import *
from .a_encryption import *
from django.conf import settings
from django.core.files import File
import os, requests, ipfsapi
from cryptography.fernet import Fernet
import subprocess,re

def pad(string):
    return "\""+string+"\""

def createAsset(l):
    current_dir=os.getcwd()
    os.chdir('/home/kali/fabric-samples/test-network')
    command="""peer chaincode invoke -o localhost:7050 --ordererTLSHostnameOverride orderer.example.com --tls --cafile "${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem" -C mychannel -n basic --peerAddresses localhost:7051 --tlsRootCertFiles "${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt" --peerAddresses localhost:9051 --tlsRootCertFiles "${PWD}/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt" -c '{"function":"CreateAsset","Args":["""+','.join(l)+"""]}'
"""
    """command="peer chaincode invoke -o localhost:7050 --ordererTLSHostnameOverride orderer.example.com --tls --cafile"\
    +"\"${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem\""\
    +"-C mychannel -n basic --peerAddresses localhost:7051 --tlsRootCertFiles"\
    +"\"${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt\""\
    +"--peerAddresses localhost:9051 --tlsRootCertFiles"\
    +"\"${PWD}/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt\""\
    +'-c'+ '\'{"function":"CreateAsset","Args":\'['+','.join(l)+']\'}\''"""
    print(os.system(command))
    os.chdir(current_dir)
    #print(command)
#createAsset(["\"1\"","\"1\"","\"1\"","\"1\"","\"1\""])   
#createAsset(['1','2','3'])
def readAsset():
    current_dir=os.getcwd()
    os.chdir('/home/kali/fabric-samples/test-network')
    command="""peer chaincode query -C mychannel -n basic -c '{"Args":["GetAllAssets"]}'"""
    print(os.system(command))
    os.chdir(current_dir)
# Create your views here.
def user_login(request):
    if request.user.role == 'teacher':
        return redirect('teacher_dashboard')
    if request.user.role == "coe":
        return redirect('coe_dashboard')
    if request.user.role == 'superintendent':
        return redirect('st_dashboard')

@login_required(login_url='login')
@csrf_exempt
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')

@login_required(login_url='login')
@csrf_exempt
def teacher_dashboard(request):
    p_request = Request.objects.filter(tusername=request.user.username,status='Pending')
    a_request = Request.objects.filter(tusername=request.user.username).exclude(status='Pending')
    if request.method == 'POST':
        if request.POST.get('accept'):
            username = request.user.username
            b_id = request.POST['b_id']
            Request.objects.filter(tusername=username,id=b_id).update(status='Accepted')
            messages.success(request, 'Request Accepted! Click on Accepted Request Section on check your requests.',extra_tags='accept')
        else:
            paper = request.FILES.get('paper',None)
            key = encrypt_file(paper)
            api = ipfsapi.Client('http://0.0.0.0', 5001)
            new_file = api.add('static/encrypted_files/'+str(paper)+'.encrypted')
            hash_id = new_file['Hash']
            arr = a_encryption(hash_id,key,request.user.teacher_id)
            file_ = open(os.path.join(settings.ENCRYPTION_ROOT,request.user.teacher_id+'_private_key.pem'),'rb')
            p_file = File(file_)
            store = Request.objects.get(tusername=request.user.username)
            store.private_key.save(request.user.teacher_id+'_private_key.pem',p_file,save=True)
            store.enc_field = arr
            store.status = 'Uploaded'
            store.save()
            os.remove('static/encrypted_files/'+str(paper)+'.encrypted')
            
            with open('filekey.key', 'rb') as filekey:
                key = filekey.read()
            fernet = Fernet(key)
            encrypted = fernet.encrypt(file_.read())
            with open('temp.enc','wb') as f:
                f.write(encrypted)
            prikey_hash=api.add('temp.enc')
            createAsset([pad(request.user.teacher_id),pad(request.user.username),pad(prikey_hash['Hash']),pad('hello'),pad(store.s_code)])
            
            messages.success(request, 'Paper uploaded successfully!', extra_tags='upload')
    return render(request,'teacher.html',{'p_request':p_request,'a_request':a_request})

@login_required(login_url='login')
@csrf_exempt
def coe_dashboard(request):
    if request.method == "POST":
        s_code = request.POST['s_code']
        t_id = request.POST['t_id']
        Request.objects.filter(s_code=s_code).exclude(id=t_id).delete()
        queryset,created = Request.objects.update_or_create(id=t_id,defaults={'status':'Finalized'})
        messages.success(request, 'Paper has been finalized and sent to respective superintendent.')
        f_papers = Request.objects.filter(id=t_id).values('tusername','enc_field','private_key','s_code')
        x=None
        for paper in f_papers:
            x=paper['tusername']
            teacher = CustomUser.objects.filter(username=paper['tusername']).values('course','semester','branch','subject')
            values = a_decryption([paper['enc_field'],paper['private_key']])
            hash_id = values[1].decode('utf-8')
            r = requests.get('http://127.0.0.1:8080/ipfs/'+hash_id)
            final_paper = decrypt_file(r,values[0],paper['s_code'])
            FinalPapers.objects.create(s_code=paper['s_code'],course=teacher[0]['course'],semester=teacher[0]['semester'],
                branch=teacher[0]['branch'],subject=teacher[0]['subject'])
            final = FinalPapers.objects.latest('id')
            final.paper.save(paper['s_code']+'.pdf',final_paper,save=True)
        
        readAsset()
        
    requests_ = Request.objects.values('tusername','status')
    arr = []
    for r in requests_:
        name = CustomUser.objects.filter(username=r['tusername']).values('first_name','last_name')
        try:
            arr.append({'name':name[0]['first_name']+ " " + name[0]['last_name'],'status':r['status']})
        except:
            pass
    return render(request,'coe.html',{'arr':arr})

@login_required(login_url='login')
@csrf_exempt
def st_dashboard(request):
    queryset = FinalPapers.objects.all()
    return render(request,'superintendent.html',{'queryset':queryset})

def get_teachers(request):
    course = request.POST.get('course',None)
    semester = request.POST.get('semester',None)
    branch = request.POST.get('branch',None)
    subject = request.POST.get('subject',None)
    queryset1 = Request.objects.values('tusername').distinct()
    s_code = SubjectCode.objects.filter(subject=subject).values()
    queryset2 = Request.objects.filter(s_code=s_code[0]['s_code'],status='Uploaded').values('id')
    queryset = CustomUser.objects.filter(course=course,semester=semester,branch=branch,subject=subject).exclude(username__in=queryset1).values()
    data = { 'queryset':list(queryset),'s_code':s_code[0]['s_code'],'queryset2':list(queryset2) }
    return JsonResponse(data)

def add_teacher(request):
    s_code = request.POST.get('s_code',None)
    syllabus = request.FILES.get('syllabus',None)
    q_pattern = request.FILES.get('q_pattern',None)
    t_id = request.POST.get('g_id')
    deadline = request.POST.get('deadline',None)
    username = CustomUser.objects.filter(id=t_id).values('username')
    print(s_code,syllabus,t_id)
    Request.objects.create(tusername=username[0]['username'],s_code=s_code,syllabus=syllabus,q_pattern=q_pattern,deadline=deadline)
    new_teacher = CustomUser.objects.filter(username=username[0]['username']).values()
    return JsonResponse({'new_teacher':list(new_teacher)})

