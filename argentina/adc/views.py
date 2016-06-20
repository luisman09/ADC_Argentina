# -*- coding: utf-8 -*-
from django.http import HttpResponse, JsonResponse
from django.template import RequestContext, loader
from django.shortcuts import get_object_or_404, render, render_to_response
from django.views import generic
from django.apps import apps
from django.db import connection
from django.core import serializers
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import csv
import xlwt
import json
import time
import codecs # Utilizada para la lectura del csv
import os, sys

from .models import *
from .listas import *

last_save = []

# Funciones

def buscarElementoEnLista(e, lista, indice):

    for elem in lista:
        if e == elem[indice]:
            return elem


def encadenarConSeparador(lista_items, separador, lista_busq, indice_busq):
    
    cad = []
    cadena = ""
    try:
        for elem in lista_items:
            e = buscarElementoEnLista(elem, lista_busq, indice_busq)
            cad.append(e[1][1])
        cadena = separador.join(cad)
    except IndexError:
        cadena = 'null'
    return cadena


def buscarCondiciones(c):

    cad = []
    cadena = ""
    try:
        # prov, dist, barr, escs
        if c[0][0] or c[1][0] or c[2][0] or c[3][0]:
            if c[0][0] and not c[1][0]:
                cad.append(lista_condiciones[0][1][1] + " = '" + c[0][0] + "'")
            if c[1][0] and not c[2][0]:
                cad.append(lista_condiciones[0][1][1] + " = '" + c[0][0] + "'" + " AND " + lista_condiciones[1][1][1] + " = '" + c[1][0] + "'")
            if c[2][0] and not c[3][0]:
                cad.append(lista_condiciones[0][1][1] + " = '" + c[0][0] + "'" + " AND " + lista_condiciones[1][1][1] + " = '" + c[1][0] + "'" + " AND " + lista_condiciones[2][1][1] + " = '" + c[2][0] + "'")
            if c[3][0]:
                cad.append(lista_condiciones[0][1][1] + " = '" + c[0][0] + "'" + " AND " + lista_condiciones[1][1][1] + " = '" + c[1][0] + "'" + " AND " + lista_condiciones[2][1][1] + " = '" + c[2][0] + "'" + " AND " + lista_condiciones[3][1][1] + " IN ('" + "','".join(c[3]) + "')")
        # dni
        if c[4][0]:
            cad.append(lista_condiciones[4][1][1] + " = " + c[4][0])
        # nombre, apellido
        if c[5][0]:
            cad.append(lista_condiciones[5][1][1] + " = '" + c[5][0] + "'") 
        if c[6][0]:
            cad.append(lista_condiciones[6][1][1] + " = '" + c[6][0] + "'")
        # sexo
        if c[7][0]:
            cad.append(lista_condiciones[7][1][1] + " = " + c[7][0])    
        # nse
        if c[8][0]:
            cad.append(lista_condiciones[8][1][1] + " IN (" + ",".join(c[8]) + ")")
        # edad
        if c[9][0] or c[10][0]:
            if c[9][0] and c[10][0]:
                cad.append(lista_condiciones[9][1][1] + " BETWEEN " + c[9][0] + " AND " + c[10][0])
            if c[9][0] and not c[10][0]:
                cad.append(lista_condiciones[9][1][1] + " BETWEEN " + c[9][0] + " AND 1000000")
            if c[10][0] and not c[9][0]:
                cad.append(lista_condiciones[9][1][1] + " BETWEEN 0 AND " + c[10][0])
        # concatenacion
        cadena = " AND ".join(cad)
    except IndexError:
        cadena = 'null'  
    return cadena


# Clases

class HomepageView(generic.TemplateView):
    template_name = 'adc/homepage.html'


class Consulta_SimpleView(generic.ListView):
    template_name = 'adc/consulta_simple.html'
    context_object_name = 'lista_attos'
    queryset = lista_attos

    def get_context_data(self, **kwargs):
        context = super(Consulta_SimpleView, self).get_context_data(**kwargs)
        context['lista_conds'] = lista_conds
        context['provincias'] = Arg_Centro.objects.order_by('provincia').distinct('provincia')
        context['distritos'] = Arg_Centro.objects.order_by('distrito').distinct('distrito')
        context['barrios'] = Arg_Centro.objects.order_by('barrio').distinct('barrio')
        context['sexos'] = lista_sexo
        context['nses'] = lista_nse
        context['ordenes'] = lista_orden[2:4]
        return context


