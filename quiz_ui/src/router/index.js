import { createRouter, createWebHistory } from 'vue-router';
import HomePage from '../views/HomePage.vue';
import NewQuizPage from "@/views/NewQuizPage.vue";
import QuizManager from '@/components/QuestionManager.vue';
import Participation from '@/views/ParticipationPage.vue';
import EditQuizPage from '@/views/EditQuizPage.vue';
import Login from '@/views/Login.vue';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'HomePage',
      component: HomePage,
    },
    {
      path: '/new-quiz',
      name: 'NewQuizPage',
      component: NewQuizPage,
    },
    {
      path: '/questions',
      name: 'QuizManager',
      component: QuizManager,
    },
    {
      path: '/results',
      name: 'Results',
      component: Participation,
    },
    {
      path: '/login',
      name: 'Login',
      component: Login,
    },
    {
      path: '/questions/edit',
      name: 'EditQuizPage',
      component: EditQuizPage,
    },
  ],
});

export default router;
