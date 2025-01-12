import axios from "axios";

const instance = axios.create({
  baseURL: `${import.meta.env.VITE_API_URL}`,
  json: true
});

instance.interceptors.request.use((config) => {
  console.log("Requête envoyée :", config);
  return config;
}, (error) => {
  return Promise.reject(error);
});

export default {
  async call(method, resource, data = null, token = null) {
    var headers = {
      "Content-Type": "application/json",
    };
    if (token != null) {
      headers.authorization = "Bearer " + token;
    }

    return instance({
      method,
      headers: headers,
      url: resource,
      data,
    })
      .then((response) => {
        return { status: response.status, data: response.data };
      })
      .catch((error) => {
        console.error(error);
      });
  },

  async getQuizInfo() {
    return this.call("get", "quiz-info");
  },

  async getQuestion(position) {
    if (typeof position !== "number") {
      throw new Error("Position must be a number.");
    }
    return this.call("get", `questions?position=${position}`);
  },

  async postResults(playerName, answersPosTab) {
    const payload = {
      playerName: playerName,
      answers: answersPosTab,
    };
    return this.call("post", "participations", payload);
  },

  async Login(password){
    const payload = {
      password: password,
    };
    return this.call("post", "login", payload);
  },

  async createQuestion(payload) {
    const authToken = window.localStorage.getItem('access_token');
    return this.call("post", "questions", payload, authToken);
  },

  async deleteQuestion(questionId) {
    const authToken = window.localStorage.getItem('access_token');
    return this.call("delete", `questions/${questionId}`, null, authToken);
  },

  async updateQuestion(questionPos, payload) {
    const authToken = window.localStorage.getItem('access_token');
    return this.call("put", `questions/${questionPos}`, payload, authToken);
  },

  async deleteQuestions() {
    const authToken = window.localStorage.getItem('access_token');
    return this.call("delete", "questions", null, authToken);
  },
};
