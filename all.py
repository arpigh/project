#весь код тут


#------------------------------------------------------------------------------------------------
import urllib.request as ur 

commonUrl = 'http://pobeda2.ru/component/k2/item/' #адрес выбранной газеты ("Победа") 

def download_pages(commonUrl): #функция, выгружающая новости по принципу краулера (обходом по номеру страницы) 
    html_dict = {} 
    for i in range(4700, 5049):#диапазон страниц 
        pageUrl = commonUrl + str(i) 
        try: 
            page = ur.urlopen(pageUrl) 
            html = page.read().decode() 
            html_dict[pageUrl] = html 
        except: 
            print('Error at', pageUrl) 
    return html_dict 

html_dict = download_pages(commonUrl) 


#------------------------------------------------------------------------------------------------
import re

regTag = re.compile('<.*?>', re.DOTALL)  # это рег. выражение находит все тэги
regScript = re.compile('<script>.*?</script>', re.DOTALL) # все скрипты
regComment = re.compile('<!--.*?-->', re.DOTALL)  # все комментарии
regText = re.compile('<div class="itemIntroText">.*?<div class="clr"></div>', re.DOTALL) #текст статьи
regTitle = re.compile(r'<meta name="title" content="(.*?)" />', re.DOTALL) #рег. выр для поиска заголовка
regData = re.compile(r'<div class="itemDate.*?div>', re.DOTALL) #рег.выражение для поиска даты
regCat = re.compile('Опубликовано в</span>.*?</a>', re.DOTALL) #рег выражение для поиска категории
regEntr = re.compile('\r[\n|\s|\t]+\r', re.DOTALL) #доп. очистка текста от множественных пробелов, табуляций и переноса строки

def clean_html(html, url): #функция для извлечения текста и данных для metadata.csv из html
    
    #извлекаем и очищаем заголовок, дату , год, категорию и текст

    title = regTitle.search(html).group(0) 
    title = re.sub(r'<meta name="title" content="|" />','', title)

    
    data = regData.search(html).group(0)    
    data = re.search('\d{2}\.\d{2}\.\d{2}', data).group(0)
    data = data[:6] + '20' + data[-2:] #изменяем формат с dd.mm.yy на dd.mm.yyyy

    year = data[-4:]
       
    cat = regCat.search(html).group(0)
    cat = regTag.sub('', cat)
    cat = re.sub(r'Опубликовано в|\t|\n','',cat)
    
    text = regText.search(html).group(0)
    
    clean_t = regScript.sub('', text)
    clean_t = regComment.sub('', clean_t)
    clean_t = regTag.sub('', clean_t)
    clean_t = regEntr.sub('', clean_t)

    
    words = clean_t.strip().split()#разбиваем текст статьи по пробелам 
    txt_len = len(words)#и считаем сколько слов в данной стратье
    
    clean_t ='@au ' + 'pobeda' + '\n@ti ' + title + '\n@da '+ data + '\n@topic '+ cat + '\n@url ' + url + '\n' + clean_t #на страницах 
                #газеты в разделе Автор всегда будет написано pobeda
    clean_t = clean_t.strip() #удаляем пробелы справа и слева
    
    return clean_t, title, data, year, cat, txt_len


#------------------------------------------------------------------------------------------------
def mystem_dir(path_, year, data,  f): #функция создающая файлы размеченные при помощи mysterm
    
    out1 ='E:\\gazeta\\mystem-plain\\' + year + '\\' + data[3:5] 
    out2 ='E:\\gazeta\\mystem-xml\\' + year + '\\' + data[3:5] 
    try: 
        os.makedirs(out1)

    except: pass
    try:
        os.makedirs(out2)
    except: pass

    os.system('E:\\mystem.exe  -nig ' + path_ + '\\' + f + ' ' + out1 + '\\'+ f)
    
    os.system('E:\\mystem.exe -cgin --format xml ' + path_ + '\\' + f + ' ' + out2 + '\\'+ f)

    

#------------------------------------------------------------------------------------------------
import os
import codecs

def make_files(text, data, year): #функция для содание файла .txt и дикертории к нему
    path_ = 'E:\\gazeta\\plain\\' + year + '\\' + data[3:5] 
    try:
        os.makedirs(path_)
    except: 
        pass    
    
    i = len(os.listdir(path = path_)) + 1
    
    f = codecs.open(path_ + '\\' + 'stat' + str(i)  + '.txt', 'w', 'utf-8')#открываем файл для записи в кодировке utf-8 ()
    f.write(text)
    f.close()
    
    mystem_dir(path_, year, data, 'stat' + str(i)  + '.txt')
    
    return path_
    

#------------------------------------------------------------------------------------------------
import pandas as pd
metadata = pd.DataFrame(columns = ['path' , 'author', 'sex', 'birthday', 'header','created',
                                  'sphere', 'genre_fi', 'type','topic','chronotop','style',
                                  'audience_age','audience_level', 'audience_size', 'source',
                                   'publication','publisher','publ_year','medium','country','region','language']) #создаем DataFram
                                                                                        #который выгрузим далее как csv файл
count_words = 0 #кол-во слов всего (для проверки что их более чем 100 тыс.)
for url in html_dict.keys(): #проходимся по всем выгруж текстам 
    try:
        text , title, data, year, cat, txt_len = clean_html(html_dict[url], url)
        path_ = make_files(text, data, year)      
        count_words = count_words + txt_len 
        metadata.loc[len(metadata)] = [path_,'pobeda', None, None, title , data,
                                       'публицистика', None, None , cat, None, 
                                       'нейтральный', 'н-возраст', 'н-уровень',
                                       'районная', url, 'Победа', None,
                                       year, 'газета',  'Россия', 'Удмуртская республика', 'ru']
    except: pass    
    

print('Количество слов всего: ', count_words)

metadata.to_csv('E:\\gazeta\\metadata.csv')
metadata.head()
