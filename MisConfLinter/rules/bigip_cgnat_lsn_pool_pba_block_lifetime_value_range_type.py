from typing import TYPE_CHECKING, Any, Dict, Union
# Auto Generated Rules. Do not change manually
from ansiblelint.rules import AnsibleLintRule
import re

if TYPE_CHECKING:
    from typing import Optional

    from ansiblelint.file_utils import Lintable

class ValueRangeTypeRule(AnsibleLintRule):
    id = 'value_range_type'
    shortdesc = 'Value must be in valid Range'
    description = 'Value  must be in valid Range. See https://docs.ansible.com/ansible/latest/collections/f5networks/f5_modules/bigip_cgnat_lsn_pool_module.html for more details'
    tags = ['Illegal Value']
    param_value_ranges ={'between': (0, 4294967295)}

    param_type = int

    _modules = ['bigip_cgnat_lsn_pool']

    def check_values(self, param_value: int, values: dict):
        try:
            if any(k in values for k in ['max', 'less']):
                max_val = values.get('max') or values.get('less')
                max_val = float(max_val)
                if float(param_value) <= max_val:
                    return True

            if any(k in values for k in ['min', 'greater']):
                min_val = values.get('min') or values.get('greater')
                min_val = float(min_val)
                if float(param_value) >= min_val:
                    return True

            if any(k in values for k in ['range', 'between']):
                range_vals = values.get('range') or values.get('between')
                # Ensure range_vals is a tuple like ('10', '20')
                if isinstance(range_vals, (list, tuple)) and len(range_vals) == 2:
                    low = float(range_vals[0])
                    high = float(range_vals[1])
                    if (low <= float(param_value)) &  (float(param_value)<= high):
                        return True

        except Exception:
            return False

        return False

    def matchtask(
        self, task: Dict[str, Any], file: 'Optional[Lintable]' = None
    ) -> Union[bool, str]:
        if task["action"]["__ansible_module__"].split('.')[-1] in self._modules:
            value = task['action'].get('pba_block_lifetime', None)
            return not self.check_values(value, self.param_value_ranges)
        return False