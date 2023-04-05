from django.urls import path

from . import views

app_name="hospital"
urlpatterns = [
    path("",views.index,name="index"),
    path("login/",views.login_view,name="login"),
    path("register/",views.register,name="register"),
    path("activate-user/<uidb64>/<token>",views.activate_user,name="activate"),
    path("logout/",views.logout_view,name="logout"),
    path("doctor/",views.doctor_view,name="doctor"),
    path("patient/",views.patient_view,name="patient"),
    path("availability/",views.availability,name="available"),
    path("patient-appointment/",views.patient_appointment,name="patient_appointment"),
    path("pharmacy/",views.pharmacy_view,name="pharmacy"),
    path("messages/",views.messages_views,name="messages"),
    path("profile/",views.get_profile,name="profile"),
    path("send-mail/<str:username>",views.send_action_mail,name="send_mail"),
    path("cart/",views.cart_view,name="cart"),
    path("edit-profile/",views.edit_profile,name="edit_profile"),
    path("send-password/<str:username>",views.send_password_mail,name="send_password_mail"),
    path("reset-password/<uidb64>/<token>",views.reset_password,name="reset_password"),
    path("set-password/",views.set_password,name="set_password"),
    
    
    
    #APIRoutes
    path("skills",views.get_skills,name="skills"),
    path("get-doctors/<int:page_num>",views.get_doctors,name="get-doctors"),
    path("doctor-profile/<int:username>",views.doctor_profile,name="doctor-profile"),
    path("search-doctors/<str:search_type>/<str:search_term>",views.search_doctor,name="search-doctors"),
    path("add-availability",views.add_availability,name="add-availability"),
    path("remove-availability/<int:id>",views.remove_availability,name="remove-availability"),
    path("add-appointment/<int:id>",views.add_appointment,name="add-appointment"),
    path("remove-appointment/<int:id>",views.remove_appointment,name="remove-appointment"),
    path("get-drugs/<int:page_num>",views.get_drugs,name="get-drugs"),
    path("search-drugs",views.search_drugs,name="search-drugs"),
    path("drug-details/<int:drug_id>",views.drug_details,name="drug-details"),
    path("add-cart",views.add_cart,name="add-cart"),
    path("remove-cart",views.remove_cart,name="remove-cart"),
    path("drug-order/<int:drug_id>",views.drug_order,name="drug-order"),
    path("checkout",views.checkout,name="checkout"),
    path("update-appointments",views.update_appointments,name="update-appointment"),
    path("add_complete/<int:id>",views.add_complete,name="add_complete"),
    path("get-messages/<int:page_num>",views.get_messages,name="get-messages"),
    path("message-details",views.message_details,name="message-details"),
    path("new-messages",views.check_new_messages,name="check-messages"),
    path("cart-drugs/<int:page_num>",views.get_carts_drugs,name="cart-drugs"),
    path("change-password",views.change_password,name="change_password"),
    path("patient-appointments/<int:page_num>",views.get_patient_appointment,name="get_patient_appointment"),
    
]
