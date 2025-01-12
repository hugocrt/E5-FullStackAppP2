<template>
  <div>
    <h1 class="page-title">Page d'édition des questions</h1>
    <div class="card">
      <Toolbar class="mb-6">
        <template #start>
          <Button label="New" icon="pi pi-plus" class="mr-2" @click="openNew" />
        </template>

        <template #end>
          <Button
            label="Delete"
            icon="pi pi-trash"
            severity="danger"
            outlined
            @click="confirmDeleteSelected"
            :disabled="!selectedQuestions.length"
          />
        </template>
      </Toolbar>

      <DataTable
        ref="dt"
        v-model:expandedRows="expandedRows"
        :value="questions"
        selectionMode="single"
        dataKey="position"
        :paginator="true"
        :rows="5"
        sort-field="position"
        :sort-order="1"
        :filters="filters"
        :globalFilterFields="['title', 'text', 'position']"
        @rowExpand="onRowExpand"
        @rowCollapse="onRowCollapse"
      >
        <template #empty>No question found.</template>
        <template #loading>Loading questions data. Please wait.</template>

        <template #header>
          <div class="flexa">
            <h4 class="m-0">Questions</h4>
            <div class="p-input-icon-left">
              <i class="pi pi-search" />
              <InputText v-model="filters['global'].value" placeholder="Chercher un mot clef" />
            </div>
          </div>
        </template>

        <Column expander style="width: 3rem" />
        <Column field="position" header="Position" sortable style="min-width: 3rem" />
        <Column field="title" header="Titre" sortable style="min-width: 12rem" />
        <Column field="text" header="Intitulé" style="min-width: 16rem" />
        <Column header="Image">
          <template #body="slotProps">
            <img :src="slotProps.data.image" :alt="slotProps.data.image" class="shadow-lg" width="64" />
          </template>
        </Column>
        <Column style="min-width: 3rem">
          <template #body="slotProps">
            <Button icon="pi pi-pencil" outlined rounded class="mr-2" @click="editQuestion(slotProps.data)" />
            <Button icon="pi pi-trash" outlined rounded severity="danger" @click="confirmDeleteQuestion(slotProps.data)" />
          </template>
        </Column>
        <template #expansion="slotProps">
          <div class="p-4">
            <h5>Réponses</h5>
            <DataTable :value="slotProps.data.possibleAnswers">
              <Column field="text" header="Texte"></Column>
              <Column field="isCorrect" header="Est correct" ></Column>
            </DataTable>
          </div>
        </template>
      </DataTable>
    </div>

    <!-- Dialogs -->
    <Dialog v-model:visible="questionDialog" :style="{ width: '90%' }" header="Question" :modal="true">
      <div class="flex flex-col gap-6">

        <!-- Image -->
        <div class="flexa">
          <ImageUploader
            :fileDataUrl="uploadedImage"
            @file-change="handleFileChange"
          />
          <div v-if="uploadedImage" class="image-preview">
            <p>Aperçu de l'image :</p>
            <img :src="uploadedImage" alt="Image prévisualisée" />
          </div>
        </div>

        <!-- Title -->
        <div class="flexa">
          <label for="title" class="block font-bold mb-3">Titre</label>
          <InputText
            id="title"
            v-model.trim="question.title"
            :class="{ 'p-invalid': submitted && !question.title }"
            required
          />
          <small v-if="submitted && !question.title" class="p-error">Title is required.</small>
        </div>

        <!-- Description -->
        <div class="flexa">
          <label for="text" class="block font-bold mb-3">Intitulé</label>
          <Textarea id="text" v-model="question.text" rows="3" required />
        </div>

        <!-- Position -->
        <div class="flexa">
          <label for="position" class="block font-bold mb-3">Position</label>
          <InputNumber id="position" v-model="question.position" integeronly />
        </div>

        <!-- Answers -->
        <div class="flexa">
          <label class="block font-bold mb-3">Réponses</label>
          <div class="grid grid-cols-2 gap-4" v-for="(answer, index) in newAnswers" :key="index">
            <InputText
              v-model="answer.text"
              placeholder="Réponse..."
            />
            <RadioButton
              v-model="selectedAnswer"
              :name="'answer-' + index"
              :value="index"
              :label="`Réponse ${index + 1}`"
              :checked="selectedAnswer === index"
              @click="onAnswerChange(index)"
            />
          </div>
        </div>
      </div>

      <template #footer>
        <Button label="Cancel" icon="pi pi-times" text @click="hideDialog" />
        <Button label="Save" icon="pi pi-check" @click="saveQuestion" />
      </template>
    </Dialog>

    <Dialog
      v-model:visible="deleteQuestionDialog"
      :style="{ width: '450px' }"
      header="Confirmez"
      :modal="true"
    >
      <div class="flex items-center gap-4">
        <i class="pi pi-exclamation-triangle text-3xl" />
        <span>Voulez-vous vraiment supprimer cette question: <b>{{ question.title }}</b>?</span>
      </div>
      <template #footer>
        <Button label="No" icon="pi pi-times" text @click="deleteQuestionDialog = false" />
        <Button label="Yes" icon="pi pi-check" text @click="deleteQuestion" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useToast } from 'primevue/usetoast';
