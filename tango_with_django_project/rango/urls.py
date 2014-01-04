from django.conf.urls import patterns, url

from rango import views

urlpatterns = patterns('',
        url(r'^$', views.index, name='index'),
        url(r'^about/$', views.about, name='about'),
        url(r'^add_category/$', views.add_category, name = "add category"),
        url(r'^register/$', views.register, name = "register"),
        url(r'^login/$', views.user_login, name='login'),
        url(r'^category/(?P<category_name_url>\w+)/add_page/$', views.add_page, name='add page'), # New!
        url(r'^category/(?P<category_name_url>\w+)/$', views.category, name='category'), # New!
        url(r'^restricted/', views.restricted, name='restricted'),
        url(r'^logout/', views.user_logout, name='user logout'),
        url(r'^profile/', views.profile, name='profile'),
        url(r'^goto/', views.track_url, name='track_url'),
        url(r'^like_category/$', views.like_category, name='like category'),
        url(r'^suggest_category/$', views.suggest_category, name='suggest category'),
        url(r'^auto_add_page/$', views.auto_add_page, name='add page from search'),
        )