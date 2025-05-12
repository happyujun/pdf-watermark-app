import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import io

st.set_page_config(page_title="PDF 워터마크 추가기", layout="centered")

st.title("📄 PDF 이미지 워터마크 삽입기")

# 파일 업로드
uploaded_pdf = st.file_uploader("PDF 파일을 업로드하세요", type="pdf")
uploaded_image = st.file_uploader("워터마크로 사용할 이미지를 업로드하세요", type=["png", "jpg", "jpeg"])

# 설정 슬라이더
opacity = st.slider("불투명도 (Opacity)", 0.0, 1.0, 0.7)
scale = st.slider("이미지 크기 비율 (Scale)", 0.1, 1.0, 0.3)

# 워터마크 함수 정의
def add_watermark_to_pdf(pdf_file, image_file, opacity, scale):
    pdf = fitz.open(stream=pdf_file.read(), filetype="pdf")
    img = Image.open(image_file).convert("RGBA")

    # 크기 조정
    new_width = int(img.width * scale)
    new_height = int(img.height * scale)
    img = img.resize((new_width, new_height))

    # 불투명도 적용
    alpha = img.split()[3]
    alpha = alpha.point(lambda p: int(p * opacity))
    img.putalpha(alpha)

    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    for page in pdf:
        page_width = page.rect.width
        page_height = page.rect.height
        x = (page_width - new_width) / 2
        y = (page_height - new_height) / 2
        rect = fitz.Rect(x, y, x + new_width, y + new_height)
        page.insert_image(rect, stream=img_byte_arr, overlay=True)

    output = io.BytesIO()
    pdf.save(output)
    pdf.close()
    output.seek(0)
    return output

# 실행 버튼
if uploaded_pdf and uploaded_image:
    if st.button("워터마크 삽입하기"):
        result_pdf = add_watermark_to_pdf(uploaded_pdf, uploaded_image, opacity, scale)
        st.success("워터마크 삽입 완료!")

        st.download_button(
            label="📥 결과 PDF 다운로드",
            data=result_pdf,
            file_name="watermarked_output.pdf",
            mime="application/pdf"
        )
