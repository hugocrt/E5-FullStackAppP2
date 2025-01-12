<script setup>
import { ref, onMounted } from 'vue';
import {RouterLink, useRoute} from 'vue-router';
import QuizApiService from "@/services/QuizApiService.js";
import Score from "@/components/Score.vue";
import Button from "primevue/button";

const route = useRoute();

const playerName = route.query.playerName;
const answers = JSON.parse(route.query.answers || '[]');
const totQuestions = window.localStorage.getItem('sizeOfQuiz')

const result = ref(null);

const loadResults = async () => {
  try {
    const response = await QuizApiService.postResults(playerName, answers);
    result.value = response.data;
  } catch (error) {
    console.error("Erreur lors de la récupération des résultats :", error);
  }
};

onMounted(() => {
  loadResults();
});
</script>

<template>
  <div class="result-container flex flex-col items-center justify-center gap-6">
    <div v-if="result">
      <h1 class="text-2xl font-bold text-center mb-4">Votre résultat</h1>


      <div class="result-details flex flex-col gap-4 items-center">
        <div class="flex gap-6 items-center">
          <p class="text-lg font-medium">Joueur : <b style="color: #007ad9">{{ result.playerName }}</b></p>
          <p class="text-xl font-semibold">Score : <b style="color: #007ad9"> {{ result.score }}/{{totQuestions}}</b></p>
          <p class="text-lg font-medium">Date : <b style="color: #007ad9">{{ new Date(result.timestamp).toLocaleString() }}</b></p>
        </div>
      </div>


      <div class="mt-6">
        <h3 class="section-title">Classement général au Quiz</h3>
        <Score/>
      </div>


      <div class="flex justify-center mt-4">

      </div>
    </div>

    <div v-else class="loading-container text-center">
      <p class="text-lg font-medium">Chargement des résultats...</p>
    </div>
  </div>
  <div style="margin-top: 50px"></div>
  <Button
    label="Retour à l'accueil"
    class="p-button-rounded p-button-outlined"
    severity="primary"
    @click="$router.push('/')"
  />
</template>

<style scoped>
.result-container {
  min-height: 100vh;
  background-color: #f9fafb;
  padding: 2rem;
}

.card {
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.loading-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
}

.result-details {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.result-details .flex {
  display: flex;
  gap: 20px;
  justify-content: center;
  align-items: center;
}

.result-details p {
  font-size: 1.1rem;
}

.text-xl {
  font-size: 1.25rem;
}

.section-title {
  font-size: 1.5rem;
  margin-top: 40px;
  margin-bottom: 10px;
  color: #333;
}
</style>

