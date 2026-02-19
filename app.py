import streamlit as st
import requests
import base64
from PIL import Image
import io
import time
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

st.set_page_config(page_title="قصتي", page_icon="📚", layout="centered")

# تهيئة session state
if 'job_id' not in st.session_state:
    st.session_state.job_id = None
if 'image_url' not in st.session_state:
    st.session_state.image_url = None
if 'checking' not in st.session_state:
    st.session_state.checking = False

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

# نموذج الإدخال (يظهر فقط إذا لم يكن هناك طلب قيد التشغيل)
if not st.session_state.job_id and not st.session_state.image_url:
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
            
            with st.spinner("🎨 جاري إرسال الطلب..."):
                try:
                    # تحويل الصورة
                    image = Image.open(uploaded_file)
                    buffered = io.BytesIO()
                    image.save(buffered, format="PNG")
                    img_base64 = base64.b64encode(buffered.getvalue()).decode()
                    
                    # إرسال لـ RunPod
                    response = requests.post(
                        "https://api.runpod.ai/v2/r1ydf3al5qv86b/run",
                        headers={
                            "Content-Type": "application/json",
                            "Authorization": "Bearer rpa_YUF652M25EB1I1IQAWDT988YIXQYLZKNN945AT9Eudu63j"
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
                        st.session_state.job_id = data.get('id')
                        st.session_state.child_name = child_name
                        st.session_state.story_data = story_data
                        st.session_state.checking = True
                        st.success("✅ تم إرسال الطلب! جاري المعالجة...")
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error(f"❌ خطأ: {response.status_code}")
                        
                except Exception as e:
                    st.error(f"❌ خطأ: {str(e)}")

# فحص تلقائي للحالة
if st.session_state.job_id and not st.session_state.image_url and st.session_state.checking:
    st.info("⏳ جاري معالجة الصورة... سيتم التحديث تلقائياً")
    
    # شريط التقدم
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    with st.spinner("جاري الفحص..."):
        try:
            status_response = requests.get(
                f"https://api.runpod.ai/v2/r1ydf3al5qv86b/status/{st.session_state.job_id}",
                headers={"Authorization": "Bearer rpa_YUF652M25EB1I1IQAWDT988YIXQYLZKNN945AT9Eudu63j"}
            )
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                status = status_data.get('status')
                
                if status == 'COMPLETED':
                    output = status_data.get('output', {})
                    image_url = None
                    
                    if isinstance(output, dict):
                        image_url = output.get('image_url') or output.get('images', [None])[0]
                    
                    if image_url:
                        st.session_state.image_url = image_url
                        st.session_state.checking = False
                        progress_bar.progress(100)
                        status_text.success("✅ تم إنشاء الصورة!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.warning("⚠️ لم يتم العثور على الصورة")
                        st.session_state.checking = False
                        
                elif status == 'IN_PROGRESS':
                    progress = min(status_data.get('progress', 50), 95)
                    progress_bar.progress(progress)
                    status_text.info(f"⏳ قيد المعالجة... ({progress}%)")
                    time.sleep(5)
                    st.rerun()
                    
                elif status == 'FAILED':
                    st.error("❌ فشلت المعالجة")
                    st.session_state.checking = False
                    st.session_state.job_id = None
                    
                else:
                    status_text.write(f"الحالة: {status}")
                    time.sleep(5)
                    st.rerun()
                    
        except Exception as e:
            st.error(f"❌ خطأ في الفحص: {str(e)}")

# عرض النتيجة وإنشاء PDF
if st.session_state.image_url:
    child_name = st.session_state.child_name
    story_data = st.session_state.story_data
    image_url = st.session_state.image_url
    
    # 🔔 نافذة منبثقة عند الانتهاء
    st.balloons()  # تأثير احتفالي
    
    st.success("✅ تم إنشاء القصة بنجاح!")
    
    # رسالة بارزة
    st.markdown("""
        <div style="
            background-color: #d4edda;
            border: 2px solid #28a745;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            margin: 20px 0;
        ">
            <h2 style="color: #155724; margin: 0;">🎉 تهانينا!</h2>
            <p style="color: #155724; font-size: 18px; margin: 10px 0;">
                تم إنشاء قصة <strong>{}</strong> بنجاح
            </p>
            <p style="color: #28a745; font-size: 24px; margin: 0;">
                👇 انقر لتحميل PDF
            </p>
        </div>
    """.format(child_name), unsafe_allow_html=True)
    
    # عرض الصورة
    st.image(image_url, caption=f"صورة {child_name}", use_column_width=True)
    
    # زر إنشاء PDF بارز
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📥 تحميل القصة الكاملة (PDF)", type="primary", use_container_width=True):
            with st.spinner("جاري إنشاء PDF..."):
                try:
                    pdf_buffer = io.BytesIO()
                    c = canvas.Canvas(pdf_buffer, pagesize=A4)
                    width, height = A4
                    
                    # صفحة الغلاف
                    c.setFont("Helvetica-Bold", 30)
                    c.drawCentredString(width/2, height-100, story_data["title"])
                    c.setFont("Helvetica", 20)
                    c.drawCentredString(width/2, height-150, f"قصة {child_name}")
                    
                    # تحميل وإدراج الصورة
                    try:
                        img_response = requests.get(image_url)
                        img = Image.open(io.BytesIO(img_response.content))
                        img_buffer = io.BytesIO()
                        img.save(img_buffer, format='PNG')
                        img_buffer.seek(0)
                        c.drawImage(ImageReader(img_buffer), 100, 300, width=400, height=400, preserveAspectRatio=True)
                    except Exception as e:
                        st.warning(f"تعذر إدراج الصورة: {e}")
                    
                    c.showPage()
                    
                    # صفحات القصة
                    for i, page_text in enumerate(story_data["pages"]):
                        c.setFont("Helvetica-Bold", 20)
                        c.drawCentredString(width/2, height-80, f"صفحة {i+1}")
                        
                        c.setFont("Helvetica", 14)
                        text = page_text.format(name=child_name)
                        
                        # تقسيم النص
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
                    
                    # زر التحميل بارز
                    st.download_button(
                        label="📥 اضغط هنا لتحميل PDF",
                        data=pdf_buffer,
                        file_name=f"قصة_{child_name}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                    
                except Exception as e:
                    st.error(f"❌ خطأ في إنشاء PDF: {str(e)}")
    
    # زر إعادة البدء
    st.markdown("---")
    if st.button("🔄 إنشاء قصة جديدة", use_container_width=True):
        # مسح جميع البيانات
        for key in ['job_id', 'image_url', 'checking', 'start_time', 'child_name', 'story_data']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
