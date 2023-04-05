from django.db import IntegrityError
from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib.auth import login,logout,authenticate
from django.core.paginator import Paginator
import json
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http  import urlsafe_base64_decode,urlsafe_base64_encode
from django.utils.encoding import force_bytes,force_str
from django.core.mail import EmailMessage,send_mail
from django.conf import settings
from django.utils.datastructures import MultiValueDictKeyError
from datetime import datetime
from .models import *
from django.utils import timezone
import time
from django.core.exceptions import ObjectDoesNotExist
from .utils import generate_token,password_generate_token

#handlers
def handler404(request, *args, **argv):
    response = render(request,'hospital/404.html')
    response.status_code = 404
    return response


def handler500(request, *args, **argv):
    response = render(request,'hospital/404.html')
    response.status_code = 500
    return response

def handler403(request, *args, **argv):
    response = render(request,'hospital/404.html')
    response.status_code = 403
    return response

def handler400(request, *args, **argv):
    response = render(request,'hospital/404.html')
    response.status_code = 400
    return response

# Create your views here.
africa_timezone = timezone.now()

def send_action_mail(request,username):
    try:
        user = User.objects.get(username=username)
        if user.is_email_verified:
            return render(request,"hospital/login.html",{
                "message":"Already verified,login with your credentials"
            })
        else:
            current_site = get_current_site(request)
            email_subject = "Activate your account"
            email_body = render_to_string("hospital/activate.html",{
                "user": user,
                "domain": current_site,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": generate_token.make_token(user),
                "type":"email",
            })
            
            email = EmailMessage(subject=email_subject,body=email_body,from_email= settings.EMAIL_HOST_USER,to=[user.email])
            
            email.send()
            return render(request,"hospital/activatefailed.html",{
                "type":"email",
                "message": "Verification mail sent to your email,please check"
            })
    except User.DoesNotExist:
        return HttpResponseRedirect(reverse("hospital:index"))
    

def activate_user(request,uidb64,token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        
        user = User.objects.get(pk=uid)
        
        
    except Exception as e:
        user = None
        
    if user and generate_token.check_token(user,token):
        user.is_email_verified = True
        user.save()
        
        login(request,user)
        
        #send welcome message
        header = f"Welcome {user.username}"
        if user.role == "Doctor":
            body = f"Welcome to the hospital platform Dr {user.first_name} {user.last_name},\n Thank you for signing up on this platform and choosing to help foster the healthcare system not only for the hospital but the society at large. Cheers \n Have a nice day"
        elif user.role == "Patient":
            body = f"Welcome to the hospital platform {user.first_name} {user.last_name},\n We are here to take care of your health needs,kindly take a tour of our platform and the features accessible to you. \n Have a nice day"

        message = Messages(recipient=user,subject=header,body=body)
        message.save()
        
        email_body = f"Your account has been authenticated {user.username}. Thanks for signing up,check out our various features on the app"
        send_mail(message=email_body,from_email=settings.EMAIL_HOST_USER,subject="Welcome to Test Hospital app",recipient_list=[user.email],fail_silently=False)
        
        return render(request,"hospital/login.html",{
            "message": "Account verified,login with your credentials"
        })
    
    return render(request,"hospital/activatefailed.html",{
        "type": "email",
        "user": user,
    })
        

def send_password_mail(request,username):
    try:
        user = User.objects.get(username=username)
        if user.is_email_verified:
            current_site = get_current_site(request)
            email_subject = "Confirm your requested for reset password"
            email_body = render_to_string("hospital/activate.html",{
                "user": user,
                "domain": current_site,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": password_generate_token.make_token(user),
                "type":"password",
            })
            
            email = EmailMessage(subject=email_subject,body=email_body,from_email= settings.EMAIL_HOST_USER,to=[user.email])
            
            email.send()
        else:
            return HttpResponseRedirect(reverse("hospital:index"))
    except User.DoesNotExist:
        return HttpResponseRedirect(reverse("hospital:index"))
    
    
def password_mail(request,username):
    send_password_mail(request,username)
    return render(request,"hospital/activatefailed.html",{
        "type":"password",
        "message": "Password verification mail sent to your email,please check"
    })    

def reset_password(request,uidb64,token):
    
    if request.method == "POST":
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            
            user = User.objects.get(pk=uid)
            
            
        except Exception as e:
            user = None
           
        if user and password_generate_token.check_token(user,token):
            newpassword = request.POST["new_password"]
            confirmation = request.POST["confirmation"]
            
            if newpassword == confirmation:
                # user.profile_change = not user.profile_change
                user.set_password(newpassword)
                user.save()
                
                #logout user
                logout(request)
                
                return render(request,"hospital/login.html",{
                    "message": "Password has been changed,login again",
                })
            else:
                return render(request,"hospital/password.html",{
                    "uid": uidb64,
                    "token": token,
                    "message": "Password and confirmation don't match",
                })
        else:
            return render(request,"hospital/activatefailed.html",{
                "type": "password",
                "user": user,
            })  
       
    else: 
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            
            user = User.objects.get(pk=uid)
            
            
        except Exception as e:
            user = None
            
        if user and password_generate_token.check_token(user,token):
            
            return render(request,"hospital/password.html",{
                "uid": uidb64,
                "token": token,
            })
        
        else:
            return render(request,"hospital/activatefailed.html",{
                "type": "password",
                "user": user,
            })    

def set_password(request):
    user = request.user
    if request.method == "POST":
        username = request.POST["username"]
        try:
            newuser = User.objects.get(username=username)
            send_password_mail(request,newuser.username)
            return render(request,"hospital/set-password.html",{
                "message": "Verification email sent,pls check your inbox",
            })
        except User.DoesNotExist:
            return render(request,"hospital/set-password.html",{
                "message" : "User doesn't exist"
            })
        
    
    else:
        if user.is_anonymous:
            return render(request,"hospital/set-password.html")
        else:
            return HttpResponseRedirect(reverse("hospital:index"))


def index(request):
    user = request.user
    if  user.is_authenticated and user.is_email_verified:
       role = user.role
       if role == "Doctor":
          return HttpResponseRedirect(reverse("hospital:doctor"))
       else:
           return HttpResponseRedirect(reverse("hospital:patient"))
       
    elif user.is_authenticated and user.is_email_verified == False:
        return render(request,"hospital/login.html",{
            "message": "pls verify your account"
        })
    else:
        return render(request,"hospital/index.html")

def register(request):
    user = request.user
    if user.is_authenticated:
        return HttpResponseRedirect(reverse("hospital:index"))
    else:
        if request.method == "POST":
            username = request.POST["username"]
            email = request.POST["email"]
            role = request.POST["role"]
            password = request.POST["password"]
            confirmation = request.POST["confirmation"]
            first_name = request.POST["first_name"]
            last_name = request.POST["last_name"]
            profilepic = request.FILES["profilepic"]
            
            if role != "Doctor" and role != "Patient":
                role = "Patient"
                
            #check to ensure the email has not been used
            alluser = User.objects.all()
            emailstatus = True
            for checkuser in alluser:
                if email == checkuser.email:
                    emailstatus = False
                    
                    
            if password == confirmation and emailstatus == True:
                #create user
                try:
                    user = User.objects.create_user(username,email,password)
                    user.save()
                    user = User(id=user.id,username=user.username,email=user.email,password=user.password,role=role,first_name=first_name,last_name=last_name,profilepic=profilepic)
                    user.save()
                    if role == "Doctor":
                        #create doctor's profile
                        try:
                            descr = request.POST["descr"]
                            skills = request.POST.getlist("skills")
                            doctorprofile = DoctorInfo(doctor=user,descr=descr)
                            doctorprofile.save()
                            for i in skills:
                                skill = Skills.objects.get(skill=i)
                                doctorprofile.skills.add(skill)
                        except IntegrityError:
                            return render(request,"hospital/register.html",{
                                "message":"Doctor profile couldn't be created,check details and try again",
                            })
                    elif role == "Patient":
                        #create patient profile
                        try:
                            patientprofile = PatientInfo(patient=user)
                            patientprofile.save()
                        except IntegrityError:
                            return render(request,"hospital/register.html",{
                                "message":"Patient profile couldn't be created,check details and try again",
                            })
                    login(request,user)
                    send_action_mail(request,user.username)
                    return render(request,"hospital/login.html",{
                        "message": "Verification mail sent to your email,please check"
                    })
                except IntegrityError:
                    return render(request,"hospital/register.html",{
                        "message":"Username already exists",
                    })
                
            else:
                return render(request,"hospital/register.html",{
                    "message": "Password is not the same as the confirmation/email has been used",
                })
            
        else:
            return render(request,"hospital/register.html")
    

def login_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("hospital:index"))
    else:
        if request.method == "POST":
            username = request.POST["username"]
            password = request.POST["password"]
            user = authenticate(request,username=username,password=password)
            
            if user is not None:
                if user.is_email_verified:
                    login(request,user)
                    return HttpResponseRedirect(reverse("hospital:index"))
                else:
                    return render(request,"hospital/login.html",{
                        "message":"Account not verified",
                    })
            else:
                return render(request,"hospital/login.html",{
                    "message":"Username/password is incorrect",
                })
            
        else:
            return render(request,"hospital/login.html")
    

