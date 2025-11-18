# MisConfLinter
**MisConfLinter** is an NLP-powered tool that automatically extracts configuration parameters and constraints from Ansible module documentation, generating rules to detect misconfigurations with Ansible Lint.


<img width="800" height="637" alt="image" src="https://github.com/user-attachments/assets/67a697b3-20b3-496f-bb33-f98589f7c10b" />

## Generate Misconfiguration Rules

The  
```
 ansible_lint_rule_generator.py
```
script automatically generates custom linting rules for each defined configuration type.

## Testing Playbooks by Customized Rules 
To test your Ansible playbooks against these generated rules, execute the following command:
```
ansible-lint -r rules test_playbook.yml
``` 
This process helps to detect and prevent misconfigurations in your playbooks efficiently.