class Consulta_AgrupadosView(generic.ListView):
    template_name = 'adc/consulta_agrupados.html'
    context_object_name = 'lista_attos'
    queryset = lista_ag_attos

    def get_context_data(self, **kwargs):
        context = super(Consulta_AgrupadosView, self).get_context_data(**kwargs)
        context['lista_agrupados'] = lista_agrupados
        context['lista_conds'] = lista_conds
        context['provincias'] = Arg_Centro.objects.order_by('provincia').distinct('provincia')
        context['distritos'] = Arg_Centro.objects.order_by('distrito').distinct('distrito')
        context['barrios'] = Arg_Centro.objects.order_by('barrio').distinct('barrio')
        context['sexos'] = lista_sexo
        context['nses'] = lista_nse
        context['ordenes'] = lista_orden[0:3]
        return context


def crearConsulta(attos_select, no_nulos, agrupado, condiciones, orden, limite):

    # Inicialización
    consulta = ""
    select_items = ""
    from_items = ""
    where_terms = []
    where_items = ""
    agrupado_item = ""
    group_by_items = ""
    order_by_items = ""
    limit_items = ""
    # Items SELECT, GROUP BY y WHERE de no nulidad
    select_items = encadenarConSeparador(attos_select, ", ", lista_attos, 0)
    if agrupado: 
        agrupado_item = encadenarConSeparador(agrupado, ", ", lista_agrupados, 0)
        if select_items:
            group_by_items = " GROUP BY " + select_items
            select_items = agrupado_item + ', ' + select_items
        else:
            select_items = agrupado_item
    else:
        if no_nulos:
            where_terms.append(encadenarConSeparador(no_nulos, " AND ", lista_no_nulos, 0))
    # Items WHERE de condiciones por usuarios
    conds = buscarCondiciones(condiciones)
    print conds
    if conds:
        where_terms.append(conds)
    if where_terms:
        where_items = " WHERE " + " AND ".join(where_terms)
    # Items FROM y WHERE de joins
    if ("arg_elector" in select_items) or ("arg_elector" in where_items):
        from_items = "arg_elector"
    if ("arg_centro" in select_items) or ("arg_centro" in where_items):
        if from_items:
            from_items = from_items + ", arg_centro"
        else:
            from_items = "arg_centro" 
    if from_items == "arg_elector, arg_centro":
        where_terms = ["arg_elector.cue = arg_centro.cue"] + where_terms
        where_items = " WHERE " + " AND ".join(where_terms)
    # Items ORDER BY y LIMIT
    print orden[0]
    if ("TOTALMENTE ALEATORIO" in orden[0]):
        print "1"
        order_by_items = " ORDER BY random()"
    elif ("DE MAYOR A MENOR" in orden[0]):
        print "2"
        order_by_items = " ORDER BY " + agrupado_item + " DESC" 
    elif ("DE MENOR A MAYOR" in orden[0]):
        print "3"
        order_by_items = " ORDER BY " + agrupado_item 
    if limite:
        if limite[0]:
            limit_items = " LIMIT " + limite[0]
    # QUERY completo
    if any(k in select_items for k in ("provincia", "distrito", "barrio")) and not "count(" in select_items:
        if order_by_items:
            consulta = "SELECT * FROM (SELECT DISTINCT " + select_items + " FROM " + from_items + where_items + group_by_items + ") AS q" + order_by_items + limit_items + ";" 
        else:
            consulta = "SELECT DISTINCT " + select_items + " FROM " + from_items + where_items + group_by_items + order_by_items + limit_items + ";"
    else:
        consulta = "SELECT " + select_items + " FROM " + from_items + where_items + group_by_items + order_by_items + limit_items + ";"
    return consulta


def ejecutarConsulta(consulta):

    print "la consulta a ejecutar es: "
    print consulta
    cursor = connection.cursor()
    cursor.execute(consulta)
    resultados = cursor.fetchall()
    return resultados


