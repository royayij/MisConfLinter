from misconftypes.parsing import parameters_module
import re

def improper_alt_def(item, data, module_name, param_name):
    alternative_list = [ 'not recommended', ' in favour of', 'incorrectly', 'otherwise']
    alternatives = '|'.join(alternative_list)
    params = parameters_module(data, module_name)
    params.remove(param_name)
    for param in params:
        if re.search(r'{}'.format(param), item):
            if re.search(r'use', item):
                    if re.search(r'\b({})\b'.format(alternatives), item):
                        if not re.search(r'\b(if|when)\b' , item):
                            return param


def gen_rule_imp_alt_value_type(df_parameter_level_texts, env):

    sel_mod_parameters = df_parameter_level_texts[df_parameter_level_texts.apply(lambda x: True if improper_alt_def(x['Tokenized_description'].lower(),df_parameter_level_texts, x['Module_Name'], x['Parameter_Name'] ) else False,
        axis=1)][['Module_Name', 'Parameter_Name', 'Tokenized_description', 'Module_Link',
                                         'Datatype_Param']].values
    for each_val in sel_mod_parameters:
        imp_alt_each_val = improper_alt_def(each_val[2], df_parameter_level_texts, each_val[0], each_val[1])
        rule_name = 'ImproperAlternativeValueTypeRule'
        tm = env.get_template('improper_alternative_value_type_template.txt')
        python_render_file = tm.render(rule_name=rule_name, rule_id=f'improper_alternative_value_type_type_{each_val[0]}_{each_val[1]}',
                                       rule_desc_short='Improper alternative Value Check',
                                       rule_desc='Value  must be checked for improper value. See ' +
                                                 each_val[3] + ' for more details',
                                       modules_sel=each_val[0],
                                       parameter_name=each_val[1],
                                       basic_type=each_val[4],
                                       imp_alt_val=imp_alt_each_val,
                                       misconfiguration_type='Legal Existence')
        # to save the results
        with open("rules/" + each_val[0] + "_" + each_val[1] + "_improper_alternative_value_type.py", "w") as fh:
            fh.write(python_render_file)
        fh.close()
