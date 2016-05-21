# coding=utf-8
__author__ = 'SXChen'


def register_mem_info(form):
    from app.ext.rules import ruleMaker

    rul = ruleMaker().rules_api_info()
    #
    prj_level = None
    if 'type_s' in form:
        prj_level = 's'
    if 'type_p' in form:
        prj_level = 'p'
    if 'type_k' in form:
        prj_level = 'k'
    if 'type_g' in form:
        prj_level = 'g'
    if 'type_b' in form:
        prj_level = 'b'
    #
    res = []
    count_c = 0
    count_d = 0
    a =  form.get('prj_name'), form.get('A'), 'A', \
         form.get('A_check', 0), form.get('A_mono'), rul[prj_level]['distribution'][0]
    b =  form.get('prj_name'), form.get('B'), 'B', \
         form.get('B_check', 0), form.get('B_mono'), rul[prj_level]['distribution'][1]
    c1 = form.get('prj_name'), form.get('C1'), 'C', \
         form.get('C1_check', 0), form.get('C1_mono'), rul[prj_level]['distribution'][2]
    c2 = form.get('prj_name'), form.get('C2'), 'C', \
         form.get('C2_check', 0), form.get('C2_mono'), rul[prj_level]['distribution'][2]
    c3 = form.get('prj_name'), form.get('C3'), 'C', \
         form.get('C3_check', 0), form.get('C3_mono'), rul[prj_level]['distribution'][2]
    c4 = form.get('prj_name'), form.get('C4'), 'C', \
         form.get('C4_check', 0), form.get('C4_mono'), rul[prj_level]['distribution'][2]
    d1 = form.get('prj_name'), form.get('D1'), 'D', \
         form.get('D1_check', 0), form.get('D1_mono'), rul[prj_level]['distribution'][3]
    d2 = form.get('prj_name'), form.get('D2'), 'D', \
         form.get('D2_check', 0), form.get('D2_mono'), rul[prj_level]['distribution'][3]
    d3 = form.get('prj_name'), form.get('D3'), 'D', \
         form.get('D3_check', 0), form.get('D3_mono'), rul[prj_level]['distribution'][3]
    d4 = form.get('prj_name'), form.get('D4'), 'D', \
         form.get('D4_check', 0), form.get('D4_mono'), rul[prj_level]['distribution'][3]
    for elements in [a, b, c1, c2, c3, c4, d1, d2, d3, d4]:
        if elements[1] != '':
            res.append(elements)
    for elements in [c1, c2, c3, c4]:
        if elements[1] != '':
            count_c += 1
    for elements in [d1, d2, d3, d4]:
        if elements[1] != '':
            count_d += 1
    return res,{'C':count_c, 'D':count_d}