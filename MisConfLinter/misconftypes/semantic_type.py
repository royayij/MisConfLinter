import re
import benepar
from misconftypes.parsing import type_convert

parser = benepar.Parser("benepar_en3")


# ##### Semantic type

def semantic_type_parse_def(item, words_list):
    return re.search(r'\b({})\b'.format('|'.join(words_list)), item)



def gen_rule_semantic_type(df_parameter_level_texts, env):
    path_keywords = ['file', 'path', 'directory']
    string_keywords = ['ip address', 'mac address', 'url', 'hostname']
    # df_parameter_level_texts = df_parameter_level_texts.apply(type_convert, axis=1)


    sel_mod_parameters_df = df_parameter_level_texts[((df_parameter_level_texts['Tokenized_description'].apply(
        lambda x: semantic_type_parse_def(x, path_keywords) is not None) & (df_parameter_level_texts[
                                                                    'Datatype_Param'] == 'path')) | (
                                                                  df_parameter_level_texts[
                                                                      'Tokenized_description'].apply(
                                                                      lambda x: semantic_type_parse_def(x,
                                                                                                        string_keywords) is not None) & (
                                                                              df_parameter_level_texts[
                                                                                  'Datatype_Param'] == 'str')) | (
                                                                  df_parameter_level_texts[
                                                                      'Tokenized_description'].apply(
                                                                      lambda x: semantic_type_parse_def(x,
                                                                                                        'format') is not None) & (
                                                                              df_parameter_level_texts[
                                                                                  'Datatype_Param'] == 'str') ))
    ]



    sel_mod_parameters = \
    sel_mod_parameters_df[['Module_Name', 'Parameter_Name', 'Module_Link', 'Datatype_Param', 'Tokenized_description']].drop_duplicates().values

    # print(sel_mod_parameters_df)


    for each_val in sel_mod_parameters:
        des_each_val = each_val[4].lower()
        rule_name = 'SemanticTypeRule'
        tm = env.get_template('semantic_type_template.txt')
        python_render_file = tm.render(rule_name=rule_name, rule_id='semantic_type',
                                       rule_desc_short='Value Type must be in valid Type',
                                       rule_desc='Value Type must be in valid Type. See ' +
                                                 each_val[2] + 'for more details',
                                       modules_sel=each_val[0],
                                       parameter_name=each_val[1],
                                       basic_type=each_val[3],
                                       semantic_description=des_each_val,
                                       misconfiguration_type='Type Format')
        # to save the results
        with open("rules/" + each_val[0] + "_" + each_val[1] + "_semantic_type.py", "w") as fh:
            fh.write(python_render_file)
        fh.close()
