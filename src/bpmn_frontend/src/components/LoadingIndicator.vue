<template>
  <v-alert type="info" class="mb-5">
    <div class="d-flex align-center flex-column">
      <div class="d-flex align-center">
        <span class="thinking-text mr-2">Thinking</span>
        <span class="dots">
          <span class="dot">.</span>
          <span class="dot">.</span>
          <span class="dot">.</span>
        </span>
      </div>
      <div v-if="showTimeout" class="timeout-message mt-2">
        This is taking longer than usual. Please be patient...
      </div>
    </div>
  </v-alert>
</template>

<script>
export default {
  data() {
    return {
      showTimeout: false,
      timeoutTimer: null,
    };
  },
  mounted() {
    this.timeoutTimer = setTimeout(() => {
      this.showTimeout = true;
    }, 15000);
  },
  beforeDestroy() {
    if (this.timeoutTimer) {
      clearTimeout(this.timeoutTimer);
    }
  },
};
</script>

<style scoped>
.thinking-text {
  font-weight: 500;
}

.dots {
  display: inline-flex;
}

.dot {
  opacity: 0;
  animation: dotFade 1.4s infinite;
  margin-left: 2px;
}

.dot:nth-child(2) {
  animation-delay: 0.2s;
}

.dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes dotFade {
  0%,
  100% {
    opacity: 0;
  }
  50% {
    opacity: 1;
  }
}

.timeout-message {
  font-size: 0.9em;
  opacity: 0.8;
  animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 0.8;
  }
}
</style>
