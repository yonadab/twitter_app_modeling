# -*- coding: utf-8 -*-
"""

Created by Yonadab

"""

##############################################################
##                                                          ##
##                 TWITTER TOPIC MODELING                   ##
##                                                          ##
##############################################################



import streamlit as st
import pandas as pd
import gensim
import snscrape.modules.twitter as snstwitter
import nltk
import pyLDAvis
from PIL import Image

#################################################
################## BACK-END #####################
#################################################

def query_tweets(query=None, limit=None):
    
    '''
    Obtenemos los Twitters mediante snscrape
    
    return:
        Dataframe con los twitters encontrados
        
    '''

    counter = 0
    tweets = []
    
    if limit == 0:
        limit = 100

    
    
    for tweet in snstwitter.TwitterSearchScraper(query).get_items():
        if counter == limit:
            break
        else:
            counter = counter + 1
            tweets.append([tweet.date, tweet.user.username, tweet.content, 
                           tweet.viewCount, tweet.likeCount])
            
            
    df = pd.DataFrame(tweets, columns=['Fecha','Usuario','Tweet','Vistas','Likes'])
    
        
    return df




def preprocess(df):
    
    '''
    Limpiamos el texto: quitamos palabras recurrentes y
    signos de puntuación
    
    return:
        Lista con twitts limpiados
        
    '''
    
    final_text = [] 
    
    punctuation = '''.,#$@&;:_-*+?]¿[¡=!/'''

    # STOPWORDS
    import pickle
    with open('./stopwords/stopwords.pickle', 'rb') as f:
        stopwords = pickle.load(f)

    
    for i in df['Tweet']:
        row_text = nltk.tokenize.word_tokenize(i)
        row_clean = []
        for token in row_text:
            rplc = token.translate(str.maketrans('','', punctuation))
            if rplc.isalpha() is True and rplc not in stopwords:  
                row_clean.append(rplc)
                
        
        
        txt = ' '.join(row_clean)
        final_text.append(txt.strip())


    return final_text




def topic_modeling(documentos):
    
    '''
    Modelamos los mejores tópicos mediante algoritmo LDA
    
    return:
        objeto  de visualización pyLDAvis
        
    '''
    
   
    # Gensim libraries
    import gensim.corpora as corpora
    from gensim.utils import simple_preprocess
    
    tokens_process = [simple_preprocess(doc, deacc=False) for doc in documentos]
    id2word = corpora.Dictionary(tokens_process)
    
    bow_words = [id2word.doc2bow(token) for token in tokens_process]
    
    from gensim.models.ldamodel import LdaModel

    lda = LdaModel(corpus=bow_words,
                   id2word= id2word,
                   num_topics=10,
                   random_state=1,
                   chunksize=100,
                   passes=10,
                   alpha='auto')
    
    visualizing = visual_model(lda, bow_words, id2word)
    
    
    return visualizing



def visual_model(lda, bow_words, id2word):
    
    '''
    Función visualizar los tópicos mediante pyLDAvis
    
    returns:
        objeto HTML de pyLDAvis 
    '''
    
    
    import pyLDAvis.gensim_models as visgensim


    vis = visgensim.prepare(lda,
                       bow_words,
                       id2word,
                       mds='PCoA',
                       R=10)



    prepared_html = pyLDAvis.prepared_data_to_html(vis)

    return prepared_html



def press_consultar():
    
    '''
    Consultamos para obtener los tweets
    
    return:
        Dataframe con ['Fecha','Usuario','Tweet']
    '''
    if fecha is True and usuario_check is True:
         consulta = '{} (from:{}) lang:es until:{} since:{}'.format(palabra, usuario, final, inicio)
         QRY = query_tweets(query=consulta, limit=limite)

                
    elif fecha is True and usuario_check is False:
        consulta = '{} lang:es until:{} since:{}'.format(palabra, final, inicio)
        QRY = query_tweets(query=consulta, limit=limite)

                
    elif fecha is False and usuario_check is True:
        consulta = '{} (from:{}) lang:es'.format(palabra, usuario)
        QRY = query_tweets(query=consulta, limit=limite)
 
                
    elif fecha is False and usuario_check is False:
         consulta = '{} lang:es'.format(palabra)
         QRY = query_tweets(query=consulta, limit=limite)
           
        

         
    return QRY



def metrics(df):
    
    '''
    Top 5 de likes y vistas de los tweets
    '''
    
    df_likes = df.sort_values(by='Likes', ascending=False)[:5]
    df_vistas = df.sort_values(by='Vistas', ascending=False)[:5]
    
    return (df_likes, df_vistas)
    
    


#######################################################
############## FRONT-END WITH STREAMLIT ###############
#######################################################

st.set_page_config(page_title='Twitter topic modeling scrapping',
                   page_icon=':page_facing_up:',
                   layout='wide')


    


