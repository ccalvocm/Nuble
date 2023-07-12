#%%
import pandas as pd
import geopandas as gpd

def catUso(gdf):
    gdf['categoria']=pd.Categorical(gdf.usoactual)
    gdf['catUso']=gdf.categoria.cat.codes+1

    return gdf

def catTipo(gdf):
    gdf['categoriaTipo']=pd.Categorical(gdf.tipo)
    gdf['catTipo']=gdf.categoriaTipo.cat.codes+1

    return gdf

def export(gdf):
    dfUso=gdf[['categoria','catUso']].drop_duplicates()
    gdf[['categoria',
         'catUso']].drop_duplicates().to_csv(r'D:\GitHub\Nuble\geodata\categoriaUso.csv')
    gdf[['categoriaTipo',
         'catTipo']].drop_duplicates().to_csv(r'D:\GitHub\Nuble\geodata\categoriaTipo.csv')
    del gdf['categoria']
    del gdf['categoriaTipo']
    gdf.to_file(r'D:\GitHub\Nuble\geodata\usoSuelo2.shp')

uso=gpd.read_file(r'D:\GitHub\Nuble\geodata\usoSuelo.shp')
uso2=catUso(uso)
uso2=catTipo(uso2)
export(uso2)
#%%