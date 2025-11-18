import pandas as pd
import re
import nltk
import benepar
import os

os.environ['TRANSFORMERS_NO_ADVISORY_WARNINGS'] = 'true'

# Download and load the pre-trained parser
# benepar.download('benepar_en3')
parser = benepar.Parser("benepar_en3")


# nltk.download('punkt')


# ### Read Data

def read_data(path):
    return pd.read_excel(path)


# #### CORPUS: Include descriptions of all parameters


def corpus_def(df):
    desc_lists = df['Description'].tolist()

    corpus = [nltk.sent_tokenize(desc) for desc in desc_lists]

    corpus_list = list(set(item.strip(' ') for sublist in corpus for item in sublist))
    return corpus_list


# #### Pararameters


def parameter_def(df, corpus_list):
    param_names = df['Parameter_Name'].unique().tolist()

    parameters = ['option', 'parameter']

    for item in corpus_list:
        pattern_item = r'^((?!http|https)[a-zA-Z]).*$'
        if bool(re.match(pattern_item, item)):
            for word in item.split():
                if '_' in word and bool(re.match(r'^((?!http|https)).*$', word)):
                    parameters.append(word.strip('.'))
    parameters.extend(param_names)
    return list(set(parameters))


def values(df):
    choices = df['Choices'].unique().tolist()
    choice_list = [eval(item) if item != '[]' else [] for item in choices]
    choice_list = [elem.replace(" ", "").replace('"', '').replace('*', '').replace('%', '') for sublist in choice_list
                   for elem in sublist]
    choice_list = set(choice_list)
    return choice_list


def tree_sentence(parser, sentence):
    tree = parser.parse(sentence)
    return tree


# #### POS_Functions


def pos_sen(sentence):
    doc = nlp(sentence)
    pos = []
    sen = []
    for token in doc:
        pos.append(token.dep_)
        sen.append(token.text)
    return pos, sen


def common_items_def(pos_1, pos_2):
    # Find the common items in the order of list 'a'
    a = pos_1.copy()
    b = pos_2.copy()
    common_items = []
    for item in a:
        if item in b and (item != 'punct'):
            common_items.append(item)
            b = b[b.index(item) + 1:]
    return common_items


def pos_def(doc):
    POS_doc = []
    for sentence in doc:
        pos = []
        # process the sentence with the model
        doc = nlp(sentence)
        for token in doc:
            #         print("{}: {}".format(token, token.dep_))
            pos.append(token.dep_)
        POS_doc.append((sentence, pos))

    return POS_doc


def is_subsequence(a, b):
    """Check if list b is a contiguous subsequence in list a"""
    a_len = len(a)
    b_len = len(b)
    i = 0
    for j in range(a_len):

        if a[j] == b[i]:
            i += 1
        if i == b_len:
            return True
    return False


def subset_common_list(lst):
    subsets = []

    for i in range(len(lst)):
        for j in range(i + 1, len(lst) + 1):
            subset = lst[i:j]
            subsets.append(subset)

    result = []
    for i in range(len(subsets)):
        for j in range(i + 1, len(subsets)):
            if len(subsets[i]) + len(subsets[j]) <= len(lst):
                merged = subsets[i] + subsets[j]
                if len(merged) > 1:
                    result.append(merged)
    result_f = set()
    for item in result:
        item = list(dict.fromkeys(item))
        result_f.add(tuple(item))
    return result_f


def find_sentences(pos_doc, common_items, doc):
    rst = []
    for item in pos_doc:
        #     print(item)
        senc_list = item[0].split(' ')
        #         for word in senc_list:
        #                     word_position = senc_list.index(word)
        #         if word_position >  item[1].index('ROOT'):
        subset_common_items = subset_common_list(common_items)
        for subset in subset_common_items:
            if subset[0] == common_items[0] and subset[-1] == common_items[-1] and 'ROOT' in subset:
                check = is_subsequence(item[1], subset)
                if check:
                    print(subset)
                    print(item[1])
                    senc = doc[pos_doc.index(item)]
                    print(senc)
                    rst.append(senc)
                    print("------------------------")
    return set(rst)


# #### Find words or a sentence in corpus

# In[33]:


def find_words(doc, word_list):
    ds_sentences = set()
    for item in doc:
        for word in item.split(' '):
            if (word.lower() or word[:-1].lower()) in word_list:
                ds_sentences.add(item)
    return list(ds_sentences)


def find_sen_corpus(sen, doc):
    for index, item in enumerate(doc):
        if sen in item:
            print(index)


# #### BFS Traverse a tree


def bfs_traversal(tree):
    """
    Performs a breadth-first traversal of the input tree.
    """
    result = []
    queue = [tree]
    while queue:
        node = queue.pop(0)
        result.append(node.label())
        #         print(node.label())
        for child in node:
            if isinstance(child, nltk.tree.Tree):
                queue.append(child)
    return result


