import re
import benepar

from misconftypes.parsing import find_if_sents, split_conditional_sentence, parameters_module, \
    aliases_parameter, detect_def


parser = benepar.Parser("benepar_en3")


def ignored_conditional_def(item, data, module_name, param_name):
    params = parameters_module(data, module_name)
    params.remove(param_name)
    params = [param.replace(')', '') for param in params]
    pattern = '|'.join(params)
    if re.search(r'({})'.format(pattern), item):
        if re.search(r'\b(if|when)\b', item):
            try:
                if_sent, exclude_sent = split_conditional_sentence(item)
                ignore_list = '|'.join(['ignored', 'not needed', 'not required', 'is optional', 'has no effect'])
                if re.search(r'({})'.format(ignore_list), exclude_sent):
                    return True
            except:
                pass
        else:
            if re.search(r'\b(is optional|has no effect)\b', item):
                return True


def detect_ign_def(data, item):
    item[2] = item[2].lower()
    result = {'module_name': item[0], 'param_name': item[1], 'choices': {}}
    parameters = parameters_module(data, item[0])
    aliases = aliases_parameter(data, item[0], item[1])
    parameters.extend(aliases)
    if re.search(r'\b(if|when)\b', item[2]):
        for if_sent in find_if_sents(item[2]):
            for param in parameters:
                if param != item[1]:
                    result = detect_def(data, if_sent, param, result, item[0])
    else:
        for param in parameters:
            if param != item[1]:
                result = detect_def(data, item[2], param, result, item[0])
    choices_keys = list(result['choices'].keys())
    for ind, key in enumerate(choices_keys):
        if ind != len(choices_keys) - 1:
            if key + '.' + choices_keys[ind + 1] in item[2]:
                del result['choices'][key]
    print(result)

    return result


def gen_rule_igc_type(df_parameter_level_texts, env):
    sel_mod_parameters = df_parameter_level_texts[df_parameter_level_texts.apply(
        lambda x: True if ignored_conditional_def(x['Tokenized_description'].lower(), df_parameter_level_texts,
                                                  x['Module_Name'], x['Parameter_Name']) else False, axis=1)][
        ['Module_Name', 'Parameter_Name', 'Tokenized_description', 'Module_Link', 'Datatype_Param']].values

    for each_val in sel_mod_parameters:
        ign_each_val = detect_ign_def(df_parameter_level_texts, each_val)
        rule_name = 'IneffectiveParameterTypeRule'
        tm = env.get_template('ineffective_parameter_type_template.txt')
        python_render_file = tm.render(rule_name=rule_name, rule_id=f'ineffective_parameter_type_{each_val[0]}_{each_val[1]}',
                                       rule_desc_short='Ineffective Parameter Check',
                                       rule_desc='Value  must be checked for conditionally ineffective with other parameters. See ' +
                                                 each_val[3] + ' for more details',
                                       modules_sel=each_val[0],
                                       parameter_name=each_val[1],
                                       basic_type=each_val[4],
                                       ign_val=ign_each_val,
                                       misconfiguration_type='Illegal Existence')
        # to save the results
        with open("rules/" + each_val[0] + "_" + each_val[1] + "_ineffective_parameter_type.py", "w") as fh:
            fh.write(python_render_file)
        fh.close()