def resultados(request):

    global last_save
    resultados_pag = []
    page = request.GET.get('page')
    if not page:
        attos_select = request.POST.getlist('attos-select')
        no_nulos = request.POST.getlist('no-nulo')              #Solo simple
        agrupado = request.POST.getlist('agrupado')             #Solo agrupados
        prov = request.POST.getlist('prov')
        dist = request.POST.getlist('dist')
        barr = request.POST.getlist('barr')
        escs = request.POST.getlist('escs')
        dni = request.POST.getlist('dni')
        nombre = request.POST.getlist('nombre')
        apellido = request.POST.getlist('apellido')
        sexo = request.POST.getlist('sexo')
        nse = request.POST.getlist('nse')
        minimo = request.POST.getlist('minimo')
        maximo = request.POST.getlist('maximo')
        orden = request.POST.getlist('orden')
        limite = request.POST.getlist('limite')
        # Solo para los de seleccion multiple.
        if len(escs) > 1:
            escs = escs[1:]
        if len(nse) > 1:
            nse = nse[1:]
        # AQUI HAY QUE AVERIGUAR PORQUE DESDE LAS CONSULTAS CON AGRUPADOS los campos escs y nse vienen vacios (seleccion multiple)
        # ESTO NO PASA CON LAS CONSULTAS SIMPLES y deberian funcionar igual. Las siguientes 4 lineas no deberian ir.
        if not escs:
            escs.append(u'')
        if not nse:
            nse.append(u'')
        condiciones = [prov, dist, barr, escs, dni, nombre, apellido, sexo, nse, minimo, maximo]
        print condiciones
        consulta = crearConsulta(attos_select, no_nulos, agrupado, condiciones, orden, limite)
        resultados = ejecutarConsulta(consulta)
        if agrupado:
            attos_select = agrupado + attos_select
        last_save = [attos_select,resultados]
    else:
        resultados = last_save[1]
        attos_select = last_save[0]
    # Paginacion.
    paginator = Paginator(resultados, 10) # Muestra 10 elementos por pagina.
    try:
        resultados_pag = paginator.page(page)
    except PageNotAnInteger:
        resultados_pag = paginator.page(1)
    except EmptyPage:
        resultados_pag = paginator.page(paginator.num_pages)
    context = {'atributos': attos_select, 'resultados': resultados, 'resultados_pag': resultados_pag, 'total_rows': len(resultados)}
    return render(request, 'adc/resultados.html', context)


class BusquedaAjaxProvView(generic.TemplateView):
    
    def get(self, request, *args, **kwargs):
        x = request.GET['prov']
        distritos = Arg_Centro.objects.filter(provincia=x).order_by('distrito').distinct('distrito')
        data = serializers.serialize('json', distritos, fields=('distrito'))
        return HttpResponse(data, content_type='application/json')


class BusquedaAjaxDistView(generic.TemplateView):
    
    def get(self, request, *args, **kwargs):
        y = request.GET['prov']
        x = request.GET['dist']
        barrios = Arg_Centro.objects.filter(provincia=y).filter(distrito=x).order_by('barrio').distinct('barrio')
        data = serializers.serialize('json', barrios, fields=('barrio'))
        return HttpResponse(data, content_type='application/json')


class BusquedaAjaxBarrView(generic.TemplateView):
    
    def get(self, request, *args, **kwargs):
        z = request.GET['prov']
        y = request.GET['dist']
        x = request.GET['barr']
        escuelas = Arg_Centro.objects.filter(provincia=z).filter(distrito=y).filter(barrio=x).order_by('escuela').distinct('escuela')
        data = serializers.serialize('json', escuelas, fields=('escuela'))
        return HttpResponse(data, content_type='application/json')


# La funcion exportar_csv permite la descarga de un archivo csv desde el asistente de consultas
# con los resultados de haber ejecutado alguna consulta.
def exportar_csv(request):

    cabecera = last_save[0]
    resultados = last_save[1]

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="consulta.csv"'
    writer = csv.writer(response)
    row = []
    for elem in cabecera:
        row.append(elem)
    writer.writerow([unicode(s).encode("utf-8") for s in row])
    for elem in resultados:
        row = []
        for e in elem:
            row.append(e)
        writer.writerow([unicode(s).encode("utf-8") for s in row])
    return response


# La funcion exportar_xls permite la descarga de un archivo excel (xlsx) desde el asistente de consultas
# con los resultados de haber ejecutado alguna consulta.
def exportar_xls(request):

    cabecera = last_save[0]
    resultados = last_save[1]

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="consulta.xls"'

    workbook = xlwt.Workbook()
    worksheet = workbook.add_sheet("consulta")

    num_fil = 0
    num_col = 0
    for elem in cabecera:
        worksheet.write(num_fil,num_col,unicode(elem).encode("utf-8"))
        num_col = num_col + 1
    num_fil = 1
    num_col = 0
    for elem in resultados:
        for e in elem:
            if isinstance(e, basestring):
                worksheet.write(num_fil,num_col,e)
            else:
                worksheet.write(num_fil,num_col,unicode(e).encode("utf-8"))
            num_col = num_col + 1
        num_fil = num_fil + 1
        num_col = 0

    workbook.save(response)

    return response



