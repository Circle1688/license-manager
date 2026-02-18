import json
from pathlib import Path
import gradio as gr
from license import License

def on_license_category_change(category):
    if category == "standalone":
        return [
            gr.update(visible=True),
            gr.update(visible=False)
        ]
    else:
        return [
            gr.update(visible=False),
            gr.update(visible=True)
        ]

def generate(category, license_category, machine_code, max_usage, days):
    if license_category == "standalone":
        activate_code = License.generate(category, machine_code, days)
    else:
        activate_code = License.generate_floating(category, max_usage, days)
    return activate_code

with gr.Blocks() as demo:
    gr.Markdown("# License Manager")
    p = Path("PEM")
    folders = [item.name for item in p.iterdir() if item.is_dir()]
    category = gr.Radio(choices=folders, label="Category", value=folders[0])

    license_category = gr.Radio(choices=['standalone', 'floating'], label="License Category", value="standalone")

    machine_code_textbox = gr.Textbox(
        lines=1,
        label="Machine Code",
        placeholder="Enter Machine Code",
        visible=True
    )

    max_usage = gr.Number(
        label="Max Usage",
        precision=0,
        value=1,
        step=1,
        minimum=1,
        visible=False
    )

    license_category.change(
        fn=on_license_category_change,
        inputs=license_category,
        outputs=[machine_code_textbox, max_usage]
    )

    days = gr.Number(
        label="Days",
        precision=0,
        value=7,
        step=1,
        minimum=1
    )
    gen_button = gr.Button("Generate", variant="primary")

    output_textbox = gr.Textbox(
        label="Activate Code",
        buttons=['copy']
    )

    gen_button.click(
        generate,
        inputs=[category, license_category, machine_code_textbox, max_usage, days],
        outputs=[output_textbox]
    )

with open("config.json", "r") as f:
    data = json.load(f)

demo.launch(server_name="0.0.0.0", auth=(data['username'], data['password']))
