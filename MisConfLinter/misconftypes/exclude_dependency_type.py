import re
import benepar

from misconftypes.parsing import parameters_module, aliases_parameter, choices_parameter

parser = benepar.Parser("benepar_en3")


def must_not_together_type_def(item, data, module_name, param_name):
    include_words = '|'.join(['cannot be \w+ in', 'cannot be \w+ with', "can’t be \w+ with", 'cannot be \w+ \w+ with', "can’t be \w+ in"])
    not_include_together_pattern = r'\b{}\b'.format(include_words)
    params = parameters_module(data, module_name)
    aliases = aliases_parameter(data, module_name, param_name)
    choices = [choices_parameter(data, module_name, param) for param in params]
    choices = [j for i in choices for j in i]
    params.extend(aliases)
    params.extend(choices)
    if re.search(not_include_together_pattern, item):
        if re.search(r'\b{}\b'.format('|'.join(params)), item):
            return True


def detect_mnt_type(data, item):
    item[2] = item[2].lower()
    params = parameters_module(data, item[0])
    aliases = aliases_parameter(data, item[0], item[1])
    choices = [choices_parameter(data, item[0], param) for param in params]
    choices = [j for i in choices for j in i]
    params.extend(aliases)
    params.extend(choices)
    result = [param for param in params if re.search(r'{}'.format(param), item[2])]
    return {item[1]: result}


def gen_rule_mnt_type(df_parameter_level_texts, env):
    sel_mod_parameters = df_parameter_level_texts[df_parameter_level_texts.apply(
        lambda x: True if must_not_together_type_def(x['Tokenized_description'].lower(), df_parameter_level_texts,
                                                     x['Module_Name'], x['Parameter_Name']) else False, axis=1)][
        ['Module_Name', 'Parameter_Name', 'Tokenized_description', 'Module_Link', 'Datatype_Param']].values

    for each_val in sel_mod_parameters:
        mnt_each_val = detect_mnt_type(df_parameter_level_texts, each_val)
        rule_name = 'ExcludeDependencyTypeRule'
        tm = env.get_template('exclude_dependency_type_template.txt')
        python_render_file = tm.render(rule_name=rule_name, rule_id=f'exclude_dependency_type_{each_val[0]}_{each_val[1]}',
                                       rule_desc_short='Must Not Used Together Check',
                                       rule_desc='Value  must be checked for must not used together with other parameters. See ' +
                                                 each_val[3] + ' for more details',
                                       modules_sel=each_val[0],
                                       parameter_name=each_val[1],
                                       basic_type=each_val[4],
                                       mnt_val=mnt_each_val,
                                       misconfiguration_type='Illegal Existence')
        # to save the results
        with open("rules/" + each_val[0] + "_" + each_val[1] + "_exclude_dependency_type.py", "w") as fh:
            fh.write(python_render_file)
        fh.close()
