import repository.models_impl as model_impl

def createModel(data):
    try:
        mark = data["Марка"]
        model = data["Модель"]
        section = data["Раздел"]
        if mark == "" or model == "" or section == "":
            raise
    except:
        return True
    model_impl.createModel(mark, model, section, data)

def GetTractorModels():
    return model_impl.getModels(section="Тракторы", model="", mark="")