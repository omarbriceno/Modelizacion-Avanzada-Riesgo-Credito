# -*- coding: utf-8 -*-
"""
Created on Sun Oct 22 08:08:24 2023

@author: Omar Briceño 
"""
import numpy as np
import pandas as pd


def sesgoregularizacion(data_in, lgd, res, t):
        
    """
    Escuela Peruana de Gestión de Riesgos
    
    La función 'sesgoregularizacion' tiene como propósito identificar 
    y cuantificar el sesgo de regularización incompleta en un conjunto 
    de datos de pérdida por incumplimiento (LGD).

    Parámetros:
    -----------
    data_in : DataFrame
        Conjunto de datos que contiene la información histórica de préstamos.
    lgd : 
        Nombre de la variable en data_in que contiene el valor de la LGD 
        (Loss Given Default) para cada observación.
    res : 
        Nombre de la variable que indica el tiempo que ha tomado la recuperación 
        de la deuda (período de resolución).
    t : 
        Tiempo de observación, es decir, el umbral que determina si un crédito 
        debe incluirse en el análisis de recuperación.

    Retorna:
    --------
    df3 : DataFrame
        Conjunto de datos resultante con la comparación entre LGD 
        observado y estimado, ajustado por el sesgo de regularización incompleta.
        
    """
        
    df = data_in
    
    df2=df.dropna(subset=[res]).copy()
    df2.loc[:,'res_period'] = df2.loc[:,res] - df2.loc[:,t]
    
    df2.loc[df2['res_period'] >= 20, 'res_period'] = 20

    data_LGD_sum = df2.groupby('res_period')[lgd].sum().reset_index(drop=False)
    data_LGD_count = df2.groupby('res_period')[lgd].count().reset_index(drop=False)
    
    data_LGD_sum = data_LGD_sum.sort_values(by='res_period', ascending=False)
    data_LGD_count = data_LGD_count.sort_values(by='res_period', ascending=False)

    data_LGD_sum_cumsum = data_LGD_sum.cumsum()
    data_LGD_count_cumsum = data_LGD_count.cumsum()
    data_LGD_mean = data_LGD_sum_cumsum/data_LGD_count_cumsum
    
    data_LGD_mean = data_LGD_mean.iloc[:,0:4]
    data_LGD_mean[t] = 61-data_LGD_mean.index
    data_LGD_mean = data_LGD_mean.set_index(t)

    data_LGD_mean2 = data_LGD_mean.iloc[np.full(41, 0)].reset_index(drop=True)
    data_LGD_mean3 = pd.concat([data_LGD_mean2, data_LGD_mean], ignore_index=True).reset_index(drop=False) 
    data_LGD_mean3 = data_LGD_mean3.rename(columns={'index': t})

    df = df[df.loc[:,res].isnull()].drop([lgd], axis = 1) 
    df = pd.merge(df, data_LGD_mean3, on=t)   
    df3 = pd.concat([df2, df], sort=True, ignore_index=True) 
    df3 = df3.drop('res_period', axis='columns').copy()
    return df3