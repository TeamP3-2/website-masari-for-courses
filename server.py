import pickle
import pandas as pd
import aiohttp  # مكتبة لجلب البيانات من الإنترنت بشكل غير متزامن
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# السماح للطلبات من الفرونت إند
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # يمكن تغييرها إلى ["https://your-frontend-link.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")  

# رابط JSON الخارجي
jsonUrl = "https://gist.githubusercontent.com/m7md1221/0a092a379eae0d060d3049131bacc8ad/raw/a5c4e9ddb2a881a6a531028216222ebfdf3d8d97/data.json"

# تحميل البيانات من الرابط
async def load_data():
    async with aiohttp.ClientSession() as session:
        async with session.get(jsonUrl) as response:
            data = await response.json()
            return pd.DataFrame(data)  # تحويل JSON إلى DataFrame

# تحميل بيانات `similarity_matrix.pkl`
with open("similarity_matrix.pkl", "rb") as f:
    similarity_matrix = pickle.load(f)

# دالة التوصيات
def get_recommendations(course_id, data, similarity_matrix, top_n=5):
    try:
        course_id = int(course_id)  
    except ValueError:
        return [{"error": "Invalid course ID"}]

    if course_id not in data["ID"].values:
        return [{"error": f"Course ID '{course_id}' not found"}]  

    course_idx = data.index[data["ID"] == course_id][0]  
    similarity_scores = list(enumerate(similarity_matrix[course_idx]))

    recommendations = []
    for idx, similarity_score in sorted(similarity_scores, key=lambda x: x[1], reverse=True)[1:top_n+1]:
        course_data = data.iloc[idx]

        recommendations.append({
            "course_name": course_data['Course Name'],
            "course_id": int(course_data['ID']), 
            "university": course_data['University'],
            "difficulty_level": course_data['Difficulty Level'],
            "course_rating": course_data['Course Rating'],
            "course_url": course_data['Course URL'],
            "similarity": round(similarity_score * 100, 2)
        })

    return sorted(recommendations, key=lambda x: x['similarity'], reverse=True)

# API لاسترجاع التوصيات
@app.get("/recommendations")
async def get_course_recommendations(course_id: int):
    data = await load_data()  # تحميل البيانات من الإنترنت
    recommended_courses = get_recommendations(course_id, data, similarity_matrix)
    return JSONResponse(content={"recommendations": recommended_courses})

# API لاسترجاع توصيات متعددة
@app.post("/myrec")
async def get_all_recommendations(request: Request):
    body = await request.json()
    courses_id = body.get("course_ids", [])

    if len(courses_id) == 0:
        return JSONResponse(content={"recommendations": []})

    data = await load_data()  # تحميل البيانات عند كل طلب
    all_recommendations = {}

    for course_id in courses_id:
        recommended_courses = get_recommendations(course_id, data, similarity_matrix, top_n=5)
        all_recommendations[course_id] = recommended_courses
    
    return JSONResponse(content={"recommendations": all_recommendations})

# فحص تشغيل API
@app.get("/")
def read_root():
    return {"message": "API is running!"}
