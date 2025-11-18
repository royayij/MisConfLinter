import re
from misconftypes.parsing import type_convert




def value_range_def(item):
    if "characters" not in item:
        if re.search(r"from\s+\d+\s+to\s+\d+", item) or re.search(r'\b(between)\b\s*\d+', item):
            return True
        elif re.search(r'(?<!\.)\b[0-9]+\b(?!\.)', item):
            if re.search(r'\b(minimum|maximum|min|max|less|greater)\b', item):
                return True
    return False

def convert_to_dict_all(items):
    if not items:
        return {}

    result = {}
    i = 0
    n = len(items)

    def as_str(item):
        return str(item).lower() if isinstance(item, str) else None

    while i < n:
        key = as_str(items[i])

        # Process only known keywords
        if key in ['min', 'minimum', 'max', 'maximum', 'between', 'range']:
            values = []
            j = i + 1

            # Collect following values until next keyword
            while j < n:
                next_item = items[j]
                next_key = as_str(next_item)
                if next_key in ['min', 'minimum', 'max', 'maximum', 'between', 'range']:
                    break

                # Case 1: next_item is a list like ['10'] or [[('0','1440')]]
                if isinstance(next_item, list) and next_item:
                    first = next_item[0]

                    # Case 1a: nested tuple like ('0', '1440')
                    if isinstance(first, tuple):
                        for val in first:
                            try:
                                values.append(val)
                            except (TypeError, ValueError):
                                continue

                    # Case 1b: simple value inside list
                    else:
                        try:
                            values.append(first)
                        except (TypeError, ValueError):
                            continue

                # Case 2: direct int, float, or string
                elif isinstance(next_item, (int, float, str)):
                    try:
                        values.append(next_item)
                    except ValueError:
                        continue

                j += 1

            # Assign values according to keyword logic
            if key in ['min', 'minimum']:
                if len(values) == 1:
                    result['min'] = values[0]
                elif len(values) >= 2:
                    result['between'] = tuple(values[:2])

            elif key in ['max', 'maximum']:
                if len(values) == 1:
                    result['max'] = values[0]
                elif len(values) >= 2:
                    result['between'] = tuple(values[:2])

            elif key in ['between', 'range']:
                if len(values) >= 2:
                    result['between'] = tuple(values[:2])
                elif len(values) == 1:
                    result['between'] = (values[0],)

            # Move to the next keyword
            i = j
        else:
            i += 1

    return result



def find_digit(item):
    print(item)
    result = []

    if re.search(r'from\s+(\d+)\s+to\s+(\d+)', item):

        from_to_matches = re.findall(r'from\s+(\d+)\s+to\s+(\d+)', item, flags=re.IGNORECASE)
        for start, end in from_to_matches:
            result.append(['between', [start], [end]])
            print(result[0])
            return convert_to_dict_all(result[0])


    for i in item.split(' '):
        if re.search(r'{}'.format('|'.join(['range', 'between', 'greater', 'less', 'min', 'max'])), i):
            result.append(i)
        if len(re.findall(r"-*\d+[A-Za-z]+", i)) == 0:
            if len(re.findall(r"[-+]?(?:\d*\.+\d+)", i)) != 0:
                result.append(re.findall(r"[-+]?(?:\d*\.+\d+)", i))
            elif re.search(r'\b(\d+)-(\d+)\s*\b', i):
                result.append(re.findall(r'\b(\d+)-(\d+)\s*\b', i))

            else:
                if re.search(r'-*\d+', i):
                    result.append(re.findall(r'-*\d+', i))
    print(result)
    return convert_to_dict_all(result)



def detect_type_from_string(value_str):
    """Detect whether a string represents an int, float, or something else."""
    print(value_str)
    if re.fullmatch(r'-?\d+', value_str):  # integer pattern
        return int(value_str)
    elif re.fullmatch(r'-?\d*\.\d+', value_str):  # float pattern
        return float(value_str)
    else:
        return value_str


def gen_rule_value_range_type(df_parameter_level_texts, env):
    df_parameter_level_texts = df_parameter_level_texts.apply(type_convert, axis=1)
    sel_mod_parameters = df_parameter_level_texts[
        df_parameter_level_texts.apply(lambda x: True if value_range_def(x['Tokenized_description'].lower()) else False,
                                       axis=1)][
        ['Module_Name', 'Parameter_Name', 'Module_Link', 'Tokenized_description', 'Datatype_Param']].values

    for each_val in sel_mod_parameters:
        print(each_val)
        value_range_each_val = find_digit(each_val[3].lower())
        param_type = each_val[4]

        filtered_value_range = {}
        for k, v in value_range_each_val.items():
            if param_type in ['str', 'int', 'float']:
                if isinstance(v, tuple):
                        filtered_value_range[k] = tuple(detect_type_from_string(x) for x in v)
                else:
                        filtered_value_range[k] = detect_type_from_string(v)
        if filtered_value_range != {}:
            rule_name = 'ValueRangeTypeRule'
            tm = env.get_template('value_range_type_template.txt')
            python_render_file = tm.render(rule_name=rule_name, rule_id='value_range_type',
                                           rule_desc_short='Value must be in valid Range',
                                           rule_desc='Value  must be in valid Range. See ' +
                                                     each_val[2] + ' for more details',
                                           modules_sel=each_val[0],
                                           parameter_name=each_val[1],
                                           basic_type=each_val[4],
                                           value_ranges=filtered_value_range,
                                           misconfiguration_type='Illegal Value')
            # to save the results
            with open("rules/" + each_val[0] + "_" + each_val[1] + "_value_range_type.py", "w") as fh:
                fh.write(python_render_file)
            fh.close()
