import re
from misconftypes.parsing import split_conditional_sentence, datatype_parameter, parameters_module


def value_dep_def(item, data, module_name, param_name, param_datatype):
    if re.search(r'\b(if|when|unless)\b', item):
        params = parameters_module(data, module_name)
        params.remove(param_name)
        semantic_types = ['hostname', 'ip', 'mac', 'file', 'path', 'directory']
        try:
            if_sent, exclude_sent = split_conditional_sentence(item)
            for param in params:
                if re.search(r'\b{}\b'.format(param), if_sent):
                    data_type_param = datatype_parameter(data, module_name, param_name)
                    for datatype in [data_type_param] + semantic_types:
                        if re.search(r'\b{}\b'.format(datatype), if_sent):
                            for parameter_datatype in [param_datatype] + semantic_types:
                                if re.search(r'\b{}\b'.format(parameter_datatype), exclude_sent):
                                    return True
        except:
            pass

def detect_value_dep_def(item, data):
    item[2] = item[2].lower()
    result = {item[1]:[]}
    params = parameters_module(data, item[0])
    params.remove(item[1])
    semantic_types = ['hostname', 'ip', 'mac', 'file', 'path', 'directory']
    try:
        if_sent, exclude_sent = split_conditional_sentence(item[2])
        for param in params:
            if re.search(r'\b{}\b'.format(param), if_sent):
                result[param] = []
                data_type_param = datatype_parameter(data, item[0], param)
                for datatype in [data_type_param]+semantic_types:
                    if re.search(r'\b{}\b'.format(datatype), if_sent):
                        result[param].append(datatype)
                        for parameter_datatype in [item[4]]+semantic_types:
                             if re.search(r'\b{}\b'.format(parameter_datatype), exclude_sent):
                                result[item[1]].append(parameter_datatype)
    except:
        pass
    return result


def gen_rule_value_type_dependency_type(df_parameter_level_texts, env):
    sel_mod_parameters = df_parameter_level_texts[
        df_parameter_level_texts.apply(lambda x: True if value_dep_def(x['Tokenized_description'].lower(), df_parameter_level_texts, x['Module_Name'], x['Parameter_Name'], x['Datatype_Param']) else False,
                                       axis=1)][
        ['Module_Name', 'Parameter_Name', 'Tokenized_description', 'Module_Link','Datatype_Param']].values

    for each_val in sel_mod_parameters:
        type_value_dep_each_val = detect_value_dep_def(each_val, df_parameter_level_texts)
        rule_name = 'ValueTypeDependencyRule'
        tm = env.get_template('value_type_dependency_template.txt')
        python_render_file = tm.render(rule_name=rule_name, rule_id=f'value_type_dependency_{each_val[0]}_{each_val[1]}',
                                       rule_desc_short='Value must be checked for value type dependency',
                                       rule_desc='Value must be checked for value type dependency. See ' +
                                                 each_val[3] + ' for more details',
                                       modules_sel=each_val[0],
                                       parameter_name=each_val[1],
                                       basic_type=each_val[4],
                                       type_value_dep_dict=type_value_dep_each_val,
                                       misconfiguration_type='Illegal Value')
        # to save the results
        with open("rules/" + each_val[0] + "_" + each_val[1] + "_value_type_dependency.py", "w") as fh:
            fh.write(python_render_file)
        fh.close()
