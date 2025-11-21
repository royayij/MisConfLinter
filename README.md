# MisConfLinter
**MisConfLinter** is an NLP-powered tool that automatically extracts configuration parameters and constraints from Ansible module documentation, generating rules to detect misconfigurations with Ansible Lint.


<img width="800" height="637" alt="image" src="https://github.com/user-attachments/assets/67a697b3-20b3-496f-bb33-f98589f7c10b" />

### Data Collection
MisConfLinter relies on detailed Ansible module and parameter documentation to detect misconfigurations. You can extract this data using the provided scripts. First, define a list of modules you want to include, then call ```save_to_files()``` to scrape and save module-level and parameter-level datasets.

from misconftypes.scraper import save_to_files
``` 
# List of modules to extract
modules_list = ['copy', 'file', 'template']

# Paths to save extracted data
module_file_path = 'files/module_docs.xlsx'
parameter_file_path = 'files/parameter_docs.xlsx'

# Extract and save documentation
save_to_files(modules_list, module_file_path, parameter_file_path)

```
After extraction, the parameter data is preprocessed and tokenized, then saved as ```tokenized_parameter_dataset.xlsx```, which is used in subsequent steps to extract MisConfLinter rules.
``` 
from misconftypes.scraper import save_preprocessed_parameter_file
import pandas as pd

# Load extracted parameter data
df_parameter = pd.read_excel('files/parameter_docs.xlsx')

# Preprocess and tokenize parameter descriptions
save_preprocessed_parameter_file(df_parameter)
``` 
### Generate Misconfiguration Rules
To automatically generate custom linting rules for each misconfiguration category, you first need to install ```benepar``` and ```NLTK``` libraries as below:
```
pip install benepar
import benepar
benepar.download('benepar_en3')
```
and 
```
pip install nltk

```

The``` ansible_lint_rule_generator.py```script automatically generates custom linting rules for each misconfiguration category.

### Testing Playbooks by Customized Rules 
To test your Ansible playbooks against these generated rules, execute the following command:
```
ansible-lint -r rules test_playbook.yml
``` 
This process helps to detect and prevent misconfigurations in your playbooks efficiently.
