import fitz  # PyMuPDF
from docx import Document

def pdf_to_word(pdf_path, word_path):
    """
    将PDF文件内容读取并保存为Word文件
    :param pdf_path: PDF文件路径
    :param word_path: 输出的Word文件路径
    """
    # 打开PDF文件
    pdf_document = fitz.open(pdf_path)
    
    # 创建一个新的Word文档
    doc = Document()
    
    # 遍历PDF的每一页
    for page_num in range(len(pdf_document)):
        # 获取当前页
        page = pdf_document.load_page(page_num)
        
        # 提取文本内容
        text = page.get_text("text")
        
        # 将文本添加到Word文档中
        doc.add_paragraph(text)
    
    # 保存Word文档
    doc.save(word_path)
    print(f"PDF内容已成功保存到 {word_path}")

# 示例用法
if __name__ == "__main__":
    pdf_file = r"C:\Users\xxx.pdf"  # 输入的PDF文件路径
    word_file = r"C:\Users\output.docx"  # 输出的Word文件路径
    
    # 调用函数
    pdf_to_word(pdf_file, word_file)
