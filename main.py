import json
from pathlib import Path
import gradio as gr
from license import License

def generate(category, machine_code, days):
    activate_code = License.generate(category, machine_code, days)
    return activate_code

with gr.Blocks() as demo:
    gr.Markdown("# License Manager")
    p = Path("PEM")
    folders = [item.name for item in p.iterdir() if item.is_dir()]
    category = gr.Radio(choices=folders, label="Category", value="VR Manager")
    machine_code_textbox = gr.Textbox(
        lines=1,
        label="Machine Code",
        placeholder="Enter Machine Code", )

    days = gr.Number(
        label="Days",
        precision=0,
        value=7,
        step=1,
        minimum=0
    )
    gen_button = gr.Button("Generate", variant="primary")

    output_textbox = gr.Textbox(
        label="Activate Code",
        buttons=['copy']
    )

    gen_button.click(
        generate,
        inputs=[category, machine_code_textbox, days],
        outputs=[output_textbox]
    )

with open("config.json", "r") as f:
    data = json.load(f)

demo.launch(server_name="0.0.0.0", auth=(data['username'], data['password']))