# ### Find a sublist with same order in a list


def is_a_in_x(A, X):
    for i in range(len(X) - len(A) + 1):
        if A == X[i:i + len(A)]:
            return True
    return False


# ### Find words based on their labels
def is_sub(sub, lst):
    ln = len(sub)
    for i in range(len(lst) - ln + 1):
        if all(sub[j] == lst[i + j] for j in range(ln)):
            return i
    return False


def find_indices(list_to_check, item_to_find):
    return [idx for idx, value in enumerate(list_to_check) if value == item_to_find]


def get_words(tree, label):
    words = []
    for subtree in tree.subtrees():
        if subtree.label() == label:
            words.append(subtree[0])
    return words


from pathlib import Path
from typing import Any


def get_python_type(type_str: str):
    """
    Convert API documentation type to Python's built-in type.
    """
    type_map = {
        'string': 'str',
        'path': 'path',
        'dictionary': 'dict',
        'boolean': 'bool',
        'list': 'list',
        'integer': 'int',
        'float': 'float',
        'any': 'any',
        'jsonarg': 'json'
    }

    return type_map.get(type_str.lower())


def type_convert(row):
    # Check if 'required' is in the Datatype_Param column
    if 'required' in str(row['Datatype_Param']):
        # Remove 'required' from the original value and strip any leading/trailing spaces
        row['Datatype_Param'] = row['Datatype_Param'].replace('required', '').strip()
        # Create a new column indicating 'required'
        row['Required'] = True
    else:
        # If 'required' is not found, set the new column to False
        row['Required'] = False

    # Split the Datatype_Param into two parts (if possible)
    split_data = row['Datatype_Param'].split(' / ')

    # Assign the resulting split data to the columns
    row['Datatype_Param'] = get_python_type(split_data[0].split(' /')[0])
    row['Datatype_Param_Second'] = split_data[1] if len(split_data) > 1 else None

    # If '=' is found in Datatype_Param_Second, split it and keep the second part
    if row['Datatype_Param_Second'] and '=' in str(row['Datatype_Param_Second']):
        row['Datatype_Param_Second'] = row['Datatype_Param_Second'].split('=')[1]
        row['Datatype_Param_Second'] = get_python_type(row['Datatype_Param_Second'].split(' /')[0])
    elif row['Datatype_Param_Second'] != None:
        row['Datatype_Param_Second'] = get_python_type(row['Datatype_Param_Second'])

    return row


def semantic_type_def(item):
    try:
        tree = tree_sentence(parser, item)
        dfs_tree = [subtree.label() for subtree in tree.subtrees()]
        if dfs_tree.count('S') == 1:
            if re.search(r'\b(must be|should be|can be)\b', item):
                VP_indecies = find_indices(dfs_tree, 'VP')
                NP_indecies = find_indices(dfs_tree, 'NP')
                for i in VP_indecies:
                    for j in NP_indecies:
                        if j > i and j - i < 3:
                            return True
    except:
        pass

def basic_type_def(item, words_list):
    # if re.search(r'\b({})\b'.format('|'.join(words_list)), item):
    try:
        tree = tree_sentence(parser, item)
        subtrees = [subtree for subtree in tree.subtrees()]
        bfs_search_tree = bfs_traversal(tree)
        if is_sub(['NP', 'NP', 'PP'], bfs_search_tree):
            index_np = is_sub(['NP', 'NP', 'PP'], bfs_search_tree)
            if item[-1] != '.':
                index_np = index_np + 1
            np_subtree = subtrees[index_np]
            wd_subtree = subtrees[index_np + 1]
            if re.search(r'\b({})\b'.format('|'.join(words_list)), ' '.join(wd_subtree.leaves())):
                for wd in words_list:
                    if wd in ' '.join(np_subtree.leaves()).lower():
                        if is_sub(['IN', 'NP'], bfs_search_tree[index_np + 3:]):
                            return True
        elif semantic_type_def(item):
            return True
    except:
        pass


# def semantic_type_def(item):
#     try:
#         tree = tree_sentence(parser, item)
#         dfs_tree = [subtree.label() for subtree in tree.subtrees()]
#         if dfs_tree.count('S') == 1:
#             if re.search(r'\b(must be|should be|can be)\b', item):
#                 VP_indecies = find_indices(dfs_tree, 'VP')
#                 NP_indecies = find_indices(dfs_tree, 'NP')
#                 for i in VP_indecies:
#                     for j in NP_indecies:
#                         if j > i and j - i < 3:
#                             return True
#     except:
#         pass


