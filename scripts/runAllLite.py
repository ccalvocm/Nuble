from pywr.core import Model
from pywr.notebook import draw_graph
import matplotlib.pyplot as plt
import os
from pywr.domains.groundwater import KeatingAquifer
from pywr.parameters.groundwater import KeatingStreamFlowParameter
from pywr.core import (Model, Input, Output, Link, Storage, Node, Catchment)
from pywr.recorders import (
    NumpyArrayNodeRecorder,
    NumpyArrayLevelRecorder,
    NumpyArrayStorageRecorder,
)
import pandas
import numpy as np
import pytest
import time

def createAquifer(model,name):

    num_streams = 1
    num_additional_inputs = 0
    stream_flow_levels = [[1.0, 10.0]]  # m
    transmissivity = [100, 2000]  # m2/d
    transmissivity = [t * 0.0001 for t in transmissivity]  # m3 to Ml
    coefficient = 1  # no units
    storativity = [0.0005]  # % este parámetro es clave
    levels = [1.0, 10.0]  # m
    area = 50000 * 50000  # m2
    
    aqfer=KeatingAquifer(
        model,
        name,
        num_streams,
        num_additional_inputs,
        stream_flow_levels,
        transmissivity,
        coefficient,
        levels,
        area=area,
        storativity=storativity)

    aqfer.initial_level=9
    
    return aqfer

def connectAquifer(modelo,acuifero,nodosRecarga,nodosDescarga):
    for nodoR in nodosRecarga:
        model.nodes[nodoR].connect(acuifero)
    
    for nodoD in nodosDescarga:
        acuifero.connect(modelo.nodes[nodoD],from_slot=0)
    
    return modelo,acuifero
    
def connectNodes(modelo,entradas,salidas):
    
    for ind,entrada in enumerate(entradas):
        modelo.nodes[entrada].connect(model.nodes[salidas[ind]])
           
    return modelo

def getDischarge(lista):
    return ['deficit'+x.replace('REM','').replace('Sub','') for x in lista]

def getOutputs(lista):
    return [x.replace('deficit','')+'Mix' for x in lista]

if __name__ == "__main__":
    
    path="nubleLite2.json"
    model = Model.load(path)
    
#     crear objetos acuíferos
    aqferNiquen=createAquifer(model,'AC01_NIQ')
    aqferChan=createAquifer(model,'AC02_CHA')
    aqferNuble=createAquifer(model,'AC03_NUB')
    
#     conectar nodos existentes al acuifero Ñiquen
    recargas=['REMJFRVirguinZemitaSub','REMSanPedroSub']
    descargas=['abstraccionAqNiq']+getDischarge(recargas)
    model,aqferNiquen=connectAquifer(model,aqferNiquen,recargas,
                                     descargas)

#     conectar nodos existentes al acuifero Changaral
    recargas=['REMGYMSub','REMMunicipalSub','REMSACCSSub',
'REMRanchilloGPSub','REMArrauNiquenSub','REMLurinSilvaSub','REMSSaraPomSMartaSub',
'REMLilahueMoreiraSub','REMSanJoseNSub']
    
    descargas=['abstraccionAqCha']+['GreeneYMairaMix','deficitMunicipal',
'deficitSACCS','deficitRanchilloGP','deficitArrauNiquen',
'deficitLurinSilva','deficitSSaraPomSMarta',
'deficitLilahueMoreira','deficitSanJoseN']
    
    model,aqferChan=connectAquifer(model,aqferChan,recargas,descargas)
    
#     conectar nodos existentes al acuifero Ñuble
    recargas=['REMCollicoSub','REMChacayalOSub','REMChacayalPSub','REMMuticuraSub',
'REMBellavistaSub','REMMonteBlancoBSub','REMPomuyetoBajoASub','REMPomuyetoBajoBSub',
'REMLasDumasSub','REMQuileltoSub','REMMBFerradaSub','REMStaRosaNSub','REMMBMendezSub',
'REMElPenonSub','REMAlazanSub','REMRelocaSub','REMRomeralSub','REMSanLuisCSub',
'REMQuinquehuaSub','REMSantaRosaCatoSub','REMMonteBlancoLSub','REMMonteBlancoJSub',
'REMStaRitaSub','REMDadincoSub','REMSanJoseSSub','REMCapillaCoxSub','REMCapillaNSub',
'REMRinconadaCSub','REMArancibiaSub','REMLaPalmaSub','REMStaLauraSub']
    
    descargas=['abstraccionAqNub']+getDischarge(recargas)
    
    model,aqferNiquen=connectAquifer(model,aqferNuble,
recargas,descargas)
        
#     conectar los nodos de déficit que faltan
    entradas=['deficitJFRVirguinZemita','deficitCollico','deficitChacayalO','deficitChacayalP',
'deficitMunicipal','deficitRanchilloGP','deficitSACCS',
'deficitSanPedro','deficitArrauNiquen','deficitLurinSilva','deficitMuticura',
'deficitSSaraPomSMarta','deficitStaRita',
'deficitLilahueMoreira','deficitBellavista','deficitMonteBlancoB','deficitPomuyetoBajoA','deficitPomuyetoBajoB',
'deficitLasDumas','deficitQuilelto','deficitMBFerrada','deficitStaRosaN',
'deficitMBMendez','deficitElPenon','deficitAlazan','deficitReloca','deficitRomeral',
'deficitSanLuisC','deficitQuinquehua','deficitSantaRosaCato','deficitMonteBlancoL',
'deficitMonteBlancoJ','deficitDadinco','deficitSanJoseS','deficitCapillaCox',
'deficitCapillaN','deficitSanJoseN','deficitRinconadaC','deficitArancibia',
'deficitStaLaura','deficitLaPalma','deficitStaLaura']
    
    salidas=getOutputs(entradas)

#     conectar los sitios de bombeo de aguas subterráneas
    model=connectNodes(model,entradas,salidas)

    plt.figure()
    draw_graph(model,labels=True,attributes=False,
               width=1300,height=1300)
    plt.show()

    # workaround
    # en vez de devolver los excedentes al río, demandar menos

        # correr modelo
    model.solver.name="glpk"
    # run the model and see if it works
    start_time = time.time()
    run_stats = model.run()

    print("--- %s seconds ---" % (time.time() - start_time))

    run_stats = run_stats.to_dataframe()
    print(run_stats)

    # bocatoma 3
    print((model.nodes['NubleSanFabian'].flow-model.nodes["bocatoma3"].flow))
    #validar el balance de masa en canal Virguin
    #validar balance de masa en canal Collico
    print(model.nodes["CollicoSup"].flow)
    print(model.nodes["CollicoMix"].flow)
    print(model.nodes["FRCollico"].flow)
    print(model.nodes["REMCollicoSub"].flow)
    print(model.nodes["deficitCollico"].flow)
    print(model.nodes["BellavistaSup"].flow)
    print(model.nodes["BellavistaMix"].flow)
    print(model.nodes["FRBellavista"].flow)
    print(model.nodes["REMBellavistaSub"].flow)
    print(model.nodes["REMBellavistaSup"].flow)
    print(model.nodes["rioNuble"].flow)


