<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { RouterLink, RouterView } from 'vue-router';
import Menubar from 'primevue/menubar';
import 'primeicons/primeicons.css';
import { eventBus } from './eventBus';

const isAuthenticated = ref(false);
const router = useRouter();

const logout = () => {
  localStorage.removeItem('access_token');
  isAuthenticated.value = false;
  eventBus.emitAuthUpdate(false);
  router.push('/login');
};

onMounted(() => {
  isAuthenticated.value = !!localStorage.getItem('access_token');
});

watch(() => eventBus.authUpdated.value, (newStatus) => {
  isAuthenticated.value = newStatus;
});
</script>

<template>
  <div>
    <header>
      <Menubar>
        <template #start>
          <div class="flexa">
              <img src="@/assets/logo.webp" alt="Logo Quiz" height="50" width="50" style="border-radius: 50%;"/>
              <div style="margin-right: 20px;"></div>
              <RouterLink to="/" class="router-link">
                <span class="pi pi-home" style="margin-right: 5px;"></span>
                Page d'accueil
              </RouterLink>
          </div>
        </template>

        <template #end>
          <!-- Vérifier si le token est dans le localStorage -->
          <template v-if="isAuthenticated">
            <div class="flexa">
              <RouterLink to="/questions/edit" class="router-link">
                <span class="pi pi-pencil" style="margin-right: 5px;"></span>
                Édition des questions
              </RouterLink>
              <RouterLink to="/" class="router-link" @click.prevent="logout">
                <span class="pi pi-sign-out" style="margin-right: 5px;"></span>
                Se déconnecter
              </RouterLink>
            </div>
          </template>
          <template v-else>
            <RouterLink to="/login" class="router-link">
              <span class="pi pi-user" style="margin-right: 5px;"></span>
              Se connecter
            </RouterLink>
          </template>
        </template>
      </Menubar>
    </header>

    <main>
      <RouterView/>
    </main>

    <footer>
    </footer>
  </div>
</template>

<style scoped>
.flexa {
  display: flex;
  align-items: center;
  gap: 10px;
}

.router-link {
  display: flex;
  align-items: center;
  text-decoration: none;
  color: inherit;
  font-weight: bold;
}

.router-link:hover {
  color: #007ad9;
  font-size: 20px;
}
</style>