def split_conditional_sentence(item):
    tree = tree_sentence(parser, item)
    sent = [' '.join(subtree.leaves()) for subtree in tree.subtrees() if subtree.label() == 'TOP'][0]
    count = 0
    for subtree in tree.subtrees():
        if subtree.label() == 'SBAR' and (
                subtree[0].leaves()[0] in ['if', 'when', 'unless', 'where', 'If', 'When']) and count < 1:
            count += 1
            if_state = ' '.join(subtree.leaves())
            regex_pattern = r'{}(\s*,\s*)?'.format(re.escape(if_state))
            exclude_sentence = re.sub(regex_pattern, '', sent)
            return (if_state, exclude_sentence)


def column_module_values_def(df, module_name, column_name):
    grouped = df.groupby('Module_Name').apply(lambda x: x[column_name].tolist())
    new_df = grouped.reset_index(name='{}_values'.format(column_name)).rename(columns={'Module_Name': 'Group'})
    return list(set(new_df[new_df['Group'] == module_name]['{}_values'.format(column_name)].tolist()[0]))


def bfs_traversal_w_subtree(tree):
    """
    Performs a breadth-first traversal of the input tree.
    """
    result_label = []
    result_leaves = []
    queue = [tree]
    while queue:
        node = queue.pop(0)
        result_label.append(node.label())
        result_leaves.append(node.leaves())
        #         print(node.label())
        for child in node:
            if isinstance(child, nltk.tree.Tree):
                queue.append(child)
    return result_label, result_leaves


def get_alias_param(test_df, module_name, parameter_name):
    module_df = test_df[(test_df['Module_Name'] == module_name)]
    return module_df[module_df['Parameter_Name'] == parameter_name]['Aliases'].tolist()[0]


def aliases_parameter(data, module_name, param_name):
    module_df = data[data['Module_Name'] == module_name]
    aliases = module_df[module_df['Parameter_Name'] == param_name]['Aliases'].tolist()
    return aliases[0] if len(aliases) != 0 else aliases


def parameters_module(data, module_name):
    params = data[data['Module_Name'] == module_name]['Parameter_Name'].unique().tolist()
    return params


def choices_parameter(data, module_name, param_name):
    module_df = data[data['Module_Name'] == module_name]
    choices = module_df[module_df['Parameter_Name'] == param_name]['Choices'].tolist()
    return choices[0] if len(choices) != 0 else choices


def datatype_parameter(data, module_name, param_name):
    module_df = data[data['Module_Name'] == module_name]
    datatypes = module_df[module_df['Parameter_Name'] == param_name]['Datatype_Param'].tolist()
    return datatypes[0] if len(datatypes) != 0 else datatypes


def is_sub(sub, lst):
    ln = len(sub)
    for i in range(len(lst) - ln + 1):
        if all(sub[j] == lst[i + j] for j in range(ln)):
            return i
    return False


def detect_def(data, item, param, result, module_name):
    if re.search(r'\b{}\b'.format(param), item):
        result['choices'][param] = []
        choices = ['no', 'yes']
        choices_param = choices_parameter(data, module_name, param)
        if choices_param != None:
            choices.extend(choices_param)
        for choice in choices:
            if re.search(r'\b{}\b'.format(choice), item):
                if re.search(r'\b{}\b'.format('not ' + choice), item):
                    result['choices'][param].append('not ' + choice)

                elif re.search(r'\b{}\b'.format(choice), item):
                    result['choices'][param].append(choice)

            else:
                if re.search(r'\b{}\b'.format('not'), item):
                    result['choices'][param].append('not')
        if ('CC' in bfs_traversal(tree_sentence(parser, item))) and (len(result['choices'][param]) > 2) and (
                'not' in result['choices'][param]):
            result['choices'][param] = [x for x in result['choices'][param] if x != 'not']
        else:
            result['choices'][param] = list(set(result['choices'][param]))
    return result


def find_if_sents(item):
    result_if = []
    tree = tree_sentence(parser, item)

    dfs = [(subtree.label(), ' '.join(subtree.leaves())) for subtree in tree.subtrees()]
    sbar_indecies = find_indices([i[0] for i in dfs], 'SBAR')
    for i, v in enumerate(sbar_indecies):
        if i == len(sbar_indecies) - 1:
            result_if.append(dfs[v][1])
        elif sbar_indecies[i + 1] - sbar_indecies[i] > 1:
            result_if.append(dfs[sbar_indecies[i]][1])
    return result_if


def label_word_def(tree, label, word):
    for subtree in tree.subtrees():
        if len(subtree.leaves()) == 1 and subtree.label() == label and subtree.leaves()[0].lower() == word:
            return True
    else:
        return False

def words_with_capital_letters(input_string):
    pattern =  r'\b[A-Z_][A-Za-z_]*\b'
    return re.findall(pattern, input_string)