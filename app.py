import streamlit as st
import requests
import base64
from PIL import Image
import io

st.set_page_config(
    page_title="قصتي",
    page_icon="📚",
    layout="centered"
)

st.title("📚 قصتي")
st.subheader("تطبيق توليد قصص أطفال")

# نموذج الإدخال
with st.form("story_form"):
    child_name = st.text_input("اسم الطفل", placeholder="مثال: أحمد")
    
    col1, col2 = st.columns(2)
    with col1:
        language = st.selectbox(
            "اللغة",
            ["AR", "FR", "EN"],
            format_func=lambda x: {"AR": "العربية", "FR": "Français", "EN": "English"}[x]
        )
    with col2:
        story = st.selectbox(
            "القصة",
            ["time_machine", "space", "pirate"],
            format_func=lambda x: {
                "time_machine": "رحلة عبر الزمن",
                "space": "رحلة الفضاء",
                "pirate": "مغامرة القراصنة"
            }[x]
        )
    
    uploaded_file = st.file_uploader("صورة الطفل", type=["jpg", "jpeg", "png"])
    
    submitted = st.form_submit_button("✨ إنشاء القصة")

if submitted:
    if not child_name or not uploaded_file:
        st.error("❌ الرجاء إدخال الاسم واختيار صورة")
    else:
        with st.spinner("جاري الإنشاء..."):
            try:
                # تحويل الصورة
                image = Image.open(uploaded_file)
                buffered = io.BytesIO()
                image.save(buffered, format="PNG")
                img_base64 = base64.b64encode(buffered.getvalue()).decode()
                
                # إرسال لـ RunPod - الرابط الصحيح
                response = requests.post(
                    "https://api.runpod.ai/v2/rlydf3a15qv86b/run",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": "Bearer rpa_YUF652M25EB1I1IQAWDT988YIXQYLZKNN945AT9Eudu63j"
                    },
                    json={
                        "input": {
                            "prompt": f"Children's book illustration of {child_name} in {story} story, Pixar style",
                            "image": img_base64
                        }
                    },
                    timeout=30
                )
                
                # عرض النتيجة للتشخيص
                st.write(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    st.success(f"✅ تم الإرسال! Job ID: {data.get('id')}")
                else:
                    st.error(f"❌ خطأ {response.status_code}")
                    st.text(response.text[:500])
                    
            except Exception as e:
                st.error(f"❌ خطأ: {str(e)}")
