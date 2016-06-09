# -*- coding: utf-8 -*-

lista_attos_elector = [("DNI",["arg_elector","arg_elector.dni"]),
                       ("Apellido",["arg_elector","arg_elector.apellido"]),
                       ("Nombre",["arg_elector","arg_elector.nombre"]),
                       ("Sexo",["arg_elector","arg_elector.sexo"]),
                       ("Edad",["arg_elector","arg_elector.edad_13 + (date_part('year', now())::integer - 2013)"]),
                       ("NSE",["arg_elector","arg_elector.nse"]),
                       ("Dirección",["arg_elector","arg_elector.direccion"]),
                       ("Email 1",["arg_elector","arg_elector.email1"], "email1-null"),
                       ("Email 2",["arg_elector","arg_elector.email2"], "email2-null"),
                       ("Telefono 1",["arg_elector","arg_elector.telefono1"], "celular1-null"),
                       ("Telefono 2",["arg_elector","arg_elector.telefono2"], "celular2-null"),
                       ("Telefono 3",["arg_elector","arg_elector.telefono3"], "celular3-null")]


lista_attos_centro = [("Provincia",["arg_centro","arg_centro.provincia"]),
                      ("Distrito",["arg_centro","arg_centro.distrito"]),
                      ("Barrio",["arg_centro","arg_centro.barrio"]),
                      ("CUE",["arg_centro","arg_centro.cue"]),
                      ("Escuela",["arg_centro","arg_centro.escuela"]),
                      ("Dirección Escuela",["arg_centro","arg_centro.dir_escuela"])]


lista_no_nulos = [("email1-null",["arg_elector","arg_elector.email1 IS NOT NULL"]),
                  ("email2-null",["arg_elector","arg_elector.email2 IS NOT NULL"]),
                  ("celular1-null",["arg_elector","arg_elector.telefono1 IS NOT NULL"]),
                  ("celular2-null",["arg_elector","arg_elector.telefono2 IS NOT NULL"]),
                  ("celular3-null",["arg_elector","arg_elector.telefono3 IS NOT NULL"])]


lista_attos = lista_attos_centro + lista_attos_elector 


lista_ag_attos = lista_attos_centro[0:5] + lista_attos_elector[3:6]


lista_agrupados = [("Cantidad de Provincias",["arg_centro","count(distinct(arg_centro.provincia))"]),
                   ("Cantidad de Distritos",["arg_centro","count(distinct(arg_centro.distrito))"]),
                   ("Cantidad de Barrios",["arg_centro","count(distinct(arg_centro.barrio))"]),
                   ("Cantidad de Centros",["arg_centro","count(arg_centro.cue)"]),
                   ("Cantidad de Electores",["arg_elector","count(arg_elector.dni)"]),
                   ("Cantidad de Emails 1",["arg_elector","count(arg_elector.email1)"]),
                   ("Cantidad de Emails 2",["arg_elector","count(arg_elector.email2)"]),
                   ("Cantidad de Telefonos 1",["arg_elector","count(arg_elector.telefono1)"]),
                   ("Cantidad de Telefonos 2",["arg_elector","count(arg_elector.telefono2)"]),
                   ("Cantidad de Telefonos 3",["arg_elector","count(arg_elector.telefono3)"])
                  ]


lista_conds = [("Ubicación demográfica",[("prov",("arg_centro","arg_centro.provincia")),("dist",("arg_centro","arg_centro.distrito")),
                                         ("barr",("arg_centro","arg_centro.barrio")),("escs",("arg_centro","arg_centro.cue"))], "ubicacion", "dependiente"),
               ("DNI específico",[("dni",("arg_elector","arg_elector.dni"))], "dni-esp", "simple"),
               ("Nombre y Apellido",[("nombre",("arg_elector","arg_elector.nombre")),("apellido",("arg_elector","arg_elector.apellido"))], "nombre-completo", "doble"),
               ("Sexo",[("sexo",("arg_elector","arg_elector.sexo"))], "genero", "simple"),
               ("NSE",[("nse",("arg_elector","arg_elector.nse"))], "nse-soc", "multiple"),
               ("Edad",[("minimo",("arg_elector","arg_elector.edad_13 + (date_part('year', now())::integer - 2013)")),
                        ("maximo",("arg_elector","arg_elector.edad_13 + (date_part('year', now())::integer - 2013)"))], "edad", "rango"),
              ]


lista_condiciones = [("prov",["agr_centro","arg_centro.provincia"]),("dist",["agr_centro","arg_centro.distrito"]),
                     ("barr",["agr_centro","arg_centro.barrio"]),("escs",["agr_centro","arg_centro.escuela"]),
                     ("dni",["arg_elector","arg_elector.dni"]),("nombre",["arg_elector","arg_elector.nombre"]),
                     ("apellido",["arg_elector","arg_elector.apellido"]),("sexo",["arg_elector","arg_elector.sexo"]),
                     ("nse",["arg_elector","arg_elector.nse"]),
                     ("minimo",["arg_elector","arg_elector.edad_13 + (date_part('year', now())::integer - 2013)"]),
                     ("maximo",["arg_elector","arg_elector.edad_13 + (date_part('year', now())::integer - 2013)"])]


lista_sexo = ['F','M']


lista_nse = ['ALTO','MEDIO','BAJO']
