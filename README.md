# MisConfLinter
**MisConfLinter** is an NLP-powered tool that automatically extracts configuration parameters and constraints from Ansible module documentation, generating rules to detect misconfigurations with Ansible Lint.


<img width="800" height="637" alt="image" src="https://github.com/user-attachments/assets/67a697b3-20b3-496f-bb33-f98589f7c10b" />
By running 
'''
python ansible_lint_rule_generator.py
'''
, the necessary linting rules are automatically generated. These rules can then be applied using 
'''
ansible-lint -r rules test_playbook.yml
''' 
to test your playbooks and detect misconfigurations.
