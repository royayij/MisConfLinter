import re
from misconftypes.parsing import parameters_module, words_with_capital_letters


def does_not_include_any_words(string, word_list):
    if re.search(r'\b({})\b'.format('|'.join(word_list)), string):
        return False
    return True


def env_inconsistency_def(df, item_des, module_name, spe_word_list, capital_word_list, verb_list):
    params = parameters_module(df, module_name)
    result = []
    flag = 0
    if len(capital_word_list[1:]) != 0:
        word_list = spe_word_list + capital_word_list[1:]
    else:
        word_list = spe_word_list
    for word in word_list:
        if re.search(r'{}'.format(word), item_des):
            for verb in verb_list:
                if (verb in item_des):
                    if does_not_include_any_words(item_des, params):
                        if item_des.index(verb) < item_des.index(word):
                            flag += 1
                            if word == '>=':
                                item_list = item_des.split(' ')
                                for i in item_list:
                                    if '>=' in i:
                                        word = i
                                        if len(word) == 2:
                                            index_word = item_list.index(word)
                                            new_word = item_list[index_word - 1] + word + item_list[index_word + 1]
                                            result.append(new_word)
                                        else:
                                            result.append(word)
                            else:
                                result.append(word)

    if flag != 0:
        return item_des, result


def gen_rule_env_inconsistency_type(df_parameter_level_texts, env):
    df_parameter_level_texts['Capital_word'] = df_parameter_level_texts['Tokenized_description'].apply(
        lambda x: words_with_capital_letters(x))

    word_list = ['host', 'environment', 'config', 'command', 'configure', 'rule', 'library', 'debian', 'azure',
                 'resource', 'python', 'version', 'api', '>=']
    verb_list = ['requires', 'enough', 'must', 'is not specified', 'exists on', 'depends on', 'make sure']
    sel_mod_parameters = df_parameter_level_texts[df_parameter_level_texts.apply(
        lambda x: True if env_inconsistency_def(df_parameter_level_texts, x['Tokenized_description'], x['Module_Name'], word_list,
                                                x['Capital_word'], verb_list) else False, axis=1)][
        ['Module_Name', 'Parameter_Name', 'Tokenized_description', 'Module_Link', 'Capital_word', 'Datatype_Param']].values

    for each_val in sel_mod_parameters:
        env_inconsistency_values = env_inconsistency_def(df_parameter_level_texts, each_val[2], each_val[0], word_list, each_val[4], verb_list)
        rule_name = 'EnvInconsistencyRule'
        tm = env.get_template('env_inconsistency_type_template.txt')
        python_render_file = tm.render(rule_name=rule_name, rule_id=f'env_inconsistency_type_{each_val[0]}_{each_val[1]}',
                                       rule_desc_short='Environment inconsistency of the parameter must be checked.',
                                       rule_desc='Environment inconsistency of the parameter must be checked. See ' +
                                                 each_val[3] + ' for more details',
                                       modules_sel=each_val[0],
                                       parameter_name=each_val[1],
                                       env_inc_parameter=env_inconsistency_values[0],
                                       misconfiguration_type='Illegal Value')
        # to save the results
        with open("rules/" + each_val[0] + "_" + each_val[1] + "_env_inconsistency_type.py", "w") as fh:
            fh.write(python_render_file)
        fh.close()
