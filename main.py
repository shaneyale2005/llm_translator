import gradio as gr
from agent import Translator
import pyperclip
import os
from dotenv import load_dotenv
from file_handler import FileHandler

load_dotenv()

agent_types = ["通用翻译", "学术翻译"]
agent = Translator()

target_languages = ["English", "中文"]
models = ["gpt-4o", "gpt-4o-mini"]  # 添加模型选项

if __name__ == "__main__":
    with gr.Blocks(
        theme=gr.themes.Soft(text_size="lg"), title="AI_Translation", fill_height=True
    ) as demo:
        with gr.Row():
            with gr.Column(scale=1):
                input_text = gr.Textbox(label="输入", lines=10)
                input_audio_button = gr.Button("🔊", scale=0, min_width=40)
            with gr.Column(scale=1):
                output_text = gr.Textbox(label="结果", lines=10)
                output_audio_button = gr.Button("🔊", scale=0, min_width=40)
        with gr.Row():
            infer_button = gr.Button("翻译", variant="primary")
            clear_button = gr.Button("清除", variant="secondary")
            paste_button = gr.Button("粘贴", variant="secondary")
            copy_button = gr.Button("复制", variant="secondary")

        # 添加音频输出组件
        input_audio = gr.Audio(label="输入音频", visible=True)
        output_audio = gr.Audio(label="结果音频", visible=True)

        # 添加语音播放按钮的点击事件
        input_audio_button.click(
            fn=lambda text: agent.text_to_speech(text, lang='zh' if target_language_dropdown.value == '中文' else 'en'),
            inputs=input_text,
            outputs=input_audio
        )
        
        output_audio_button.click(
            fn=lambda text: agent.text_to_speech(text, lang='zh' if target_language_dropdown.value == '中文' else 'en'),
            inputs=output_text,
            outputs=output_audio
        )
        with gr.Row():
            with gr.Column():
                model_dropdown = gr.Dropdown(  # 修改为下拉列表
                    label="模型", choices=models, value=models[0]
                )
                temperature_slider = gr.Slider(
                    label="温度", minimum=0, maximum=1.3, value=1.3, step=0.1
                )
            with gr.Column():
                agent_type_dropdown = gr.Dropdown(
                    label="选择Agent类型", choices=agent_types, value=agent_types[0]
                )
                target_language_dropdown = gr.Dropdown(
                    label="目标语言",
                    choices=target_languages,
                    value=target_languages[0],
                )
        with gr.Row():
            file_input = gr.File(label="上传文件", type="filepath")

        def stream_output(text, model, temperature, target_language, agent_type):
            for output in agent.infer(
                text, model, temperature, target_language, agent_type
            ):
                yield output

        def process_file(file, model, temperature, target_language, agent_type):
            try:
                # 使用 FileHandler 处理文件
                text = FileHandler.read_file(file.name)
        
                # 使用处理后的文本进行翻译
                return list(
                    stream_output(
                        text, model, temperature, target_language, agent_type
                    )
                )[-1]
            except Exception as e:
                raise ValueError(f"文件处理失败: {str(e)}")

        infer_button.click(
            fn=stream_output,
            inputs=[
                input_text,
                model_dropdown,  # 修改为使用下拉列表的值
                temperature_slider,
                target_language_dropdown,
                agent_type_dropdown,
            ],
            outputs=output_text,
        )
        copy_button.click(
            fn=lambda x: pyperclip.copy(x), inputs=output_text, outputs=None
        )
        paste_button.click(
            fn=lambda: pyperclip.paste(), inputs=None, outputs=input_text
        )
        clear_button.click(fn=lambda: "", inputs=None, outputs=input_text)
        file_input.change(
            fn=process_file,
            inputs=[
                file_input,
                model_dropdown,  # 修改为使用下拉列表的值
                temperature_slider,
                target_language_dropdown,
                agent_type_dropdown,
            ],
            outputs=output_text,
        )
    # 运行
    if os.getenv("APP_PORT") is not None:
        demo.launch(server_port=int(os.getenv("APP_PORT")))
    else:
        demo.launch()
        