<template>
  <div class="home-page">
    <h1 class="page-title">Page d'accueil</h1>
    <Button
      label="Appuyer pour accéder au Quiz"
      class="p-button-rounded p-button-outlined"
      severity="secondary"
      @click="$router.push('/new-quiz')"
    />
    <h3 class="section-title">Classement général au Quiz</h3>
    <Score></Score>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import Button from 'primevue/button';
import Score from "@/components/Score.vue";
import quizApiService from "@/services/QuizApiService";

onMounted(async () => {
  localStorage.clear();
  const registeredScores = await quizApiService.getQuizInfo();
  localStorage.setItem('sizeOfQuiz', registeredScores.data.size);
});

</script>

<style scoped>
.home-page {
  max-width: 95%;
  margin: 0 auto;
  padding: 20px;
  text-align: center;
}

.page-title {
  font-size: 2.5rem;
  margin-bottom: 20px;
  color: #333;
}

.section-title {
  font-size: 1.5rem;
  margin-top: 40px;
  margin-bottom: 10px;
  color: #333;
}

.router-link {
  display: inline-block;
  text-decoration: none;
  color: inherit;
  font-weight: bold;
  padding: 10px 20px;
}
</style>
