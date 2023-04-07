from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from cloudinary.models import CloudinaryField

Role_CHOICES = (
    ("Doctor","Doctor"),
    ("Patient","Patient"),
)
    
# Create your models here.
class User(AbstractUser):
    role = models.CharField(choices=Role_CHOICES,max_length=50,default="Patient")
    profilepic = CloudinaryField('image')
    is_email_verified = models.BooleanField(default=False)
    
    def serialize(self):
        return{
            "id": self.id,
            "username":self.username,
            "role": self.role,
            "profilepic": self.profilepic.url,
            "first_name": self.first_name,
            "last_name": self.last_name,
        }

class Skills(models.Model):
    code = models.CharField(max_length=5)
    skill = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.skill}({self.code})"
    
    def serialize(self):
        return{
            "id":self.id,
            "skill":self.skill,
        }
    

class DocAppointment(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.PROTECT,related_name="available")
    startdate = models.DateTimeField(auto_now=False, auto_now_add=False,null=True,blank=True)
    enddate = models.DateTimeField(auto_now=False, auto_now_add=False,null=True,blank=True)
    
    def __str__(self):
        return f"{self.id}: {self.doctor} is available {self.startdate.strftime('%m %d, %Y, %I:%M %p')} to {self.enddate.strftime('%m %d, %Y, %I:%M %p')}"
    
    def serialize(self):
        return{
            "id": self.id,
            "startdate": timezone.localtime(self.startdate).strftime("%m %d, %Y, %I:%M %p"),
            "enddate": timezone.localtime(self.enddate).strftime("%m %d, %Y, %I:%M %p"),
        }
        
    # def is_valid_docappointment(self):
    #     return
    
    
class DeletedAppointment(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.PROTECT,related_name="deleteddoctorappointment")
    patient = models.ForeignKey(User, on_delete=models.PROTECT,related_name="deletedpatientappointment")
    startdate = models.DateTimeField(auto_now=False, auto_now_add=False,null=True,blank=True)
    enddate = models.DateTimeField(auto_now=False, auto_now_add=False,null=True,blank=True)
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
    
    
    def __str__(self):
        return f"{self.id}: The appointment made by {self.doctor.username} that was from {self.startdate.strftime('%m %d, %Y, %I:%M %p')} to {self.enddate.strftime('%m %d, %Y, %I:%M %p')} has been deleted by {self.patient.username} at {self.timestamp.strftime('%m %d, %Y, %I:%M %p')}"
    
    def serialize(self):
        return{
            "id": self.id,
            "doctor": self.doctor.serialize(),
            "patient": self.patient.serialize(),
            "startdate": self.startdate.strftime("%m %d, %Y, %I:%M %p"),
            "enddate": self.enddate.strftime("%m %d, %Y, %I:%M %p"),
            "timestamp": self.timestamp.strftime("%m %d, %Y, %I:%M %p")
        }
        
    # def is_valid_docappointment(self):
    #     return

class PatientAppointment(models.Model):
    patient = models.ForeignKey(User,on_delete=models.PROTECT,related_name="appointee")
    appointment = models.OneToOneField(DocAppointment,on_delete=models.CASCADE,related_name="patientappoint")
    
    def __str__(self):
        return f"{self.patient} wants to see the doctor {self.appointment}"
    
    def serialize(self):
        return{
            "id": self.id,
            "patient": self.patient.serialize(),
            "appointment": self.appointment.serialize(),
        }
        
    # def is_valid_patientappoint(self):
    #     return
    
class Messages(models.Model):
    recipient = models.ForeignKey(User,on_delete=models.PROTECT,related_name="receivers")
    subject = models.CharField(max_length=200)
    body = models.TextField(max_length=500)
    read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
    
    def __str__(self):
        return f"{self.recipient.username} has a message with a subject of {self.subject} and a body of {self.body} sent {self.timestamp.strftime('%m %d, %Y, %I:%M %p')} and its read status is {self.read}"
    
    def serialize(self):
        return{
            "id": self.id,
            "recipient": self.recipient.username,
            "subject": self.subject,
            "body": self.body,
            "read": self.read,
            "timestamp": self.timestamp.strftime("%m %d, %Y, %I:%M %p")
        }
    
