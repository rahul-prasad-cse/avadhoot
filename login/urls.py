from django.conf.urls import url
from . import views
from django.contrib.auth.views import login
app_name = 'login'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^products/', views.products, name='products'),
    url(r'^signin/',views.signin,name = 'signin'),
    url(r'^orders/',views.orders,name = 'orders'),
    url(r'^contactus/',views.contactus,name = 'contactus'),
    url(r'^sendmail/',views.sendmail,name = 'sendmail'),
    url(r'^cart/',views.cart,name = 'cart'),
    url(r'^signup/',views.signup,name='signup'),
    url(r'^register/',views.UserFormView.as_view(),name = 'register'),
    url(r'^logout/',views.logout,name = 'logout'),
    url(r'^addtocart/(?P<productid>[0-9]+)/$',views.addtocart,name = 'addtocart'),
    url(r'^removecartitem/(?P<itemid>[0-9]+)/(?P<custid>[0-9]+)/$',views.removecartitem, name = 'removecartitem'),
    url(r'^placeorder/',views.placeorder,name = 'placeorder'),
    url(r'^cancelorder/(?P<orderid>[0-9]+)/$',views.cancelorder,name= 'cancelorder'),
    url(r'^adminpages/',views.adminpages,name = 'adminpages'),
    url(r'^redirecttopay/(?P<orderid>[0-9]+)/$',views.redirecttopay,name = 'redirecttopay'),
    url(r'^feedback/',views.feedback,name = 'feedback'),
    url(r'^viewfeedback',views.viewfeedback,name ='viewfeedback'),

    url(r'^admin_user_details/',views.admin_user_details,name = 'admin_user_details'),
    url(r'^admin_orders/',views.admin_orders,name = 'admin_orders'),
    url(r'^admin_employee/',views.admin_employee,name = 'admin_employee'),
    url(r'^admin_products/',views.admin_products,name = 'admin_products'),
    url(r'^admin_supplier/', views.admin_supplier, name='admin_supplier'),
    url(r'^admin_stock/',views.admin_stock,name = 'admin_stock'),

    url(r'^view_user_orders/(?P<orderid>[0-9]+)/$',views.view_user_orders,name = 'view_user_orders'),
    url(r'^addemployee/',views.addemployee,name='addemployee'),
    url(r'^removeemployee/(?P<emplid>[0-9]+)/$',views.removeemployee,name = 'removeemployee'),
    url(r'^insertemployee/',views.insertemployee,name = 'insertemployee'),
    url(r'^viewstockproduct/(?P<prodid>[0-9]+)/$',views.viewstockproduct,name='viewstockproduct'),
    url(r'^viewstocksupplier/(?P<suppid>[0-9]+)/$',views.viewstocksupplier,name='viewstocksupplier'),
    url(r'^addsupplier/',views.addsupplier,name='addsupplier'),
    url(r'^insertsupplier/',views.insertsupplier,name = 'insertsupplier'),
    url(r'^addstock/',views.addstock,name='addstock'),
    url(r'^insertstock/',views.insertstock,name = 'insertstock'),


]