@login_required(login_url="hospital:login")
def logout_view(request):
    user = request.user
    if user.is_email_verified:
       logout(request)
        
    return HttpResponseRedirect(reverse("hospital:index"))

@login_required(login_url="hospital:login")
def doctor_view(request):
    #extra layer of confirmation to ensure user is a doctor
    user = request.user
    if user.role == "Doctor" and user.is_email_verified:
        #get users that have made appointments with the doctor
        try:
            docprofile = DoctorInfo.objects.get(doctor=user)

        except DoctorInfo.DoesNotExist:
            #create the docprofile
            docprofile = DoctorInfo(doctor=user,descr=f"I am {user.username}")
            docprofile.save()
            
        appointments = docprofile.appointments.all()
        appointments = appointments.order_by("appointment").all()
        appointments = Paginator(appointments,10)
        
        return render(request,"hospital/doctor.html",{
            "appointments": appointments.page(1),
            "page_range" : appointments.page_range,
            "max_page": appointments.num_pages,
        })
    else:
        return HttpResponseRedirect(reverse("hospital:index"))

@login_required(login_url="hospital:login")
def patient_view(request):
    #extra layer of confirmation to ensure user is a patient
    user = request.user
    if user.role == "Patient" and user.is_email_verified:
        doctors = User.objects.filter(role="Doctor")
        doctors = doctors.order_by("first_name").all()
        docpage = Paginator(doctors,10)
        return render(request,"hospital/patient.html",{
            "max_num": docpage.num_pages,
        })
    else:
        return HttpResponseRedirect(reverse("hospital:index"))
    
@login_required(login_url="hospital:login")
def get_profile(request):
    user = request.user
    if user.is_email_verified:
        if user.role == "Doctor":
            doctorinfo = DoctorInfo.objects.get(doctor=user)
            return render(request,"hospital/profile.html",{
                "info": doctorinfo,
                "skills": doctorinfo.skills.all(),
                "appointments":doctorinfo.appointments.all(),
                "availables":doctorinfo.availables.all(),
                "completed": doctorinfo.completed.all(),
            })
        elif user.role == "Patient":
            patientinfo = PatientInfo.objects.get(patient=user)
            return render(request,"hospital/profile.html",{
                "info": patientinfo,
                "appointments":patientinfo.appointments.all(),
                "completed": patientinfo.completed.all(),
                "cart":patientinfo.cart.all(),
                "successful_orders": patientinfo.successful_orders.all(),
                "cancelled_orders": patientinfo.cancelled_orders.all()
            })
    else:
        return HttpResponseRedirect(reverse("hospital:index"))
        
        
@login_required(login_url="hospital:login")
def availability(request):
    user = request.user
    #confirm that user is a doctor
    if user.role == "Doctor" and user.is_email_verified:
        try:
            docprofile = DoctorInfo.objects.get(doctor=user)
        except DoctorInfo.DoesNotExist:
            docprofile = DoctorInfo(doctor = user,descr=f"I am {user.username}")
            docprofile.save()
            
        return render(request,"hospital/available.html",{
            "availables": docprofile.availables.all(),
        })
    else:
        return HttpResponseRedirect(reverse("hospital:index"))
    
    
@login_required(login_url="hospital:login")
def patient_appointment(request):
    user = request.user
    if user.role == "Patient" and user.is_email_verified:
        patientinfo = PatientInfo.objects.get(patient=user)
        #localize timezones
        appointments = []
        patientappointments = patientinfo.appointments.all()
        if patientappointments.count() > 0:
            for appoint in patientappointments:
                startdate = timezone.localtime(appoint.startdate)
                enddate = timezone.localtime(appoint.enddate)
                startdate = startdate.strftime("%m/%d/%Y %I:%M %p")
                enddate = enddate.strftime("%m/%d/%Y %I:%M %p")
                doctor = appoint.doctor
                docappoint = {
                    "id":appoint.id,
                    "startdate" : startdate,
                    "enddate": enddate,
                    "doctor": doctor,
                }
                appointments.append(docappoint)
                
        return render(request,"hospital/patient-appointments.html",{
            "appointments": appointments
        })
    else:
        return HttpResponseRedirect(reverse("hospital:index"))

@login_required(login_url="hospital:login")
def pharmacy_view(request):
    user = request.user
    if user.role == "Patient" and user.is_email_verified:
        pharmacy = Pharmacy.objects.all()
        pharmacy = pharmacy.order_by("name").all()
        pharmacy = Paginator(pharmacy,6)
        return render(request,"hospital/pharmacy.html",{
            "pharmacy": pharmacy.page(1),
            "page_range": pharmacy.page_range,
            "pagemax": pharmacy.num_pages,
        })
    else:
        return HttpResponseRedirect(reverse("hospital:index"))
    
@login_required(login_url="hospital:login")
def messages_views(request):
    user = request.user
    if user.is_email_verified:
        messages = Messages.objects.filter(recipient=user)
        messages = messages.order_by("-timestamp").all()
        messages = Paginator(messages,15)
        return render(request,"hospital/messages.html",{
            "messages" : messages.page(1),
            "page_range": messages.page_range,
            "maxpage": messages.num_pages,
        })
    else:
        return HttpResponseRedirect(reverse("hospital:index"))
    

@login_required(login_url="hospital:login")
def cart_view(request):
    user = request.user
    if user.is_email_verified:
        patientprofile = PatientInfo.objects.get(patient=user)
        cart = patientprofile.cart.all()
        cart = cart.order_by("amount").all()
        cart = Paginator(cart,6)
        return render(request,"hospital/cart.html",{
            "cart": cart.page(1),
            "page_range": cart.page_range,
            "max_page": cart.num_pages,
        })
    else:
        return HttpResponseRedirect(reverse("hospital:index"))
    
    