st.title('Topic modeling desde Twitter :page_facing_up:')
st.caption('By Yonadab |   visita mi Github: https://github.com/yonadab')


analizar = st.button('Analizar')
           

st.markdown('---')

principal, tab1, tab2, otras_metricas = st.tabs([':pushpin: Principal ','Buscar :mag:','Análisis :bar_chart:','Otras Métricas :eyes:'])


###------ PRINCIPAL ------###

with principal:
    
    with open('./info.txt', 'r', encoding='utf-8') as f:
        info = f.read()
    
    
    with st.expander('**¿Qué es topic modeling y para qué sirve?**'):
        st.write(info)
        
        
    with st.expander('**¿Cómo buscar tweets?**'):
        image_consultar = Image.open('./como_consultar.png')
        st.image(image_consultar)
        st.write('**NOTA: Si no selecciona ninguna fecha ni usuario ni se busca por alguna palabra en particular,\
                 el programa buscará los tweets más relevantes del momento de manera aleatoria')
        
        
        
    with st.expander('**¿Cómo analizar los tweets?**'):
        image_analizar_topic = Image.open('./analizar_topic.png')
        st.image(image_analizar_topic, width=850)
        
        
    with st.expander('**¿Cómo se muestran los resultados?**'):
        image_topic = Image.open('./topicos.png')
        st.image(image_topic, width=850)
        st.write('**NOTA: Para una mejor descripción dirígete a la sección _Analizar_')
        



###----- OTRAS METRICAS -----###
with otras_metricas:
    
    # Agregamos dos columnas
    metrics_column1, metrics_column2 = st.columns(2)
    
    with metrics_column1:
        st.subheader('Top 5 de tweets con mayores likes:')
        
    with metrics_column2:
        st.subheader('Top 5 de tweets con mayores vistas:')     
                

    


### ----- TABLA 1 ----- ###

with tab1:
    col1, col2 = st.columns(2)

    
    
    with col1:
        fecha = st.checkbox('Seleccionar por fecha')
        
        if fecha:
            
            inicio = st.date_input('Desde:')
            final = st.date_input('Hasta: ')
            
    with col2:
        usuario_check = st.checkbox('Analizar a un usuario específico')
        
        if usuario_check:
            st.caption('Asegurate de escribir el nombre de usuario correctamente: sin espacios, con mayúsculas y minúsculas')
            usuario = st.text_input('Escribe el nombre de usuario: ', placeholder='Ejemplo: elonmusk / no escribas el @')
            
    
    st.markdown('---')
    
    sub_col1, sub_col_dataframe = st.columns(2)
    
    with sub_col_dataframe:
        st.subheader('Tweets extraídos:')
    
    with sub_col1:
        global QRY
        palabra = st.text_input('Escribe la palabra o frase de búsqueda')
        limite = st.slider('Selecciona un número de tweets: ', 0, 500, 10)
        
        consultar = st.button('Consultar')
        
        if consultar:
            df_tweets = press_consultar()
            
            # Agregamos el dataframe a la columna sub_col_dataframe
            with sub_col_dataframe:
                st.dataframe(df_tweets.iloc[:,:3])
              
                likes, vistas = metrics(df_tweets)
                with metrics_column1:
                    st.dataframe(likes[['Usuario','Tweet','Likes']])
                
                with metrics_column2:
                    st.dataframe(vistas[['Usuario','Tweet','Vistas']])








########################
# -- BOTON ANALIZAR -- #
########################

if analizar:
    
    QRY_consulta = press_consultar() ## Dataframe
    pre = preprocess(QRY_consulta)
    
    prepared = topic_modeling(pre)
    
    #Integramos el df en el apartado de buscar
    with sub_col_dataframe:
        st.dataframe(QRY_consulta.iloc[:, :3])
      
        
    # Integramos las metricas
    
    likes, vistas = metrics(QRY_consulta)
    with metrics_column1:
        st.dataframe(likes[['Usuario','Tweet','Likes']])
                     
    with metrics_column2:
        st.dataframe(vistas[['Usuario','Tweet','Vistas']])
    
    
    
    ###------ TABLA 2 - ANALISIS (TOPIC MODELING) -------###
    
    with tab2:
        from streamlit import components
        components.v1.html(prepared, width=1300, height=800, scrolling=True)
     
        
     
    # Mensaje éxito
    st.success('Análisis completado', icon='✅')





#### --- TAB 2 --- ####

with tab2:
    
    with open('./info_pyLDAvis.txt', 'r', encoding='utf-8') as f:
        info_LDA = f.read()
    
    
    with st.expander('**Interpretación de resultados**'):
        st.write(info_LDA)



###### REMOVIENDO DETALLES FINALES DE STREAMLIT ######    

hide_st_style = """
	<style>
	#MainMenu {visibility: hidden;}
	footer {visibility: hidden;}
	header {visibility: hidden;}
	</style>
"""

st.markdown(hide_st_style, unsafe_allow_html=True)

