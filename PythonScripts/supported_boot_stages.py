PowerOffStage = "PowerOffStage"
FivrBreak = 'FivrBreak'
FuseBreak = 'FuseBreak'
EFIStage = 'EfiStage'
UbuntuStage ='UbuntuStage'
SuseStage = 'SuseStage'


def get_marionette_stages():
    return [EFIStage,UbuntuStage,SuseStage]

def get_python_stages():
    return [PowerOffStage,FivrBreak,FuseBreak]
