# file_handler.py
import fitz  # PyMuPDF
from docx import Document
import os
import markdown

class FileHandler:
    @staticmethod
    def read_pdf(file_path):
        """读取PDF文件内容"""
        try:
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            return text
        except Exception as e:
            raise Exception(f"PDF文件读取失败: {str(e)}")

    @staticmethod
    def read_docx(file_path):
        """读取DOCX文件内容"""
        try:
            doc = Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except Exception as e:
            raise Exception(f"DOCX文件读取失败: {str(e)}")

    @staticmethod
    def read_md(file_path):
        """读取Markdown文件内容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            return markdown.markdown(text)
        except Exception as e:
            raise Exception(f"Markdown文件读取失败: {str(e)}")

    @staticmethod
    def read_file(file_path):
        """根据文件类型读取内容"""
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.pdf':
            return FileHandler.read_pdf(file_path)
        elif file_extension == '.docx':
            return FileHandler.read_docx(file_path)
        elif file_extension == '.md':
            return FileHandler.read_md(file_path)
        elif file_extension == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            raise ValueError(f"不支持的文件类型: {file_extension}")