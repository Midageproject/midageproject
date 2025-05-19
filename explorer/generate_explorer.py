import jinja2
from ruamel.yaml import YAML
import os
import shutil
from pathlib import Path

base = os.path.dirname(__file__)

partials_path = f"{base}/partials/hero.html"
template_dir = f"{base}/templates"
yaml_path = f"{base}/../db/pipeline.yaml"
output_dir = f"{base}/../dist/"
output_path = f"{output_dir}/index.html"
db_path = Path(__file__).parent.parent / "db" / "components"


os.makedirs(output_dir, exist_ok=True)

yaml = YAML(typ='rt')
with open(yaml_path) as f:
    config = yaml.load(f)

with open(partials_path) as f:
    partial_html = f.read()

env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
main = env.get_template('base.j2')
selection = env.get_template('selection.j2')
symdata = env.get_template('component.j2')

shutil.copytree(f'{base}/assets', f'{output_dir}/assets', dirs_exist_ok=True)
rendered = main.render(content_block=partial_html)

with open(output_path, 'w') as f:
    f.write(rendered)

# Automation begins here, so is abomination
os.mkdir(f'{output_dir}/explorer')
rendered = selection.render(data=config['versions'], title='Select a version')
rendered = main.render(data=config, content_block=rendered)

with open(f'{output_dir}/explorer/index.html', 'w') as f:
    f.write(rendered)

for component in config['include']:
    try:
        with open(f"{db_path}/{component}.yaml") as f:
            db = yaml.load(f)
        for idx, appearance in enumerate(db['appearances']):
         os.makedirs(f'{output_dir}/explorer/{appearance["version"]}/{component}', exist_ok=True)
         rendered = symdata.render(data=db, appearance_index=idx)
         rendered = main.render(data=config, content_block=rendered)
         with open(f'{output_dir}/explorer/{appearance["version"]}/{component}/index.html', 'w') as f:
            f.write(rendered)

    except Exception as e:
        print(f"Error processing component {component}")
        continue


versions = [d.name for d in Path(f'{output_dir}/explorer').iterdir() if d.is_dir()]

for i in versions:
        root = Path(f'{output_dir}/explorer/{i}')
        dirs = []
        for path in root.rglob("*"):
         if path.is_dir() and any(p.is_dir() for p in path.iterdir()):
           continue  # skip intermediate dirs like vmm32
         if path.is_dir():
            dirs.append(str(path.relative_to(root)))
            rendered = selection.render(data=dirs, title="Files")
            rendered = main.render(data=config, content_block=rendered)
            with open(f'{output_dir}/explorer/{i}/index.html', 'w') as f:
                f.write(rendered)