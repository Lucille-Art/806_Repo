# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""


import os
import pandas as pd
from bs4 import BeautifulSoup
import requests as r
import numpy as np
import time
    
    

def scrap(url1,url2):
    
    
    resp_indeed = r.get(url1)
    resp_pe = r.get(url2)
    content_type_indeed = resp_indeed.headers['Content-Type'].lower()
    content_type_pe = resp_pe.headers['Content-Type'].lower()
    
    if (resp_indeed.status_code==200 and content_type_indeed is not None and content_type_indeed.find('html')>-1) & (resp_pe.status_code==200 and content_type_pe is not None and content_type_pe.find('html')>-1):
        print('We can start downloading the datas.\n\n')
        
    else:
        print('There is an issue accessing the server.')
        
    return get_datas_indeed(url1,url2)


def get_datas_indeed(url1,url2):
    
    step=0
    i=10
    
    locations_indeed =[]
    companies_indeed =[]
    jobs_indeed =[]
    dates_indeed =[]
    rates_indeed=[]
    rates=[]
    
    while i>=0:
        url1=f'https://www.indeed.fr/jobs?q=data+analyst&start={i}'
        resp_indeed=r.get(url1)
        soup_indeed = BeautifulSoup(resp_indeed.content)

        if step%5==0:
            time.sleep(2.4)
            print('[Indeed] Page',step,'is done.')

        locations_indeed += [i.text for j in [i.select('.location') for i in soup_indeed.select('div.jobsearch-SerpJobCard')] for i in j]       
        companies_indeed += [i.text.strip('\n').title() for i in soup_indeed.select('span.company')]
        jobs_indeed += [i.text.lower().strip('\n (h/f) h/f').capitalize() for i in soup_indeed.select('h2')]
        dates_indeed += [i.text.lower().lstrip('il y a plus de').rstrip('jours ') for i in soup_indeed.select('span.date')]
        for j in [i.select('.ratingsContent') for i in soup_indeed.select('div.jobsearch-SerpJobCard')]:
            if j==[]:
                rates.append('Not specified')
            else:
                rates.append([k.text.strip('\n') for k in j])

        step+=1
        i+=10

        if i>=660:
            print('Indeed is done.\n')

            break

        else:
            continue
            
    dict_indeed = {'Job': jobs_indeed,
        'Company': companies_indeed,
        'Location': locations_indeed,
        'Publication date': dates_indeed,
        'Company\'s rate':rates}

            
    return get_datas_pe(dict_indeed, url2)



def get_datas_pe(dict_indeed,url2):
    
    step=0
    i=0
    
    locations_pe =[]
    jobs_pe =[]
    dates_pe = []

    while i>=0:
        url2=f'https://candidat.pole-emploi.fr/offres/recherche.rechercheoffre:afficherplusderesultats/{i}-{i+9}?motsCles=data+analyst&offresPartenaires=true&range={i-10}-{i-1}&rayon=10&tri=0'
        resp_pe=r.get(url2)
        soup_pe = BeautifulSoup(resp_pe.content)

        if step%5==0:
            time.sleep(2.4)
            print('[Pôle Emploi] Page',step,'is done.')

        locations_pe += [i.text.strip('\n').title() for i in soup_pe.select('p.subtext')]
        jobs_pe += [i.text.lower().strip('\n (h/f) h/f').capitalize() for i in soup_pe.select('h2.t4')]
        dates_pe += [i.text.lower().strip('\n publié il y a jours de') for i in soup_pe.select('p.date')]
      
        step +=1
        i+=10

        if i>=185:
            print('Pôle Emploi is done.')
            break

        else:
            continue

    dict_pe = {'Job': jobs_pe,
             'Location': locations_pe,
              'Publication date':dates_pe}
    
    return into_dataframe(dict_indeed,dict_pe)


def into_dataframe(dict_indeed, dict_pe):
    
    df1=pd.DataFrame(dict_indeed)
    df2=pd.DataFrame(dict_pe)
    df = pd.concat([df1,df2])
    
    return cleaning_df(df)
    


def cleaning_df(df):
    
    df['Company'] = df['Company'].fillna('Not specified')
    df['Company\'s rate'] = df['Company\'s rate'].fillna('Not specified')
    df['Publication date'] = df['Publication date'].fillna(100)
    df.loc[df['Publication date']=='d\'h', 'Publication date']=1
    df.loc[df['Publication date']=='jourd\'hui', 'Publication date']=0
    df.loc[df['Publication date']=='bliée à l\'instant', 'Publication date']=0
    df.loc[df['Publication date']=='Not specified', 'Publication date']=100
    df.loc[df['Publication date']=='h', 'Publication date']=1
    df.loc[df['Publication date']=='\'h', 'Publication date']=1
    df.loc[df['Publication date']=='30 jours\n\noffre avec peu de candidat', 'Publication date']=30
    df['Publication date'].unique()
    df['Publication date']=df['Publication date'].astype(int)
    
    df=df.sort_values(by='Publication date')
    
    df = df.reset_index(drop=True)

    display(df)
    
    return saving_df(df)
    


def saving_df(df):
    
    save_df=True

    while save_df:
        save = str(input('Do you want to save the changes in the database ?:'))
        if save=='yes':
            df.to_csv('Jobs.csv',index=False)
            print('Changes are saved.')
            save_df=False
        
        elif save=='no':
            print('Changes not saved.')
            save_df=False
            
        else:
            print('You must answer "yes" or "no".')
            continue
            
    return
    


url1 = 'https://www.indeed.fr/jobs?q=data+analyst&start=20'
url2 = 'https://candidat.pole-emploi.fr/offres/recherche.rechercheoffre:afficherplusderesultats/10-19?motsCles=data+analyst&offresPartenaires=true&rayon=10&tri=0'

scrap(url1,url2)
