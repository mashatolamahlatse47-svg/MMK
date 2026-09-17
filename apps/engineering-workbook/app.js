let lessons = [];
let currentDay = Number(localStorage.getItem("mmkEngineeringCurrentDay")) || 1;

const lessonTitle = document.getElementById("lessonTitle");
const lessonLearn = document.getElementById("lessonLearn");
const exerciseList = document.getElementById("exerciseList");
const mamelodiExercise = document.getElementById("mamelodiExercise");
const mmkExercise = document.getElementById("mmkExercise");
const reflection = document.getElementById("reflection");
const notes = document.getElementById("notes");
const completeButton = document.getElementById("completeButton");
const status = document.getElementById("status");
const progressFill = document.getElementById("progressFill");
const dayCounter = document.getElementById("dayCounter");
const progressText = document.getElementById("progressText");

const previousButton = document.getElementById("previousButton");
const nextButton = document.getElementById("nextButton");

function notesKey(day) {
  return `mmkEngineeringDay${day}Notes`;
}

function completeKey(day) {
  return `mmkEngineeringDay${day}Complete`;
}

function renderLesson(lesson) {
  if (!lesson) return;

  currentDay = lesson.day;
  localStorage.setItem("mmkEngineeringCurrentDay", currentDay);

  const completedDays = lessons.filter(
    (item) => localStorage.getItem(completeKey(item.day)) === "true"
  ).length;

  const totalDays = lessons.length;
  const percent = totalDays === 0 ? 0 : (completedDays / totalDays) * 100;

  dayCounter.textContent = `Day ${currentDay} of ${totalDays}`;
  progressText.textContent = `${completedDays}/${totalDays} completed — ${Math.round(percent)}%`;
  progressFill.style.width = `${percent}%`;

  lessonTitle.textContent =
    `${lesson.flag} Day ${lesson.day}: ${lesson.title}`;

  lessonLearn.textContent = lesson.learn;

  exerciseList.innerHTML = "";

  lesson.exercise.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    exerciseList.appendChild(li);
  });

  mamelodiExercise.textContent = lesson.mamelodi;
  mmkExercise.textContent = lesson.mmk;
  reflection.textContent = lesson.reflection;

  notes.value = localStorage.getItem(notesKey(currentDay)) || "";

  const completed =
    localStorage.getItem(completeKey(currentDay)) === "true";

  if (completed) {
    completeButton.textContent = `Day ${currentDay} Completed ✓`;
    status.textContent =
      `Day ${currentDay} completed. Your progress is saved on this device.`;
  } else {
    completeButton.textContent = `Complete Day ${currentDay}`;
    status.textContent = `Day ${currentDay} is in progress.`;
  }

  previousButton.disabled = currentDay === 1;
  nextButton.disabled = currentDay === lessons.length;
}

function goToDay(day) {
  const lesson = lessons.find((item) => item.day === day);

  if (lesson) {
    renderLesson(lesson);
  }
}

async function loadLessons() {
  try {
    const response = await fetch("data/lessons.json");

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    lessons = await response.json();

    if (!Array.isArray(lessons) || lessons.length === 0) {
      throw new Error("Lesson database is empty.");
    }

    const firstAvailableDay =
      lessons.find((item) => item.day === currentDay) || lessons[0];

    renderLesson(firstAvailableDay);
  } catch (error) {
    console.error(error);
    status.textContent = "Could not load lesson data.";
  }
}

notes.addEventListener("input", () => {
  localStorage.setItem(notesKey(currentDay), notes.value);
});

completeButton.addEventListener("click", () => {
  localStorage.setItem(completeKey(currentDay), "true");
  renderLesson(lessons.find((item) => item.day === currentDay));
});

previousButton.addEventListener("click", () => {
  if (currentDay > 1) {
    goToDay(currentDay - 1);
  }
});

nextButton.addEventListener("click", () => {
  if (currentDay < lessons.length) {
    goToDay(currentDay + 1);
  }
});

loadLessons();
