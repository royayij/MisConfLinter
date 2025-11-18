import re
import benepar

from misconftypes.parsing import parameters_module, aliases_parameter, choices_parameter

parser = benepar.Parser("benepar_en3")


def must_together_type_def(item ,data, module_name, param_name):
    params = parameters_module(data, module_name)
    aliases = aliases_parameter(data, module_name, param_name)
    params.extend(aliases)
    params.remove(param_name)
    if re.search(r'\bRequires\b', item):
        params_result = []
        for param in params:
            if re.search(r'\b{}\b'.format(param), item):
                params_result.append(param)
        if len(params_result) != 0:
            return True


def detect_mt_def(item, data):
    result = {item[1]: []}
    params = parameters_module(data, item[0])
    params.remove(item[1])
    for param in params:
        aliases = aliases_parameter(data, item[0], param)
        choices = choices_parameter(data, item[0], param)
        aliases.append(param)
        for i in aliases:
            if re.search(r'\b{}\b'.format(i), item[2]):
                result[param] = []
                for choice in choices:
                    if re.search(r'\b{}\b'.format(choice), item[2]):
                        result[param].append(choice)
    return result


def gen_rule_mt_type(df_parameter_level_texts, env):
    sel_mod_parameters = df_parameter_level_texts[df_parameter_level_texts.apply(
        lambda x: True if must_together_type_def(x['Tokenized_description'].lower(), df_parameter_level_texts,
                                                     x['Module_Name'], x['Parameter_Name']) else False, axis=1)][
        ['Module_Name', 'Parameter_Name', 'Tokenized_description', 'Module_Link', 'Datatype_Param']].values

    for each_val in sel_mod_parameters:
        mt_each_val = detect_mt_def(df_parameter_level_texts, each_val)
        rule_name = 'IncludeDependencyTypeRule'
        tm = env.get_template('include_dependency_type_template.txt')
        python_render_file = tm.render(rule_name=rule_name, rule_id=f'include_dependency_type_{each_val[0]}_{each_val[1]}',
                                       rule_desc_short='Must Used Together Check',
                                       rule_desc='Value  must be checked for must used together with other parameters. See ' +
                                                 each_val[3] + ' for more details',
                                       modules_sel=each_val[0],
                                       parameter_name=each_val[1],
                                       basic_type=each_val[4],
                                       mt_val=mt_each_val,
                                       misconfiguration_type='Illegal Existence')
        # to save the results
        with open("rules/" + each_val[0] + "_" + each_val[1] + "_include_dependency_type.py", "w") as fh:
            fh.write(python_render_file)
        fh.close()
