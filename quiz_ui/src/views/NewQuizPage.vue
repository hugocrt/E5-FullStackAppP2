<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import FloatLabel from 'primevue/floatlabel';
import Message from 'primevue/message';
import 'primeicons/primeicons.css';

import participationStorageService from "@/services/ParticipationStorageService";

const router = useRouter();

const username = ref('');
const errorMessage = ref('');

const onFormSubmit = () => {
  if (!username.value.trim()) {
    errorMessage.value = 'Username is required.';
    return;
  }

  errorMessage.value = '';

  participationStorageService.savePlayerName(username.value);
  router.push('/questions');
};
</script>

<template>
  <div class="quiz-page">
    <h1 class="page-title text-center">New Quiz Page</h1>
    <Form
      class="form-container flex justify-center flex-col gap-4 p-4 rounded shadow-lg bg-white"
      @submit.prevent="onFormSubmit"
    >
      <div class="input-group flex flex-col gap-2">
        <FloatLabel>
          <InputText id="over_label" v-model="username" class="input-field"/>
          <label for="over_label" class="label">Username</label>
        </FloatLabel>

        <Message
          v-if="errorMessage"
          size="small"
          severity="error"
          variant="simple"
          class="error-message"
        >
          {{ errorMessage }}
        </Message>
        <Message
          v-else
          size="small"
          severity="secondary"
          variant="simple"
          class="info-message"
        >
          Enter your username to start the Quiz.
        </Message>
      </div>
      <Button
        type="submit"
        severity="secondary"
        label="Start Quiz"
        class="start-button"
      />
    </Form>
  </div>
</template>

<style scoped>
.quiz-page {
  max-width: 30%;
  margin-top: 10%;
  margin-left: 35%;
  padding: 2rem;
  background-color: #f9f9f9;
  border-radius: 8px;
}

.page-title {
  font-size: 1.5rem;
  font-weight: bold;
  color: #333;
}

.input-group {
  margin-bottom: 1rem;
}

.input-field {
  width: 100%;
  padding: 0.5rem;
}

.start-button {
  width: 100%;
  font-weight: bold;
}
</style>
