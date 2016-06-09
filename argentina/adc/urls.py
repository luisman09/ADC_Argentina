from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.HomepageView.as_view(), name='homepage'),    
    url(r'^consulta_simple/$', views.Consulta_SimpleView.as_view(), name='consulta_simple'),
    url(r'^consulta_agrupados/$', views.Consulta_AgrupadosView.as_view(), name='consulta_agrupados'),
    url(r'^resultados/$', views.resultados, name='resultados'),
    url(r'^busqueda_ajax_prov/$', views.BusquedaAjaxProvView.as_view(), name='busqueda_ajax_prov'),
    url(r'^busqueda_ajax_dist/$', views.BusquedaAjaxDistView.as_view(), name='busqueda_ajax_dist'),
    url(r'^busqueda_ajax_barr/$', views.BusquedaAjaxBarrView.as_view(), name='busqueda_ajax_barr'),
    url(r'^exportar_csv/$', views.exportar_csv, name='exportar_csv'),
    url(r'^exportar_xls/$', views.exportar_xls, name='exportar_xls'),
]