class Pharmacy(models.Model):
    drugpic = CloudinaryField('image')
    name = models.CharField(max_length=150)
    descr = models.TextField()
    prescription = models.TextField()
    orders = models.IntegerField(default=0)
    price = models.IntegerField()
    instock = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
    
    def __str__(self):
        return f"{self.id}: {self.name} has {self.descr} and the prescriptions is {self.prescription} and has {self.orders} orders created on {self.timestamp.strftime('%m %d, %Y, %I:%M %p')} and costs {self.price} and there are {self.instock} packs left"
    
    def serialize(self):
        return{
            "id": self.id,
            "drugpic": self.drugpic.url,
            "name": self.name,
            "descr": self.descr,
            "prescription": self.prescription,
            "orders": self.orders,
            "instock": self.instock,
            "price": self.price,
            "timestamp": self.timestamp.strftime("%m %d, %Y, %I:%M %p")
        }
        
class Order(models.Model):
    patient = models.ForeignKey(User,on_delete=models.CASCADE,related_name="orderer")
    amount = models.IntegerField(default=0)
    itemprice = models.IntegerField(default=0)
    drug = models.ForeignKey(Pharmacy,on_delete=models.CASCADE,related_name="ordered_drugs")
    sucessful = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.patient.username} ordered for {self.drug.name} and the orderpositon is {self.sucessful}"
    
    def serialize(self):
        return{
            "id":self.id,
            "patient": self.patient.serialize(),
            "drug": self.drug.serialize(),
            "amount": self.amount,
            "price": self.itemprice,
            "successful": self.sucessful,
        }
    
    

class DoctorInfo(models.Model):
    doctor = models.OneToOneField(User, on_delete=models.PROTECT,related_name="healthcare")
    descr = models.TextField(max_length=250)
    skills = models.ManyToManyField(Skills,related_name="workskills",blank=True)
    appointments = models.ManyToManyField(PatientAppointment,related_name="patientappointments",blank=True)
    availables = models.ManyToManyField(DocAppointment,related_name="timeavailable",blank=True)
    completed = models.ManyToManyField(PatientAppointment,related_name="appointmentscomplete",blank=True,default=None)
    
    def __str__(self):
        return f"{self.doctor} {self.descr} and is skilled in {self.skills.all()} has {self.appointments.all()} appointments and is available {self.availables}"
    
    def serialize(self):
        return{
            "id": self.id,
            "doctor": self.doctor.username,
            "descr": self.descr,
            "skills": [skill.serialize() for skill in self.skills.all()],
            "appointments": [appoint.serialize() for appoint in self.appointments.all()],
            "available": [avail.serialize() for avail in self.availables.all()],
        }
        
    # def is_valid_doctorinfo(self):
    #     return
    
    
class PatientInfo(models.Model):
    patient = models.OneToOneField(User,on_delete=models.PROTECT,related_name="customers")
    appointments = models.ManyToManyField(DocAppointment,related_name="appointments",blank=True)
    completed = models.ManyToManyField(PatientAppointment,related_name="patientcomplete",blank=True,default=None)
    cart = models.ManyToManyField(Order,blank=True,related_name="drugs_carted",default=None)
    successful_orders = models.ManyToManyField(Order,blank=True,related_name="orders_successful",default=None)
    cancelled_orders = models.ManyToManyField(Order,blank=True,related_name="orders_cancelled",default=None)
    
    def __str__(self):
        return f"{self.patient} has made {self.appointments.all()} appointments"
    
    def serialize(self):
        return{
            "patient":self.patient,
            "appointments":[appoint.serialize() for appoint in self.appointments.all()],
            "available": [avail.serialize() for avail in self.cancelled.all()],
            "completed": [complete.serialize() for complete in self.completed.all()],
            "cart": [cart.serialize() for cart in self.cart.all()],
            "successful_orders": [success.serialize() for success in self.successful_orders.all()],
            "cancelled_orders": [cancelled.serialize() for cancelled in self.cancelled_orders.all()],
        }
    
    