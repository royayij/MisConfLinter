from jinja2 import Environment, FileSystemLoader

from ansible_module_documentation import load_module_parameter_docs
from ansible_module_documentation import load_tokenized_parameter_docs
from misconftypes.aliases import gen_rule_aliases_type
from misconftypes.basic_type import gen_rule_basic_type
from misconftypes.semantic_type import gen_rule_semantic_type
from misconftypes.conditionally_mandatory_type import gen_rule_cm_type
from misconftypes.env_inconsistency_type import gen_rule_env_inconsistency_type
from misconftypes.ineffective_parameter import gen_rule_igc_type
from misconftypes.improper_values import gen_rule_imp_value_type
from misconftypes.improper_alt_values import gen_rule_imp_alt_value_type
from misconftypes.include_dependency_type import gen_rule_mt_type
from misconftypes.exclude_dependency_type import gen_rule_mnt_type
from misconftypes.value_set import gen_rule_value_set_type
from misconftypes.value_range import gen_rule_value_range_type
from misconftypes.inclusion_dependency import gen_rule_inclusion_dependency_type
from misconftypes.exclusion_dependancy import gen_rule_exclusion_dependency_type
from misconftypes.value_type_dependency import gen_rule_value_type_dependency_type
from misconftypes.mandatory_exclusive_type import gen_rule_xor_type
from misconftypes.Parameter_module_check import gen_rule_parameter_type



def generate_linter_rules():
    env = Environment(loader=FileSystemLoader('templates'))
    # df_module_level_texts, df_parameter_level_texts = load_module_parameter_docs()
    df_parameter_level_texts = load_tokenized_parameter_docs()
    # gen_rule_basic_type(df_parameter_level_texts.copy(), env)
    # gen_rule_semantic_type(df_parameter_level_texts.copy(), env)
    # gen_rule_value_range_type(df_parameter_level_texts.copy(), env)
    # gen_rule_value_set_type(df_parameter_level_texts.copy(), env)
    # gen_rule_inclusion_dependency_type(df_parameter_level_texts.copy(), env)
    # gen_rule_exclusion_dependency_type(df_parameter_level_texts.copy(), env)
    # gen_rule_value_type_dependency_type(df_parameter_level_texts.copy(), env)
    # gen_rule_env_inconsistency_type(df_parameter_level_texts.copy(), env)
    # gen_rule_cm_type(df_parameter_level_texts.copy(), env)
    # gen_rule_xor_type(df_parameter_level_texts.copy(), env)
    gen_rule_igc_type(df_parameter_level_texts.copy(), env)
    # gen_rule_mnt_type(df_parameter_level_texts.copy(), env)
    # gen_rule_mt_type(df_parameter_level_texts.copy(), env)
    # gen_rule_imp_value_type(df_parameter_level_texts.copy(), env)
    # gen_rule_aliases_type(df_parameter_level_texts.copy(), env)
    # gen_rule_imp_alt_value_type(df_parameter_level_texts.copy(), env)
    # gen_rule_parameter_type(df_parameter_level_texts.copy(), env)


generate_linter_rules()