@login_required(login_url="hospital:login")
def edit_profile(request):
    user = request.user
    if user.is_email_verified:
        if request.method == "POST":
            username = request.POST["username"]
            first_name = request.POST["first_name"]
            last_name = request.POST["last_name"]
            
            try:
                profilepic = request.FILES["profilepic"]
            except MultiValueDictKeyError:
                profilepic = " "
            
            #save the new information
            try:
                user.first_name = first_name
                user.last_name = last_name
                user.save()
                try:
                    user.username = username
                    user.save()
                    
                except IntegrityError:
                    return render(request,"hospital/edit-profile.html",{
                        "message" : "Username already taken",
                    })
                
            except IntegrityError:
                return render(request,"hospital/edit-profile.html",{
                    "message" : "An error occured",
                })
            
            if profilepic != " ":
                user.profilepic = profilepic
                user.save()
                
            if user.role == "Doctor":
                descr = request.POST["descr"]
                
                try:
                    docprofile = DoctorInfo.objects.get(doctor=user)
                    #check if any skill was added
                    try:
                        skills = request.POST.getlist("skills")
                    except MultiValueDictKeyError:
                        skills = docprofile.skills.all()
                        
                    #remove all existing skills
                    for rskill in docprofile.skills.all():
                        docprofile.skills.remove(rskill)
                        
                    for skill in skills:
                        skill = Skills.objects.get(skill=skill)
                        docprofile.skills.add(skill)
                    docprofile.descr = descr
                    docprofile.save()
                except DoctorInfo.DoesNotExist:
                    return render(request,"hospital/edit-profile.html",{
                        "message" : "Doctor profile doesn't exist",
                    }) 
                    
            return HttpResponseRedirect(reverse("hospital:profile")) 
            
        else:
            skills = Skills.objects.all()
            skills = skills.order_by("skill").all()
            if user.role == "Doctor":
                profile = DoctorInfo.objects.get(doctor=user) 
            
            else:
                profile = PatientInfo.objects.get(patient=user) 

            return render(request,"hospital/edit-profile.html",{
                "profile" : profile,
                "skills": skills,
            })
        
    else:
        return HttpResponseRedirect(reverse("hospital:index"))

#APIVIEWS
def get_skills(request):
    if request.method == "GET":
        skills = Skills.objects.all()
        skills = skills.order_by("skill").all()
        return JsonResponse([skill.serialize() for skill in skills],safe=False,status=201)
    else:
        return JsonResponse({"message":"wrong request method"},status=400)
    

def get_doctors(request,page_num):
    user = request.user
    #check if user is authentiacted
    if user.is_authenticated and request.method== "GET" and user.is_email_verified:
        # time.sleep(0.5)
        #get the doctors
        doctors = User.objects.filter(role="Doctor")
        doctors = doctors.order_by("first_name").all()
        docpage = Paginator(doctors,10)
        if page_num in docpage.page_range:
            docpages = docpage.page(page_num)
            return JsonResponse([doctor.serialize() for doctor in docpages],safe=False,status=201)
        else:
            return JsonResponse({"message":"Page requested not found"},status=400)
    else:
        return JsonResponse({"message":"user not signed in/wrong request method"},status=400)    
    
    
def doctor_profile(request,username):
    user = request.user
    if user.is_authenticated and request.method == "GET" and user.role == "Patient" and user.is_email_verified:
        # time.sleep(0.5)
        #check if doctor exists
        try:
            doc = User.objects.get(id=username)
            #check if user has a doctorinfo
            try:
                docinfo = DoctorInfo.objects.get(doctor=doc)
                return JsonResponse(docinfo.serialize(),safe=False,status=201)
            except DoctorInfo.DoesNotExist:
                return JsonResponse({"message":"Doctor info doesn't exist"},status=400)
            
        except User.DoesNotExist:
            return JsonResponse({"message":"User requested for doesn't exist"},status=403)
    else:
        return JsonResponse({"messsage":"User is not logged in/wrong request method"},status=400)
    
    
def search_doctor(request,search_type,search_term):
    user = request.user
    if user.is_authenticated and request.method == "POST" and user.role == "Patient" and user.is_email_verified:
        search = search_type.lower()
        term = search_term.lower()
        try: 
            doctors = User.objects.filter(role="Doctor")
            docList = []
            failed = []
            if search == "name":
                #search through the names
                for doc in doctors:
                    if term in doc.first_name.lower() and term in doc.last_name.lower():
                        docList.append(doc.serialize())
                    
                    elif term in doc.first_name.lower():
                        docList.append(doc.serialize())
                    
                    elif term in doc.last_name.lower():
                        docList.append(doc.serialize())
                        
                    elif term in f"{doc.first_name.lower()} {doc.last_name.lower()}":
                        docList.append(doc.serialize())
                        
                    elif term in f"{doc.last_name.lower()} {doc.first_name.lower()}":
                        docList.append(doc.serialize())
                                      
            elif search == "descr":
                #search through all the doctor profile for the descr
                for doc in doctors:
                    try:
                        docprofile = DoctorInfo.objects.get(doctor = doc)
                        if term in docprofile.descr:
                            docList.append(doc.serialize())
                    except DoctorInfo.DoesNotExist:
                        failed.append(doc)
            elif search == "skills":
                for doc in doctors:
                    try:
                        docprofile = DoctorInfo.objects.get(doctor = doc)
                        if len(term.split(" ")) > 1:
                            terms = term.split(" ")
                            for t in terms:
                                for skill in docprofile.skills.all():
                                    if t in skill.skill.lower():
                                        if doc.serialize() not in docList:
                                            docList.append(doc.serialize())
                            # return JsonResponse({"message":"There is space in search term"},status=201)
                        elif len(term.split(",")) > 1:
                            terms = term.split(",")
                            for t in terms:
                                for skill in docprofile.skills.all():
                                    if t in skill.skill.lower():
                                        if doc.serialize() not in docList:
                                            docList.append(doc.serialize())
                        else:
                            for skill in docprofile.skills.all():
                                if term in skill.skill.lower():
                                    docList.append(doc.serialize())
                    except DoctorInfo.DoesNotExist:
                        failed.append(doc)
            else:
                return JsonResponse({"message":"Wrong search request"},status=400)
            
            # check if doclist is empty
            if len(docList) > 0:
                return JsonResponse(docList,safe=False,status=201)
            else:
                return JsonResponse({"message":f"Search term not found for {search} try another search term"},status=201)
            
        except User.DoesNotExist:
            return JsonResponse({"message":"No doctors on the app"},status=400)
    else:
        return JsonResponse({"message":"User not logged in/request method is wrong"},status=403)
    
    
