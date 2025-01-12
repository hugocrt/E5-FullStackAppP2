<script setup>
import {ref, onMounted} from 'vue';
import { useRouter } from 'vue-router';
import QuestionDisplay from './QuestionDisplay.vue';
import QuizApiService from "@/services/QuizApiService.js";
import ParticipationStorageService from "@/services/ParticipationStorageService.js";

// Variables réactives
const router = useRouter();
const currentQuestion = ref(null); // Question actuelle
const currentPosition = ref(1);    // Position actuelle
const totalQuestions = ref(localStorage.getItem('sizeOfQuiz')); // Nombre total de questions
const quizEnded = ref(false);      // Indique si le quiz est terminé
const answerPosTab = ref([]);      // Tableau pour enregistrer les positions des réponses

// Fonction pour charger une question par position
const loadQuestion = async (position) => {
  try {
    const response = await QuizApiService.getQuestion(position);
    currentQuestion.value = response.data; // Mettre à jour la question actuelle
  } catch (error) {
    console.error("Erreur lors du chargement de la question :", error);
  }
};

// Fonction pour gérer le clic sur une réponse
const answersClickedHandler = async (selectedAnswerIndex) => {
  // Enregistrer la position actuelle dans le tableau
  answerPosTab.value.push(selectedAnswerIndex+1);

  if (currentPosition.value < totalQuestions.value) {
    // Passer à la question suivante
    currentPosition.value += 1;
    await loadQuestion(currentPosition.value); // Charger la question suivante
  } else {
    endQuiz();
  }
};

const endQuiz = () => {
  quizEnded.value = true;

  // Récupérer le nom du joueur depuis le service
  const playerName = ParticipationStorageService.getPlayerName();

  router.push({
    path: '/results',
    query: {
      playerName: playerName,
      answers: JSON.stringify(answerPosTab.value), // Convertir le tableau en chaîne
    },
  });
};

// Charger la première question lors du montage
onMounted(() => {
  loadQuestion(currentPosition.value);
});
</script>

<template>
  <div v-if="!quizEnded">
    <!-- Affiche la question si elle est disponible -->
    <QuestionDisplay
      v-if="currentQuestion"
      :currentQuestion="currentQuestion"
      @answerSelected="answersClickedHandler"
    />
  </div>
  <div v-else>
    <h2>Quiz terminé ! Merci d'avoir participé.</h2>
  </div>
</template>
