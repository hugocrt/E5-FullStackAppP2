<template>
  <div class="card">
    <DataTable
      v-model:filters="filters"
      :value="registeredScores"
      paginator
      showGridlines
      :rows="5"
      dataKey="playerName"
      filterDisplay="menu"
      sort-field="score"
      :sort-order="-1"
      :loading="loading"
      :globalFilterFields="['playerName', 'date']"
    >
      <template #empty>No score found.</template>
      <template #loading>Loading scores data. Please wait.</template>

      <Column field="playerName" header="Player Name" style="min-width: 12rem">
        <template #body="{ data }">
          {{ data.player_name }}
        </template>
      </Column>

      <Column field="score" sortable="" header="Score" style="min-width: 8rem">
        <template #body="{ data }">
          {{ data.score }}
        </template>
      </Column>

      <Column field="date" header="Date" style="min-width: 10rem">
        <template #body="{ data }">
          {{ formatDate(data.date) }}
        </template>
        <template #filter="{ filterModel }">
          <Calendar v-model="filterModel.value" dateFormat="mm/dd/yy" placeholder="mm/dd/yyyy" />
        </template>
      </Column>
    </DataTable>
  </div>
</template>

<script setup>
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Calendar from 'primevue/calendar'
import { ref, onMounted } from 'vue';
import { FilterMatchMode, FilterOperator } from '@primevue/core/api';

import quizApiService from "@/services/QuizApiService";

const registeredScores = ref([]);
const filters = ref();
const loading = ref(true);

// Initialiser les filtres
const initFilters = () => {
  filters.value = {
    date: { operator: FilterOperator.AND, constraints: [{ value: null, matchMode: FilterMatchMode.DATE_IS }] },
  };
};

// Charger les données depuis l'API
onMounted(async () => {
  try {
    const response = await quizApiService.getQuizInfo();
    registeredScores.value = response.data.scores.map(score => ({
      ...score,
      date: new Date(score.date), // Convertir la date en objet `Date` pour un formtage correct
    }));
    loading.value = false;
  } catch (error) {
    console.error("Erreur lors du chargement des scores :", error);
    loading.value = false;
  }
});

// Formatage des dates pour l'affichage
const formatDate = (value) => {
  if (!value) return '';
  return value.toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  });
};

// Réinitialiser les filtres
const clearFilter = () => {
  initFilters();
};

// Initialisation des filtres
initFilters();
</script>
