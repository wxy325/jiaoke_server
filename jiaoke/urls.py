from django.conf.urls import patterns, include, url

from django.contrib import admin
import ma.views.user
import ma.views.driver


admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'jiaoke.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^user_register$', ma.views.user.userRegister),
    url(r'^user_login$', ma.views.user.userLogin),
    url(r'^user_logout$', ma.views.user.userLogout),
    url(r'^user_get_info$', ma.views.user.userGetInfo),

    #driver
    url(r'^driver/update_location$', ma.views.driver.driverUpdateLocation),
    url(r'^driver/get_location$',ma.views.driver.driverGetLocation),
    url(r'^driver/get_order$',ma.views.driver.driverGetOrder),
    url(r'^driver/update_order$',ma.views.driver.driverUpdateOrder),

)
