import streamlit as st
import requests
import base64
from PIL import Image
import io
import time
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import os

st.set_page_config(page_title="قصتي", page_icon="📚", layout="centered")

st.title("📚 قصتي")
st.subheader("تطبيق توليد قصص أطفال")

# قصص محفوظة
STORIES = {
    "time_machine": {
        "title": "رحلة عبر الزمن",
        "pages": [
            "كان {name} يحلم بالسفر عبر الزمن.",
            "وجد {name} آلة زمن غامضة في العلية.",
            "ضغط {name} على الزر وانطلق!",
            "وجد نفسه في عصر الديناصورات.",
            "تعرف {name} على ديناصور صديق.",
            "مغامرة مثيرة معاً في الغابة القديمة.",
            "حان وقت العودة إلى المنزل.",
            "ودع {name} صديقه الديناصور.",
            "عاد {name} بذكريات لا تُنسى.",
            "نام {name} محلقاً في الأحلام."
        ]
    },
    "space": {
        "title": "رحلة الفضاء",
        "pages": [
            "حلم {name} بأن يصبح رائد فضاء.",
            "انضم {name} إلى أكاديمية الفضاء.",
            "صعد {name} إلى الصاروخ.",
            "انطلق إلى النجوم!",
            "رأى {name} كواكب ملونة.",
            "التقى {name} بكائن فضائي ودود.",
            "ساعدوا معاً في إصلاح القمر الصناعي.",
            "غادر {name} الكوكب الغريب.",
            "عبر {name} حزام الكويكبات.",
            "عاد {name} بطل الفضاء."
        ]
    },
    "pirate": {
        "title": "مغامرة القراصنة",
        "pages": [
            "عثر {name} على خريطة كنز قديمة.",
            "أبحرت السفينة في البحار العاصفة.",
            "واجه {name} قراصنة آخرين.",
            "فاز {name} في تحدي السيف.",
            "وصل {name} إلى جزيرة الكنز.",
            "حل {name} الألغاز الغامضة.",
            "وجد {name} الصندوق المخفي.",
            "فتح {name} الكنز المذهل!",
            "شارك {name} الغنيمة مع الفريق.",
            "عاد {name} أسطورة البحار."
        ]
    }
}

# نموذج الإدخال
with st.form("story_form"):
    child_name = st.text_input("اسم الطفل", placeholder="مثال: أحمد")
    
    col1, col2 = st.columns(2)
    with col1:
        language = st.selectbox("اللغة", ["AR", "FR", "EN"])
    with col2:
        story_key = st.selectbox(
            "القصة",
            list(STORIES.keys()),
            format_func=lambda x: STORIES[x]["title"]
        )
    
    uploaded_file = st.file_uploader("صورة الطفل", type=["jpg", "jpeg", "png"])
    
    submitted = st.form_submit_button("✨ إنشاء القصة")

if submitted:
    if not child_name or not uploaded_file:
        st.error("❌ الرجاء إدخال الاسم واختيار صورة")
    else:
        story_data = STORIES[story_key]
        
        with st.spinner("🎨 جاري إنشاء القصة... قد يستغرق 2-3 دقائق"):
            try:
                # تحويل الصورة
                image = Image.open(uploaded_file)
                buffered = io.BytesIO()
                image.save(buffered, format="PNG")
                img_base64 = base64.b64encode(buffered.getvalue()).decode()
                
                # إرسال لـ RunPod
                response = requests.post(
                    "https://api.runpod.ai/v2/rlydf3a15qv86b/run",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": "Bearer rpa_F2URUMLY40LQC6S0SG3GGV4JGNHFBP1tqIz1"
                    },
                    json={
                        "input": {
                            "prompt": f"Children's book illustration of {child_name} in {story_data['title']}, Pixar style, storybook art, magical atmosphere, high quality",
                            "image": img_base64,
                            "width": 1024,
                            "height": 1024,
                            "steps": 30
                        }
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    job_id = data.get('id')
                    
                    st.success(f"✅ تم إرسال الطلب! Job ID: {job_id}")
                    
                    # انتظار النتيجة
                    with st.spinner("⏳ جاري معالجة الصورة..."):
                        image_url = None
                        for i in range(30):  # انتظر 30 محاولة (دقيقتين)
                            time.sleep(5)
                            
                            status_response = requests.get(
                                f"https://api.runpod.ai/v2/rlydf3a15qv86b/status/{job_id}",
                                headers={"Authorization": "Bearer rpa_F2URUMLY40LQC6S0SG3GGV4JGNHFBP1tqIz1"}
                            )
                            
                            if status_response.status_code == 200:
                                status_data = status_response.json()
                                if status_data.get('status') == 'COMPLETED':
                                    output = status_data.get('output', {})
                                    if isinstance(output, dict) and 'image_url' in output:
                                        image_url = output['image_url']
                                    break
                                elif status_data.get('status') == 'FAILED':
                                    st.error("❌ فشلت المعالجة")
                                    break
                        
                        if image_url:
                            st.success("✅ تم إنشاء الصورة!")
                            st.image(image_url, caption=f"صورة {child_name}")
                            
                            # إنشاء PDF
                            with st.spinner("📄 جاري إنشاء PDF..."):
                                pdf_buffer = io.BytesIO()
                                c = canvas.Canvas(pdf_buffer, pagesize=A4)
                                width, height = A4
                                
                                # صفحة الغلاف
                                c.setFont("Helvetica-Bold", 30)
                                c.drawCentredString(width/2, height-100, story_data["title"])
                                c.setFont("Helvetica", 20)
                                c.drawCentredString(width/2, height-150, f"قصة {child_name}")
                                
                                # تحميل الصورة
                                try:
                                    img_response = requests.get(image_url)
                                    img = Image.open(io.BytesIO(img_response.content))
                                    img_buffer = io.BytesIO()
                                    img.save(img_buffer, format='PNG')
                                    img_buffer.seek(0)
                                    
                                    # إدراج الصورة في الغلاف
                                    c.drawImage(ImageReader(img_buffer), 100, 300, width=400, height=400, preserveAspectRatio=True)
                                except:
                                    pass
                                
                                c.showPage()
                                
                                # صفحات القصة
                                for i, page_text in enumerate(story_data["pages"]):
                                    c.setFont("Helvetica", 16)
                                    text = page_text.format(name=child_name)
                                    c.drawCentredString(width/2, height-100, f"صفحة {i+1}")
                                    c.setFont("Helvetica", 14)
                                    
                                    # تقسيم النص لسطور
                                    words = text.split()
                                    lines = []
                                    current_line = []
                                    for word in words:
                                        current_line.append(word)
                                        if len(' '.join(current_line)) > 50:
                                            lines.append(' '.join(current_line[:-1]))
                                            current_line = [current_line[-1]]
                                    if current_line:
                                        lines.append(' '.join(current_line))
                                    
                                    y = height - 200
                                    for line in lines:
                                        c.drawCentredString(width/2, y, line)
                                        y -= 30
                                    
                                    c.showPage()
                                
                                c.save()
                                pdf_buffer.seek(0)
                                
                                st.success("✅ تم إنشاء PDF!")
                                st.download_button(
                                    label="📥 تحميل القصة (PDF)",
                                    data=pdf_buffer,
                                    file_name=f"قصة_{child_name}.pdf",
                                    mime="application/pdf"
                                )
                        else:
                            st.warning("⏳ الصورة قيد المعالجة، جرب تحديث الصفحة بعد دقيقة")
                else:
                    st.error(f"❌ خطأ: {response.status_code}")
                    
            except Exception as e:
                st.error(f"❌ خطأ: {str(e)}")
