# MisConfLinter
**MisConfLinter** is an NLP-powered tool that automatically extracts configuration parameters and constraints from Ansible module documentation, generating rules to detect misconfigurations with Ansible Lint.


<img width="800" height="637" alt="image" src="https://github.com/user-attachments/assets/67a697b3-20b3-496f-bb33-f98589f7c10b" />

### Prerequisites

Linux environment: MisConfLinter is tested on Linux and should be run there for compatibility.

Python >= 3.8

Install required Python packages:
```
pip install benepar
pip install nltk
pip install ansible
pip install ansible-lint
```
Then download the Benepar model: 
```
import benepar
benepar.download('benepar_en3')

```
Guidelines for the packages:
- [Benepar documentation](https://github.com/nikitakit/self-attentive-parser)
- [NLTK documentation](https://www.nltk.org/)
- [Ansible Lint documentation](https://docs.ansible.com/projects/lint/) 

### Data Collection
MisConfLinter relies on detailed Ansible module and parameter documentation to detect misconfigurations. You can extract this data using the provided scripts:

1- Define a list of modules you want to include.

2- Call save_to_files() to scrape and save module-level and parameter-level datasets.
```
from ansible_module_documentation import save_to_files

# List of modules to extract
modules_list = ['copy', 'file', 'template']

# Paths to save extracted data
module_file_path = 'files/module_docs.xlsx'
parameter_file_path = 'files/parameter_docs.xlsx'

# Extract and save documentation
save_to_files(modules_list, module_file_path, parameter_file_path)

```
After extraction, the parameter data is preprocessed and tokenized, then saved as ```tokenized_parameter_dataset.xlsx```. This dataset is used in the subsequent step to generate MisConfLinter rules.

``` 
from ansible_module_documentation import save_preprocessed_parameter_file
import pandas as pd

# Load extracted parameter data
df_parameter = pd.read_excel('files/parameter_docs.xlsx')

# Preprocess and tokenize parameter descriptions
save_preprocessed_parameter_file(df_parameter)
``` 
### Generate Misconfiguration Rules

Run the ``` ansible_lint_rule_generator.py ``` script to generate custom linting rules for each misconfiguration category.

### Testing Playbooks by Customized Rules 
To test your Ansible playbooks against these generated rules, execute the following command:
```
ansible-lint -r rules test_playbook.yml
``` 
This process helps to detect and prevent misconfigurations in your playbooks efficiently.