@login_required(login_url="hospital:login")
def add_availability(request):
    user = request.user
    if user.role == "Doctor" and request.method == "POST" and user.is_email_verified:
        data = json.loads(request.body)
        times = data.get("datetimes","")
        if len(times.split("-")) > 1:
            startdate = times.split(" - ")[0]
            enddate = times.split(" - ")[1]
            startdate = datetime.strptime(startdate, "%m/%d/%Y %I:%M %p")
            enddate = datetime.strptime(enddate, "%m/%d/%Y %I:%M %p")
            # startdate = africa_timezone.localize(startdate)
            # enddate = africa_timezone.localize(enddate)
            today = africa_timezone
            today = today.strftime("%m/%d/%Y %I:%M %p")
            today = datetime.strptime(today,"%m/%d/%Y %I:%M %p")
            # today = africa_timezone.localize(today)
            res = True
            #check if the dates clash by checking is startdate is lesser than present time or lesser than other enddates
            try:
                docprofile = DoctorInfo.objects.get(doctor=user)
                
            except DoctorInfo.DoesNotExist:
                #create docprofile
                docprofile = DoctorInfo(doctor=user,descr=f"I am {user.username}")
                docprofile.save()
            
            #check if date is valid before comparison
            if today <= startdate < enddate:
                #check for all appointments made by the doctor
                try:
                    checkers = DocAppointment.objects.filter(doctor=user)
                    for avail in checkers:
                        #check if the appointment is completed,so we would add it automatically
                        try:
                            avail.patientappoint
                            res = True
                            
                        except ObjectDoesNotExist:
                            availstart = avail.startdate.strftime("%m/%d/%Y %I:%M %p")
                            availend = avail.enddate.strftime("%m/%d/%Y %I:%M %p")
                            availstart = datetime.strptime(availstart, "%m/%d/%Y %I:%M %p")
                            availend = datetime.strptime(availend, "%m/%d/%Y %I:%M %p")
                            #check if startdate and enddate are between any start and end date
                            if availstart <= startdate <= availend or availstart <= enddate <= availend or startdate <= availstart <= enddate or startdate <= availend <= enddate:
                                res = False
                                if startdate < availstart >= enddate:
                                    res = True
                                #check if any appointment date is inbetween the proposed appointment
                                elif availstart < startdate and availend <= enddate:
                                    res = False
                    if res == True:
                        #save the dates in both docappointment and and the doctor's profile
                        try:
                            docappointment = DocAppointment(doctor=user,startdate=startdate,enddate=enddate)
                            docappointment.save()
                            docprofile.availables.add(docappointment)
                            #send doctor message that he has added a new availability
                            try:
                                docbody = f"You just created a new appointment Dr {user.first_name} from {startdate} to {enddate},\n Cheers to improving healthcare in the world"
                                docmessage = Messages(recipient=user,subject=f"You just created a new appointment Dr {user.username}",body=docbody)
                                docmessage.save()
                            except IntegrityError:
                                sent = False
                            return JsonResponse(docprofile.serialize(),status=201)
                        except IntegrityError:
                            return JsonResponse({"message":"Couldn't save the new date,try again"},status=400)
                    else:
                        return JsonResponse({"message":"Dates couldn't be saved because they are inbetween an existing date vice versa"},status=400)
                        
                except DocAppointment.DoesNotExist:
                    #save the dates in both docappointment and and the doctor's profile
                    try:
                        docappointment = DocAppointment(doctor=user,startdate=startdate,enddate=enddate)
                        docappointment.save()
                        docprofile.availables.add(docappointment)
                        #send doctor message that he has added a new availability
                        try:
                            docbody = f"You just created a new appointment Dr {user.first_name} from {startdate} to {enddate},\n Cheers to improving healthcare in the world"
                            docmessage = Messages(recipient=user,subject=f"You just created a new appointment Dr {user.username}",body=docbody)
                            docmessage.save()
                        except IntegrityError:
                            sent = False
                        return JsonResponse(docprofile.serialize(),safe=False,status=201)
                    except IntegrityError:
                        return JsonResponse({"message":"Couldn't save the new date,try again"},status=400)                                
            else:
                return JsonResponse({"message":"Dates are not valid"},status=400)
                
            
        else:
            return JsonResponse({"message":"Incorrect date format"},status=400)
        
    else:
        return JsonResponse({"message":"User doesn't exist/wrong request method"},status=403)
    
    
@login_required(login_url="hospital:login")
def remove_availability(request,id):
    user = request.user
    if user.role == "Doctor" and request.method == "PUT" and user.is_email_verified:
        try:
            docappoint = DocAppointment.objects.get(id=id)
            docprofile = DoctorInfo.objects.get(doctor=user)
            docprofile.availables.get(id = docappoint.id)
            if docappoint.doctor == user:
                docprofile.availables.remove(docappoint)
                #send removal confirmation message to the doctor
                docbody = f"You just removed an appointment Dr {user.first_name} from {docappoint.startdate.strftime('%m %d, %Y, %I:%M %p')} to {docappoint.enddate.strftime('%m %d, %Y, %I:%M %p')},\n We hope you add another soon enough"
                docmessage = Messages(recipient=user,subject=f"You just removed an appointment Dr {user.username}",body=docbody)
                docmessage.save()

                #delete appointment
                docappoint.delete()
                return JsonResponse(docprofile.serialize(),safe=False,status=201)
            else:
                return JsonResponse({"message":"Wrong appointment"},status=403)
        except DocAppointment.DoesNotExist or DoctorInfo.DoesNotExist:
            return JsonResponse({"message":"Appointment does not exist"},status=400)
        
    else:
        return JsonResponse({"message":"User not authenticated/wrong request user"},status=403)
    
    
@login_required(login_url="hospital:login")
def add_appointment(request,id):
    user = request.user
    if request.method == "PUT" and user.role == "Patient" and user.is_email_verified:
        try:
            docappoint = DocAppointment.objects.get(id=id)
            doc = docappoint.doctor
            docprofile = DoctorInfo.objects.get(doctor = doc)
            docprofile.availables.get(id = docappoint.id)
            #check if appointment has been created before
            try:
                patientappoint = PatientAppointment.objects.get(patient=user,appointment=docappoint)
                patientappoint.delete()
            except PatientAppointment.DoesNotExist:
                #create patient appointment and add appointment to patient appointment
                try:
                    patientappoint = PatientAppointment(patient=user,appointment=docappoint)
                    patientappoint.save()
                    docprofile.availables.remove(docappoint)
                    docprofile.appointments.add(patientappoint)
                    try:
                        patientprofile = PatientInfo.objects.get(patient=user)
                    except PatientInfo.DoesNotExist:
                        try:
                            patientprofile = PatientInfo(patient=user)
                            patientprofile.save()
                            #check if the appointment has been cancelled
                        except IntegrityError:
                            return JsonResponse({"message":"Couldn't add appointment"},safe=False,status=400)
                    patientprofile.appointments.add(docappoint)
                    
                    #send a confirmation message
                    body = f"Hello {user.username} You just made a new appointment with Dr {doc.first_name} {doc.last_name} from {docappoint.startdate.strftime('%m %d, %Y, %I:%M %p')} to {docappoint.enddate.strftime('%m %d, %Y, %I:%M %p')},\n Cheers to taking note and caring for your health. \n As they say,health is wealth"
                    message = Messages(recipient=user,subject=f"You just made a new appointment with Dr {doc.first_name}",body=body)
                    message.save()
                    
                    return JsonResponse(docprofile.serialize(),safe=False,status=201)
                except IntegrityError:
                    return JsonResponse({"message":"Couldn't add appointment(main)"},status=400)
        except DocAppointment.DoesNotExist or DoctorInfo.DoesNotExist:
            return JsonResponse({"message":"Appointment doesn't exist"},status=400)
    else:
        return JsonResponse({"message":"User not logged in/wrong request method"},status=403)
    
    
