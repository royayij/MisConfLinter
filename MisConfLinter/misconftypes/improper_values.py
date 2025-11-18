import re
import numpy as np
import benepar

from misconftypes.parsing import parameters_module, aliases_parameter, choices_parameter, label_word_def, tree_sentence

parser = benepar.Parser("benepar_en3")


def improper_val_def(item, disability, disability_list):
    if re.search(r'\b({})\b'.format(disability), item):
        tree = tree_sentence(parser, item)
        for word in disability_list:
            if label_word_def(tree, 'JJ', word):
                return item


def improve_def(item):
    if re.search(r'\b(improve|incorrectly)\b', item):
        return item


def gen_rule_imp_value_type(df_parameter_level_texts, env):
    disability_list = ['unsafe', 'corruption', 'undesirable', 'non-idempotent']
    disability = '|'.join(disability_list)
    sel_mod_parameters = np.vstack((df_parameter_level_texts[df_parameter_level_texts.apply(
        lambda x: True if improper_val_def(x['Tokenized_description'].lower(), disability, disability_list) else False,
        axis=1)][
                                        ['Module_Name', 'Parameter_Name', 'Tokenized_description', 'Module_Link',
                                         'Datatype_Param', 'Choices']].values, df_parameter_level_texts[
                                        df_parameter_level_texts.apply(lambda x: True if improve_def(
                                            x['Tokenized_description'].lower()) else False, axis=1)][
                                        ['Module_Name', 'Parameter_Name', 'Tokenized_description', 'Module_Link',
                                         'Datatype_Param', 'Choices']].values))

    for each_val in sel_mod_parameters:
        print(each_val)
        imp_each_val = each_val[5]
        rule_name = 'ImproperValueTypeRule'
        tm = env.get_template('improper_value_type_template.txt')
        python_render_file = tm.render(rule_name=rule_name, rule_id=f'improper_value_type_type_{each_val[0]}_{each_val[1]}',
                                       rule_desc_short='Improper Value Check',
                                       rule_desc='Value  must be checked for improper value. See ' +
                                                 each_val[3] + ' for more details',
                                       modules_sel=each_val[0],
                                       parameter_name=each_val[1],
                                       basic_type=each_val[4],
                                       imp_val=imp_each_val,
                                       misconfiguration_type='Legal Value')
        # to save the results
        with open("rules/" + each_val[0] + "_" + each_val[1] + "_improper_value_type.py", "w") as fh:
            fh.write(python_render_file)
        fh.close()
