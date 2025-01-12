<script setup>
import { ref } from 'vue';
import RadioButton from 'primevue/radiobutton';
import Button from 'primevue/button';

// Props
defineProps({
  currentQuestion: Object,
});

// Émission d'un événement vers le parent
const emit = defineEmits(['answerSelected']);

// Variable pour stocker la réponse sélectionnée
const selectedAnswer = ref(null);

// Handler pour émettre la réponse sélectionnée
const onAnswerSubmit = () => {
  if (selectedAnswer.value !== null) {
    emit('answerSelected', selectedAnswer.value);
    console.log('Réponse sélectionnée :', selectedAnswer.value);
    selectedAnswer.value = null; // Réinitialiser la sélection pour la prochaine question
  } else {
    alert('Veuillez sélectionner une réponse.');
  }
};
</script>

<template>
  <div class="card flex justify-center">
    <div class="question-container flex flex-wrap gap-4">
      <h2 class="text-center">{{ currentQuestion.title }}</h2>

      <div v-if="currentQuestion.image !== 'falseb64imagecontent'" class="flex justify-center">
        <img :src="currentQuestion.image" alt="Question illustration" class="question-image" />
      </div>

      <p class="text-center">{{ currentQuestion.text }}</p>

      <div class="flex flex-wrap gap-4">
        <div
          v-for="(answer, index) in currentQuestion.possibleAnswers"
          :key="index"
          class="flexa"
        >
          <RadioButton
            v-model="selectedAnswer"
            :inputId="'answer' + index"
            :value="index"
            name="answers"
            size="large"
          />

          <label :for="'answer' + index" class="text-lg ml-2">{{ answer.text }}</label>
        </div>
      </div>

      <Button
        label="Suivant"
        @click="onAnswerSubmit"
        class="submit-button p-button-rounded p-button-outlined"
        severity="secondary"
      />
    </div>
  </div>
</template>

<style scoped>
.card {
  max-width: 600px;
  margin: auto;
  padding: 1.5rem;
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.question-container {
  gap: 50px;
}

.question-image {
  max-width: 300px;
  max-height: 300px;
  width: auto;
  height: auto;
}


.submit-button {
  margin-top: 1rem;
  align-content: end;
}

.flexa {
 display: flex;
 align-items: center;
 justify-content: space-between;
 gap: 10px;
}

</style>