@login_required(login_url="hospital:login")
def remove_appointment(request,id):
    user = request.user
    if user.role == "Patient" and request.method == "PUT" and user.is_email_verified:
        try:
            patientprofile = PatientInfo.objects.get(patient=user)
            docappoint = DocAppointment.objects.get(id=id)
            doc = docappoint.doctor
            #confirm that the user has the appointment and the user created the patientappointment
            patientprofile.appointments.get(id=docappoint.id)
            patientappointment = PatientAppointment.objects.get(patient=user,appointment=docappoint)
            docprofile = DoctorInfo.objects.get(doctor=doc)
            #remove patient appointment,add to cancelled,remove appointment from the doctor and add the availability back
            patientprofile.appointments.remove(docappoint)
            docprofile.appointments.remove(patientappointment)
            docprofile.availables.add(docappoint)
            
            #send a confirmation message
            body = f"Hello {user.username} You just removed an appointment with Dr {doc.first_name} {doc.last_name} from {docappoint.startdate.strftime('%m %d, %Y, %I:%M %p')} to {docappoint.enddate.strftime('%m %d, %Y, %I:%M %p')},\n We hope no problem as to why you decided to remove the appointment. \n Enjoy the rest of your day"
            message = Messages(recipient=user,subject=f"You just removed an appointment with Dr {doc.first_name}",body=body)
            message.save()
            
            #delete appointment
            patientappointment.delete()
            return JsonResponse(docprofile.serialize(),safe=False,status=201)
        except PatientInfo.DoesNotExist or DocAppointment.DoesNotExist or PatientAppointment.DoesNotExist or User.DoesNotExist or DoctorInfo.DoesNotExist:
            return JsonResponse({"message":"An error occured try again later"},status=400)
    else:
        return JsonResponse({"message":"User not logged in/wrong request method"},status=403)
    
    
@login_required(login_url="hospital:login")
def get_drugs(request,page_num):
    user = request.user
    if user.role == "Patient" and request.method == "GET" and user.is_email_verified:
        pharmacy = Pharmacy.objects.all()
        pharmacy = pharmacy.order_by("name").all()
        pharmacy = Paginator(pharmacy,6)
        if page_num <= pharmacy.num_pages:
            pharmacy = pharmacy.page(page_num)
            return JsonResponse([drug.serialize() for drug in pharmacy],safe=False,status=201)
        else:
            return JsonResponse({"message":"Page requested doesn't exist"},status=400)
        
    else:
        return JsonResponse({"message":"Wrong request method/User not logged in"},status=403)

@login_required(login_url="hospital:login")
def search_drugs(request):
    user = request.user
    if user.role == "Patient" and request.method == "POST" and user.is_email_verified:
        data = json.loads(request.body)
        term = data.get("term","")
        term = term.lower()
        drugs = []
        alldrugs = Pharmacy.objects.all()
        alldrugs = alldrugs.order_by("name").all()
        for drug in alldrugs:
            if term in drug.name.lower() or term in drug.descr.lower():
                drugs.append(drug.serialize())
            
                
        if len(drugs) >= 1:
            return JsonResponse(drugs,safe=False,status=201)
        else:
            return JsonResponse({"message":"Search term couldn't be found"},status=201)
    else:
        return JsonResponse({"message":"User not logged in/wrong request method"},status=403)
    
@login_required(login_url="hospital:login")
def drug_details(request,drug_id):
    user = request.user
    if user.role == "Patient" and request.method  == "GET" and user.is_email_verified:
        #check if drug exists
        try:
            drug = Pharmacy.objects.get(pk=drug_id)
            return JsonResponse(drug.serialize(),safe=False,status=201)
        except Pharmacy.DoesNotExist:
            return JsonResponse({"message":"Drug doesn't exist"},status=400)
    else:
        return JsonResponse({"message":"User not logged in/wrong request method"},status=403)
    
    
@login_required(login_url="hospital:login")
def add_cart(request):
    user = request.user
    if request.method == "PUT" and user.role == "Patient" and user.is_email_verified:
        data = json.loads(request.body)
        pk = data.get("pk","")
        #check if drug exists
        try:
            drug = Pharmacy.objects.get(pk=int(pk))
            #check if order exists
            try:
                neworder = Order.objects.get(patient=user,drug=drug)
            except Order.DoesNotExist:
                try:
                    neworder = Order(patient=user,drug=drug)
                    neworder.save()
                except IntegrityError:
                    return JsonResponse({"message":"Order couldn't be created"},status=400)
                
            #check if patient has a profile
            try:
                patientprofile = PatientInfo.objects.get(patient = user)
            except PatientInfo.DoesNotExist:
                patientinfo = PatientInfo(patientprofile = user)
                patientinfo.save()
            patientprofile.cart.add(neworder)
            
            #send a confirmation message
            body = f"Hello {user.username}. \n You just added to cart a drug with the name of {drug.name}.You can check the cart page for your orders and its details. Then you can add amount you want to order when you checkout \n Thanks for your patronage,we hope you order it soon"
            message = Messages(recipient=user,subject=f"You just added an order to cart",body=body)
            message.save()
            
            return JsonResponse({"message":"Success"},status=201)
        except Pharmacy.DoesNotExist:
            return JsonResponse({"message":"Drug doesn't exist"},status=400)
    else:
        return JsonResponse({"message":"User not logged in/wrong request method"},status=403)


@login_required(login_url="hospital:login")
def remove_cart(request):
    user = request.user
    if request.method == "PUT" and user.role == "Patient" and user.is_email_verified:
        data = json.loads(request.body)
        pk = data.get("pk","")
        #check if drug exists
        try:
            drug = Pharmacy.objects.get(pk=int(pk))
            order = Order.objects.get(patient=user,drug=drug)
            if order.patient == user:
               patientprofile = PatientInfo.objects.get(patient=user)
               patientprofile.cart.remove(order)
               
               #send a confirmation message
               body = f"Hello {user.username}. \n You just removed from cart a drug with the name of {drug.name}.\n Enjoy the rest of your day"
               message = Messages(recipient=user,subject=f"You just removed an order from your cart",body=body)
               message.save()
                
               order.delete()
               return JsonResponse({"message":"Removed successfully"},status=201) 
            else:
                return JsonResponse({"message":"Not allowed"},status=400)
        except Order.DoesNotExist or Pharmacy.DoesNotExist:
            return JsonResponse({"message":"Order doesn't exist"},status=400)
    else:
        return JsonResponse({"message":"User not logged in/wrong request method"},status=403)
        
        
@login_required(login_url="hospital:login")
def drug_order(request,drug_id):
    user = request.user
    if request.method == "GET" and user.role == "Patient" and user.is_email_verified:
        #check if drug exists 
        try:
            drug = Pharmacy.objects.get(pk=drug_id)
            patientprofile = PatientInfo.objects.get(patient=user)
            
            #check if order exists
            try:
                order = Order.objects.get(patient=user,drug=drug)
                patientprofile.cart.get(id=order.id)
                return JsonResponse({"message":True},status=201)
            except Order.DoesNotExist:
                return JsonResponse({"message":False},status=201)
            
        except Pharmacy.DoesNotExist:
            return JsonResponse({"message":"Drug doesn't exist"},status=400)
        
    else:
        return JsonResponse({"message":"User not logged in/wrong request method"},status=403)
   
    
