# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 13:35:39 2020

@author: Esteban Ochoa Torres
"""

###se importan las librerias necesarias
import numpy as np
import os 
import gdal 
import matplotlib.pyplot as plt

def metadato(archivo):
    metadatos={}
    for i in archivo.readlines():
        if "=" in i:
            separador= i.split("=")
            clave=separador[0].strip()
            valor=separador[1].strip()
            metadatos[clave]=valor
    archivo.close()
    return metadatos

def guardar_tif(salida, matriz, im_entrada): #nom_salida, matriz de radiancia, banda de entrada
	#Definir coordenadas iniciales raster y resoluciones
	geoTs = im_entrada.GetGeoTransform() # 6 parámetros [ulx,resx(+),0,uly,0,resy(-)] resY(-) lat disminuye
	driver = gdal.GetDriverByName("GTiff") #Voy a manejar un tiff
	prj = im_entrada.GetProjection()  #Consulto la proyección al tif inicial
	cols = im_entrada.RasterXSize #Consulto columnas
	filas = im_entrada.RasterYSize #Consulto filas
	#Crear el espacio
	export=driver.Create(salida,cols,filas,1,gdal.GDT_Float32) #Escribir tif, nombre, cols,filas,num_bandas,tipo_dato (float)
	banda=export.GetRasterBand(1) #Cargo la banda creada en el paso anterior
	banda.WriteArray(matriz) #Escribe la matriz de radiancia
	export.SetGeoTransform(geoTs) #Asigna los parametros de la transformacion a la salida
	export.SetProjection(prj) #definir proyeccion
	banda.FlushCache()#descargar de la memoria virtual al disco
	export.FlushCache()#descargar de la memoria virtual al disco
    
##Calculo de reflectancia
def reflectancia (M,ND,A):
    refle=M*ND+A
    return(refle)

##Calculo de reflectancia corregida
def refle_corregida (r):
    correccion=r-np.nanmin(r)
    return(correccion)

##NVDI
def nvdi (r,nir):
    n=(nir-r)/(nir+r)
    return (n)

##EVI
def evi (b,r,nir):
    e=(2.5*(nir-r))/(1+nir+(6*r)-(7.5*b))
    return(e)
    
    
    
    
arch_mtl=r'D:\descargas\LC08_L1TP_008053_20200102_20200113_01_T1\LC08_L1TP_008053_20200102_20200113_01_T1_MTL.txt'
ruta_mtl=open(arch_mtl,'r')
datos=metadato(ruta_mtl)

path_img=r'D:\descargas\LC08_L1TP_008053_20200102_20200113_01_T1'
imagen='LC08_L1TP_008053_20200102_20200113_01_T1'

mask=r'D:\descargas\LC08_L1TP_008053_20200102_20200113_01_T1/SHAPE/cuenca.shp'
salida_corte=r'D:\descargas\LC08_L1TP_008053_20200102_20200113_01_T1/recorte3'
os.mkdir(salida_corte)
reflectancia_cort=[]


for banda in range (1,12):
    if (banda==2 or banda==4 or banda==5):
        print ('Inicia procedimiento de: ' +imagen+'_B'+str(banda)+'.TIF')

        #RECORTE
        corte=salida_corte+os.sep+'B'+str(banda)+'.TIF'
        raster=path_img+os.sep+imagen+'_B'+str(banda)+'.TIF'
        os.system('gdalwarp -dstnodata 0 -q -cutline %s -crop_to_cutline -of GTiff %s %s'%(mask,raster,corte))
        
        #ABRIR RECORTE
        img_banda=gdal.Open(corte)
        nd=img_banda.GetRasterBand(1).ReadAsArray().astype('float')
        nd [[nd==0]]= np.nan
        
        #REFLECTANCIA
        m=float(datos['REFLECTANCE_MULT_BAND_'+str(banda)])
        a=float(datos['REFLECTANCE_ADD_BAND_'+str(banda)])
        reflec=reflectancia(m,nd,a)
        
        #REFLECTANCIA CORREGIDA
        reflectancia_cor=refle_corregida(reflec)
        reflectancia_cort.append(reflectancia_cor)
        print("Ya están tus chingadazos")
        
indice_NVDI=nvdi(reflectancia_cort[1],reflectancia_cort[2])
salida_nvdi=(salida_corte+os.sep+'NVDI.TIF')        
gt=guardar_tif(salida_nvdi,indice_NVDI,img_banda)

if gt==gt:
    print("ya se imprimió el chingon NDVI")
else:
    print("ni modo cabron, revisa el codigo de guardar tif")

indice_EVI=evi(reflectancia_cort[0],reflectancia_cort[1],reflectancia_cort[2])
salida_evi=(salida_corte+os.sep+'EVI.TIF')        
gte=guardar_tif(salida_evi, indice_EVI,img_banda)

if gte==gte:
    print("ya se imprimió el chingon EVI")
else:
    print("ni modo cabron, revisa el codigo de guardar tif")
    
    
####EVI vs NDVI
plt.scatter(indice_NVDI,indice_EVI)
plt.title('NDVI vs EVI')
plt.xlabel('NDVI')
plt.ylabel('EVI')
plt.grid()
plt.show()