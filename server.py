import pickle
import pandas as pd
import requests
import numpy as np
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Enable CORS for all origins (or specify specific origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://teamp3-2.github.io"],  # Allow only localhost:3000 (your frontend)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# تحميل البيانات من الرابط
url = "https://gist.githubusercontent.com/m7md1221/0a092a379eae0d060d3049131bacc8ad/raw/a5c4e9ddb2a881a6a531028216222ebfdf3d8d97/data.json"
response = requests.get(url)
df = pd.DataFrame(response.json())  # تحويل البيانات من JSON إلى DataFrame

# تحميل المصفوفة similarity من ملف pickle المحلي
with open("similarity_matrix.pkl", "rb") as f:
    similarity_matrix = pickle.load(f)

# Function to get recommendations based on course ID
def get_recommendations(course_id, data, similarity_matrix, top_n=5, rating_weight=0.05):
    try:
        course_id = int(course_id)  # Ensure it's an integer
    except ValueError:
        return [{"error": "Invalid course ID"}]  # Handle invalid input

    if course_id not in data["ID"].values:
        return [{"error": f"Course ID '{course_id}' not found"}]  # Handle missing course

    course_idx = data.index[data["ID"] == course_id][0]  # Find index
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
            "similarity": round(similarity_score * 100, 2)  # تحويلها إلى نسبة مئوية
        })

    return sorted(recommendations, key=lambda x: x['similarity'], reverse=True)

def get_recommendations_from_list_of_courses(courses_id, data, similarity_matrix, top_n=5):
    recommended = {}

    for course_id in courses_id:
        courses = get_recommendations(course_id=course_id, similarity_matrix=similarity_matrix, data=data)

        for course in courses:
            course_id = course['course_id']
            similarity_score = course['similarity']

            if course_id in recommended:
                recommended[course_id]['similarity'] += similarity_score
            else:
                course_data = data[data['ID'] == course_id].iloc[0]

                recommended[course_id] = {
                    "course_id": int(course_data['ID']),
                    "course_name": course_data['Course Name'],
                    "university": course_data['University'],
                    "difficulty_level": course_data['Difficulty Level'],
                    "course_rating": course_data['Course Rating'],
                    "course_url": course_data['Course URL'],
                    "similarity": round(similarity_score , 2)  # تحويلها إلى نسبة مئوية
                }

    return sorted(recommended.values(), key=lambda x: x['similarity'], reverse=True)[:top_n]

@app.get("/recommendations")
async def get_course_recommendations(course_id: int):
    recommended_courses = get_recommendations(course_id, df, similarity_matrix)
    return JSONResponse(content={"recommendations": recommended_courses})

@app.post("/myrec")
async def get_all_recommendations(request: Request):
    body = await request.json()
    courses_id = body.get("course_ids", [])

    if len(courses_id) == 0:
        return JSONResponse(content={"recommendations": []})

    all_recommendations = {}

    for course_id in courses_id:
        recommended_courses = get_recommendations_from_list_of_courses(
            [course_id], df, similarity_matrix, top_n=5
        )
        all_recommendations[course_id] = recommended_courses
    
    return JSONResponse(content={"recommendations": all_recommendations})

@app.get("/")
def read_root():
    return {"message": "API is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
