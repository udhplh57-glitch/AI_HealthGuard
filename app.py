import os
from flask import Flask, render_template, request
import openai
import urllib.parse

app = Flask(__name__)

# ضع مفتاح OpenAI الخاص بك في متغير البيئة OPENAI_API_KEY
openai.api_key = os.getenv("OPENAI_API_KEY")

# كلمات خطيرة لتحديد الحالة عالية الخطورة
danger_keywords = [
    "severe", "شديد", "حاد", "ألم شديد", "ألم حاد", "وجع قوي",
    "ألم في الصدر", "ضيق تنفس", "صعوبة التنفس",
    "إغماء", "غيبوبة", "نزيف", "قيء دم",
    "سعال دموي", "تشنجات", "ارتفاع شديد في الحرارة"
]

# علاقة بعض الكلمات بخبراء/أطباء محددين
doctor_mapping = {
    "ألم في الصدر": "طبيب قلب",
    "ضيق تنفس": "طبيب رئة",
    "تشنجات": "طبيب أعصاب",
    "نزيف": "طبيب طوارئ",
    "حرارة": "طبيب باطنة"
}

def is_dangerous(symptoms):
    symptoms = symptoms.lower()
    for word in danger_keywords:
        if word.lower() in symptoms:
            return True
    return False

def get_doctor(symptoms):
    symptoms = symptoms.lower()
    for key, doctor in doctor_mapping.items():
        if key.lower() in symptoms:
            return doctor
    return "طبيب مختص"

def get_chatgpt_response(symptoms):
    """استدعاء ChatGPT للحصول على نصائح علاجية للأعراض"""
    prompt = f"قدم نصائح طبية عامة للتعامل مع هذه الأعراض: {symptoms}. لا تقدم تشخيص شخصي."
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.7,
        )
        answer = response.choices[0].message.content.strip()
        return answer
    except Exception as e:
        return "حدث خطأ أثناء جلب الحلول من ChatGPT."

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    symptoms = request.form.get("symptoms", "").strip()
    if not symptoms:
        return render_template("index.html", error_message="يجب إدخال الأعراض أولًا.")

    confidence = 100

    if is_dangerous(symptoms):
        risk = "مرتفع"
        tips = [
            "الراحة وشرب السوائل الدافئة",
            "متابعة الأعراض بدقة والذهاب للطبيب فورًا",
            "تجنب استخدام أي أدوية دون استشارة طبية",
            "مراقبة درجة الحرارة والأعراض التنفسية"
        ]
        doctor = get_doctor(symptoms)
        tips.append(f"يُنصح بالذهاب إلى {doctor} بناءً على الأعراض المدخلة")
    else:
        risk = "منخفض"
        tips = [
            "الراحة وشرب الماء بانتظام",
            "تجنب الإجهاد والتوتر",
            "النوم الكافي",
            "السوائل الدافئة"
        ]

    # جلب نصائح مباشرة من ChatGPT
    chatgpt_advice = get_chatgpt_response(symptoms)

    # إنشاء رابط لمحادثة ChatGPT جاهزة بنفس السؤال
    encoded_symptoms = urllib.parse.quote(f"ما هي طرق علاج هذه الأعراض: {symptoms}؟")
    chatgpt_link = f"https://chat.openai.com/?prompt={encoded_symptoms}"

    return render_template(
        "result.html",
        symptoms=symptoms,
        risk=risk,
        confidence=confidence,
        tips=tips,
        chatgpt_advice=chatgpt_advice,
        chatgpt_link=chatgpt_link
    )

if __name__ == "__main__":
    import webbrowser
    import threading

    def open_browser():
        webbrowser.open_new("http://127.0.0.1:5000/")

    threading.Timer(1, open_browser).start()
    app.run(debug=True)
