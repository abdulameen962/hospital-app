from django.contrib import admin

from .models import *
# Register your models here.
class SkillAdmin(admin.ModelAdmin):
    list_display= ("code","skill")
    
class DocAppointmentAdmin(admin.ModelAdmin):
    list_display = ("doctor","startdate","enddate")
    
class PatientAdmin(admin.ModelAdmin):
    list_display = ("patient","appointment")
    # filter_horizontal= ("appointment",)
    
class DocInfoAdmin(admin.ModelAdmin):
    list_display = ("doctor","descr",)
    filter_horizontal = ("skills","appointments","availables","completed")
    
class PatientInfoAdmin(admin.ModelAdmin):
    list_display= ("patient",)
    filter_horizontal= ("appointments","completed","cart","successful_orders","cancelled_orders")
    
class MessagesAdmin(admin.ModelAdmin):
    list_display= ("recipient","subject","body","read","timestamp")    
    
class PharmacyAdmin(admin.ModelAdmin):
    list_display= ("id","name","descr","prescription","orders","price","instock","timestamp","drugpic")   
    
class OrderAdmin(admin.ModelAdmin):
    list_display= ("id","patient","drug","sucessful")  
    
class DeletedAppointmentAdmin(admin.ModelAdmin):
    list_display= ("id","doctor","patient","startdate","enddate","timestamp")  

admin.site.register(User)
admin.site.register(Skills,SkillAdmin)
admin.site.register(DocAppointment,DocAppointmentAdmin)
admin.site.register(PatientAppointment,PatientAdmin)
admin.site.register(DoctorInfo,DocInfoAdmin)
admin.site.register(PatientInfo,PatientInfoAdmin)
admin.site.register(Messages,MessagesAdmin)
admin.site.register(Pharmacy,PharmacyAdmin)
admin.site.register(Order,OrderAdmin)
admin.site.register(DeletedAppointment,DeletedAppointmentAdmin)