@login_required(login_url="hospital:login")
def checkout(request):
    user = request.user
    if user.role == "Patient" and request.method == "POST" and user.is_email_verified:
        data = json.loads(request.body)
        pk = data.get("pk"," ")
        pieces = data.get("pieces"," ")
        #check if drug exists 
        try:
            drug = Pharmacy.objects.get(pk=pk)
            #check if the order has been created
            try:
                order = Order.objects.get(patient=user,drug=drug,sucessful=False)
            except Order.DoesNotExist:
                order = Order(patient=user,drug=drug)
                order.save()
                
            #check if user has a patient profile
            try:
                patientprofile = PatientInfo.objects.get(patient=user)
            except PatientInfo.DoesNotExist:
                patientprofile = PatientInfo(patient=user)
                patientprofile.save()
                
            #check if the order is in the cart
            try:
                patientprofile.cart.get(id=order.id)
            except Order.DoesNotExist:
                patientprofile.cart.add(order)
                
            #update the order amount
            newprice = int(order.drug.price) * int(pieces)
            try:
                neworder = Order(id=order.id,patient=order.patient,amount=int(pieces),itemprice=int(newprice),drug=order.drug,sucessful=order.sucessful)
                neworder.save()
                
                #send a confirmation message
                body = f"Hello {user.username}. \n You just checked out a drug with the name of {drug.name} ordering {neworder.amount} and totalled to ${neworder.itemprice} .\n We are sorry payment methods doesn't exist now sir,we will message you about how to pay. Thank you"
                message = Messages(recipient=user,subject=f"You just checked out an order",body=body)
                message.save()
                
                return JsonResponse({"message":"Order created successfully but the payment mechanism not yet present","amount":neworder.amount,"price":neworder.itemprice},status=201)
            except IntegrityError:
                return JsonResponse({"message":"Couldn't save"},status=400)
            
        except Pharmacy.DoesNotExist:
            return JsonResponse({"message":"Drug doesn't exist"},status=400)
        
    else:
        return JsonResponse({"message":"User not logged in/wrong request method"},status=403)
    
    
def update_appointments(request):
    if request.method == "GET":
        docappointments = DocAppointment.objects.all()
        today = africa_timezone
        today = today.strftime("%m/%d/%Y %I:%M %p")
        today = datetime.strptime(today,"%m/%d/%Y %I:%M %p")
        for docappoint in docappointments:
            startdate = docappoint.startdate.strftime("%m/%d/%Y %I:%M %p")
            enddate = docappoint.enddate.strftime("%m/%d/%Y %I:%M %p")
            startdate = datetime.strptime(startdate,"%m/%d/%Y %I:%M %p")
            enddate = datetime.strptime(enddate,"%m/%d/%Y %I:%M %p")
            #check if appointment is not valid
            if today > startdate or today > enddate:
                #check if any patient has made the appointment
                try:
                    patientappointments = docappoint.patientappoint
                    appoint = patientappointments
                    #check whether appointment is completed
                    completedappointment = appoint.patientcomplete.all()
                    if completedappointment.count() < 1:
                        patient = appoint.patient
                        doc = docappoint.doctor
                        header = f"Confirm completion of appointment {patient.username}"
                        #send messages to the user to confirm dates whether the appointments held
                        #check if admin has sent the first message
                        patientbody = f"Hi {patient.first_name} {patient.last_name}.\n Hope your day was wonderful. We are checking if you have completed your appointment which lasted from {docappoint.startdate.strftime('%m/%d/%Y %I:%M %p')} to {docappoint.enddate.strftime('%m/%d/%Y %I:%M %p')} and we hope it was wonderful.This is the first message concerning this appointment \n <button class='btn btn-primary' onclick='addComplete(event,{appoint.id})'>Attended</button> \n <button class='btn btn-secondary' onclick='addComplete(event,{appoint.id})'>Not Attended</button>"
                        try:
                            message1 = Messages.objects.filter(recipient=patient,subject=header)
                            #look for the exact message
                            res1 = False
                            if len(message1) > 0:
                                for message in message1:
                                    if f"{docappoint.startdate.strftime('%m/%d/%Y %I:%M %p')} to {docappoint.enddate.strftime('%m/%d/%Y %I:%M %p')}" in message.body and "first message concerning this appointment" in message.body:
                                        res1 = True
                                        message1 = message
                                        
                            if res1 == False:
                                #send first message
                                patientmessage = Messages(recipient=patient,subject=header,body=patientbody)
                                patientmessage.save()
                            else:
                                #check if admin has sent second message 
                                try:
                                    res2 = False
                                    patientbody2 = f"Hi {patient.first_name} {patient.last_name}.\n Hope your day was wonderful. We are checking on you again if you have completed your appointment which lasted from {docappoint.startdate.strftime('%m/%d/%Y %I:%M %p')} to {docappoint.enddate.strftime('%m/%d/%Y %I:%M %p')} and we hope it was wonderful. Please note that this message will be sent once more after then the appointment will be deleted \n <button class='btn btn-primary' onclick='addComplete(event,{appoint.id})'>Attended</button> \n <button class='btn btn-secondary' onclick='addComplete(event,{appoint.id})'>Not Attended</button>"
                                    message2 = Messages.objects.filter(recipient=patient,subject=header)
                                    if len(message2) > 0:
                                        for message in message2:
                                            if f"{docappoint.startdate.strftime('%m/%d/%Y %I:%M %p')} to {docappoint.enddate.strftime('%m/%d/%Y %I:%M %p')}" in message.body and "sent once more" in message.body:
                                                res2 = True
                                                message2 = message
                                                
                                    if res2 == False:
                                        #make sure the time difference the first and second message is at least 2 hrs
                                        timestamp1 = message1.timestamp.strftime('%m/%d/%Y %I:%M %p')
                                        timestamp1 = datetime.strptime(timestamp1,'%m/%d/%Y %I:%M %p')
                                        
                                        difference1 = today - timestamp1
                                        difference1 = difference1.total_seconds()
                                        difference1 = difference1 / 3600
                                        #convert to hrs
                                        if difference1 >=2:
                                            #send the second message    
                                            patientmessage2 = Messages(recipient=patient,subject=header,body=patientbody2)
                                            patientmessage2.save()
                                    else:
                                        #check if admin has sent the third message
                                        try:
                                            res3 = False
                                            patientbody3 = f"Hi {patient.first_name} {patient.last_name}.\n Hope your day was wonderful. We are checking on you again if you have completed your appointment which lasted from {docappoint.startdate.strftime('%m/%d/%Y %I:%M %p')} to {docappoint.enddate.strftime('%m/%d/%Y %I:%M %p')} and we hope it was wonderful. Please note that this message is the last concerning this appointment,if you don't reply within 2 hrs it will be deleted \n <button class='btn btn-primary' onclick='addComplete(event,{appoint.id})'>Attended</button> \n <button class='btn btn-secondary' onclick='addComplete(event,{appoint.id})'>Not Attended</button>"
                                            message3 = Messages.objects.filter(recipient=patient,subject=header,body=patientbody3)
                                            if len(message3) > 0:
                                                for message in message3:
                                                    if f"{docappoint.startdate.strftime('%m/%d/%Y %I:%M %p')} to {docappoint.enddate.strftime('%m/%d/%Y %I:%M %p')}" in message.body and "last concerning this appointment,if you don't reply within 2 hrs" in message.body:
                                                        res3 = True
                                                        message3 = message
                                                        
                                            if res3 == False:
                                                #make sure that the time difference between the second and third message is at least 2 hrs
                                                timestamp2 = message2.timestamp.strftime('%m/%d/%Y %I:%M %p')
                                                timestamp2 = datetime.strptime(timestamp2,'%m/%d/%Y %I:%M %p')
                                                
                                                difference2 = today - timestamp2
                                                difference2 = difference2.total_seconds()
                                                difference2 = difference2 / 3600
                                                if difference2  >= 2:
                                                    #send third message
                                                    patientmessage3 = Messages(recipient=patient,subject=header,body=patientbody3)
                                                    patientmessage3.save()
                                            else:
                                                #delete after 2hrs of no reply
                                                timestamp3 = message3.timestamp.strftime('%m/%d/%Y %I:%M %p')
                                                timestamp3 = datetime.strptime(timestamp3,'%m/%d/%Y %I:%M %p')
                                                difference3 = today - timestamp3
                                                difference3 = difference3.total_seconds()
                                                difference3 = difference3 / 3600
                                                if difference3 >= 2:
                                                    #send message to  doctor and patient that appointment has been deleted
                                                    docbody = f"Hi Dr {doc.first_name} {doc.last_name}.\n This message is to inform you that the appointment from {docappoint.startdate.strftime('%m/%d/%Y %I:%M %p')} to {docappoint.enddate.strftime('%m/%d/%Y %I:%M %p')} that was made by patient {patient.first_name} {patient.last_name} because the patient didn't confirm whether the appointment held or not.If it held please report to the appropriate quarters"
                                                    patientbody4 = f"Hi {patient.first_name} {patient.last_name}.\n This message is to inform you that the appointment from {docappoint.startdate.strftime('%m/%d/%Y %I:%M %p')} to {docappoint.enddate.strftime('%m/%d/%Y %I:%M %p')} has just been deleted because you didn't confirm whether the appointment held or not. If it held,please go to the appropriate quarters to report this"
                                                    header = "Deletion of an appointment"
                                                    docmessage = Messages(recipient = doc,subject=header,body=docbody)
                                                    docmessage.save()
                                                    patientmessage4 = Messages(recipient = patient,subject=header,body=patientbody4)
                                                    patientmessage4.save()
                                                    try:
                                                        #add it to deleted appointments
                                                        newdeleted1 = DeletedAppointment.objects.create(doctor=doc,patient=patient,startdate=docappoint.startdate,enddate=docappoint.enddate)
                                                        newdeleted1.save()
                                                        
                                                    except IntegrityError:
                                                        return JsonResponse({"message":"Deleted appointment couldn't be created"},status=400)
                                                    
                                                    #delete appointments
                                                    appoint.delete()
                                                    docappoint.delete()
                                        except Messages.DoesNotExist:
                                            #make sure that the time difference between the second and third message is at least 2 hrs
                                            timestamp2 = message2.timestamp.strftime('%m/%d/%Y %I:%M %p')
                                            timestamp2 = datetime.strptime(timestamp2,'%m/%d/%Y %I:%M %p')
                                            
                                            difference2 = today - timestamp2
                                            difference2 = difference2.total_seconds()
                                            difference2 = difference2 / 3600
                                            if difference2 >= 2:
                                                #send third message
                                                patientmessage3 = Messages(recipient=patient,subject=header,body=patientbody3)
                                                patientmessage3.save()
                                except Messages.DoesNotExist:
                                    #make sure the time difference the first and second message is at least 2 hrs
                                    timestamp1 = message1.timestamp.strftime('%m/%d/%Y %I:%M %p')
                                    timestamp1 = datetime.strptime(timestamp1,'%m/%d/%Y %I:%M %p')
                                    
                                    difference1 = today - timestamp1
                                    difference1 = difference1.total_seconds()
                                    difference1 = difference1 / 3600
                                    #convert to hrs
                                    if difference1 >=2:
                                        #send the second message    
                                        patientmessage2 = Messages(recipient=patient,subject=header,body=patientbody2)
                                        patientmessage2.save()
                        except Messages.DoesNotExist:
                            #send first message
                            patientmessage = Messages(recipient=patient,subject=header,body=patientbody)
                            patientmessage.save()
                            
                except ObjectDoesNotExist:
                    #send a message to the doctor
                    body = f"Hi, {docappoint.doctor.first_name} {docappoint.doctor.last_name}.\n This is to inform you that the appointment you created from {docappoint.startdate.strftime('%m/%d/%Y %I:%M %p')} to {docappoint.enddate.strftime('%m/%d/%Y %I:%M %p')} has expired.\n As no patient made the appointment,do well to create another. \n Thanks for using this webapp and continue to save lives and provide fantastic healthcare"
                    try:
                        newmessage = Messages(recipient=docappoint.doctor,subject="Expired appointment",body=body)
                        newmessage.save()
                        docappoint.delete()                        
                    except IntegrityError:
                        return JsonResponse({"message":"Couldn't send message"},status=400)   
                                 
            
        return JsonResponse({"message":"Updated"},status=201)   
    else:
        return JsonResponse({"message":"wrong request method"},status=403)
    
    
