import pandas as pd
import requests
from bs4 import BeautifulSoup
from nltk.tokenize import sent_tokenize
from misconftypes.parsing import read_data, type_convert


def scrap_module_info(modules_list):
    list_all_modules = []
    path_module_documentation = 'https://docs.ansible.com/ansible/latest/collections/'
    req = requests.get(path_module_documentation)
    soup = BeautifulSoup(req.content, 'html.parser')
    all_collection_list = soup.find_all("ul", class_="simple")
    top_module_dataframe = []
    for each_list in all_collection_list:
        for each_reference_link in each_list.find_all('li'):
            link_to_collection = 'https://docs.ansible.com/ansible/latest/collections/' + each_reference_link.find(
                'a').get('href')
            name_collection = each_reference_link.find('a').text
            req_collection = requests.get(link_to_collection)
            soup_collection = BeautifulSoup(req_collection.content, 'html.parser')
            soup_coll_modules = soup_collection.find("section", {"id": "modules"})
            if (soup_coll_modules):
                ul_module = soup_coll_modules.find_all('ul', class_='simple')

                for each_ul in ul_module:
                    for each_link_li in each_ul.find_all('li'):
                        name_module = each_link_li.find('a').text
                        name_module = name_module.split(" ")[0]

                        list_all_modules.append(name_module)
                        if (name_module in modules_list):

                            link_to_module = (link_to_collection.split('#')[0].replace('index.html', '') + (
                                each_link_li.find('a').get('href').split('#')[0]))

                            req_module = requests.get(link_to_module)
                            soup_each_module = BeautifulSoup(req_module.content, 'html.parser')
                            synopsis_list = soup_each_module.find("section", {"id": "synopsis"})
                            if (synopsis_list != None):
                                synopsis_list = synopsis_list.find_all('li')
                                synopsis_text = []
                                for each_syn in synopsis_list:
                                    synopsis_text.append(each_syn.text)
                            else:
                                synopsis_text = None
                            notes_list = soup_each_module.find("section", {"id": "notes"})
                            if (notes_list != None):
                                notes_list = notes_list.find_all('li')
                                notes_text = []
                                for each_note in notes_list:
                                    notes_text.append(each_note.text)
                            else:
                                notes_text = None
                            requirements_list = soup_each_module.find("section", {"id": "requirements"})
                            if (requirements_list != None):
                                requirements_list = requirements_list.find_all('li')
                                requirements_text = []
                                for each_requirement in requirements_list:
                                    requirements_text.append(each_requirement.text)
                            else:
                                requirements_text = None

                            parameters = soup_each_module.find("section", {"id": "parameters"})
                            if (parameters):
                                rows = parameters.findAll('tr')
                                for tr in rows:
                                    each_parameter_detail = []
                                    x = 0
                                    cols = tr.findAll('td')
                                    for td in cols:
                                        x = x + 1
                                        list_str = td.text.strip().split('\n')
                                        list_str = filter(None, list_str)
                                        list_str = list(list_str)
                                        each_parameter_detail.append(list_str)
                                    if (len(each_parameter_detail) > 0):
                                        if (len(each_parameter_detail[0]) > 0):
                                            name_param = each_parameter_detail[0][0]
                                            if each_parameter_detail[0][1].startswith('aliases:'):
                                                alias = each_parameter_detail[0][1]
                                            else:
                                                alias = None
                                            datatype_param = each_parameter_detail[0][-1]
                                            if 'added in' in datatype_param:
                                                datatype_param = each_parameter_detail[0][-2]
                                            choices_default = each_parameter_detail[1]
                                            choices = None
                                            default = None
                                            choices_clean = []
                                            if (len(choices_default) > 0):
                                                if ('Choices:' in choices_default):
                                                    choices = choices_default[choices_default.index('Choices:') + 1:]
                                                    desc_param = choices_default[:choices_default.index('Choices:')]
                                                    for each_choice in choices:
                                                        choices_clean.append(each_choice.split('←')[0])
                                                        if '←' in each_choice:
                                                            default = each_choice.split('←')[0]
                                                elif ('Default: ' in ''.join(choices_default)):
                                                    default_index = next(
                                                        i for i, s in enumerate(choices_default) if 'Default: ' in s)
                                                    default = choices_default[default_index][9:]
                                                    desc_param = choices_default[:default_index]
                                                else:
                                                    desc_param = each_parameter_detail[1]
                                            top_module_dataframe.append(
                                                [name_param, alias, datatype_param, choices_clean, default, desc_param,
                                                 name_module, link_to_module, name_collection, synopsis_text,
                                                 notes_text, requirements_text])
    top_module_df = pd.DataFrame(top_module_dataframe)
    top_module_df.columns = ['Parameter_Name', 'Aliases', 'Datatype_Param', 'Choices', 'Default', 'Description',
                             'Module_Name',
                             'Module_Link', 'Collection_Name', 'Synopsis', 'Notes', 'Requirements']
    return ([top_module_df, list_all_modules])


