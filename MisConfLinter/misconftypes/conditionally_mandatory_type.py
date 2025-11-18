import re
import benepar

from misconftypes.parsing import tree_sentence, bfs_traversal, split_conditional_sentence, parameters_module, \
    aliases_parameter, choices_parameter

parser = benepar.Parser("benepar_en3")


def conditionally_mandatory_def(item, data, module_name, param_name):
    params = parameters_module(data, module_name)
    params.remove(param_name)
    params = [param.replace(')', '') for param in params]
    pattern = '|'.join(params)
    if re.search(r'({})'.format(pattern), item):
        if re.search(r'\b(if|when)\b', item):
            try:
                if_sent, exclude_sent = split_conditional_sentence(item)
                if re.search(r'\b(required|mandatory|is needed)\b', exclude_sent) and (
                        'RB' not in bfs_traversal(tree_sentence(parser, exclude_sent))) and (
                        'RB' not in bfs_traversal(tree_sentence(parser, if_sent))):
                    return True
            except:
                pass


def detect_conm_def(data, item):
    item[2] = item[2].lower()
    result = {'module_name': item[0], 'param_name': item[1], 'choices': {}}
    parameters = parameters_module(data, item[0])
    aliases = aliases_parameter(data, item[0], item[1])
    parameters.extend(aliases)
    for param in parameters:
        try:
            if re.search(r'\b{}\b'.format(param), item[2]):
                result['choices'][param] = []
                choices = ['no', 'yes']
                choices_param = choices_parameter(data, item[0], param)
                if choices_param != None:
                    choices.extend(choices_param)
                for choice in choices:
                    if re.search(r'\b{}\b'.format(choice), item[2]):
                        result['choices'][param].append(choice)

        except:
            pass
    return result


def gen_rule_cm_type(df_parameter_level_texts, env):
    df_parameter_level_texts = df_parameter_level_texts[df_parameter_level_texts['Required'] == True]
    sel_mod_parameters = df_parameter_level_texts[df_parameter_level_texts.apply(
        lambda x: True if conditionally_mandatory_def(x['Tokenized_description'].lower(), df_parameter_level_texts,
                                                      x['Module_Name'], x['Parameter_Name']) else False, axis=1)][
        ['Module_Name', 'Parameter_Name', 'Tokenized_description', 'Module_Link', 'Datatype_Param']].values

    for each_val in sel_mod_parameters:
        cm_each_val = detect_conm_def(df_parameter_level_texts, each_val)
        print(cm_each_val)
        rule_name = 'ConditionallyMandatoryTypeRule'
        tm = env.get_template('conditionally_mandatory_type_template.txt')
        python_render_file = tm.render(rule_name=rule_name, rule_id=f'conditionally_mandatory_type_{each_val[0]}_{each_val[1]}',
                                       rule_desc_short='Conditionally Mandatory Check',
                                       rule_desc='Value  must be checked for conditionally mandatory with other parameters. See ' +
                                                 each_val[3] + ' for more details',
                                       modules_sel=each_val[0],
                                       parameter_name=each_val[1],
                                       basic_type=each_val[4],
                                       cm_val=cm_each_val,
                                       misconfiguration_type='Illegal Existence')
        # to save the results
        with open("rules/" + each_val[0] + "_" + each_val[1] + "_conditionally_mandatory_type.py", "w") as fh:
            fh.write(python_render_file)
        fh.close()