@login_required(login_url="hospital:login")
def add_complete(request,id):
    user = request.user
    if user.is_email_verified:
        if request.method == "PUT" and user.role == "Patient":
            data = json.loads(request.body)
            command = data.get("command"," ")
            command = command.lower()
            if command == "add":
                
                #check if patientappointment exists and user created it
                try:
                    appointment = PatientAppointment.objects.get(pk=id,patient=user)
                    patientprofile = PatientInfo.objects.get(patient=user)
                    doc = appointment.appointment.doctor
                    docprofile = DoctorInfo.objects.get(doctor=doc)
                    
                    #check if the appointment is in the doctor's active appointments and also the patient
                    docprofile.appointments.get(id=appointment.id)
                    patientprofile.appointments.get(id=appointment.appointment.id)
                    
                    
                    #add appointment to completed,remove from active appointments and add to the doctor completed
                    docprofile.appointments.remove(appointment)
                    docprofile.completed.add(appointment)
                    patientprofile.appointments.remove(appointment.appointment)
                    patientprofile.completed.add(appointment)
                    
                    #send a completion message to the doctor and the patient
                    docbody = f"Hello Dr {doc.first_name} {doc.last_name}. \n Thanks for completing your appointment with {user.first_name} {user.last_name} from {appointment.appointment.startdate.strftime('%m/%d/%Y %I:%M %p')} to {appointment.appointment.enddate.strftime('%m/%d/%Y %I:%M %p')} \n We hope it was fruitful.\n If you didn't complete this appointment,pls report to the appropriate quarters"
                    patientbody = f"Hello {user.first_name} {user.last_name}. \n Thanks for completing your appointment with Dr {doc.first_name} {doc.last_name} from {appointment.appointment.startdate.strftime('%m/%d/%Y %I:%M %p')} to {appointment.appointment.enddate.strftime('%m/%d/%Y %I:%M %p')} \n We hope it was fruitful.\n If you didn't complete this appointment,pls report to the appropriate quarters"
                    try:
                        header = f"Completed appointment🎉🎉"
                        docmessage = Messages(recipient=doc,subject=header,body=docbody)
                        docmessage.save()
                        patientmessage = Messages(recipient=user,subject=header,body=patientbody)
                        patientmessage.save()
                        
                        mail_body = f"You have marked this appointment as complete.If you didn't,report to the appropriate quarters"
                        #get the messages and edit them
                        usermailbox = Messages.objects.filter(recipient=user)
                        for mail in usermailbox:
                            startdate = appointment.appointment.startdate.strftime('%m/%d/%Y %I:%M %p')
                            enddate = appointment.appointment.enddate.strftime('%m/%d/%Y %I:%M %p')
                            if startdate in mail.body and enddate in mail.body:
                                mail.body = mail_body
                                mail.save()
                                
                        return JsonResponse({"message":mail_body},status=201)
                    except IntegrityError:
                        return JsonResponse({"message":"Updated succesfully but couldnt send message"},status=400)
                    
                except PatientAppointment.DoesNotExist or PatientInfo.DoesNotExist or User.DoesNotExist or DocAppointment.DoesNotExist or DoctorInfo.DoesNotExist or IntegrityError:
                    return JsonResponse({"message":"Appointment doesn't exist/profile doesn't exist/Doctor doesn't exist/Doctor profile doesnt exist"},status=403)
                
            elif command == "remove":
                #remove the patientappointment
                
                #check if patientappointment exists and user created it
                try:
                    appointment = PatientAppointment.objects.get(pk=id,patient=user)
                    docappoint = appointment.appointment
                    doc = docappoint.doctor
                    docprofile = DoctorInfo.objects.get(doctor=doc)
                    patient = appointment.patient
                    
                    #send deletion confirmation to the doctor and the user
                    docbody = f"Hi Dr {doc.first_name} {doc.last_name}.\n This message is to inform you that the appointment from {docappoint.startdate.strftime('%m/%d/%Y %I:%M %p')} to {docappoint.enddate.strftime('%m/%d/%Y %I:%M %p')} that was made by patient {patient.first_name} {patient.last_name} because the patient confirmed that the appointment didn't hold.If it held please report to the appropriate quarters"
                    patientbody4 = f"Hi {patient.first_name} {patient.last_name}.\n This message is to inform you that the appointment from {docappoint.startdate.strftime('%m/%d/%Y %I:%M %p')} to {docappoint.enddate.strftime('%m/%d/%Y %I:%M %p')} has just been deleted because you confirmed that the appointment didn't hold. If it held,please go to the appropriate quarters to report this"
                    header = "Deletion of an appointment"
                    docmessage = Messages(recipient = doc,subject=header,body=docbody)
                    docmessage.save()
                    patientmessage4 = Messages(recipient = patient,subject=header,body=patientbody4)
                    patientmessage4.save()
                    
                    try:
                        #add to deleted appointments
                        newdeleted = DeletedAppointment.objects.create(doctor=doc,patient=patient,startdate=docappoint.startdate,enddate=docappoint.enddate)
                        newdeleted.save()
                        #delete patientappointment and appointments
                        appointment.delete()
                        docappoint.delete()
                        
                        mail_body = f"You have marked this appointment not attended and has been removed.If you didn't,report to the appropriate quarters"
                        #get the messages and edit them
                        usermailbox = Messages.objects.filter(recipient=user)
                        for mail in usermailbox:
                            startdate = appointment.appointment.startdate.strftime('%m/%d/%Y %I:%M %p')
                            enddate = appointment.appointment.enddate.strftime('%m/%d/%Y %I:%M %p')
                            if startdate in mail.body and enddate in mail.body:
                                mail.body = mail_body
                                mail.save()
                        
                        return JsonResponse({"message":mail_body},status=201)
                    except Exception as e:
                        return JsonResponse({"message":f"Appointment couldn't be created {e}"},status=400)
                
                except PatientAppointment.DoesNotExist or DocAppointment.DoesNotExist or User.DoesNotExist or DoctorInfo.DoesNotExist:
                    return JsonResponse({"message":"Patient appointment doesn't exist"},status=400)
                
            else:
                return JsonResponse({"message":"Wrong command"},status=400)
                    
        else:
            return JsonResponse({"message":"User not logged in/wrong request method"})
    
    
