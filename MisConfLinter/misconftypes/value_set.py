import re



def gen_rule_value_set_type(df_parameter_level_texts, env):
    sel_mod_parameters = df_parameter_level_texts[['Module_Name', 'Parameter_Name', 'Module_Link', 'Choices', 'Datatype_Param']].values

    for each_val in sel_mod_parameters:
        rule_name = 'ValueSetTypeRule'
        tm = env.get_template('value_set_type_template.txt')
        python_render_file = tm.render(rule_name=rule_name, rule_id=f'value_set_type_{each_val[0]}_{each_val[1]}',
                                       rule_desc_short='Value must be in valid set',
                                       rule_desc='Value  must be in valid Range. See ' +
                                                 each_val[2] + ' for more details',
                                       modules_sel=each_val[0],
                                       parameter_name=each_val[1],
                                       basic_type=each_val[4],
                                       value_set=each_val[3],
                                       misconfiguration_type='Illegal Value')
        # to save the results
        with open("rules/" + each_val[0] + "_" + each_val[1] + "_value_set_type.py", "w") as fh:
            fh.write(python_render_file)
        fh.close()