def load_module_parameter_docs(module_path, parameter_path):
    df_module_level_texts = pd.read_excel(module_path)
    df_parameter_level_texts = pd.read_excel(parameter_path)

    # df_parameter_level_texts = df_parameter_level_texts.dropna(how='all')
    # df_module_level_texts = df_module_level_texts.dropna(how='all')
    return df_module_level_texts, df_parameter_level_texts


def save_to_files(list_modules, module_file_path, parameter_file_path):
    module_documentation = scrap_module_info(list_modules)
    df_module_documentation = module_documentation[0]
    all_available_modules = module_documentation[1]
    df_module_documentation['Requirements'] = df_module_documentation['Requirements'].apply(
        lambda x: str(x) if x is not None else None)

    df_module_documentation['Module_Name'].nunique()

    synopsis = df_module_documentation.explode('Synopsis')[
        ['Collection_Name', 'Module_Name', 'Module_Link', 'Requirements', 'Synopsis']].drop_duplicates().dropna()
    synopsis.columns = ['Collection_Name', 'Module_Name', 'Module_Link', 'Requirements', 'Text']
    synopsis['section'] = 'synopsis'
    notes = df_module_documentation.explode('Notes')[
        ['Collection_Name', 'Module_Name', 'Module_Link', 'Requirements', 'Notes']].drop_duplicates().dropna()
    notes.columns = ['Collection_Name', 'Module_Name', 'Module_Link', 'Requirements', 'Text']
    notes['section'] = 'notes'
    df_module_level_texts = pd.concat([synopsis, notes])

    df_module_level_texts.to_excel(module_file_path, index=False)

    parameters_column = ['Parameter_Name', 'Aliases', 'Datatype_Param', 'Choices', 'Default',
                         'Description', 'Module_Name', 'Module_Link', 'Collection_Name']

    df_module_documentation[parameters_column].to_excel(parameter_file_path, index=False)

def save_preprocessed_parameter_file(parameter_df):
    parameter_df['Aliases'] = parameter_df['Aliases'].apply(lambda x: x[8:].strip(' ') if type(x) != float else x)
    parameter_df['Description'] = parameter_df['Description'].apply(lambda x: eval(x))
    parameter_df['Choices'] = parameter_df['Choices'].apply(lambda x: eval(x))
    parameter_df['Choices'] = parameter_df['Choices'].apply(
        lambda x: [item.replace(" ", "").replace('"', '').replace('*', '').replace('%', '') for item in x]).tolist()
    test_df = parameter_df.explode('Description')
    test_df['Description'].fillna('', inplace=True)
    test_df['Description'] = test_df['Description'].apply(
        lambda x: x.replace('. (i.e', ' (i-e') if '. (i.e' in x else x)
    test_df.reset_index(inplace=True)
    test_df['Tokenized_description'] = test_df['Description'].apply(lambda x: sent_tokenize(x))
    test_df = test_df.explode('Tokenized_description')
    test_df['Tokenized_description'].fillna('', inplace=True)
    test_df.drop('index', axis=1, inplace=True)
    test_df = test_df.apply(type_convert, axis=1)
    test_df.to_excel('files/tokenized_parameter_dataset.xlsx', index=False)


def load_tokenized_parameter_docs():
    test_df = read_data('files/tokenized_parameter_dataset.xlsx')
    test_df['Tokenized_description'].fillna('', inplace=True)
    test_df['Description'].fillna('', inplace=True)
    test_df['Aliases'] = test_df['Aliases'].apply(
        lambda x: [i.strip(' ') for i in x.split(',')] if type(x) != float else [])
    test_df['Parameter_Name'] = test_df['Parameter_Name'].apply(lambda x: x.replace('(', '').replace(')', ''))
    test_df['Datatype_Param'] = test_df['Datatype_Param'].apply(lambda x: x.split('/')[0])
    test_df['Default'] = test_df['Default'].astype(str).str.replace('"', '')

    test_df['Choices'] = test_df['Choices'].apply(lambda x: eval(x))
    test_df['index_col'] = test_df.index
    return test_df




