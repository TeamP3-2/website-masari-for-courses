let allCourses = []; 

document.addEventListener("DOMContentLoaded", function() {
    let preferencesForm = document.getElementById("coursesContainer");
    let loginForm = document.getElementById("loginForm");
    let signupForm = document.getElementById("signupForm");
    let logoutBtn = document.getElementById("logoutBtn");
    const storedName = localStorage.getItem("username");

    let currentPath = window.location.pathname.split("/").pop();
    let navLinks = document.querySelectorAll(".nav-list a");

    navLinks.forEach(link => {
        if (link.getAttribute("href") === currentPath) {
            link.classList.add("active");
        }
    });

    let storedEmail = localStorage.getItem("userEmail");

    if (logoutBtn) {
        if (storedEmail) {
            logoutBtn.style.display = "inline-block";
        } else {
            logoutBtn.style.display = "none";
        }
    
        logoutBtn.addEventListener("click", function () {
            let ratingModal = document.getElementById("ratingModal");
            let closeBtn = document.querySelector(".close");
            let stars = document.querySelectorAll(".star");
            let submitRating = document.getElementById("submitRating");
            let selectedRating = 0;
    
            // عرض نافذة التقييم
            ratingModal.style.display = "block";
    
            // اختيار النجوم
            stars.forEach(star => {
                star.addEventListener("click", function () {
                    selectedRating = this.getAttribute("data-value");
                    stars.forEach(s => s.classList.remove("active"));
                    for (let i = 0; i < selectedRating; i++) {
                        stars[i].classList.add("active");
                    }
                });
            });
    
            // إغلاق النافذة
            closeBtn.addEventListener("click", function () {
                ratingModal.style.display = "none";
            });
    
            // إرسال التقييم وتسجيل الخروج
            submitRating.addEventListener("click", function () {
                if (selectedRating > 0) {
                    alert("شكرًا على تقييمك: " + selectedRating + " نجوم!");
                    window.location.href = "signin.html";
                } else {
                    alert("يرجى اختيار تقييم قبل المتابعة.");
                }
            });
        });
    }
    
    if (preferencesForm) {
        fetch("http://localhost:3000/api/course")
            .then(response => response.json())
            .then(courses => {
               allCourses = courses;          
               displayCourses(allCourses); 
            })
            .catch(error => console.error("❌ Error fetching courses:", error));
    }

    if (loginForm) {
        loginForm.addEventListener("submit", function(event) {
            event.preventDefault();
            let email = document.getElementById("email").value;
            let password = document.getElementById("password").value;

            let storedEmail = localStorage.getItem("userEmail");
            let storedPassword = localStorage.getItem("userPassword");

            if (email === storedEmail && password === storedPassword) {
                alert("🎉 مرحبًا بك مجددًا!");
                window.location.href = "index.html";
            } else {
                alert("❌ البريد الإلكتروني أو كلمة المرور غير صحيحة!");
            }
        });
    }

    if (signupForm) {
        signupForm.addEventListener("submit", function(event) {
            event.preventDefault();
            let email = document.getElementById("email").value;
            let password = document.getElementById("password").value;
            let name = document.getElementById("username").value;

            if (localStorage.getItem("userEmail") === email) {
                alert("❌ هذا البريد الإلكتروني مسجل بالفعل. حاول تسجيل الدخول.");
                return;
            }

            localStorage.setItem("userEmail", email);
            localStorage.setItem("userPassword", password);
            localStorage.setItem("username", name);

            alert("✅ تم إنشاء الحساب بنجاح! يمكنك الآن تسجيل الدخول.");
            window.location.href = "signin.html";
        });
    }
});



function searchCourses() {
    let input = document.getElementById("searchInput").value.toLowerCase();
    let filteredCourses = allCourses.filter(course => 
        course["Course Name"].toLowerCase().includes(input)
        );

    displayCourses(filteredCourses); 
}
function displayCourses(courses) {
    let clusters = {}; 
    let coursesContainer = document.getElementById("coursesContainer");
    
    if (coursesContainer) {
        courses.forEach(course => {
            let clusterTitle = course["Cluster Title"] || "غير مصنف"; 
            
            if (!clusters[clusterTitle]) {
                clusters[clusterTitle] = []; 
            }
            clusters[clusterTitle].push(course);
        });

        let coursesHTML = "";
        for (let clusterTitle in clusters) {
            coursesHTML += `         
                <h2><i class="fa-solid fa-book-open"></i>   ${clusterTitle}</h2>
                     
            `;
            
            clusters[clusterTitle].slice(0, 8).forEach(course => { 
                coursesHTML += `
                    <div class="course-card">
                        <h3>${course["Course Name"]}</h3>
                        <p><strong>University:</strong> ${course["University"]}</p>
                        <p><strong>Level:</strong> ${course["Difficulty Level"]}</p>
                        <p><strong>Rating:</strong> ${course["Course Rating"]}</p>
                        <button class="enroll-btn" data-course-id="${course["ID"]}">التسجيل</button>
                        <span class="inf" onclick="showMoreInfo(${course["ID"]})">عرض المزيد من المعلومات</span>
                    </div>
                `;
            });

        
        }

        coursesContainer.innerHTML = coursesHTML;

        document.querySelectorAll(".enroll-btn").forEach(button => {
            button.addEventListener("click", function() {
                let courseId = this.getAttribute("data-course-id");
                let storedCourses = JSON.parse(localStorage.getItem("enrolledCourses")) || [];

                if (!storedCourses.includes(courseId)) {
                    storedCourses.push(courseId); // إضافة معرف الدورة للمصفوفة
                    localStorage.setItem("enrolledCourses", JSON.stringify(storedCourses)); // تخزين المصفوفة في localStorage
                    alert(`تم تسجيلك بالكورس رقم ${courseId}`);
                } else {
                    alert("✅ أنت مسجل بالفعل في هذا الكورس!");
                }
            });
        });
    } else {
        console.error("❌ العنصر 'coursesContainer' غير موجود في الصفحة.");
    }
}

