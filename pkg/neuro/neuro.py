from joblib import load
import os
from pkg.config.config import PATH
from pkg.neuro.sub_neuro import get_tyagovoe_type_14_57, work_type_ids

model = load(PATH+'model.joblib')

 
Pf = ("Залежь, пласт много летних трав, уплотненная стерня",
      "Стерня зерновых колосовых и однолетних трав",
      "Поле после уборки кукурузы и подсолнечника",
      "дискованная стерня",
      "Поле подготовленно под посев",
      "культивированное поле дисковання пашня",
      "Слежавшаяся уплотненная пашня",
      "Свежевспаханное поле")

def get_tyagovoe_type(ukl, work_type, soil_background, tp):
    if 14 <= work_type <= 58:
        return get_tyagovoe_type_14_57(ukl, work_type, soil_background, tp)
    vsr = work_type_ids[work_type]
    pf = Pf[soil_background-1]
    input_data = [ukl, "Поле подготовленно под посев", "Поле после уборки кукурузы и подсолнечника", "Свежевспаханное поле", 
        "Слежавшаяся уплотненная пашня", "Стерня зерновых колосовых и однолетних трав", "дискованная стерня", "культивированное поле дисковання пашня", 
        "Легкие", "Средние", "Тяжелые", "Боронование почвы Ножевыми боронами", "Боронование почвы Сетчатыми боронами", "Боронование почвы пружинными боронами", 
        "Вспашка почвы прицепным плугом", "Выравнивание прочвы агрегатами типа ВП", "Дискование стерни Боронами типа БД", 
        "Лущение стерни дисковыми орудиями типа ЛДГ  глубина обр. 6-8 см", "Лущение стерни дисковыми орудиями типа ЛДГ глубина обр. 8-10", 
        "Прикатывание почвы гладкими катками, кольчато-шпоровыми"]
    for i in range(1,len(input_data)):
        if input_data[i] == vsr or input_data[i] == pf or input_data[i] == tp:
            input_data[i] = True
        else:
            input_data[i] = False
    print(input_data)
        
    tygovoe_type = model.predict(input_data)[0]
    return tygovoe_type