
import gradio as gr

def generate(category, machine_code):
    register_code = machine_code
    return register_code

with gr.Blocks() as demo:
    gr.Markdown("# License Manager")
    category = gr.Radio(choices=['VR Manager'], label="Category", value="VR Manager")
    machine_code_textbox = gr.Textbox(
        lines=1,
        label="Machine Code",
        placeholder="Enter Machine Code", )
    gen_button = gr.Button("Generate", variant="primary")

    output_textbox = gr.Textbox(
        label="Register Code",
        buttons=['copy']
    )

    gen_button.click(
        generate,
        inputs=[category, machine_code_textbox],
        outputs=[output_textbox]
    )

demo.launch(server_name="0.0.0.0")
