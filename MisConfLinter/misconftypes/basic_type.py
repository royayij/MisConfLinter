# import re
# import benepar
from misconftypes.parsing import type_convert
# from parsing import tree_sentence, bfs_traversal, basic_type_def, semantic_type_def, is_sub, find_indices


def gen_rule_basic_type(df_parameter_level_texts, env):
    sel_mod_parameters = df_parameter_level_texts[
        ['Module_Name', 'Parameter_Name', 'Module_Link','Datatype_Param', 'Datatype_Param_Second']].drop_duplicates().values

    for each_val in sel_mod_parameters:
        basic_type_each_val = each_val[3]
        basic_type_item = each_val[4]
        rule_name = 'BasicTypeRule'
        tm = env.get_template('basic_type_template.txt')
        python_render_file = tm.render(rule_name=rule_name, rule_id=f'basic_type_{each_val[0]}_{each_val[1]}',
                                       rule_desc_short='Value Type must be in valid Type',
                                       rule_desc='Value Type must be in valid Type. See ' +
                                                 each_val[2] + ' for more details',
                                       modules_sel=each_val[0],
                                       parameter_name=each_val[1],
                                       basic_type=basic_type_each_val,
                                       basic_type_item=basic_type_item,
                                       misconfiguration_type='Type Format')
        # to save the results
        with open("rules/" + each_val[0] + "_" + each_val[1] + "_basic_type.py", "w") as fh:
            fh.write(python_render_file)
        fh.close()
