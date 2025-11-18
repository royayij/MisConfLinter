# import re
# import benepar
from misconftypes.parsing import type_convert
# from parsing import tree_sentence, bfs_traversal, basic_type_def, semantic_type_def, is_sub, find_indices




def gen_rule_parameter_type(df_parameter_level_texts, env):

    sel_mod_parameters = df_parameter_level_texts[
        ['Module_Name', 'Module_Link']].drop_duplicates().values

    module_params = (
        df_parameter_level_texts
        .groupby('Module_Name')['Parameter_Name']
        .apply(list)
        .to_dict()
    )
    for each_val in sel_mod_parameters:
        parameters_each_val = module_params.get(each_val[0], None)

        rule_name = 'ParameterTypeRule'
        tm = env.get_template('parameter_type_template.txt')
        python_render_file = tm.render(rule_name=rule_name, rule_id=f'parameter_type_{each_val[0]}_{each_val[1]}',
                                       rule_desc_short='Parameter is invalid',
                                       rule_desc='Parameter is invalid. See ' +
                                                 each_val[1] + ' for more details',
                                       modules_sel=each_val[0],
                                       parameters=parameters_each_val,
                                       misconfiguration_type='Permitting')
        # to save the results
        with open("rules/" + each_val[0] + "_parameter_type.py", "w") as fh:
            fh.write(python_render_file)
        fh.close()
