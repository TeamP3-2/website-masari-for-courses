import pickle
import pandas as pd
import numpy as np
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse

# import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory="templates")


from fastapi import FastAPI
from fastapi.responses import JSONResponse
import pickle
import pandas as pd

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Load dataset
df = pd.read_csv("coursera_processed_data.csv")

# Load similarity matrix
with open("similarity_matrix.pkl", "rb") as f:
    similarity_matrix = pickle.load(f)


######################################33 


from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
import pickle
import pandas as pd

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS for all origins (or specify specific origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://teamp3-2.github.io"],  # Allow only localhost:3000 (your frontend)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Load dataset and similarity matrix
df = pd.read_csv("coursera_processed_data.csv")
with open("similarity_matrix.pkl", "rb") as f:
    similarity_matrix = pickle.load(f)

templates = Jinja2Templates(directory="templates")  # Directory where your HTML templates are located

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
            # "course_id": int(course_data['ID']),
            # "course_name": course_data['Course Name'],
            # "skills": course_data.get('Skills', 'Unknown'),
            # "similarity": similarity_score


            "course_name": course_data['Course Name'],
            "course_id": int(course_data['ID']), 
            "university": course_data['University'],
            "difficulty_level": course_data['Difficulty Level'],
            "course_rating": course_data['Course Rating'],
            "course_url": course_data['Course URL'] ,
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
    print("hellp")
    print("*////*******************")
    print(get_recommendations_from_list_of_courses([17], data= df, similarity_matrix=similarity_matrix))
    print("*////*******************")

    recommended_courses = get_recommendations(course_id, df, similarity_matrix)
    # console.log(recommended_courses)
    return JSONResponse(content={"recommendations": recommended_courses})
    # return JSONResponse(content={recommended_courses})


from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

@app.post("/myrec")
async def get_all_recommendations(request: Request):
    body = await request.json()
    courses_id = body.get("course_ids", [])
    
    # إذا كانت القائمة فارغة
    if len(courses_id) == 0:
        return JSONResponse(content={"recommendations": []})

    # تخزين التوصيات لكل كورس على حدة
    all_recommendations = {}

    # التصفية حسب كل كورس على حدة
    for course_id in courses_id:
        recommended_courses = get_recommendations_from_list_of_courses(
            [course_id], df, similarity_matrix, top_n=5
        )
        all_recommendations[course_id] = recommended_courses
    
    # إعادة التوصيات لجميع الكورسات
    return JSONResponse(content={"recommendations": all_recommendations})



if __name__ == "__main__":
    
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
    
@app.get("/")
def read_root():
    return {"message": "API is running!"}
