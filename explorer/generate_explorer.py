import jinja2
from ruamel.yaml import YAML
import os

# Create output directory if it doesn't exist
output_dir = '../work/explorer'
os.makedirs(output_dir, exist_ok=True)

yaml = YAML(typ='rt')

# Load JSON data
with open('../db/pipeline.yaml') as f:
    config = yaml.load(f)
template_dir = 'templates'
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))

index = jinja_env.get_template('index.j2')

# Render the template
rendered_template = index.render(data=config)

output_path = os.path.join(output_dir, 'index.html')
with open(output_path, 'w') as f:
    f.write(rendered_template)