from projects.models import Projects


def create_word(project: Projects):
    pass

def genereate_neg_con_table(project: Projects):

    # Вид риска (ущерба), Возможные негативные последствия
    pass

def generate_obj_inf_table(project: Projects):
    # Негативные последствия (нег поз (лвл риска)), объект воздействия, вид воздействия (возможно придётся оставлять пустым)
    pass

def generate_violators_type_table(project: Projects):
    # вид нарушителя(название), тип нарушителя (внеш, внут), Возможные цели (мотивация) реализации угроз безопасности информации
    pass

def generate_violators_potential_table(project: Projects):
    # Уровень возможностей, вид нарушителя(название), потенциал нарушителя
    pass


def generate_bdu_table(project: Projects):
    # номер угрозы, название, уязвимость(опционально), вектор капек, нег пос, объект воздействия, нарушитель, сценарий реализации
    pass