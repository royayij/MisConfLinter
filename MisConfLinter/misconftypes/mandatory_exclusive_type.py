import re
import benepar

from misconftypes.parsing import tree_sentence, bfs_traversal_w_subtree, get_alias_param, type_convert

parser = benepar.Parser("benepar_en3")


def xor_mandatory_def(item):
    if re.search(r"\b(either|unless)\b", item):
        if re.search(r"\b(required)\b", item):
            return True
    if re.search(r"\b(mutually)\b", item):
        return True


def detect_xorm_def(test_df, module, param, item):
    parameters = test_df[test_df['Module_Name'] == module]['Parameter_Name'].tolist()
    aliases = test_df[test_df['Module_Name'] == module]['Aliases'].explode().tolist()
    parameters.extend(aliases)
    param_aliases = get_alias_param(test_df, module, param)
    tree = tree_sentence(parser, item)
    bfs_labels, bfs_words = bfs_traversal_w_subtree(tree)
    result = set()
    params = {param}
    values = []
    for bfs, word in zip(bfs_labels, bfs_words):
        if bfs == 'NN':
            if word[0] not in ['this', 'these', 'the', 'option'] and word[0] != param and word[0] in set(parameters):
                if word[0] in param_aliases:
                    params.add(word[0])
                else:
                    result.add(word[0])
        if bfs == 'JJ' and '=' in word[0]:
            result.add(word[0].split('=')[0])
            values.append(word[0].split('=')[1])
        if bfs == 'DT' and word[0] not in ['this', 'these', 'the', 'option', 'either']:
            values.append(word[0])
    return list(params), list(result), values


def gen_rule_xor_type(df_parameter_level_texts, env):
    df_parameter_level_texts = df_parameter_level_texts[df_parameter_level_texts['Required'] == True]
    sel_mod_parameters = df_parameter_level_texts[
        df_parameter_level_texts.apply(
            lambda x: True if xor_mandatory_def(x['Tokenized_description'].lower()) else False,
            axis=1)][['Module_Name', 'Parameter_Name', 'Module_Link', 'Tokenized_description', 'Datatype_Param']].values

    for each_val in sel_mod_parameters:
        xor_each_val = detect_xorm_def(df_parameter_level_texts, each_val[0], each_val[1], each_val[3].lower())
        rule_name = 'MandatoryExclusiveTypeRule'
        tm = env.get_template('mandatory_exclusive_template.txt')
        python_render_file = tm.render(rule_name=rule_name, rule_id=f'mandatory_exclusive_type_{each_val[0]}_{each_val[1]}',
                                       rule_desc_short='Mutually Exclusive check',
                                       rule_desc='Value  must be checked for Mutually Exclusive with other parameters. See ' +
                                                 each_val[2] + ' for more details',
                                       modules_sel=each_val[0],
                                       parameter_name=each_val[1],
                                       basic_type=each_val[4],
                                       xor_val=xor_each_val,
                                       misconfiguration_type='Illegal Existence')
        # to save the results
        with open("rules/" + each_val[0] + "_" + each_val[1] + "_mandatory_exclusive_type.py", "w") as fh:
            fh.write(python_render_file)
        fh.close()
