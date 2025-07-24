import os
from prompt import SYSTEM_PROMPT_GENERAL_TRANSLATOR, SYSTEM_PROMPT_ACADEMIC_TRANSLATOR, USER_PROMPT_TRANSLATOR
from openai import OpenAI
from file_handler import FileHandler
import tempfile

class Translator:
    def __init__(self):
        # 从环境变量获取 OPENAI_API_KEY 和 OPENAI_API_BASE
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_API_BASE")
        self.llm = OpenAI(api_key=api_key, base_url=base_url)
        self.file_handler = FileHandler()

        # 获取 TTS 的 API Key 和 API Base，如果没有提供则使用翻译的 API Key 和 API Base
        tts_api_key = os.getenv("TTS_API_KEY", api_key)
        tts_base_url = os.getenv("TTS_API_BASE", base_url)
        self.tts_llm = OpenAI(api_key=tts_api_key, base_url=tts_base_url)

    def infer(self, input_content, model, temperature, target_language="中文", agent_type="通用翻译"):
        # 判断输入是文件路径还是文本
        if isinstance(input_content, str) and os.path.exists(input_content):
            text = self.file_handler.read_file(input_content)
        else:
            text = input_content

        if agent_type == "通用翻译":
            self.system_prompt = SYSTEM_PROMPT_GENERAL_TRANSLATOR
            self.user_prompt = USER_PROMPT_TRANSLATOR
        elif agent_type == "学术翻译":
            self.system_prompt = SYSTEM_PROMPT_ACADEMIC_TRANSLATOR
            self.user_prompt = USER_PROMPT_TRANSLATOR
        else:
            raise ValueError(f"Invalid agent type: {agent_type}")
        
        # 分段处理长文本
        max_chunk_size = 2048  # 假设模型的最大输入长度为2048字符
        chunks = [text[i:i + max_chunk_size] for i in range(0, len(text), max_chunk_size)]
        
        full_response = ""
        for chunk in chunks:
            response = self.llm.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": self.user_prompt.format(target_language=target_language, text=chunk)}
                ],
                temperature=temperature,
                stream=True
            )
            for chunk_response in response:
                if chunk_response.choices[0].delta.content is not None:
                    full_response += chunk_response.choices[0].delta.content
                    yield full_response

        yield full_response

    def text_to_speech(self, text, lang='zh'):
        """将文本转换为语音"""
        try:
            response = self.tts_llm.audio.speech.create(  # 改用 audio.create
                model="tts-1",
                voice="onyx",
                input=text,
                response_format="mp3"
            )
        
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
               # 直接写入响应内容
                fp.write(response.content)  # 使用 response.content 而不是 streaming
                return fp.name
        except Exception as e:
            print(f"Text-to-speech error: {str(e)}")
            return None

if __name__ == "__main__":
    agent = Translator()
    agent.infer("Hello, world!", "gpt-4o", 1.3, "中文", "通用翻译")
