def gen_rule_aliases_type(df_parameter_level_texts, env):
    sel_mod_parameters = df_parameter_level_texts[
        ['Module_Name', 'Parameter_Name', 'Module_Link', 'Aliases', 'Datatype_Param']].values

    for each_val in sel_mod_parameters:
        rule_name = 'AliasesTypeRule'
        tm = env.get_template('aliases_type_template.txt')
        python_render_file = tm.render(rule_name=rule_name, rule_id=f'aliases_type_{each_val[0]}_{each_val[1]}',
                                       rule_desc_short='Aliases check',
                                       rule_desc='Parameter name must be checked for its aliases. See ' +
                                                 each_val[2] + ' for more details',
                                       modules_sel=each_val[0],
                                       parameter_name=each_val[1],
                                       basic_type=each_val[4],
                                       aliases_val=each_val[3],
                                       misconfiguration_type='Legal Existence')
        # to save the results
        with open("rules/" + each_val[0] + "_" + each_val[1] + "_aliases_type.py", "w") as fh:
            fh.write(python_render_file)
        fh.close()
