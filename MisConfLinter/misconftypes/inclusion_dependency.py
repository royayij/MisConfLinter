import re
import benepar

from misconftypes.parsing import  split_conditional_sentence, column_module_values_def, tree_sentence, bfs_traversal, parameters_module, choices_parameter

parser = benepar.Parser("benepar_en3")

def inclusion_dep_def(data, item, module_name, param_name):
    if not re.search(r'(ignored|removed|not need)', item):
        try:
            tree = tree_sentence(parser, item)
            bfs_tree = bfs_traversal(tree)
            boolean_choices = ['yes', 'enabled', 'set', 'is specified', 'default', '*', '+', '=']
            params = parameters_module(data, module_name)
            params.remove(param_name)
            parameter_choices = choices_parameter(data, module_name, param_name)
            pattern_params = '|'.join(params)
            if re.search(r'({})'.format(pattern_params), item):
                if re.search(r'\b(if|when|unless)\b', item) and not re.search(r'\b(even|not|no)\b', item) and bfs_tree.count('SBAR') == 1:
                    try:
                        if_sent, exclude_sent = split_conditional_sentence(item)
                        for param in params:
                                param_choices = choices_parameter(data, module_name, param)
                                if re.search(r'\b{}\b'.format(param), if_sent):
                                    for choice in param_choices+boolean_choices:
                                        if re.search(r'\b{}\b'.format(choice), if_sent):

                                            for parameter_choice in parameter_choices+boolean_choices:
                                                 if re.search(r'\b{}\b'.format(parameter_choice), exclude_sent):

                                                    return True
                    except:
                        pass
        except:
            pass


def detect_conditional_inco(data, item):
    if not re.search(r'(ignored|removed|not need)', item[2]):
        det_result = {item[1]: []}
        tree = tree_sentence(parser, item[2])
        bfs_tree = bfs_traversal(tree)
        boolean_choices = ['yes', 'no', 'enabled', 'set', 'is specified', '*', '+', 'default']
        params = parameters_module(data, item[0])
        params.remove(item[1])
        #     print(params)
        parameter_choices = choices_parameter(data, item[0], item[1])
        pattern_params = '|'.join(params)
        # print(pattern_params)
        if re.search(r'({})'.format(pattern_params), item[2]):
            try:
                if_sent, exclude_sent = split_conditional_sentence(item[2])
                # print(if_sent)
                for param in params:
                    param_choices = choices_parameter(data, item[0], param)
                    if re.search(r'\b{}\b'.format(param), if_sent):

                        det_result[param] = []
                        for choice in param_choices + boolean_choices:
                            if re.search(r'\b{}\b'.format(choice), if_sent):
                                det_result[param].append(choice)
                                for parameter_choice in parameter_choices + boolean_choices:
                                    if re.search(r'\b{}\b'.format(parameter_choice), exclude_sent):
                                        det_result[item[1]].append(parameter_choice)
                # print(det_result)

            except:
                pass
        for key in det_result.keys():
            if det_result[key] == [] and re.search(r'\b{}\b'.format('default'), if_sent):
                det_result[key].append('default')
        if det_result[item[1]] == [] and re.search(r'\b{}\b'.format('default'), exclude_sent):
            det_result[item[1]].append('default')
        for key in det_result.keys():
            if len(det_result[key]) > 1 and re.search(r'\b{}\b'.format('default'), exclude_sent):
                index_defualt = item[2].find('default')
                keys_index = {val: abs(item[2].find(val) - index_defualt) for val in det_result[key]}
                # print(min(keys_index, key=lambda k: keys_index[k]))
                det_result[key].remove(min(keys_index, key=lambda k: keys_index[k]))
            if re.search(r'\b({})\b'.format('|'.join(['enabled', 'set', 'is specified', 'yes'])),
                         ' '.join(det_result[key])):
                det_result[key] = 'True'

        return det_result
def gen_rule_inclusion_dependency_type(df_parameter_level_texts, env):
    sel_mod_parameters = df_parameter_level_texts[df_parameter_level_texts.apply(
        lambda x: True if inclusion_dep_def(df_parameter_level_texts, x['Tokenized_description'], x['Module_Name'],
                                               x['Parameter_Name']) else False, axis=1)] [
        ['Module_Name', 'Parameter_Name','Tokenized_description','Module_Link', 'Datatype_Param']].values

    for each_val in sel_mod_parameters:
        inc_dep_each_val = detect_conditional_inco(df_parameter_level_texts, each_val)
        rule_name = 'InclusionDependencyTypeRule'
        tm = env.get_template('inclusion_dependency_type_template.txt')
        python_render_file = tm.render(rule_name=rule_name, rule_id=f'inclusion_dependency_type_{each_val[0]}_{each_val[1]}',
                                       rule_desc_short='Value must be checked for inclusion dependency',
                                       rule_desc='Value must be checked for inclusion dependency. See ' +
                                                 each_val[3] + ' for more details',
                                       modules_sel=each_val[0],
                                       parameter_name=each_val[1],
                                       basic_type=each_val[4],
                                       inc_dep_dict=inc_dep_each_val,
                                       misconfiguration_type='Illegal Value')
        # to save the results
        with open("rules/" + each_val[0] + "_" + each_val[1] + "_inclusion_dependency_type.py", "w") as fh:
            fh.write(python_render_file)
        fh.close()