document.addEventListener("DOMContentLoaded", function() {
    let enrolledCoursesList = document.getElementById("coursesContainer1");

    let enrolledCourses = localStorage.getItem("enrolledCourses");

    try {
        enrolledCourses = JSON.parse(enrolledCourses);
    } catch (error) {
        console.error("❌ خطأ في قراءة البيانات من localStorage:", error);
        enrolledCourses = [];
    }

    if (!Array.isArray(enrolledCourses)) {
        console.warn("⚠️ البيانات المخزنة ليست مصفوفة. سيتم إعادة ضبطها.");
        enrolledCourses = [];
    }

    if (enrolledCourses.length === 0) {
        enrolledCoursesList.innerHTML = "<li>لم تسجل في أي دورة حتى الآن.</li>";
    } else {
        fetch("http://localhost:3000/api/course")
            .then(response => response.json())
            .then(courses => {
                console.log("قائمة الكورسات من API:", courses);

                let enrolledCoursesHTML = "";
                enrolledCoursesHTML += enrolledCourses.map(courseId => {
                    console.log("الـ courseId الموجود في localStorage:", courseId);

                    let course = courses.find(c => String(c.ID) === String(courseId));

                    if (course) {
                        return `
                            <div class="course-card" id="course-${course["ID"]}">
                                <h3>${course["Course Name"]}</h3>
                                <p><strong>University:</strong> ${course["University"]}</p>
                                <p><strong>Level:</strong> ${course["Difficulty Level"]}</p>
                                <p><strong>Rating:</strong> ${course["Course Rating"]}</p>
                                <button class="enroll-btn" data-course-id="${course["ID"]}">حذف</button>
                                <span class="inf" onclick="showMoreInfo(${course['ID']})">عرض المزيد من المعلومات</span>
                            </div>
                        `;
                    } else {
                        console.log(`لم يتم العثور على الدورة مع الـ courseId: ${courseId}`);
                    }
                }).join("");
                enrolledCoursesList.innerHTML = enrolledCoursesHTML;
                let deleteButtons = document.querySelectorAll(".enroll-btn");
                deleteButtons.forEach(button => {
                    button.addEventListener("click", function() {
                        let courseId = this.getAttribute("data-course-id");
                        removeCourse(courseId);
                    });
                });
            })
            .catch(error => {
                console.error("❌ حدث خطأ أثناء جلب بيانات الدورات:", error);
                enrolledCoursesList.innerHTML = "<li>حدث خطأ أثناء جلب الدورات.</li>";
            });
    }
});




function removeCourse(courseId) {
    let enrolledCourses = JSON.parse(localStorage.getItem("enrolledCourses")) || [];
    enrolledCourses = enrolledCourses.filter(course => course !== courseId);  // إزالة الدورة من المصفوفة

    localStorage.setItem("enrolledCourses", JSON.stringify(enrolledCourses));

    let courseElement = document.getElementById(`course-${courseId}`);
    if (courseElement) {
        courseElement.remove();
    }
}
function showMoreInfo(courseId) {
    const enrolledCourseIds = JSON.parse(localStorage.getItem("enrolledCourses")) || [];

        fetch("http://localhost:3000/api/course")
            .then(response => response.json())
            .then(courses => {
                const course = courses.find(courses => Number(courses.ID) === courseId);
                console.log(courseId);
                console.log(course);
                if (course) {
                    const url = `../html/courseDetails.html?courseId=${courseId}`;
                    const newWindow = window.open(url, '_blank');
                } else {
                    alert("لم يتم العثور على الدورة!");
                }
            })
            .catch(error => {
                console.error("❌ حدث خطأ أثناء جلب بيانات الدورة:", error);
                alert("حدث خطأ أثناء جلب بيانات الدورة.");
            });
   
}  