@login_required(login_url="hospital:login")
def get_messages(request,page_num):
    user = request.user
    if request.method == "GET" and user.is_email_verified:
        messages = Messages.objects.filter(recipient=user)
        messages = messages.order_by("-timestamp").all()
        messages = Paginator(messages,15) 
        pagerange = messages.page_range
        if page_num in pagerange:
            messages = messages.page(page_num)
            return JsonResponse([message.serialize() for message in messages],safe=False,status=201)
        else:
            return JsonResponse({"message":"Page doesn't exist"},status=400)
    else:
        return JsonResponse({"message":"Wrong request method"},status=400)


@login_required(login_url="hospital:login")
def message_details(request):
    user = request.user
    if request.method == "POST" and user.is_email_verified:
        data = json.loads(request.body)
        pk = data.get("pk"," ")
        try:
            message = Messages.objects.get(pk=int(pk),recipient=user)
            #make the message read
            try:
                message.read = True
                message.save()
                
            except IntegrityError:
                return JsonResponse({"message":"Couldn't save new changed"},status=400)
            
            return JsonResponse(message.serialize(),safe=False,status=201)
        except Messages.DoesNotExist:
            return JsonResponse({"message":"Message doesn't exist"},status=403)
    else:
        return JsonResponse({"message":"Wrong request method"},status=400)


def check_new_messages(request):
    user = request.user
    if request.method == "GET" and user.is_authenticated and user.is_email_verified:
        #try getting messages user has read
        try:
            messages = Messages.objects.filter(recipient=user,read=False)
            amount = len(messages)
            return JsonResponse({"status":amount},status=201)
        except Messages.DoesNotExist:
            return JsonResponse({"message":False},status=201)
    else:
        return JsonResponse({"message":"Wrong request method/user doesn't exist"},status=403)

@login_required(login_url="hospital:login")
def get_carts_drugs(request,page_num):
    user = request.user
    if user.is_email_verified and request.method == "GET":
        patientprofile = PatientInfo.objects.get(patient=user)
        carts = patientprofile.cart.all()
        carts = carts.order_by("amount").all()
        carts = Paginator(carts,6)
        if page_num in carts.page_range:
            carts = carts.page(page_num)
            return JsonResponse([cart.serialize() for cart in carts],safe=False,status=201)
        else:
            return JsonResponse({"message":"Page doesn't exist"},status=400)
    else:
        return JsonResponse({"Wrong request method/user not logged in"},status=403)
   
    
@login_required(login_url="hospital:login")
def change_password(request):
    user = request.user
    if user.is_email_verified and request.method == "PUT":
        send_password_mail(request,user)
        return JsonResponse({"message":"A confirmation mail has been sent,pls check"},status=201)
    
    else:
        return JsonResponse({"message":"Invalid request method/user not logged in"},status=403)
    
    
@login_required(login_url="hospital:login")
def get_patient_appointment(request,page_num):
    user = request.user
    if user.is_email_verified and request.method == "GET":
        #get users that have made appointments with the doctor
        try:
            docprofile = DoctorInfo.objects.get(doctor=user)

        except DoctorInfo.DoesNotExist:
            #create the docprofile
            docprofile = DoctorInfo(doctor=user,descr=f"I am {user.username}")
            docprofile.save()
            
        appointments = docprofile.appointments.all()
        appointments = appointments.order_by("appointment").all()
        appointments = Paginator(appointments,10)
        if page_num in appointments.page_range:
            appointments = appointments.page(page_num)
            return JsonResponse([appointments.serialize() for appointments in appointments],safe=False,status=201)
        else:
            return JsonResponse({"message":"Page doesn't exist"},status=400)
    else:
        return JsonResponse({"Wrong request method/user not logged in"},status=403)
    
    