import Button from "primevue/button";
import Column from "primevue/column";
import DataTable from "primevue/datatable";
import Toolbar from "primevue/toolbar";
import InputText from "primevue/inputtext";
import Textarea from "primevue/textarea";
import Dialog from "primevue/dialog";
import InputNumber from "primevue/inputnumber";
import RadioButton from "primevue/radiobutton";
import QuizApiService from '@/services/QuizApiService';
import ImageUploader from '@/components/imgUploader.vue';

const toast = useToast();
const dt = ref();
const questions = ref([]);
const questionDialog = ref(false);
const deleteQuestionDialog = ref(false);
const question = ref({});
const selectedQuestions = ref([]);
const filters = ref({ global: { value: null, matchMode: 'contains' } });
const submitted = ref(false);
const expandedRows = ref([]);
const selectedAnswer = ref(null);  // This is the single selected answer for the correct answer

const newAnswers = ref([]);

// Sync newAnswers with existing answers when editing
watch(question, (newValue) => {
  if (newValue.possibleAnswers && newValue.possibleAnswers.length > 0) {
    newAnswers.value = newValue.possibleAnswers.map(answer => ({
      text: answer.text,
      isCorrect: answer.isCorrect,
    }));
    // Automatically set the selectedAnswer to the one marked as correct
    selectedAnswer.value = newAnswers.value.findIndex(answer => answer.isCorrect);
  } else {
    // If no answers exist, initialize with empty answers
    newAnswers.value = [
      { text: '', isCorrect: false },
      { text: '', isCorrect: false },
      { text: '', isCorrect: false },
      { text: '', isCorrect: false },
    ];
    selectedAnswer.value = null;
  }
}, { immediate: true });

// Fetch questions
onMounted(async () => {
  try {
    const totQuestions = Number.parseInt(window.localStorage.getItem("sizeOfQuiz"), 10);

    if (isNaN(totQuestions)) {
      throw new Error("Invalid sizeOfQuiz value in localStorage");
    }

    const fetchedQuestions = [];
    for (let i = 1; i <= totQuestions; i++) {
      const response = await QuizApiService.getQuestion(i);
      if (response && response.data) {
        fetchedQuestions.push(response.data);
      }
    }
    questions.value = fetchedQuestions;

  } catch (error) {
    console.error("Failed to load questions:", error);
    toast.add({
      severity: "error",
      summary: "Error",
      detail: "Failed to load questions",
      life: 3000,
    });
  }
});

// Open new dialog
const openNew = () => {
  question.value = { possibleAnswers: [] };
  submitted.value = false;
  questionDialog.value = true;
};

const hideDialog = () => {
  questionDialog.value = false;
  submitted.value = false;
};

// Save question
const saveQuestion = async () => {
  submitted.value = true;

  if (question.value.title && question.value.text) {
    try {
      const questionPayload = {
        text: question.value.text,
        title: question.value.title,
        image: uploadedImage.value || '',
        position: question.value.position || 0,
        possibleAnswers: newAnswers.value.map((answer, index) => ({
          text: answer.text,
          isCorrect: index === selectedAnswer.value,
        })),
      };

      uploadedImage.value = '';

      if (question.value.id) {
        await QuizApiService.updateQuestion(question.value.position, questionPayload);
        window.location.reload();
      } else {
        const response = await QuizApiService.createQuestion(questionPayload);
        question.value.id = response.data.id;

        let sizeOfQuiz = window.localStorage.getItem('sizeOfQuiz');

        sizeOfQuiz = isNaN(parseInt(sizeOfQuiz, 10)) ? 0 : parseInt(sizeOfQuiz, 10);

        sizeOfQuiz++;

        window.localStorage.setItem('sizeOfQuiz', sizeOfQuiz);

        window.location.reload();
      }

      questionDialog.value = false;
    } catch (error) {
      toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to save question', life: 3000 });
    }
  }
};

// Delete question
const deleteQuestion = async () => {
  try {
    await QuizApiService.deleteQuestion(question.value.id);
    questions.value = questions.value.filter(q => q.id !== question.value.id);
    deleteQuestionDialog.value = false;
    let sizeOfQuiz = window.localStorage.getItem('sizeOfQuiz');
    sizeOfQuiz = parseInt(sizeOfQuiz, 10);
    sizeOfQuiz--;
    window.localStorage.setItem('sizeOfQuiz', sizeOfQuiz.toString());
    window.location.reload();
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to delete question', life: 3000 });
  }
};

// Edit question
const editQuestion = (prod) => {
  question.value = { ...prod };
  questionDialog.value = true;
};

// Confirm delete question
const confirmDeleteQuestion = (prod) => {
  question.value = prod;
  deleteQuestionDialog.value = true;
};

const uploadedImage = ref('');
function handleFileChange(newFileDataUrl) {
  uploadedImage.value = newFileDataUrl;
}
</script>

<style scoped>
.page-title {
  font-size: 2.5rem;
  margin-bottom: 20px;
  color: #333;
}
.flexa {
  display: flex;
  align-items: center;
  justify-content: space-evenly;
  gap: 10px;
}
</style>
