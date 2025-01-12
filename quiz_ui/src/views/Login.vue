<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import FloatLabel from 'primevue/floatlabel';
import Message from 'primevue/message';
import 'primeicons/primeicons.css';

import quizApiService from "@/services/QuizApiService";
import { eventBus } from '@/eventBus'; // Importer le bus d'événements

const router = useRouter();

const password = ref('');
const errorMessage = ref('');

const onFormSubmit = async () => {
  if (!password.value) {
    errorMessage.value = 'Error on password';
    return;
  }

  errorMessage.value = '';

  try {
    const response = await quizApiService.Login(password.value);
    console.log(response.status);

    if (response.status === 200) {
      const token = response.data.token;
      if (token) {
        window.localStorage.setItem("access_token", token);

        eventBus.emitAuthUpdate(true);

        await router.push('/questions/edit');
      } else {
        console.log("Token not found in response data");
      }
    } else {
      errorMessage.value = 'Login failed';
    }
  } catch (error) {
    console.log("Error during login:", error);
    errorMessage.value = 'Login failed';
  }
};
</script>

<template>
  <div class="quiz-page">
    <h1 class="page-title text-center">Login Page</h1>
    <Form
      class="form-container flex justify-center flex-col gap-4 p-4 rounded shadow-lg bg-white"
      @submit.prevent="onFormSubmit"
    >
      <div class="input-group flex flex-col gap-2">
        <FloatLabel>
          <InputText id="over_label" v-model="password" class="input-field"/>
          <label for="over_label" class="label">Password</label>
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
          Enter admin password to connect.
        </Message>
      </div>
      <Button
        type="submit"
        severity="secondary"
        label="Login"
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
