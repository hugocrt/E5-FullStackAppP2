// src/eventBus.js
import { ref } from 'vue';

export const eventBus = {
  authUpdated: ref(false), // Cette référence sera mise à jour lorsqu'il y a un changement d'authentification
  emitAuthUpdate(status) {
    this.authUpdated.value = status;
  },
  onAuthUpdate(callback) {
    this.authUpdated.value && callback(this.authUpdated.value);
  },
};
