from projects.models import Projects


def create_word(project: Projects):
    pass


def genereate_neg_con_table(project: Projects):
    table = {'column_name': ['Вид риска (ущерба)', 'Возможные негативные последствия']}
    neg_cons = project.negative_consequences.all()
    for neg_con in neg_cons:
        if neg_con.type in table:
            table[neg_con.type].append(neg_con.name)
        else:
            table[neg_con.type] = [neg_con.name]
    print(table)

    #todo создать excel файл и вернуть его
    return table


def generate_obj_inf_table(project: Projects):
    # Негативные последствия (нег поз (лвл риска)), объект воздействия, вид воздействия (возможно придётся оставлять пустым)
    # todo создать excel файл и вернуть его
    pass


def generate_violators_type_table(project: Projects):
    # вид нарушителя(название), тип нарушителя (внеш, внут), Возможные цели (мотивация) реализации угроз безопасности информации
    # todo создать excel файл и вернуть его
    pass


def generate_violators_potential_table(project: Projects):
    # Уровень возможностей, вид нарушителя(название), потенциал нарушителя
    # todo создать excel файл и вернуть его
    pass


def generate_bdu_table(project: Projects):
    # номер угрозы, название, уязвимость(опционально), вектор капек, нег пос, объект воздействия, нарушитель, сценарий реализации
    # todo создать excel файл и вернуть его
    pass
